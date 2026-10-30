from backend.app.services.validation_service import IndependentValidationService
from backend.app.models.entities import Room, Course, StudentCohort, Faculty, TimetableSchedule

def test_independent_validation_valid_case(db_session):
    ai_lab_2 = db_session.query(Room).filter_by(code="AI-LAB-02").first()
    sch = db_session.query(TimetableSchedule).filter_by(day_of_week="Monday", start_time="09:00").first()

    validator = IndependentValidationService(db=db_session)
    valid_proposal = [{
        "original_schedule_id": sch.id,
        "course_id": sch.course_id,
        "faculty_id": sch.faculty_id,
        "cohort_id": sch.cohort_id,
        "new_room_id": ai_lab_2.id,
        "new_room_code": ai_lab_2.code,
        "new_day_of_week": "Monday",
        "new_start_time": "09:00",
        "new_end_time": "11:00",
        "cohort_size": 36,
        "required_room_type": "Computer Lab",
        "required_equipment": ["GPU Workstations"]
    }]

    result = validator.validate_proposed_changes(valid_proposal, disrupted_room_id=sch.room_id)
    assert result.is_valid is True
    assert result.compliance_score == 100.0
    assert len(result.violations) == 0

def test_independent_validation_disrupted_room_reused(db_session):
    sch = db_session.query(TimetableSchedule).filter_by(day_of_week="Monday", start_time="09:00").first()
    validator = IndependentValidationService(db=db_session)

    # Trying to reassign to the exact same disrupted room
    invalid_proposal = [{
        "original_schedule_id": sch.id,
        "course_id": sch.course_id,
        "faculty_id": sch.faculty_id,
        "cohort_id": sch.cohort_id,
        "new_room_id": sch.room_id,
        "new_room_code": "AI-LAB-01",
        "new_day_of_week": "Monday",
        "new_start_time": "09:00",
        "new_end_time": "11:00",
        "cohort_size": 36,
        "required_room_type": "Computer Lab",
        "required_equipment": ["GPU Workstations"]
    }]

    result = validator.validate_proposed_changes(invalid_proposal, disrupted_room_id=sch.room_id)
    assert result.is_valid is False
    assert any("disrupted" in v.details.lower() for v in result.violations)

def test_independent_validation_capacity_shortage(db_session):
    small_room = db_session.query(Room).filter_by(code="CLASS-302").first() # cap: 30
    sch = db_session.query(TimetableSchedule).filter_by(day_of_week="Monday", start_time="09:00").first()
    validator = IndependentValidationService(db=db_session)

    invalid_proposal = [{
        "original_schedule_id": sch.id,
        "course_id": sch.course_id,
        "faculty_id": sch.faculty_id,
        "cohort_id": sch.cohort_id,
        "new_room_id": small_room.id,
        "new_room_code": small_room.code,
        "new_day_of_week": "Monday",
        "new_start_time": "09:00",
        "new_end_time": "11:00",
        "cohort_size": 36, # 36 > 30!
        "required_room_type": "Classroom",
        "required_equipment": []
    }]

    result = validator.validate_proposed_changes(invalid_proposal, disrupted_room_id=999)
    assert result.is_valid is False
    assert any("capacity" in v.details.lower() for v in result.violations)
