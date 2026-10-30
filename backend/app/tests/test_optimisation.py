from backend.app.optimisation.solver import TimetableRecoverySolver
from backend.app.tools.schedule_tools import find_affected_schedules
from backend.app.models.entities import Room

def test_ortools_solver_main_demo(db_session):
    # Find AI-LAB-01
    ai_lab_1 = db_session.query(Room).filter_by(code="AI-LAB-01").first()
    assert ai_lab_1 is not None

    # Find affected schedule for Monday 09:00-11:00
    affected = find_affected_schedules(
        db=db_session,
        resource_type="Room",
        resource_id=ai_lab_1.id,
        day_of_week="Monday",
        start_time="09:00",
        end_time="11:00"
    )
    assert len(affected) == 1
    assert affected[0]["course_code"] == "AI501-LAB"
    assert affected[0]["cohort_size"] == 36

    # Run solver
    solver = TimetableRecoverySolver(db=db_session, timeout_seconds=5)
    result = solver.solve(
        affected_schedules=affected,
        disrupted_room_id=ai_lab_1.id,
        day_of_week="Monday",
        start_time="09:00",
        end_time="11:00"
    )

    assert result["is_feasible"] is True
    assert result["solver_status"] in ["OPTIMAL", "FEASIBLE"]
    assert len(result["proposed_changes"]) == 1

    proposed = result["proposed_changes"][0]
    # Check that proposed room is either AI-LAB-02 or CS-LAB-03 (both have GPU & cap >= 36)
    # And specifically AI-LAB-02 is preferred because it's in the same building (Turing Centre)
    assert proposed["new_room_code"] in ["AI-LAB-02", "CS-LAB-03"]
    assert proposed["new_room_code"] != "AI-LAB-01"
    assert proposed["new_room_code"] != "CS-LAB-01"  # CS-LAB-01 lacks GPU
    assert proposed["new_room_code"] != "CLASS-302" # Capacity 30 < 36
    assert proposed["new_room_code"] != "CS-LAB-02"  # Occupied by CS503-LAB

    # Verify zero displacement in time: runs Monday 09:00-11:00
    assert proposed["new_day_of_week"] == "Monday"
    assert proposed["new_start_time"] == "09:00"
    assert proposed["new_end_time"] == "11:00"

def test_ortools_solver_empty_schedules(db_session):
    solver = TimetableRecoverySolver(db=db_session, timeout_seconds=5)
    result = solver.solve(
        affected_schedules=[],
        disrupted_room_id=999,
        day_of_week="Sunday",
        start_time="08:00",
        end_time="10:00"
    )
    assert result["is_feasible"] is True
    assert result["solver_status"] == "NO_ACTION_REQUIRED"
    assert len(result["proposed_changes"]) == 0
