import json
from tools import Tool
from backend.app.core.database import SessionLocal
from backend.app.models.entities import Room, TimetableSchedule, Disruption
from backend.app.tools.schedule_tools import find_affected_schedules
from backend.app.optimisation.solver import TimetableRecoverySolver
from backend.app.services.validation_service import IndependentValidationService

class ScanCampusDisruptions(Tool):
    name = "scan_campus_disruptions"
    description = "Scans campus rooms and active timetable schedules to identify affected classes and blast radius for a given room or day."
    args_doc = '{"room_code": "optional string e.g. AI-LAB-01", "day_of_week": "e.g. Monday", "start_time": "09:00", "end_time": "11:00"}'

    def execute(self, room_code: str = "AI-LAB-01", day_of_week: str = "Monday", start_time: str = "09:00", end_time: str = "11:00"):
        db = SessionLocal()
        try:
            room = db.query(Room).filter(Room.code == room_code).first()
            if not room:
                return f"Room {room_code} not found in campus inventory."
            
            affected = find_affected_schedules(
                db=db,
                resource_type="Room",
                resource_id=room.id,
                day_of_week=day_of_week,
                start_time=start_time,
                end_time=end_time
            )

            if not affected:
                return f"No classes scheduled in {room_code} on {day_of_week} between {start_time}-{end_time}."

            res = {
                "room_code": room.code,
                "room_name": room.name,
                "building": room.building,
                "affected_classes_count": len(affected),
                "affected_classes": [
                    {
                        "course_code": a["course_code"],
                        "course_name": a["course_name"],
                        "faculty": a["faculty_name"],
                        "cohort": a["cohort_code"],
                        "students_count": a["cohort_size"],
                        "required_equipment": a["required_equipment"]
                    }
                    for a in affected
                ]
            }
            return json.dumps(res, indent=2)
        finally:
            db.close()


class SolveCampusRecovery(Tool):
    name = "solve_campus_recovery"
    description = "Deterministically runs Google OR-Tools CP-SAT solver to formulate optimal conflict-free room reallocation for a disrupted room."
    args_doc = '{"disrupted_room_code": "e.g. AI-LAB-01", "day_of_week": "Monday", "start_time": "09:00", "end_time": "11:00"}'

    def execute(self, disrupted_room_code: str = "AI-LAB-01", day_of_week: str = "Monday", start_time: str = "09:00", end_time: str = "11:00"):
        db = SessionLocal()
        try:
            room = db.query(Room).filter(Room.code == disrupted_room_code).first()
            if not room:
                return f"Room {disrupted_room_code} not found."

            affected = find_affected_schedules(
                db=db,
                resource_type="Room",
                resource_id=room.id,
                day_of_week=day_of_week,
                start_time=start_time,
                end_time=end_time
            )

            solver = TimetableRecoverySolver(db=db, timeout_seconds=10)
            solve_res = solver.solve(
                affected_schedules=affected,
                disrupted_room_id=room.id,
                day_of_week=day_of_week,
                start_time=start_time,
                end_time=end_time
            )

            validator = IndependentValidationService(db=db)
            val_res = validator.validate_proposed_changes(
                proposed_changes=solve_res["proposed_changes"],
                disrupted_room_id=room.id
            )

            output = {
                "solver_status": solve_res["solver_status"],
                "is_feasible": solve_res["is_feasible"],
                "objective_score": solve_res["objective_value"],
                "solve_time_ms": solve_res["solver_time_ms"],
                "displacement_score": solve_res["displacement_metric"],
                "proposed_reallocations": [
                    {
                        "course": p["course_code"],
                        "reassigned_room": p["new_room_code"],
                        "room_name": p["new_room_name"],
                        "building": p["new_building"],
                        "slot": f"{p['new_day_of_week']} {p['new_start_time']}-{p['new_end_time']}",
                        "reason": p["reason"]
                    }
                    for p in solve_res["proposed_changes"]
                ],
                "independent_validation": {
                    "is_valid": val_res.is_valid,
                    "compliance_score": val_res.compliance_score,
                    "violations": [v.dict() for v in val_res.violations]
                },
                "disqualified_alternatives": [
                    f"{r['room_code']}: {r['rejection_reason']}"
                    for r in solve_res.get("rejected_alternatives", [])[:4]
                ]
            }
            return json.dumps(output, indent=2)
        finally:
            db.close()
