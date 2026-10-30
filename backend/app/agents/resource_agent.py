import time
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from backend.app.schemas.agents import (
    AgentWorkflowState, ResourceIntelligenceResult, ResourceAlternative
)
from backend.app.agents.llm_client import llm_client
from backend.app.models.entities import AgentExecution
from backend.app.tools.resource_tools import evaluate_rooms_for_recovery

AGENT_NAME = "Resource Intelligence Agent"
AGENT_ROLE = "Smart Infrastructure Evaluator & Room Suitability Classifier"

def run_resource_agent(state: AgentWorkflowState, db: Session) -> AgentWorkflowState:
    start_time = datetime.utcnow()
    t0 = time.time()
    tools_used = ["InventoryAuditor", "ConstraintEvaluator", "EquipmentMatcher"]

    analysis = state.disruption_analysis
    affected_schedules = analysis.affected_schedules if analysis else []

    # If no schedules affected, return clean result
    if not affected_schedules:
        suitable_alts, rejected_alts = [], []
        total_searched = 0
        summary = "No schedules were affected; campus room inventory scanning skipped."
        is_llm_flag = False
    else:
        first_sch = affected_schedules[0]
        req_type = first_sch["required_room_type"]
        min_cap = first_sch["cohort_size"]
        req_eq = first_sch["required_equipment"]
        day_of_week = first_sch["day_of_week"]
        s_time = first_sch["start_time"]
        e_time = first_sch["end_time"]
        pref_bldg = first_sch["building"]
        disrupted_room_id = state.disruption.get("affected_resource_id")

        suitable_list, rejected_list = evaluate_rooms_for_recovery(
            db=db,
            required_type=req_type,
            min_capacity=min_cap,
            required_equipment=req_eq,
            day_of_week=day_of_week,
            start_time=s_time,
            end_time=e_time,
            preferred_building=pref_bldg,
            exclude_room_ids=[disrupted_room_id]
        )

        suitable_alts = [ResourceAlternative(**r) for r in suitable_list]
        rejected_alts = [ResourceAlternative(**r) for r in rejected_list]
        total_searched = len(suitable_alts) + len(rejected_alts)

        system_prompt = (
            "You are the Resource Intelligence Agent for Nexora Smart Campus. "
            "Synthesize the room search results, explaining which rooms qualify and why rejected rooms were disqualified."
        )
        user_prompt = (
            f"Searched {total_searched} campus rooms for {req_type} requiring {req_eq} and capacity >= {min_cap}.\n"
            f"Suitable Candidates: {', '.join(f'{r.room_code} (Score: {r.suitability_score})' for r in suitable_alts)}\n"
            f"Disqualified Rooms: {', '.join(f'{r.room_code} (Reason: {r.rejection_reason})' for r in rejected_alts[:4])}\n\n"
            "Generate a structured JSON response with:\n"
            "{\n"
            '  "recommendations_summary": "string"\n'
            "}"
        )

        llm_out, is_llm, _ = llm_client.generate_json(system_prompt, user_prompt)

        if is_llm and llm_out:
            summary = llm_out.get("recommendations_summary", "")
            is_llm_flag = True
        else:
            top_rec = suitable_alts[0].room_code if suitable_alts else "None"
            summary = (
                f"Evaluated {total_searched} total campus facilities. Found {len(suitable_alts)} fully qualified "
                f"candidate(s). Primary recommendation: {top_rec} with full GPU hardware alignment and adequate capacity. "
                f"{len(rejected_alts)} room(s) disqualified due to capacity shortages, missing GPU equipment, or schedule occupancy."
            )
            is_llm_flag = False

    result = ResourceIntelligenceResult(
        suitable_alternatives=suitable_alts,
        rejected_alternatives=rejected_alts,
        total_searched=total_searched,
        recommendations_summary=summary,
        is_llm_generated=is_llm_flag
    )

    duration_ms = int((time.time() - t0) * 1000)
    end_time = datetime.utcnow()

    input_payload = {
        "required_room_type": affected_schedules[0]["required_room_type"] if affected_schedules else "N/A",
        "min_capacity": affected_schedules[0]["cohort_size"] if affected_schedules else 0,
        "required_equipment": affected_schedules[0]["required_equipment"] if affected_schedules else []
    }

    exec_rec = AgentExecution(
        recovery_run_id=state.recovery_run_id,
        agent_name=AGENT_NAME,
        agent_role=AGENT_ROLE,
        input_data=input_payload,
        output_data=result.dict(),
        tools_used=tools_used,
        status="Completed",
        retry_count=0,
        start_time=start_time,
        completion_time=end_time,
        duration_ms=duration_ms
    )
    db.add(exec_rec)
    db.commit()

    state.resource_intelligence = result
    state.current_step = "timetable_coordination"
    return state
