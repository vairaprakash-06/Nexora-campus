from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.entities import (
    TimetableSchedule, Course, Faculty, StudentCohort, Room, Department
)
from backend.app.schemas.api import TimetableScheduleOut

router = APIRouter(prefix="/schedules", tags=["Schedules"])

@router.get("", response_model=List[TimetableScheduleOut])
def get_schedules(
    day_of_week: Optional[str] = Query(None),
    department_id: Optional[int] = Query(None),
    faculty_id: Optional[int] = Query(None),
    cohort_id: Optional[int] = Query(None),
    room_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(TimetableSchedule)

    if day_of_week:
        query = query.filter(TimetableSchedule.day_of_week == day_of_week)
    if faculty_id:
        query = query.filter(TimetableSchedule.faculty_id == faculty_id)
    if cohort_id:
        query = query.filter(TimetableSchedule.cohort_id == cohort_id)
    if room_id:
        query = query.filter(TimetableSchedule.room_id == room_id)
    if status:
        query = query.filter(TimetableSchedule.status == status)

    schedules = query.order_by(TimetableSchedule.day_of_week, TimetableSchedule.start_time).all()

    result = []
    for s in schedules:
        c = db.query(Course).filter(Course.id == s.course_id).first()
        f = db.query(Faculty).filter(Faculty.id == s.faculty_id).first()
        co = db.query(StudentCohort).filter(StudentCohort.id == s.cohort_id).first()
        r = db.query(Room).filter(Room.id == s.room_id).first()

        if department_id and c and c.department_id != department_id:
            continue

        item = TimetableScheduleOut(
            id=s.id,
            course_id=s.course_id,
            faculty_id=s.faculty_id,
            cohort_id=s.cohort_id,
            room_id=s.room_id,
            day_of_week=s.day_of_week,
            start_time=s.start_time,
            end_time=s.end_time,
            status=s.status,
            academic_term=s.academic_term,
            course_code=c.code if c else "N/A",
            course_name=c.name if c else "N/A",
            faculty_name=f.name if f else "N/A",
            cohort_code=co.code if co else "N/A",
            cohort_size=co.size if co else 0,
            room_code=r.code if r else "N/A",
            room_name=r.name if r else "N/A",
            building=r.building if r else "N/A",
            required_equipment=c.required_equipment if c else []
        )
        result.append(item)

    return result

@router.get("/filters")
def get_schedule_filters(db: Session = Depends(get_db)):
    departments = db.query(Department).all()
    faculties = db.query(Faculty).all()
    cohorts = db.query(StudentCohort).all()
    rooms = db.query(Room).all()

    return {
        "departments": [{"id": d.id, "name": d.name, "code": d.code} for d in departments],
        "faculties": [{"id": f.id, "name": f.name} for f in faculties],
        "cohorts": [{"id": c.id, "name": c.name, "code": c.code} for c in cohorts],
        "rooms": [{"id": r.id, "name": r.name, "code": r.code, "building": r.building} for r in rooms],
        "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    }
