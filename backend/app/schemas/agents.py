from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class DisruptionAnalysisResult(BaseModel):
    incident_id: int
    incident_title: str
    affected_resource_type: str
    affected_resource_id: int
    affected_resource_name: str
    day_of_week: str
    time_window: str
    affected_schedules: List[Dict[str, Any]] = []
    affected_courses: List[str] = []
    affected_faculty: List[str] = []
    affected_cohorts: List[str] = []
    severity_assessment: str
    impact_score: float
    analysis_narrative: str
    is_llm_generated: bool = False

class ResourceAlternative(BaseModel):
    room_id: int
    room_code: str
    room_name: str
    building: str
    capacity: int
    room_type: str
    equipment: List[str] = []
    is_available_in_slot: bool
    capacity_sufficient: bool
    equipment_match: bool
    room_type_match: bool
    suitability_score: float
    rejection_reason: Optional[str] = None

class ResourceIntelligenceResult(BaseModel):
    suitable_alternatives: List[ResourceAlternative] = []
    rejected_alternatives: List[ResourceAlternative] = []
    total_searched: int
    recommendations_summary: str
    is_llm_generated: bool = False

class TimetableCoordinationResult(BaseModel):
    affected_classes_count: int
    candidate_slots: List[Dict[str, Any]] = []
    faculty_availability_checked: bool
    cohort_availability_checked: bool
    coordination_strategy: str
    minimization_factor: str
    coordination_narrative: str
    is_llm_generated: bool = False

class OptimisationResult(BaseModel):
    solver_status: str  # OPTIMAL, FEASIBLE, INFEASIBLE, TIMEOUT
    is_feasible: bool
    objective_value: float
    proposed_changes: List[Dict[str, Any]] = []
    solver_time_ms: int
    displacement_metric: float
    solver_statistics: Dict[str, Any] = {}
    is_deterministic: bool = True

class ValidationViolation(BaseModel):
    constraint_name: str
    severity: str  # CRITICAL, WARNING
    details: str
    schedule_id: Optional[int] = None
    room_id: Optional[int] = None

class ValidationResult(BaseModel):
    is_valid: bool
    checked_constraints: List[str] = []
    violations: List[ValidationViolation] = []
    compliance_score: float
    validation_status: str  # PASSED, FAILED, WARNINGS
    is_deterministic: bool = True

class ExplanationResult(BaseModel):
    executive_summary: str
    why_selected: str
    rejected_alternatives_explanation: str
    constraints_verified_summary: str
    timetable_displacement_impact: str
    administrator_recommendation: str
    trade_off_analysis: str
    is_llm_generated: bool = False

class AgentWorkflowState(BaseModel):
    recovery_run_id: int
    disruption_id: int
    current_step: str = "supervisor"
    retry_count: int = 0
    max_retries: int = 2
    
    # Raw context
    disruption: Dict[str, Any] = {}
    
    # Agent outputs
    supervisor_plan: Optional[Dict[str, Any]] = None
    disruption_analysis: Optional[DisruptionAnalysisResult] = None
    resource_intelligence: Optional[ResourceIntelligenceResult] = None
    timetable_coordination: Optional[TimetableCoordinationResult] = None
    optimisation: Optional[OptimisationResult] = None
    validation: Optional[ValidationResult] = None
    explanation: Optional[ExplanationResult] = None
    
    # Final status
    status: str = "Running"  # Running, Completed, Infeasible, Failed, Escalated
    error: Optional[str] = None
