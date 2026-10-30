from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.entities import AgentExecution, RecoveryRun
from backend.app.schemas.api import AgentExecutionOut
from backend.app.agents.llm_client import llm_client

router = APIRouter(prefix="/agents", tags=["Agents"])

SEVEN_AGENTS_METADATA = [
    {
        "id": "supervisor",
        "name": "Campus Supervisor Agent",
        "role": "Strategic Incident Orchestrator & Multi-Agent Dispatcher",
        "responsibilities": [
            "Receive user disruption requests",
            "Understand the incident scope & severity",
            "Delegate tasks across specialized agents",
            "Monitor multi-agent execution & graph state",
            "Produce final recovery recommendation"
        ],
        "engine": "Hybrid (Groq LLM + StateGraph)",
        "tools": ["WorkflowCoordinator", "IncidentParser"]
    },
    {
        "id": "disruption_analysis",
        "name": "Disruption Analysis Agent",
        "role": "Incident Impact Assessor & Schedule Blast Radius Analyzer",
        "responsibilities": [
            "Analyse incident details",
            "Identify affected resources and schedules",
            "Identify affected courses, faculty, and cohorts",
            "Determine disruption severity and calculate impact score"
        ],
        "engine": "Deterministic Database Scanner + Groq Narrative",
        "tools": ["ScheduleScanner", "DatabaseImpactCalculator"]
    },
    {
        "id": "resource_intelligence",
        "name": "Resource Intelligence Agent",
        "role": "Smart Infrastructure Evaluator & Room Suitability Classifier",
        "responsibilities": [
            "Search available campus rooms",
            "Compare room capacities against cohort sizes",
            "Check mandatory equipment (e.g. GPU Workstations)",
            "Verify room types and buildings",
            "Explicitly document rejected candidate rooms"
        ],
        "engine": "Deterministic Constraint Filter + Groq Explainer",
        "tools": ["InventoryAuditor", "ConstraintEvaluator", "EquipmentMatcher"]
    },
    {
        "id": "timetable_coordination",
        "name": "Timetable Coordination Agent",
        "role": "Faculty & Student Schedule Synchronizer",
        "responsibilities": [
            "Analyse affected class timetables",
            "Find alternative candidate time slots",
            "Check faculty busy/free availability",
            "Check student cohort busy/free availability",
            "Minimise overall calendar displacement"
        ],
        "engine": "Deterministic Calendar Resolver + Groq Synthesizer",
        "tools": ["ScheduleConflictResolver", "CohortCalendarInspector", "FacultyWorkloadAuditor"]
    },
    {
        "id": "optimisation",
        "name": "Optimisation Agent",
        "role": "Constraint Programming Engine & OR-Tools CP-SAT Bridge",
        "responsibilities": [
            "Call the Google OR-Tools CP-SAT engine",
            "Generate mathematically feasible, optimal schedule changes",
            "Minimise timetable changes and displacement penalties",
            "Return solver status, objective score, and metrics"
        ],
        "engine": "Google OR-Tools CP-SAT (Pure Deterministic Mathematical Optimization)",
        "tools": ["Google-ORTools-CPSAT", "WeightedCostMinimizer", "ConstraintSatisfactionSolver"]
    },
    {
        "id": "validation",
        "name": "Validation and Compliance Agent",
        "role": "Authoritative Policy & Constraint Verification Gatekeeper",
        "responsibilities": [
            "Independently validate proposed changes against database state",
            "Detect room double-bookings",
            "Detect faculty and cohort schedule overlaps",
            "Check capacity and equipment compliance",
            "Verify disrupted rooms are not reused"
        ],
        "engine": "Authoritative Deterministic Compliance Engine",
        "tools": ["IndependentConstraintChecker", "ConflictMatrixAuditor", "ZeroTrustTimetableValidator"]
    },
    {
        "id": "explanation",
        "name": "Explanation Agent",
        "role": "Transparent AI Reasoning & Administrator Decision Explainer",
        "responsibilities": [
            "Explain why the selected room was chosen",
            "Explain why alternatives were rejected",
            "Summarise timetable displacement impact",
            "Detail optimization trade-offs and constraint compliance",
            "Produce administrator-friendly approval recommendations"
        ],
        "engine": "Hybrid (Groq LLM + Structured Deterministic Synthesis)",
        "tools": ["ReasoningSynthesizer", "TradeoffAnalyzer", "AuditNarrativeGenerator"]
    }
]

@router.get("/status")
def get_agents_status(db: Session = Depends(get_db)):
    # Query latest executions for each agent
    agents_status_list = []
    for meta in SEVEN_AGENTS_METADATA:
        latest_exec = db.query(AgentExecution).filter(
            AgentExecution.agent_name == meta["name"]
        ).order_by(AgentExecution.start_time.desc()).first()

        agents_status_list.append({
            **meta,
            "current_status": latest_exec.status if latest_exec else "Idle",
            "last_duration_ms": latest_exec.duration_ms if latest_exec else 0,
            "last_executed_at": latest_exec.completion_time if latest_exec else None,
            "latest_output": latest_exec.output_data if latest_exec else None,
            "latest_tools_used": latest_exec.tools_used if latest_exec else meta["tools"],
            "error_details": latest_exec.error_details if latest_exec else None,
            "llm_active": llm_client.is_available()
        })

    return {
        "agents": agents_status_list,
        "total_agents": len(SEVEN_AGENTS_METADATA),
        "llm_provider": "Groq",
        "llm_model": llm_client.model,
        "llm_enabled": llm_client.is_available()
    }

@router.get("/executions/{run_id}", response_model=List[AgentExecutionOut])
def get_run_agent_executions(run_id: int, db: Session = Depends(get_db)):
    run = db.query(RecoveryRun).filter(RecoveryRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Recovery run not found")

    executions = db.query(AgentExecution).filter(
        AgentExecution.recovery_run_id == run_id
    ).order_by(AgentExecution.id.asc()).all()

    return executions
