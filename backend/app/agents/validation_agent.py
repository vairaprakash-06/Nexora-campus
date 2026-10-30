import time
from datetime import datetime
from typing import Dict, Any
from sqlalchemy.orm import Session
from backend.app.schemas.agents import AgentWorkflowState, ValidationResult
from backend.app.models.entities import AgentExecution
from backend.app.services.validation_service import IndependentValidationService

AGENT_NAME = "Validation and Compliance Agent"
AGENT_ROLE = "Authoritative Policy & Constraint Verification Gatekeeper"

def run_validation_agent(state: AgentWorkflowState, db: Session) -> AgentWorkflowState:
    start_time = datetime.utcnow()
    t0 = time.time()
    tools_used = ["IndependentConstraintChecker", "ConflictMatrixAuditor", "ZeroTrustTimetableValidator"]

    opt = state.optimisation
    proposed_changes = opt.proposed_changes if opt else []
    disrupted_room_id = state.disruption.get("affected_resource_id")

    validator = IndependentValidationService(db=db)
    val_result = validator.validate_proposed_changes(
        proposed_changes=proposed_changes,
        disrupted_room_id=disrupted_room_id
    )

    duration_ms = int((time.time() - t0) * 1000)
    end_time = datetime.utcnow()

    exec_status = "Completed" if val_result.is_valid else "Failed"

    exec_rec = AgentExecution(
        recovery_run_id=state.recovery_run_id,
        agent_name=AGENT_NAME,
        agent_role=AGENT_ROLE,
        input_data={
            "proposed_changes_count": len(proposed_changes),
            "disrupted_room_id": disrupted_room_id,
            "verification_mode": "Strict Deterministic Compliance"
        },
        output_data=val_result.dict(),
        tools_used=tools_used,
        status=exec_status,
        retry_count=0,
        error_details=None if val_result.is_valid else f"{len(val_result.violations)} constraint violation(s) detected.",
        start_time=start_time,
        completion_time=end_time,
        duration_ms=duration_ms
    )
    db.add(exec_rec)
    db.commit()

    state.validation = val_result
    state.current_step = "explanation"
    return state
