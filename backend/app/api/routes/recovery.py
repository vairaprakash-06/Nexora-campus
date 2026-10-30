from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.entities import (
    RecoveryRun, Disruption, ProposedScheduleChange, TimetableSchedule,
    Course, Faculty, StudentCohort, Room, AgentExecution
)
from backend.app.schemas.api import (
    RecoveryRunOut, ApprovalRequest, ProposedScheduleChangeOut, DisruptionOut, AgentExecutionOut
)
from backend.app.services.recovery_service import RecoveryService

router = APIRouter(prefix="/recovery", tags=["Recovery"])

def enrich_recovery_run(run: RecoveryRun, db: Session) -> RecoveryRunOut:
    disruption = db.query(Disruption).filter(Disruption.id == run.disruption_id).first()
    disruption_out = None
    if disruption:
        res_name = f"Resource #{disruption.affected_resource_id}"
        if disruption.affected_resource_type.lower() == "room":
            r = db.query(Room).filter(Room.id == disruption.affected_resource_id).first()
            if r:
                res_name = f"{r.code} - {r.name}"
        disruption_out = DisruptionOut(
            id=disruption.id,
            title=disruption.title,
            description=disruption.description,
            category=disruption.category,
            affected_resource_type=disruption.affected_resource_type,
            affected_resource_id=disruption.affected_resource_id,
            day_of_week=disruption.day_of_week,
            date=disruption.date,
            start_time=disruption.start_time,
            end_time=disruption.end_time,
            severity=disruption.severity,
            status=disruption.status,
            reported_by=disruption.reported_by,
            created_at=disruption.created_at,
            updated_at=disruption.updated_at,
            affected_resource_name=res_name
        )

    # Enrich proposed changes
    changes = db.query(ProposedScheduleChange).filter(
        ProposedScheduleChange.recovery_run_id == run.id
    ).all()

    enriched_changes = []
    for c in changes:
        sch = db.query(TimetableSchedule).filter(TimetableSchedule.id == c.original_schedule_id).first()
        co = db.query(Course).filter(Course.id == sch.course_id).first() if sch else None
        f = db.query(Faculty).filter(Faculty.id == sch.faculty_id).first() if sch else None
        cohort = db.query(StudentCohort).filter(StudentCohort.id == sch.cohort_id).first() if sch else None
        old_r = db.query(Room).filter(Room.id == sch.room_id).first() if sch else None
        new_r = db.query(Room).filter(Room.id == c.new_room_id).first()

        enriched_changes.append(ProposedScheduleChangeOut(
            id=c.id,
            recovery_run_id=c.recovery_run_id,
            original_schedule_id=c.original_schedule_id,
            new_room_id=c.new_room_id,
            new_day_of_week=c.new_day_of_week,
            new_start_time=c.new_start_time,
            new_end_time=c.new_end_time,
            reason=c.reason,
            displacement_score=c.displacement_score,
            status=c.status,
            course_code=co.code if co else "N/A",
            course_name=co.name if co else "N/A",
            faculty_name=f.name if f else "N/A",
            cohort_code=cohort.code if cohort else "N/A",
            cohort_size=cohort.size if cohort else 0,
            old_room_code=old_r.code if old_r else "N/A",
            new_room_code=new_r.code if new_r else "N/A",
            new_room_name=new_r.name if new_r else "N/A",
            old_day_of_week=sch.day_of_week if sch else "N/A",
            old_start_time=sch.start_time if sch else "N/A",
            old_end_time=sch.end_time if sch else "N/A"
        ))

    # Agent executions
    executions = db.query(AgentExecution).filter(
        AgentExecution.recovery_run_id == run.id
    ).order_by(AgentExecution.id.asc()).all()

    return RecoveryRunOut(
        id=run.id,
        disruption_id=run.disruption_id,
        status=run.status,
        strategy=run.strategy,
        objective_value=run.objective_value,
        solver_status=run.solver_status,
        execution_time_ms=run.execution_time_ms,
        agent_summary=run.agent_summary,
        created_at=run.created_at,
        updated_at=run.updated_at,
        disruption=disruption_out,
        proposed_changes=enriched_changes,
        agent_executions=[AgentExecutionOut.from_orm(e) for e in executions]
    )

@router.post("/run/{disruption_id}", response_model=RecoveryRunOut)
def trigger_recovery_run(disruption_id: int, db: Session = Depends(get_db)):
    run = RecoveryService.trigger_recovery(db=db, disruption_id=disruption_id)
    return enrich_recovery_run(run, db)

@router.get("/runs", response_model=List[RecoveryRunOut])
def get_all_recovery_runs(db: Session = Depends(get_db)):
    runs = db.query(RecoveryRun).order_by(RecoveryRun.created_at.desc()).all()
    return [enrich_recovery_run(r, db) for r in runs]

@router.get("/runs/{run_id}", response_model=RecoveryRunOut)
def get_recovery_run_by_id(run_id: int, db: Session = Depends(get_db)):
    run = db.query(RecoveryRun).filter(RecoveryRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Recovery run not found")
    return enrich_recovery_run(run, db)

@router.post("/approve/{run_id}")
def approve_recovery(
    run_id: int,
    payload: ApprovalRequest = ApprovalRequest(),
    db: Session = Depends(get_db)
):
    return RecoveryService.approve_recovery(
        db=db,
        recovery_run_id=run_id,
        comments=payload.comments,
        approved_by=payload.approved_by
    )

@router.post("/reject/{run_id}")
def reject_recovery(
    run_id: int,
    payload: ApprovalRequest = ApprovalRequest(),
    db: Session = Depends(get_db)
):
    return RecoveryService.reject_recovery(
        db=db,
        recovery_run_id=run_id,
        comments=payload.comments,
        rejected_by=payload.approved_by
    )
