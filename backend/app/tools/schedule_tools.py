from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from backend.app.models.entities import (
    TimetableSchedule, Course, Faculty, StudentCohort, Room
)
from backend.app.tools.resource_tools import slots_overlap

def find_affected_schedules(
    db: Session,
    resource_type: str,
    resource_id: int,
    day_of_week: str,
    start_time: str,
    end_time: str
) -> List[Dict[str, Any]]:
    """
    Finds all scheduled classes affected by a disruption.
    """
    query = db.query(TimetableSchedule).filter(
        TimetableSchedule.day_of_week == day_of_week,
        TimetableSchedule.status.in_(["Scheduled", "Rescheduled"])
    )

    if resource_type.lower() == "room":
        query = query.filter(TimetableSchedule.room_id == resource_id)
    elif resource_type.lower() == "faculty":
        query = query.filter(TimetableSchedule.faculty_id == resource_id)
    elif resource_type.lower() in ["cohort", "student_cohort"]:
        query = query.filter(TimetableSchedule.cohort_id == resource_id)

    candidates = query.all()
    affected = []

    for sch in candidates:
        if slots_overlap(start_time, end_time, sch.start_time, sch.end_time):
            course = db.query(Course).filter(Course.id == sch.course_id).first()
            faculty = db.query(Faculty).filter(Faculty.id == sch.faculty_id).first()
            cohort = db.query(StudentCohort).filter(StudentCohort.id == sch.cohort_id).first()
            room = db.query(Room).filter(Room.id == sch.room_id).first()

            affected.append({
                "schedule_id": sch.id,
                "course_id": sch.course_id,
                "course_code": course.code if course else "UNKNOWN",
                "course_name": course.name if course else "Unknown Course",
                "required_room_type": course.required_room_type if course else "Classroom",
                "required_equipment": course.required_equipment if course else [],
                "faculty_id": sch.faculty_id,
                "faculty_name": faculty.name if faculty else "Unknown Faculty",
                "cohort_id": sch.cohort_id,
                "cohort_code": cohort.code if cohort else "UNKNOWN",
                "cohort_size": cohort.size if cohort else 30,
                "room_id": sch.room_id,
                "room_code": room.code if room else "UNKNOWN",
                "room_name": room.name if room else "Unknown Room",
                "building": room.building if room else "Campus Block",
                "day_of_week": sch.day_of_week,
                "start_time": sch.start_time,
                "end_time": sch.end_time,
                "academic_term": sch.academic_term
            })

    return affected

def check_faculty_availability(
    db: Session,
    faculty_id: int,
    day_of_week: str,
    start_time: str,
    end_time: str,
    exclude_schedule_id: Optional[int] = None
) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Checks if a faculty member has any conflicting class in the specified slot.
    Returns (is_available, conflict_schedule_dict)
    """
    schedules = db.query(TimetableSchedule).filter(
        TimetableSchedule.faculty_id == faculty_id,
        TimetableSchedule.day_of_week == day_of_week,
        TimetableSchedule.status.in_(["Scheduled", "Rescheduled"])
    ).all()

    for sch in schedules:
        if exclude_schedule_id and sch.id == exclude_schedule_id:
            continue
        if slots_overlap(start_time, end_time, sch.start_time, sch.end_time):
            return False, {
                "schedule_id": sch.id,
                "course_id": sch.course_id,
                "start_time": sch.start_time,
                "end_time": sch.end_time
            }
    return True, None

def check_cohort_availability(
    db: Session,
    cohort_id: int,
    day_of_week: str,
    start_time: str,
    end_time: str,
    exclude_schedule_id: Optional[int] = None
) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Checks if a student cohort has any conflicting class in the specified slot.
    Returns (is_available, conflict_schedule_dict)
    """
    schedules = db.query(TimetableSchedule).filter(
        TimetableSchedule.cohort_id == cohort_id,
        TimetableSchedule.day_of_week == day_of_week,
        TimetableSchedule.status.in_(["Scheduled", "Rescheduled"])
    ).all()

    for sch in schedules:
        if exclude_schedule_id and sch.id == exclude_schedule_id:
            continue
        if slots_overlap(start_time, end_time, sch.start_time, sch.end_time):
            return False, {
                "schedule_id": sch.id,
                "course_id": sch.course_id,
                "start_time": sch.start_time,
                "end_time": sch.end_time
            }
    return True, None

def get_candidate_time_slots(
    db: Session,
    cohort_id: int,
    faculty_id: int,
    duration_hours: int = 2,
    target_day: str = "Monday"
) -> List[Dict[str, Any]]:
    """
    Finds available 2-hour slots on the target day where both faculty and cohort are free.
    Standard academic slots: 09:00-11:00, 11:30-13:30, 14:00-16:00, 16:00-18:00
    """
    standard_slots = [
        ("09:00", "11:00"),
        ("11:30", "13:30"),
        ("14:00", "16:00"),
        ("16:00", "18:00"),
    ]
    candidates = []
    for s_start, s_end in standard_slots:
        f_free, _ = check_faculty_availability(db, faculty_id, target_day, s_start, s_end)
        c_free, _ = check_cohort_availability(db, cohort_id, target_day, s_start, s_end)
        if f_free and c_free:
            candidates.append({
                "day_of_week": target_day,
                "start_time": s_start,
                "end_time": s_end,
                "both_available": True
            })
    return candidates
