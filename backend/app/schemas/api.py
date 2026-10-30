from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# --- Room Schemas ---
class RoomBase(BaseModel):
    code: str
    name: str
    capacity: int
    room_type: str
    building: str
    floor: int = 1
    equipment: List[str] = []
    is_available: bool = True
    maintenance_notes: Optional[str] = None

class RoomCreate(RoomBase):
    pass

class RoomUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    capacity: Optional[int] = None
    room_type: Optional[str] = None
    building: Optional[str] = None
    floor: Optional[int] = None
    equipment: Optional[List[str]] = None
    is_available: Optional[bool] = None
    maintenance_notes: Optional[str] = None

class RoomOut(RoomBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# --- Department Schemas ---
class DepartmentOut(BaseModel):
    id: int
    code: str
    name: str
    building: str

    class Config:
        from_attributes = True

# --- Faculty Schemas ---
class FacultyOut(BaseModel):
    id: int
    name: str
    email: str
    department_id: int
    designation: str

    class Config:
        from_attributes = True

# --- Course Schemas ---
class CourseOut(BaseModel):
    id: int
    code: str
    name: str
    department_id: int
    credits: int
    required_room_type: str
    required_equipment: List[str] = []
    semester: int

    class Config:
        from_attributes = True

# --- Cohort Schemas ---
class StudentCohortOut(BaseModel):
    id: int
    code: str
    name: str
    department_id: int
    size: int
    semester: int

    class Config:
        from_attributes = True

# --- Timetable Schemas ---
class TimetableScheduleOut(BaseModel):
    id: int
    course_id: int
    faculty_id: int
    cohort_id: int
    room_id: int
    day_of_week: str
    start_time: str
    end_time: str
    status: str
    academic_term: str
    
    # Enriched details for frontend view
    course_code: Optional[str] = None
    course_name: Optional[str] = None
    faculty_name: Optional[str] = None
    cohort_code: Optional[str] = None
    cohort_size: Optional[int] = None
    room_code: Optional[str] = None
    room_name: Optional[str] = None
    building: Optional[str] = None
    required_equipment: Optional[List[str]] = None

    class Config:
        from_attributes = True

# --- Disruption Schemas ---
class DisruptionCreate(BaseModel):
    title: str = Field(..., example="AI Lab 01 Equipment Failure")
    description: Optional[str] = Field(None, example="AI Lab 01 is unavailable on Monday from 09:00 AM to 11:00 AM because of equipment failure.")
    category: str = Field("Equipment Failure", example="Equipment Failure")
    affected_resource_type: str = Field("Room", example="Room")
    affected_resource_id: int = Field(..., example=1)
    day_of_week: str = Field(..., example="Monday")
    date: str = Field(..., example="2026-11-02")
    start_time: str = Field(..., example="09:00")
    end_time: str = Field(..., example="11:00")
    severity: str = Field("High", example="High")
    reported_by: Optional[str] = Field("Administrator", example="Administrator")

class DisruptionOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    category: str
    affected_resource_type: str
    affected_resource_id: int
    day_of_week: str
    date: str
    start_time: str
    end_time: str
    severity: str
    status: str
    reported_by: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Enriched resource name for display
    affected_resource_name: Optional[str] = None

    class Config:
        from_attributes = True

# --- Agent Execution Schemas ---
class AgentExecutionOut(BaseModel):
    id: int
    recovery_run_id: int
    agent_name: str
    agent_role: str
    input_data: Dict[str, Any] = {}
    output_data: Dict[str, Any] = {}
    tools_used: List[str] = []
    status: str
    retry_count: int = 0
    error_details: Optional[str] = None
    start_time: Optional[datetime] = None
    completion_time: Optional[datetime] = None
    duration_ms: int = 0

    class Config:
        from_attributes = True

# --- Proposed Schedule Change Schemas ---
class ProposedScheduleChangeOut(BaseModel):
    id: int
    recovery_run_id: int
    original_schedule_id: int
    new_room_id: int
    new_day_of_week: str
    new_start_time: str
    new_end_time: str
    reason: Optional[str] = None
    displacement_score: float = 0.0
    status: str
    
    # Enriched fields
    course_code: Optional[str] = None
    course_name: Optional[str] = None
    faculty_name: Optional[str] = None
    cohort_code: Optional[str] = None
    cohort_size: Optional[int] = None
    old_room_code: Optional[str] = None
    new_room_code: Optional[str] = None
    new_room_name: Optional[str] = None
    old_day_of_week: Optional[str] = None
    old_start_time: Optional[str] = None
    old_end_time: Optional[str] = None

    class Config:
        from_attributes = True

# --- Recovery Run Schemas ---
class RecoveryRunOut(BaseModel):
    id: int
    disruption_id: int
    status: str
    strategy: str
    objective_value: Optional[float] = None
    solver_status: Optional[str] = None
    execution_time_ms: int = 0
    agent_summary: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Nested relations
    disruption: Optional[DisruptionOut] = None
    agent_executions: List[AgentExecutionOut] = []
    proposed_changes: List[ProposedScheduleChangeOut] = []

    class Config:
        from_attributes = True

# --- Approval Schemas ---
class ApprovalRequest(BaseModel):
    comments: Optional[str] = None
    approved_by: Optional[str] = "Campus Administrator"

class ApprovalOut(BaseModel):
    id: int
    recovery_run_id: int
    disruption_id: int
    status: str
    comments: Optional[str] = None
    approved_by: str
    approved_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# --- Dashboard & Analytics Schemas ---
class DashboardOverview(BaseModel):
    total_rooms: int
    available_rooms: int
    occupied_rooms: int
    active_disruptions: int
    pending_approvals: int
    scheduled_classes_today: int
    recovery_success_rate: float
    system_health: str = "Optimal"
    ai_mode: str = "Hybrid Groq/Deterministic"
    recent_incidents: List[DisruptionOut] = []
    recent_agent_activities: List[AgentExecutionOut] = []
    room_utilization: List[Dict[str, Any]] = []

class AnalyticsData(BaseModel):
    room_utilization_by_type: List[Dict[str, Any]] = []
    disruptions_by_category: List[Dict[str, Any]] = []
    recovery_statistics: Dict[str, Any] = {}
    department_impact: List[Dict[str, Any]] = []
    resource_demand: List[Dict[str, Any]] = []

# --- Audit Log Schemas ---
class AuditLogOut(BaseModel):
    id: int
    entity_type: str
    entity_id: int
    action: str
    details: Dict[str, Any] = {}
    actor: str
    timestamp: datetime

    class Config:
        from_attributes = True
