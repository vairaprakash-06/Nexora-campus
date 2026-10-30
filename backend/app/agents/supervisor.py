import time
from datetime import datetime
from typing import Dict, Any
from sqlalchemy.orm import Session
from backend.app.schemas.agents import AgentWorkflowState
from backend.app.agents.llm_client import llm_client
from backend.app.models.entities import AgentExecution

AGENT_NAME = "Campus Supervisor Agent"
AGENT_ROLE = "Strategic Incident Orchestrator & Multi-Agent Dispatcher"

def run_supervisor_agent(state: AgentWorkflowState, db: Session) -> AgentWorkflowState:
    start_time = datetime.utcnow()
    t0 = time.time()
    tools_used = ["WorkflowCoordinator", "IncidentParser"]

    disruption = state.disruption
    input_payload = {
        "incident_id": disruption.get("id"),
        "title": disruption.get("title"),
        "category": disruption.get("category"),
        "resource": disruption.get("affected_resource_name"),
        "window": f"{disruption.get('day_of_week')} {disruption.get('start_time')}-{disruption.get('end_time')}"
    }

    system_prompt = (
        "You are the Campus Supervisor Agent for Nexora Smart Campus. "
        "Your duty is to triage reported campus disruptions, define an incident response plan, "
        "and delegate recovery tasks across specialised agents: Disruption Analysis, Resource Intelligence, "
        "Timetable Coordination, OR-Tools Optimisation, Independent Validation, and Explanation."
    )
    user_prompt = (
        f"Incident Details:\n"
        f"Title: {disruption.get('title')}\n"
        f"Category: {disruption.get('category')}\n"
        f"Description: {disruption.get('description')}\n"
        f"Time Window: {disruption.get('day_of_week')}, {disruption.get('start_time')} - {disruption.get('end_time')}\n"
        f"Severity: {disruption.get('severity')}\n\n"
        "Generate a structured JSON response with:\n"
        "{\n"
        '  "triage_assessment": "string",\n'
        '  "delegation_plan": ["string"],\n'
        '  "recommended_strategy": "string",\n'
        '  "urgency_level": "string"\n'
        "}"
    )

    llm_out, is_llm, err = llm_client.generate_json(system_prompt, user_prompt)

    if not is_llm or not llm_out:
        # Structured Deterministic Fallback
        output_payload = {
            "triage_assessment": (
                f"Incident '{disruption.get('title')}' verified on {disruption.get('day_of_week')} "
                f"from {disruption.get('start_time')} to {disruption.get('end_time')}. "
                f"Disruption severity evaluated as {disruption.get('severity')}."
            ),
            "delegation_plan": [
                "1. Disruption Analysis Agent: Identify affected courses, faculty, and cohorts.",
                "2. Resource Intelligence Agent: Filter available rooms matching capacity and GPU requirements.",
                "3. Timetable Coordination Agent: Scan slot alternatives and conflict boundaries.",
                "4. Optimisation Agent: Invoke Google OR-Tools CP-SAT solver for minimal-cost rescheduling.",
                "5. Validation & Compliance Agent: Authoritatively verify zero room/faculty clashes.",
                "6. Explanation Agent: Draft multi-faceted reasoning and admin audit report."
            ],
            "recommended_strategy": "Deterministic Constrained Room Reallocation with Zero Timetable Displacement",
            "urgency_level": disruption.get("severity", "High"),
            "is_llm_generated": False
        }
    else:
        output_payload = {
            "triage_assessment": llm_out.get("triage_assessment", "Triage completed."),
            "delegation_plan": llm_out.get("delegation_plan", []),
            "recommended_strategy": llm_out.get("recommended_strategy", "Optimal Room Swap"),
            "urgency_level": llm_out.get("urgency_level", disruption.get("severity")),
            "is_llm_generated": True
        }

    duration_ms = int((time.time() - t0) * 1000)
    end_time = datetime.utcnow()

    # Persist agent execution record
    exec_rec = AgentExecution(
        recovery_run_id=state.recovery_run_id,
        agent_name=AGENT_NAME,
        agent_role=AGENT_ROLE,
        input_data=input_payload,
        output_data=output_payload,
        tools_used=tools_used,
        status="Completed",
        retry_count=0,
        start_time=start_time,
        completion_time=end_time,
        duration_ms=duration_ms
    )
    db.add(exec_rec)
    db.commit()

    state.supervisor_plan = output_payload
    state.current_step = "disruption_analysis"
    return state
