from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from backend.app.models.entities import (
    TimetableSchedule, Room, Course, Faculty, StudentCohort
)
from backend.app.tools.resource_tools import slots_overlap
from backend.app.schemas.agents import ValidationResult, ValidationViolation

class IndependentValidationService:
    """
    Authoritative, deterministic compliance engine that independently checks
    all proposed timetable changes against physical and organizational campus constraints.
    """
    def __init__(self, db: Session):
        self.db = db

    def validate_proposed_changes(
        self,
        proposed_changes: List[Dict[str, Any]],
        disrupted_room_id: int = None
    ) -> ValidationResult:
        violations: List[ValidationViolation] = []
        checked_constraints = [
            "No Room Double-Booking",
            "No Faculty Overlapping Classes",
            "No Cohort Overlapping Classes",
            "Room Capacity Greater Than Cohort Size",
            "Mandatory Equipment Availability",
            "Room Type Suitability",
            "Disrupted/Maintenance Room Exclusion"
        ]

        if not proposed_changes:
            return ValidationResult(
                is_valid=True,
                checked_constraints=checked_constraints,
                violations=[],
                compliance_score=100.0,
                validation_status="PASSED",
                is_deterministic=True
            )

        # Pre-fetch existing unaffected schedules from the database
        active_schedules = self.db.query(TimetableSchedule).filter(
            TimetableSchedule.status.in_(["Scheduled", "Rescheduled"])
        ).all()

        # Build a temporary timetable overlay representing proposed changes
        # Map: original_schedule_id -> proposed change
        prop_map = {p["original_schedule_id"]: p for p in proposed_changes}

        # Check internal conflicts among proposed changes themselves
        for i in range(len(proposed_changes)):
            p1 = proposed_changes[i]
            for j in range(i + 1, len(proposed_changes)):
                p2 = proposed_changes[j]

                # Check same room overlap
                if p1["new_room_id"] == p2["new_room_id"] and p1["new_day_of_week"] == p2["new_day_of_week"]:
                    if slots_overlap(p1["new_start_time"], p1["new_end_time"], p2["new_start_time"], p2["new_end_time"]):
                        violations.append(ValidationViolation(
                            constraint_name="No Room Double-Booking",
                            severity="CRITICAL",
                            details=f"Proposed room conflict: Room '{p1.get('new_room_code')}' assigned simultaneously to Course {p1.get('course_code')} and {p2.get('course_code')}.",
                            schedule_id=p1.get("original_schedule_id"),
                            room_id=p1.get("new_room_id")
                        ))

                # Check same faculty overlap
                if p1["faculty_id"] == p2["faculty_id"] and p1["new_day_of_week"] == p2["new_day_of_week"]:
                    if slots_overlap(p1["new_start_time"], p1["new_end_time"], p2["new_start_time"], p2["new_end_time"]):
                        violations.append(ValidationViolation(
                            constraint_name="No Faculty Overlapping Classes",
                            severity="CRITICAL",
                            details=f"Faculty conflict: {p1.get('faculty_name')} assigned to overlapping classes at {p1.get('new_start_time')}.",
                            schedule_id=p1.get("original_schedule_id")
                        ))

                # Check same cohort overlap
                if p1["cohort_id"] == p2["cohort_id"] and p1["new_day_of_week"] == p2["new_day_of_week"]:
                    if slots_overlap(p1["new_start_time"], p1["new_end_time"], p2["new_start_time"], p2["new_end_time"]):
                        violations.append(ValidationViolation(
                            constraint_name="No Cohort Overlapping Classes",
                            severity="CRITICAL",
                            details=f"Cohort conflict: {p1.get('cohort_code')} assigned to overlapping classes at {p1.get('new_start_time')}.",
                            schedule_id=p1.get("original_schedule_id")
                        ))

        # Check each proposed change against unaffected schedules & physical room specs
        for prop in proposed_changes:
            new_room_id = prop["new_room_id"]
            new_day = prop["new_day_of_week"]
            new_start = prop["new_start_time"]
            new_end = prop["new_end_time"]
            orig_id = prop["original_schedule_id"]
            course_id = prop["course_id"]
            faculty_id = prop["faculty_id"]
            cohort_id = prop["cohort_id"]

            room = self.db.query(Room).filter(Room.id == new_room_id).first()
            course = self.db.query(Course).filter(Course.id == course_id).first()
            cohort = self.db.query(StudentCohort).filter(StudentCohort.id == cohort_id).first()
            faculty = self.db.query(Faculty).filter(Faculty.id == faculty_id).first()

            # Check Disrupted Room Exclusion
            if disrupted_room_id and new_room_id == disrupted_room_id:
                violations.append(ValidationViolation(
                    constraint_name="Disrupted/Maintenance Room Exclusion",
                    severity="CRITICAL",
                    details=f"Proposed room '{room.code if room else new_room_id}' is the disrupted room under maintenance!",
                    schedule_id=orig_id,
                    room_id=new_room_id
                ))

            if room and not room.is_available:
                violations.append(ValidationViolation(
                    constraint_name="Disrupted/Maintenance Room Exclusion",
                    severity="CRITICAL",
                    details=f"Room '{room.code}' is marked unavailable in campus inventory.",
                    schedule_id=orig_id,
                    room_id=new_room_id
                ))

            # Check Capacity
            cohort_size = cohort.size if cohort else prop.get("cohort_size", 30)
            if room and room.capacity < cohort_size:
                violations.append(ValidationViolation(
                    constraint_name="Room Capacity Greater Than Cohort Size",
                    severity="CRITICAL",
                    details=f"Room capacity violation: Room '{room.code}' capacity ({room.capacity}) < Cohort size ({cohort_size}).",
                    schedule_id=orig_id,
                    room_id=new_room_id
                ))

            # Check Room Type
            req_type = course.required_room_type if course else prop.get("required_room_type", "Computer Lab")
            if room and room.room_type.lower() != req_type.lower():
                violations.append(ValidationViolation(
                    constraint_name="Room Type Suitability",
                    severity="CRITICAL",
                    details=f"Room type mismatch: Course requires '{req_type}', but '{room.code}' is '{room.room_type}'.",
                    schedule_id=orig_id,
                    room_id=new_room_id
                ))

            # Check Equipment
            req_eq = course.required_equipment if course else prop.get("required_equipment", [])
            req_set = set(e.strip().lower() for e in (req_eq or []))
            room_set = set(e.strip().lower() for e in (room.equipment if room else []))
            missing_eq = req_set - room_set
            if missing_eq:
                violations.append(ValidationViolation(
                    constraint_name="Mandatory Equipment Availability",
                    severity="CRITICAL",
                    details=f"Missing equipment in room '{room.code if room else new_room_id}': {', '.join(missing_eq).title()}.",
                    schedule_id=orig_id,
                    room_id=new_room_id
                ))

            # Check against unaffected schedules
            for sch in active_schedules:
                if sch.id == orig_id or sch.id in prop_map:
                    continue  # already replaced by proposal
                if sch.day_of_week != new_day:
                    continue
                if not slots_overlap(new_start, new_end, sch.start_time, sch.end_time):
                    continue

                # Room clash
                if sch.room_id == new_room_id:
                    violations.append(ValidationViolation(
                        constraint_name="No Room Double-Booking",
                        severity="CRITICAL",
                        details=f"Room clash with existing class: Room '{room.code if room else new_room_id}' already booked for Schedule #{sch.id} ({sch.start_time}-{sch.end_time}).",
                        schedule_id=orig_id,
                        room_id=new_room_id
                    ))

                # Faculty clash
                if sch.faculty_id == faculty_id:
                    violations.append(ValidationViolation(
                        constraint_name="No Faculty Overlapping Classes",
                        severity="CRITICAL",
                        details=f"Faculty clash: {faculty.name if faculty else faculty_id} already has a class in Schedule #{sch.id} ({sch.start_time}-{sch.end_time}).",
                        schedule_id=orig_id
                    ))

                # Cohort clash
                if sch.cohort_id == cohort_id:
                    violations.append(ValidationViolation(
                        constraint_name="No Cohort Overlapping Classes",
                        severity="CRITICAL",
                        details=f"Cohort clash: {cohort.code if cohort else cohort_id} already has a class in Schedule #{sch.id} ({sch.start_time}-{sch.end_time}).",
                        schedule_id=orig_id
                    ))

        is_valid = len(violations) == 0
        status = "PASSED" if is_valid else "FAILED"
        score = 100.0 if is_valid else max(0.0, 100.0 - (len(violations) * 25.0))

        return ValidationResult(
            is_valid=is_valid,
            checked_constraints=checked_constraints,
            violations=violations,
            compliance_score=score,
            validation_status=status,
            is_deterministic=True
        )
