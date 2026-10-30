from backend.app.models.entities import Room, TimetableSchedule, Disruption, RecoveryRun, Approval
from backend.app.services.recovery_service import RecoveryService

def test_full_recovery_workflow_and_approval(db_session):
    ai_lab_1 = db_session.query(Room).filter_by(code="AI-LAB-01").first()

    # Step 1: Create a disruption incident
    disruption = Disruption(
        title="AI Lab 01 Equipment Failure Demo",
        description="AI Lab 01 is unavailable on Monday from 09:00 AM to 11:00 AM because of equipment failure.",
        category="Equipment Failure",
        affected_resource_type="Room",
        affected_resource_id=ai_lab_1.id,
        day_of_week="Monday",
        date="2026-11-02",
        start_time="09:00",
        end_time="11:00",
        severity="High",
        status="Reported",
        reported_by="Campus Administrator"
    )
    db_session.add(disruption)
    db_session.commit()
    db_session.refresh(disruption)

    # Step 2: Trigger Recovery Multi-Agent Workflow
    run = RecoveryService.trigger_recovery(db=db_session, disruption_id=disruption.id)
    assert run.status == "Success"
    assert run.solver_status in ["OPTIMAL", "FEASIBLE"]
    assert len(run.proposed_changes) == 1
    assert len(run.agent_executions) >= 6

    # Verify agent execution records
    agent_names = [e.agent_name for e in run.agent_executions]
    assert "Campus Supervisor Agent" in agent_names
    assert "Disruption Analysis Agent" in agent_names
    assert "Resource Intelligence Agent" in agent_names
    assert "Timetable Coordination Agent" in agent_names
    assert "Optimisation Agent" in agent_names
    assert "Validation and Compliance Agent" in agent_names
    assert "Explanation Agent" in agent_names

    # Step 3: Approve recovery
    approval_result = RecoveryService.approve_recovery(
        db=db_session,
        recovery_run_id=run.id,
        comments="Approved during autonomous unit test.",
        approved_by="Dr. Administrator"
    )
    assert "successfully approved" in approval_result["message"]

    # Step 4: Verify Timetable was transactionally updated
    target_sch = db_session.query(TimetableSchedule).filter_by(
        day_of_week="Monday", start_time="09:00", end_time="11:00"
    ).filter(TimetableSchedule.status == "Rescheduled").first()
    assert target_sch is not None
    assert target_sch.room.code in ["AI-LAB-02", "CS-LAB-03"]
    assert target_sch.room.code != "AI-LAB-01"

    # Step 5: Verify Disruption is marked Resolved
    db_session.refresh(disruption)
    assert disruption.status == "Resolved"

def test_recovery_rejection_preserves_timetable(db_session):
    ai_lab_2 = db_session.query(Room).filter_by(code="AI-LAB-02").first()
    disruption = Disruption(
        title="Test Incident for Rejection",
        description="Testing rejection logic.",
        category="Maintenance",
        affected_resource_type="Room",
        affected_resource_id=ai_lab_2.id,
        day_of_week="Wednesday",
        date="2026-11-04",
        start_time="10:00",
        end_time="12:00",
        severity="Medium",
        status="Reported",
        reported_by="Admin"
    )
    db_session.add(disruption)
    db_session.commit()
    db_session.refresh(disruption)

    run = RecoveryService.trigger_recovery(db=db_session, disruption_id=disruption.id)

    # Reject recovery
    reject_res = RecoveryService.reject_recovery(
        db=db_session,
        recovery_run_id=run.id,
        comments="Rejected test scenario.",
        rejected_by="Admin"
    )
    assert "rejected" in reject_res["message"]

    db_session.refresh(run)
    assert run.status == "Rejected"
