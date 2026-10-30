import time
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from backend.app.schemas.agents import AgentWorkflowState, DisruptionAnalysisResult
from backend.app.agents.llm_client import llm_client
from backend.app.models.entities import AgentExecution, Room
from backend.app.tools.schedule_tools import find_affected_schedules

AGENT_NAME = "Disruption Analysis Agent"
AGENT_ROLE = "Incident Impact Assessor & Schedule Blast Radius Analyzer"

def run_disruption_agent(state: AgentWorkflowState, db: Session) -> AgentWorkflowState:
    start_time = datetime.utcnow()
    t0 = time.time()
    tools_used = ["ScheduleScanner", "DatabaseImpactCalculator"]

    disruption = state.disruption
    res_type = disruption.get("affected_resource_type", "Room")
    res_id = disruption.get("affected_resource_id")
    day_of_week = disruption.get("day_of_week")
    s_time = disruption.get("start_time")
    e_time = disruption.get("end_time")

    room = db.query(Room).filter(Room.id == res_id).first() if res_type == "Room" else None
    room_code = room.code if room else f"Resource #{res_id}"

    # 1. Deterministic tool execution to find affected schedules
    affected_schedules = find_affected_schedules(
        db=db,
        resource_type=res_type,
        resource_id=res_id,
        day_of_week=day_of_week,
        start_time=s_time,
        end_time=e_time
    )

    affected_courses = list(set(s["course_code"] for s in affected_schedules))
    affected_faculty = list(set(s["faculty_name"] for s in affected_schedules))
    affected_cohorts = list(set(s["cohort_code"] for s in affected_schedules))
    total_students = sum(s["cohort_size"] for s in affected_schedules)

    input_payload = {
        "resource_type": res_type,
        "resource_id": res_id,
        "resource_name": room_code,
        "day_of_week": day_of_week,
        "window": f"{s_time}-{e_time}",
        "severity": disruption.get("severity")
    }

    # 2. LLM Narrative Enhancement (if available)
    system_prompt = (
        "You are the Disruption Analysis Agent in Nexora Smart Campus. "
        "Assess the blast radius and operational impact of this campus disruption."
    )
    user_prompt = (
        f"Incident: {disruption.get('title')}\n"
        f"Resource: {room_code} (Capacity: {room.capacity if room else 'N/A'})\n"
        f"Window: {day_of_week} {s_time}-{e_time}\n"
        f"Affected Schedules Count: {len(affected_schedules)}\n"
        f"Affected Courses: {', '.join(affected_courses) if affected_courses else 'None'}\n"
        f"Affected Faculty: {', '.join(affected_faculty) if affected_faculty else 'None'}\n"
        f"Affected Cohorts: {', '.join(affected_cohorts) if affected_cohorts else 'None'}\n"
        f"Total Students Impacted: {total_students}\n\n"
        "Generate a structured JSON response with:\n"
        "{\n"
        '  "severity_assessment": "string",\n'
        '  "impact_score": 0.0 to 10.0,\n'
        '  "analysis_narrative": "string"\n'
        "}"
    )

    llm_out, is_llm, _ = llm_client.generate_json(system_prompt, user_prompt)

    if not is_llm or not llm_out:
        severity_eval = "High" if len(affected_schedules) > 0 else "Low"
        impact_score = min(10.0, len(affected_schedules) * 3.5 + (total_students / 10.0))
        narrative = (
            f"Deterministic Impact Assessment: Disruption in {room_code} directly affects {len(affected_schedules)} "
            f"scheduled lab/lecture session(s), impacting {len(affected_courses)} course(s), {len(affected_faculty)} "
            f"faculty member(s), and {total_students} registered students. High urgency resolution is required."
        )
        is_llm_flag = False
    else:
        severity_eval = llm_out.get("severity_assessment", disruption.get("severity", "High"))
        impact_score = float(llm_out.get("impact_score", 8.5))
        narrative = llm_out.get("analysis_narrative", "")
        is_llm_flag = True

    result = DisruptionAnalysisResult(
        incident_id=disruption.get("id", 0),
        incident_title=disruption.get("title", ""),
        affected_resource_type=res_type,
        affected_resource_id=res_id,
        affected_resource_name=room_code,
        day_of_week=day_of_week,
        time_window=f"{s_time}-{e_time}",
        affected_schedules=affected_schedules,
        affected_courses=affected_courses,
        affected_faculty=affected_faculty,
        affected_cohorts=affected_cohorts,
        severity_assessment=severity_eval,
        impact_score=round(impact_score, 1),
        analysis_narrative=narrative,
        is_llm_generated=is_llm_flag
    )

    duration_ms = int((time.time() - t0) * 1000)
    end_time = datetime.utcnow()

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

    state.disruption_analysis = result
    state.current_step = "resource_intelligence"
    return state
