import time
from datetime import datetime
from typing import Dict, Any
from sqlalchemy.orm import Session
from backend.app.schemas.agents import AgentWorkflowState, OptimisationResult
from backend.app.models.entities import AgentExecution, ProposedScheduleChange
from backend.app.optimisation.solver import TimetableRecoverySolver

AGENT_NAME = "Optimisation Agent"
AGENT_ROLE = "Constraint Programming Engine & OR-Tools CP-SAT Bridge"

def run_optimisation_agent(state: AgentWorkflowState, db: Session) -> AgentWorkflowState:
    start_time = datetime.utcnow()
    t0 = time.time()
    tools_used = ["Google-ORTools-CPSAT", "WeightedCostMinimizer", "ConstraintSatisfactionSolver"]

    analysis = state.disruption_analysis
    affected_schedules = analysis.affected_schedules if analysis else []
    disrupted_room_id = state.disruption.get("affected_resource_id")
    day_of_week = state.disruption.get("day_of_week", "Monday")
    s_time = state.disruption.get("start_time", "09:00")
    e_time = state.disruption.get("end_time", "11:00")

    solver = TimetableRecoverySolver(db=db, timeout_seconds=10)
    solve_res = solver.solve(
        affected_schedules=affected_schedules,
        disrupted_room_id=disrupted_room_id,
        day_of_week=day_of_week,
        start_time=s_time,
        end_time=e_time
    )

    opt_result = OptimisationResult(
        solver_status=solve_res["solver_status"],
        is_feasible=solve_res["is_feasible"],
        objective_value=solve_res["objective_value"],
        proposed_changes=solve_res["proposed_changes"],
        solver_time_ms=solve_res["solver_time_ms"],
        displacement_metric=solve_res["displacement_metric"],
        solver_statistics=solve_res["solver_statistics"],
        is_deterministic=True
    )

    duration_ms = int((time.time() - t0) * 1000)
    end_time = datetime.utcnow()

    # Save proposed schedule changes to database under this recovery run
    for prop in solve_res["proposed_changes"]:
        prop_rec = ProposedScheduleChange(
            recovery_run_id=state.recovery_run_id,
            original_schedule_id=prop["original_schedule_id"],
            new_room_id=prop["new_room_id"],
            new_day_of_week=prop["new_day_of_week"],
            new_start_time=prop["new_start_time"],
            new_end_time=prop["new_end_time"],
            reason=prop["reason"],
            displacement_score=prop["displacement_score"],
            status="Proposed"
        )
        db.add(prop_rec)
    db.commit()

    exec_status = "Completed" if solve_res["is_feasible"] else "Infeasible"

    exec_rec = AgentExecution(
        recovery_run_id=state.recovery_run_id,
        agent_name=AGENT_NAME,
        agent_role=AGENT_ROLE,
        input_data={
            "affected_schedules_count": len(affected_schedules),
            "solver": "Google OR-Tools CP-SAT",
            "timeout_seconds": 10
        },
        output_data=opt_result.dict(),
        tools_used=tools_used,
        status=exec_status,
        retry_count=0,
        start_time=start_time,
        completion_time=end_time,
        duration_ms=duration_ms
    )
    db.add(exec_rec)
    db.commit()

    state.optimisation = opt_result
    state.current_step = "validation"
    return state
