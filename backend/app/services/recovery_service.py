import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from backend.app.models.entities import (
    Disruption, RecoveryRun, ProposedScheduleChange,
    TimetableSchedule, Room, Approval, Course, Faculty, StudentCohort
)
from backend.app.schemas.agents import AgentWorkflowState
from backend.app.agents.graph import execute_agent_workflow
from backend.app.services.validation_service import IndependentValidationService
from backend.app.services.audit_service import log_audit_event

class RecoveryService:
    @staticmethod
    def trigger_recovery(db: Session, disruption_id: int) -> RecoveryRun:
        disruption = db.query(Disruption).filter(Disruption.id == disruption_id).first()
        if not disruption:
            raise HTTPException(status_code=404, detail="Disruption incident not found")

        # Mark disruption as analyzing
        disruption.status = "Analyzing"
        db.commit()

        # Create new RecoveryRun
        recovery_run = RecoveryRun(
            disruption_id=disruption.id,
            status="Running",
            strategy="LangGraph 7-Agent OR-Tools CP-SAT Workflow"
        )
        db.add(recovery_run)
        db.commit()
        db.refresh(recovery_run)

        # Get affected resource name
        res_name = f"Resource #{disruption.affected_resource_id}"
        if disruption.affected_resource_type.lower() == "room":
            room = db.query(Room).filter(Room.id == disruption.affected_resource_id).first()
            if room:
                res_name = f"{room.code} ({room.name})"

        disruption_dict = {
            "id": disruption.id,
            "title": disruption.title,
            "description": disruption.description,
            "category": disruption.category,
            "affected_resource_type": disruption.affected_resource_type,
            "affected_resource_id": disruption.affected_resource_id,
            "affected_resource_name": res_name,
            "day_of_week": disruption.day_of_week,
            "date": disruption.date,
            "start_time": disruption.start_time,
            "end_time": disruption.end_time,
            "severity": disruption.severity,
            "status": disruption.status
        }

        # Initialize shared workflow state
        initial_state = AgentWorkflowState(
            recovery_run_id=recovery_run.id,
            disruption_id=disruption.id,
            current_step="supervisor",
            disruption=disruption_dict
        )

        t0 = time.time()
        final_state = execute_agent_workflow(initial_state, db)
        elapsed_ms = int((time.time() - t0) * 1000)

        # Update recovery_run record
        opt = final_state.optimisation
        val = final_state.validation
        exp = final_state.explanation

        recovery_run.status = "Success" if (val and val.is_valid) else ("Infeasible" if (opt and not opt.is_feasible) else "Failed")
        recovery_run.solver_status = opt.solver_status if opt else "ERROR"
        recovery_run.objective_value = opt.objective_value if opt else 0.0
        recovery_run.execution_time_ms = elapsed_ms
        recovery_run.agent_summary = exp.administrator_recommendation if exp else "Recovery plan generated."

        if val and val.is_valid:
            disruption.status = "Recovery Proposed"
        else:
            disruption.status = "Escalated"

        db.commit()
        db.refresh(recovery_run)

        log_audit_event(
            db=db,
            entity_type="RecoveryRun",
            entity_id=recovery_run.id,
            action="EXECUTE_RECOVERY",
            details={
                "disruption_id": disruption.id,
                "status": recovery_run.status,
                "solver_status": recovery_run.solver_status,
                "duration_ms": elapsed_ms
            }
        )

        return recovery_run

    @staticmethod
    def approve_recovery(db: Session, recovery_run_id: int, comments: Optional[str], approved_by: str) -> Dict[str, Any]:
        recovery_run = db.query(RecoveryRun).filter(RecoveryRun.id == recovery_run_id).first()
        if not recovery_run:
            raise HTTPException(status_code=404, detail="Recovery run not found")

        disruption = db.query(Disruption).filter(Disruption.id == recovery_run.disruption_id).first()
        if not disruption:
            raise HTTPException(status_code=404, detail="Associated disruption not found")

        # Check for existing approval
        existing_appr = db.query(Approval).filter(
            Approval.recovery_run_id == recovery_run_id,
            Approval.status == "Approved"
        ).first()
        if existing_appr:
            raise HTTPException(status_code=400, detail="This recovery run has already been approved and applied.")

        # Re-run Independent Validation before committing transactional changes!
        proposed_changes = db.query(ProposedScheduleChange).filter(
            ProposedScheduleChange.recovery_run_id == recovery_run_id
        ).all()

        prop_list = []
        for p in proposed_changes:
            sch = db.query(TimetableSchedule).filter(TimetableSchedule.id == p.original_schedule_id).first()
            if sch:
                prop_list.append({
                    "original_schedule_id": p.original_schedule_id,
                    "new_room_id": p.new_room_id,
                    "new_day_of_week": p.new_day_of_week,
                    "new_start_time": p.new_start_time,
                    "new_end_time": p.new_end_time,
                    "course_id": sch.course_id,
                    "faculty_id": sch.faculty_id,
                    "cohort_id": sch.cohort_id
                })

        validator = IndependentValidationService(db=db)
        reval = validator.validate_proposed_changes(
            proposed_changes=prop_list,
            disrupted_room_id=disruption.affected_resource_id
        )

        if not reval.is_valid:
            raise HTTPException(
                status_code=409,
                detail=f"Re-validation failed prior to database commit: {reval.violations[0].details if reval.violations else 'Constraint violation'}"
            )

        # Atomic Transactional Database Update
        try:
            for p in proposed_changes:
                sch = db.query(TimetableSchedule).filter(TimetableSchedule.id == p.original_schedule_id).first()
                if sch:
                    sch.room_id = p.new_room_id
                    sch.day_of_week = p.new_day_of_week
                    sch.start_time = p.new_start_time
                    sch.end_time = p.new_end_time
                    sch.status = "Rescheduled"
                p.status = "Applied"

            disruption.status = "Resolved"
            recovery_run.status = "Success"

            approval = Approval(
                recovery_run_id=recovery_run.id,
                disruption_id=disruption.id,
                status="Approved",
                comments=comments or "Approved by Campus Administrator. Timetable transactionally updated.",
                approved_by=approved_by or "Campus Administrator",
                approved_at=datetime.utcnow()
            )
            db.add(approval)
            db.commit()

            log_audit_event(
                db=db,
                entity_type="Approval",
                entity_id=approval.id,
                action="APPROVE_RECOVERY",
                details={
                    "recovery_run_id": recovery_run.id,
                    "disruption_id": disruption.id,
                    "changes_applied": len(proposed_changes),
                    "approved_by": approved_by
                },
                actor=approved_by
            )

            return {
                "message": "Recovery successfully approved and applied to campus timetable.",
                "recovery_run_id": recovery_run.id,
                "disruption_status": disruption.status,
                "applied_changes_count": len(proposed_changes),
                "revalidation_status": reval.validation_status
            }
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Transaction failed while applying recovery: {str(e)}")

    @staticmethod
    def reject_recovery(db: Session, recovery_run_id: int, comments: Optional[str], rejected_by: str) -> Dict[str, Any]:
        recovery_run = db.query(RecoveryRun).filter(RecoveryRun.id == recovery_run_id).first()
        if not recovery_run:
            raise HTTPException(status_code=404, detail="Recovery run not found")

        disruption = db.query(Disruption).filter(Disruption.id == recovery_run.disruption_id).first()

        # Preserve original timetable schedules unchanged
        proposed_changes = db.query(ProposedScheduleChange).filter(
            ProposedScheduleChange.recovery_run_id == recovery_run_id
        ).all()
        for p in proposed_changes:
            p.status = "Rejected"

        if disruption:
            disruption.status = "Rejected"
        recovery_run.status = "Rejected"

        approval = Approval(
            recovery_run_id=recovery_run.id,
            disruption_id=disruption.id if disruption else 0,
            status="Rejected",
            comments=comments or "Recovery proposal rejected by Administrator. Timetable left unmodified.",
            approved_by=rejected_by or "Campus Administrator",
            approved_at=datetime.utcnow()
        )
        db.add(approval)
        db.commit()

        log_audit_event(
            db=db,
            entity_type="Approval",
            entity_id=approval.id,
            action="REJECT_RECOVERY",
            details={
                "recovery_run_id": recovery_run.id,
                "comments": comments,
                "rejected_by": rejected_by
            },
            actor=rejected_by
        )

        return {
            "message": "Recovery proposal rejected. Original timetable remains unchanged.",
            "recovery_run_id": recovery_run.id,
            "disruption_status": disruption.status if disruption else "Rejected"
        }
