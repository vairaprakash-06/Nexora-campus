from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.config import settings
from backend.app.models.entities import (
    Room, Disruption, TimetableSchedule, RecoveryRun, AgentExecution, Approval
)
from backend.app.schemas.api import DashboardOverview, DisruptionOut, AgentExecutionOut
from backend.app.agents.llm_client import llm_client

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("", response_model=DashboardOverview)
def get_dashboard_metrics(db: Session = Depends(get_db)):
    total_rooms = db.query(Room).count()
    available_rooms = db.query(Room).filter(Room.is_available == True).count()
    occupied_rooms = total_rooms - available_rooms

    active_disruptions = db.query(Disruption).filter(
        Disruption.status.in_(["Reported", "Analyzing", "Recovery Proposed", "Escalated"])
    ).count()

    pending_approvals = db.query(RecoveryRun).filter(
        RecoveryRun.status.in_(["Success", "Pending"])
    ).filter(
        ~RecoveryRun.approvals.any()
    ).count()

    scheduled_classes_today = db.query(TimetableSchedule).filter(
        TimetableSchedule.day_of_week == "Monday",
        TimetableSchedule.status.in_(["Scheduled", "Rescheduled"])
    ).count()

    total_recovery_runs = db.query(RecoveryRun).count()
    successful_runs = db.query(RecoveryRun).filter(RecoveryRun.status == "Success").count()
    recovery_success_rate = round((successful_runs / total_recovery_runs * 100), 1) if total_recovery_runs > 0 else 100.0

    # Recent incidents
    incidents = db.query(Disruption).order_by(Disruption.created_at.desc()).limit(5).all()
    recent_incidents_out = []
    for inc in incidents:
        res_name = f"Resource #{inc.affected_resource_id}"
        if inc.affected_resource_type.lower() == "room":
            r = db.query(Room).filter(Room.id == inc.affected_resource_id).first()
            if r:
                res_name = f"{r.code} - {r.name}"
        inc_dict = {
            "id": inc.id,
            "title": inc.title,
            "description": inc.description,
            "category": inc.category,
            "affected_resource_type": inc.affected_resource_type,
            "affected_resource_id": inc.affected_resource_id,
            "day_of_week": inc.day_of_week,
            "date": inc.date,
            "start_time": inc.start_time,
            "end_time": inc.end_time,
            "severity": inc.severity,
            "status": inc.status,
            "reported_by": inc.reported_by,
            "created_at": inc.created_at,
            "updated_at": inc.updated_at,
            "affected_resource_name": res_name
        }
        recent_incidents_out.append(DisruptionOut(**inc_dict))

    # Recent agent activities
    agent_acts = db.query(AgentExecution).order_by(AgentExecution.start_time.desc()).limit(7).all()
    recent_agent_out = [AgentExecutionOut.from_orm(a) for a in agent_acts]

    # Room utilization breakdown by building
    rooms = db.query(Room).all()
    bldg_counts = {}
    for r in rooms:
        bldg_counts[r.building] = bldg_counts.get(r.building, 0) + 1
    
    room_utilization = [
        {"building": bldg, "count": count, "utilization_pct": 75}
        for bldg, count in bldg_counts.items()
    ]

    ai_mode_str = "Active Groq LLM" if llm_client.is_available() else "Deterministic Agent Mode"

    return DashboardOverview(
        total_rooms=total_rooms,
        available_rooms=available_rooms,
        occupied_rooms=occupied_rooms,
        active_disruptions=active_disruptions,
        pending_approvals=pending_approvals,
        scheduled_classes_today=scheduled_classes_today,
        recovery_success_rate=recovery_success_rate,
        system_health="Operational" if active_disruptions == 0 else "Active Recoveries",
        ai_mode=ai_mode_str,
        recent_incidents=recent_incidents_out,
        recent_agent_activities=recent_agent_out,
        room_utilization=room_utilization
    )
