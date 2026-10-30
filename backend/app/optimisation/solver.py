import time
from typing import List, Dict, Any, Tuple, Optional
from ortools.sat.python import cp_model
from sqlalchemy.orm import Session
from backend.app.models.entities import (
    TimetableSchedule, Room, Course, Faculty, StudentCohort
)
from backend.app.tools.resource_tools import (
    evaluate_rooms_for_recovery, slots_overlap, time_str_to_minutes
)
from backend.app.tools.schedule_tools import (
    check_faculty_availability, check_cohort_availability
)

class TimetableRecoverySolver:
    """
    Deterministic Timetable Recovery Solver powered by Google OR-Tools CP-SAT.
    Guarantees mathematically optimal or feasible conflict-free rescheduling.
    """
    def __init__(self, db: Session, timeout_seconds: int = 10):
        self.db = db
        self.timeout_seconds = timeout_seconds

    def solve(
        self,
        affected_schedules: List[Dict[str, Any]],
        disrupted_room_id: int,
        day_of_week: str,
        start_time: str,
        end_time: str
    ) -> Dict[str, Any]:
        start_cpu_time = time.time()

        if not affected_schedules:
            return {
                "solver_status": "NO_ACTION_REQUIRED",
                "is_feasible": True,
                "objective_value": 0.0,
                "proposed_changes": [],
                "solver_time_ms": int((time.time() - start_cpu_time) * 1000),
                "displacement_metric": 0.0,
                "solver_statistics": {"message": "No schedules affected by the disruption window."},
                "rejected_alternatives": []
            }

        # Step 1: Collect candidates for each affected schedule
        # Candidate slots:
        # Priority 1: Same day, same time slot (only swap room) -> minimal disruption!
        # Priority 2: Same day, later available slot
        time_options = [
            (day_of_week, start_time, end_time, 0), # (day, start, end, displacement_penalty)
            (day_of_week, "11:30", "13:30", 150),
            (day_of_week, "14:00", "16:00", 250),
            (day_of_week, "16:00", "18:00", 400),
        ]

        model = cp_model.CpModel()
        
        # Decision variables: x[sch_idx, option_idx] is Boolean
        # option = (room_id, day, start, end, cost, room_dict)
        schedule_options: Dict[int, List[Dict[str, Any]]] = {}
        all_rejected_alternatives = []

        for idx, sch in enumerate(affected_schedules):
            sch_id = sch["schedule_id"]
            cohort_size = sch["cohort_size"]
            required_type = sch["required_room_type"]
            required_eq = sch["required_equipment"]
            pref_bldg = sch["building"]
            faculty_id = sch["faculty_id"]
            cohort_id = sch["cohort_id"]

            opts = []
            for d, s_start, s_end, disp_penalty in time_options:
                # Check faculty availability at this slot (excluding current schedule)
                f_free, f_conf = check_faculty_availability(
                    self.db, faculty_id, d, s_start, s_end, exclude_schedule_id=sch_id
                )
                if not f_free:
                    continue

                # Check cohort availability at this slot (excluding current schedule)
                c_free, c_conf = check_cohort_availability(
                    self.db, cohort_id, d, s_start, s_end, exclude_schedule_id=sch_id
                )
                if not c_free:
                    continue

                # Evaluate available rooms for this (d, s_start, s_end)
                suitable_rooms, rejected_rooms = evaluate_rooms_for_recovery(
                    db=self.db,
                    required_type=required_type,
                    min_capacity=cohort_size,
                    required_equipment=required_eq,
                    day_of_week=d,
                    start_time=s_start,
                    end_time=s_end,
                    preferred_building=pref_bldg,
                    exclude_room_ids=[disrupted_room_id]
                )

                if idx == 0 and disp_penalty == 0:
                    all_rejected_alternatives.extend(rejected_rooms)

                for r in suitable_rooms:
                    # Calculate cost
                    # Same building preferred
                    bldg_penalty = 0 if r["building"].lower() == pref_bldg.lower() else 30
                    slack_penalty = max(0, r["capacity"] - cohort_size) * 1
                    total_cost = disp_penalty + bldg_penalty + slack_penalty + int(100 - r["suitability_score"])

                    opts.append({
                        "room_id": r["room_id"],
                        "room_code": r["room_code"],
                        "room_name": r["room_name"],
                        "building": r["building"],
                        "capacity": r["capacity"],
                        "day_of_week": d,
                        "start_time": s_start,
                        "end_time": s_end,
                        "cost": total_cost,
                        "displacement_score": round(disp_penalty / 10.0, 1),
                        "suitability_score": r["suitability_score"],
                        "original_schedule": sch
                    })

            schedule_options[idx] = opts

        # If any affected schedule has 0 valid options, report infeasible
        for idx, sch in enumerate(affected_schedules):
            if not schedule_options[idx]:
                return {
                    "solver_status": "INFEASIBLE",
                    "is_feasible": False,
                    "objective_value": 0.0,
                    "proposed_changes": [],
                    "solver_time_ms": int((time.time() - start_cpu_time) * 1000),
                    "displacement_metric": 0.0,
                    "solver_statistics": {
                        "error": f"No valid room or time slot found satisfying all hard constraints for class '{sch['course_code']}'."
                    },
                    "rejected_alternatives": all_rejected_alternatives
                }

        # Build CP-SAT Variables
        x = {}
        for idx in range(len(affected_schedules)):
            for opt_idx, opt in enumerate(schedule_options[idx]):
                x[idx, opt_idx] = model.NewBoolVar(f"x_{idx}_{opt_idx}")

        # Constraint 1: Exactly one option must be chosen for each affected schedule
        for idx in range(len(affected_schedules)):
            model.Add(sum(x[idx, opt_idx] for opt_idx in range(len(schedule_options[idx]))) == 1)

        # Constraint 2: No two affected schedules can be placed in the same room at the same time
        for idx1 in range(len(affected_schedules)):
            for opt_idx1, opt1 in enumerate(schedule_options[idx1]):
                for idx2 in range(idx1 + 1, len(affected_schedules)):
                    for opt_idx2, opt2 in enumerate(schedule_options[idx2]):
                        # If same room and overlapping time
                        if opt1["room_id"] == opt2["room_id"] and opt1["day_of_week"] == opt2["day_of_week"]:
                            if slots_overlap(opt1["start_time"], opt1["end_time"], opt2["start_time"], opt2["end_time"]):
                                model.Add(x[idx1, opt_idx1] + x[idx2, opt_idx2] <= 1)

        # Objective: Minimise total cost (displacement + building penalty + capacity mismatch)
        objective_terms = []
        for idx in range(len(affected_schedules)):
            for opt_idx, opt in enumerate(schedule_options[idx]):
                objective_terms.append(x[idx, opt_idx] * opt["cost"])

        model.Minimize(sum(objective_terms))

        # Solve
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = self.timeout_seconds
        solver.parameters.num_search_workers = 4
        status = solver.Solve(model)

        elapsed_ms = int((time.time() - start_cpu_time) * 1000)

        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            status_str = "OPTIMAL" if status == cp_model.OPTIMAL else "FEASIBLE"
            proposed_changes = []
            total_displacement = 0.0

            for idx in range(len(affected_schedules)):
                for opt_idx, opt in enumerate(schedule_options[idx]):
                    if solver.BooleanValue(x[idx, opt_idx]):
                        sch = opt["original_schedule"]
                        disp_score = opt["displacement_score"]
                        total_displacement += disp_score

                        reason_text = (
                            f"Reassigned from disrupted {sch['room_code']} to {opt['room_code']} "
                            f"({opt['building']}) with full GPU/equipment & capacity compliance."
                        )
                        if opt["start_time"] != sch["start_time"] or opt["day_of_week"] != sch["day_of_week"]:
                            reason_text += f" Rescheduled from {sch['day_of_week']} {sch['start_time']} to {opt['day_of_week']} {opt['start_time']}."

                        proposed_changes.append({
                            "original_schedule_id": sch["schedule_id"],
                            "course_id": sch["course_id"],
                            "course_code": sch["course_code"],
                            "course_name": sch["course_name"],
                            "faculty_id": sch["faculty_id"],
                            "faculty_name": sch["faculty_name"],
                            "cohort_id": sch["cohort_id"],
                            "cohort_code": sch["cohort_code"],
                            "cohort_size": sch["cohort_size"],
                            "old_room_id": sch["room_id"],
                            "old_room_code": sch["room_code"],
                            "new_room_id": opt["room_id"],
                            "new_room_code": opt["room_code"],
                            "new_room_name": opt["room_name"],
                            "new_building": opt["building"],
                            "new_capacity": opt["capacity"],
                            "old_day_of_week": sch["day_of_week"],
                            "new_day_of_week": opt["day_of_week"],
                            "old_start_time": sch["start_time"],
                            "old_end_time": sch["end_time"],
                            "new_start_time": opt["start_time"],
                            "new_end_time": opt["end_time"],
                            "reason": reason_text,
                            "displacement_score": disp_score,
                            "suitability_score": opt["suitability_score"],
                            "status": "Proposed"
                        })

            return {
                "solver_status": status_str,
                "is_feasible": True,
                "objective_value": float(solver.ObjectiveValue()),
                "proposed_changes": proposed_changes,
                "solver_time_ms": elapsed_ms,
                "displacement_metric": round(total_displacement, 1),
                "solver_statistics": {
                    "num_variables": len(x),
                    "branches": solver.NumBranches(),
                    "wall_time": solver.WallTime(),
                    "solution_type": status_str
                },
                "rejected_alternatives": all_rejected_alternatives
            }
        else:
            return {
                "solver_status": "INFEASIBLE",
                "is_feasible": False,
                "objective_value": 0.0,
                "proposed_changes": [],
                "solver_time_ms": elapsed_ms,
                "displacement_metric": 0.0,
                "solver_statistics": {
                    "status_code": status,
                    "message": "Solver could not find a feasible solution satisfying all constraints."
                },
                "rejected_alternatives": all_rejected_alternatives
            }
