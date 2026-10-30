import logging
from typing import Dict, Any, TypedDict, Optional
from langgraph.graph import StateGraph, START, END
from sqlalchemy.orm import Session
from backend.app.schemas.agents import (
    AgentWorkflowState, DisruptionAnalysisResult,
    ResourceIntelligenceResult, TimetableCoordinationResult,
    OptimisationResult, ValidationResult, ExplanationResult
)
from backend.app.agents.supervisor import run_supervisor_agent
from backend.app.agents.disruption_agent import run_disruption_agent
from backend.app.agents.resource_agent import run_resource_agent
from backend.app.agents.timetable_agent import run_timetable_agent
from backend.app.agents.optimisation_agent import run_optimisation_agent
from backend.app.agents.validation_agent import run_validation_agent
from backend.app.agents.explanation_agent import run_explanation_agent

logger = logging.getLogger("nexora_campus.workflow")

class WorkflowGraphState(TypedDict):
    state_obj: AgentWorkflowState
    db: Any

def supervisor_node(graph_state: WorkflowGraphState) -> WorkflowGraphState:
    logger.info("LangGraph Node: Campus Supervisor Agent executing...")
    graph_state["state_obj"] = run_supervisor_agent(graph_state["state_obj"], graph_state["db"])
    return graph_state

def disruption_node(graph_state: WorkflowGraphState) -> WorkflowGraphState:
    logger.info("LangGraph Node: Disruption Analysis Agent executing...")
    graph_state["state_obj"] = run_disruption_agent(graph_state["state_obj"], graph_state["db"])
    return graph_state

def resource_node(graph_state: WorkflowGraphState) -> WorkflowGraphState:
    logger.info("LangGraph Node: Resource Intelligence Agent executing...")
    graph_state["state_obj"] = run_resource_agent(graph_state["state_obj"], graph_state["db"])
    return graph_state

def timetable_node(graph_state: WorkflowGraphState) -> WorkflowGraphState:
    logger.info("LangGraph Node: Timetable Coordination Agent executing...")
    graph_state["state_obj"] = run_timetable_agent(graph_state["state_obj"], graph_state["db"])
    return graph_state

def optimisation_node(graph_state: WorkflowGraphState) -> WorkflowGraphState:
    logger.info("LangGraph Node: Optimisation Agent executing...")
    graph_state["state_obj"] = run_optimisation_agent(graph_state["state_obj"], graph_state["db"])
    return graph_state

def validation_node(graph_state: WorkflowGraphState) -> WorkflowGraphState:
    logger.info("LangGraph Node: Validation & Compliance Agent executing...")
    graph_state["state_obj"] = run_validation_agent(graph_state["state_obj"], graph_state["db"])
    return graph_state

def explanation_node(graph_state: WorkflowGraphState) -> WorkflowGraphState:
    logger.info("LangGraph Node: Explanation Agent executing...")
    graph_state["state_obj"] = run_explanation_agent(graph_state["state_obj"], graph_state["db"])
    return graph_state

def validation_condition(graph_state: WorkflowGraphState) -> str:
    state_obj = graph_state["state_obj"]
    val = state_obj.validation
    if val and val.is_valid:
        return "explanation"
    
    if state_obj.retry_count < state_obj.max_retries:
        state_obj.retry_count += 1
        logger.warning(f"Validation failed. Retrying workflow (attempt {state_obj.retry_count}/{state_obj.max_retries})...")
        return "retry_coordination"
    else:
        logger.error("Validation failed and max retries exceeded. Escalating to administrator.")
        state_obj.status = "Escalated"
        return "explanation"

def build_recovery_workflow_graph():
    builder = StateGraph(WorkflowGraphState)

    builder.add_node("supervisor", supervisor_node)
    builder.add_node("disruption_analysis", disruption_node)
    builder.add_node("resource_intelligence", resource_node)
    builder.add_node("timetable_coordination", timetable_node)
    builder.add_node("optimisation", optimisation_node)
    builder.add_node("validation", validation_node)
    builder.add_node("explanation", explanation_node)

    builder.add_edge(START, "supervisor")
    builder.add_edge("supervisor", "disruption_analysis")
    builder.add_edge("disruption_analysis", "resource_intelligence")
    builder.add_edge("resource_intelligence", "timetable_coordination")
    builder.add_edge("timetable_coordination", "optimisation")
    builder.add_edge("optimisation", "validation")

    builder.add_conditional_edges(
        "validation",
        validation_condition,
        {
            "explanation": "explanation",
            "retry_coordination": "timetable_coordination"
        }
    )

    builder.add_edge("explanation", END)

    return builder.compile()

recovery_graph = build_recovery_workflow_graph()

def execute_agent_workflow(initial_state: AgentWorkflowState, db: Session) -> AgentWorkflowState:
    """
    Executes the full compiled LangGraph multi-agent orchestration.
    """
    initial_graph_state: WorkflowGraphState = {
        "state_obj": initial_state,
        "db": db
    }
    result_state = recovery_graph.invoke(initial_graph_state)
    return result_state["state_obj"]
