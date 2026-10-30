from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey, 
    Text, Float, JSON, Index
)
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(150), nullable=False)
    building = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    faculties = relationship("Faculty", back_populates="department")
    courses = relationship("Course", back_populates="department")
    cohorts = relationship("StudentCohort", back_populates="department")


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(150), nullable=False)
    capacity = Column(Integer, nullable=False)
    room_type = Column(String(50), nullable=False)  # Computer Lab, Classroom, Lecture Hall, Seminar Hall
    building = Column(String(100), nullable=False)
    floor = Column(Integer, default=1)
    equipment = Column(JSON, default=list)  # ["GPU Workstation", "Smart Projector", "Audio System"]
    is_available = Column(Boolean, default=True)
    maintenance_notes = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    schedules = relationship("TimetableSchedule", back_populates="room")


class Faculty(Base):
    __tablename__ = "faculties"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="CASCADE"), nullable=False)
    designation = Column(String(100), default="Assistant Professor")
    created_at = Column(DateTime, default=datetime.utcnow)

    department = relationship("Department", back_populates="faculties")
    schedules = relationship("TimetableSchedule", back_populates="faculty")


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(150), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="CASCADE"), nullable=False)
    credits = Column(Integer, default=3)
    required_room_type = Column(String(50), nullable=False)
    required_equipment = Column(JSON, default=list)
    semester = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

    department = relationship("Department", back_populates="courses")
    schedules = relationship("TimetableSchedule", back_populates="course")


class StudentCohort(Base):
    __tablename__ = "student_cohorts"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(150), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="CASCADE"), nullable=False)
    size = Column(Integer, nullable=False)
    semester = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

    department = relationship("Department", back_populates="cohorts")
    schedules = relationship("TimetableSchedule", back_populates="cohort")


class TimetableSchedule(Base):
    __tablename__ = "timetable_schedules"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    faculty_id = Column(Integer, ForeignKey("faculties.id", ondelete="CASCADE"), nullable=False)
    cohort_id = Column(Integer, ForeignKey("student_cohorts.id", ondelete="CASCADE"), nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)
    day_of_week = Column(String(20), nullable=False, index=True)  # Monday - Saturday
    start_time = Column(String(10), nullable=False)  # HH:MM format e.g. "09:00"
    end_time = Column(String(10), nullable=False)    # HH:MM format e.g. "11:00"
    status = Column(String(30), default="Scheduled") # Scheduled, Disrupted, Rescheduled, Cancelled
    academic_term = Column(String(50), default="Fall 2026")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    course = relationship("Course", back_populates="schedules")
    faculty = relationship("Faculty", back_populates="schedules")
    cohort = relationship("StudentCohort", back_populates="schedules")
    room = relationship("Room", back_populates="schedules")

    __table_args__ = (
        Index("idx_schedule_slot", "day_of_week", "start_time", "end_time"),
    )


class Disruption(Base):
    __tablename__ = "disruptions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=False)  # Equipment Failure, Maintenance, Faculty Unavailable, Room Overflow
    affected_resource_type = Column(String(50), nullable=False)  # Room, Faculty, Cohort
    affected_resource_id = Column(Integer, nullable=False)
    day_of_week = Column(String(20), nullable=False)
    date = Column(String(20), nullable=False)  # YYYY-MM-DD
    start_time = Column(String(10), nullable=False)  # HH:MM
    end_time = Column(String(10), nullable=False)    # HH:MM
    severity = Column(String(20), default="High")   # Low, Medium, High, Critical
    status = Column(String(30), default="Reported")  # Reported, Analyzing, Recovery Proposed, Approved, Rejected, Resolved
    reported_by = Column(String(100), default="Administrator")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    recovery_runs = relationship("RecoveryRun", back_populates="disruption", cascade="all, delete-orphan")


class RecoveryRun(Base):
    __tablename__ = "recovery_runs"

    id = Column(Integer, primary_key=True, index=True)
    disruption_id = Column(Integer, ForeignKey("disruptions.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(30), default="Pending")  # Pending, Running, Success, Failed, Infeasible, Escalated
    strategy = Column(String(100), default="OR-Tools CP-SAT Timetable Optimization")
    objective_value = Column(Float, nullable=True)
    solver_status = Column(String(50), nullable=True)  # OPTIMAL, FEASIBLE, INFEASIBLE, TIMEOUT
    execution_time_ms = Column(Integer, default=0)
    agent_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    disruption = relationship("Disruption", back_populates="recovery_runs")
    agent_executions = relationship("AgentExecution", back_populates="recovery_run", cascade="all, delete-orphan")
    proposed_changes = relationship("ProposedScheduleChange", back_populates="recovery_run", cascade="all, delete-orphan")
    approvals = relationship("Approval", back_populates="recovery_run", cascade="all, delete-orphan")


class AgentExecution(Base):
    __tablename__ = "agent_executions"

    id = Column(Integer, primary_key=True, index=True)
    recovery_run_id = Column(Integer, ForeignKey("recovery_runs.id", ondelete="CASCADE"), nullable=False)
    agent_name = Column(String(100), nullable=False)
    agent_role = Column(String(150), nullable=False)
    input_data = Column(JSON, default=dict)
    output_data = Column(JSON, default=dict)
    tools_used = Column(JSON, default=list)
    status = Column(String(30), default="Waiting")  # Waiting, Running, Completed, Failed, Retrying, Escalated
    retry_count = Column(Integer, default=0)
    error_details = Column(Text, nullable=True)
    start_time = Column(DateTime, nullable=True)
    completion_time = Column(DateTime, nullable=True)
    duration_ms = Column(Integer, default=0)

    recovery_run = relationship("RecoveryRun", back_populates="agent_executions")


class ProposedScheduleChange(Base):
    __tablename__ = "proposed_schedule_changes"

    id = Column(Integer, primary_key=True, index=True)
    recovery_run_id = Column(Integer, ForeignKey("recovery_runs.id", ondelete="CASCADE"), nullable=False)
    original_schedule_id = Column(Integer, ForeignKey("timetable_schedules.id", ondelete="CASCADE"), nullable=False)
    new_room_id = Column(Integer, ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)
    new_day_of_week = Column(String(20), nullable=False)
    new_start_time = Column(String(10), nullable=False)
    new_end_time = Column(String(10), nullable=False)
    reason = Column(String(255), nullable=True)
    displacement_score = Column(Float, default=0.0)
    status = Column(String(30), default="Proposed")  # Proposed, Approved, Rejected, Applied

    recovery_run = relationship("RecoveryRun", back_populates="proposed_changes")
    original_schedule = relationship("TimetableSchedule")
    new_room = relationship("Room")


class Approval(Base):
    __tablename__ = "approvals"

    id = Column(Integer, primary_key=True, index=True)
    recovery_run_id = Column(Integer, ForeignKey("recovery_runs.id", ondelete="CASCADE"), nullable=False)
    disruption_id = Column(Integer, ForeignKey("disruptions.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(30), default="Pending")  # Pending, Approved, Rejected
    comments = Column(Text, nullable=True)
    approved_by = Column(String(100), default="Campus Administrator")
    approved_at = Column(DateTime, nullable=True)

    recovery_run = relationship("RecoveryRun", back_populates="approvals")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(50), nullable=False, index=True)
    entity_id = Column(Integer, nullable=False, index=True)
    action = Column(String(50), nullable=False)  # CREATE, UPDATE, RECOVER, APPROVE, REJECT, OPTIMIZE, VALIDATE
    details = Column(JSON, default=dict)
    actor = Column(String(100), default="System")
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
