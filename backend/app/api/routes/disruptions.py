from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.entities import Disruption, Room
from backend.app.schemas.api import DisruptionOut, DisruptionCreate
from backend.app.services.recovery_service import RecoveryService
from backend.app.services.audit_service import log_audit_event

router = APIRouter(prefix="/disruptions", tags=["Disruptions"])

@router.get("", response_model=List[DisruptionOut])
def get_all_disruptions(db: Session = Depends(get_db)):
    disruptions = db.query(Disruption).order_by(Disruption.created_at.desc()).all()
    results = []
    for d in disruptions:
        res_name = f"Resource #{d.affected_resource_id}"
        if d.affected_resource_type.lower() == "room":
            r = db.query(Room).filter(Room.id == d.affected_resource_id).first()
            if r:
                res_name = f"{r.code} - {r.name}"
        item = DisruptionOut(
            id=d.id,
            title=d.title,
            description=d.description,
            category=d.category,
            affected_resource_type=d.affected_resource_type,
            affected_resource_id=d.affected_resource_id,
            day_of_week=d.day_of_week,
            date=d.date,
            start_time=d.start_time,
            end_time=d.end_time,
            severity=d.severity,
            status=d.status,
            reported_by=d.reported_by,
            created_at=d.created_at,
            updated_at=d.updated_at,
            affected_resource_name=res_name
        )
        results.append(item)
    return results

@router.post("", response_model=DisruptionOut)
def create_disruption(
    payload: DisruptionCreate,
    trigger_recovery: bool = True,
    db: Session = Depends(get_db)
):
    disruption = Disruption(
        title=payload.title,
        description=payload.description,
        category=payload.category,
        affected_resource_type=payload.affected_resource_type,
        affected_resource_id=payload.affected_resource_id,
        day_of_week=payload.day_of_week,
        date=payload.date,
        start_time=payload.start_time,
        end_time=payload.end_time,
        severity=payload.severity,
        status="Reported",
        reported_by=payload.reported_by or "Administrator"
    )
    db.add(disruption)
    db.commit()
    db.refresh(disruption)

    log_audit_event(
        db=db,
        entity_type="Disruption",
        entity_id=disruption.id,
        action="REPORT_INCIDENT",
        details=payload.dict(),
        actor=disruption.reported_by
    )

    # If trigger_recovery is true, execute the multi-agent workflow immediately
    if trigger_recovery:
        RecoveryService.trigger_recovery(db=db, disruption_id=disruption.id)
        db.refresh(disruption)

    res_name = f"Resource #{disruption.affected_resource_id}"
    if disruption.affected_resource_type.lower() == "room":
        r = db.query(Room).filter(Room.id == disruption.affected_resource_id).first()
        if r:
            res_name = f"{r.code} - {r.name}"

    return DisruptionOut(
        id=disruption.id,
        title=disruption.title,
        description=disruption.description,
        category=disruption.category,
        affected_resource_type=disruption.affected_resource_type,
        affected_resource_id=disruption.affected_resource_id,
        day_of_week=disruption.day_of_week,
        date=disruption.date,
        start_time=disruption.start_time,
        end_time=disruption.end_time,
        severity=disruption.severity,
        status=disruption.status,
        reported_by=disruption.reported_by,
        created_at=disruption.created_at,
        updated_at=disruption.updated_at,
        affected_resource_name=res_name
    )

@router.get("/{disruption_id}", response_model=DisruptionOut)
def get_disruption_by_id(disruption_id: int, db: Session = Depends(get_db)):
    d = db.query(Disruption).filter(Disruption.id == disruption_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Disruption incident not found")
    
    res_name = f"Resource #{d.affected_resource_id}"
    if d.affected_resource_type.lower() == "room":
        r = db.query(Room).filter(Room.id == d.affected_resource_id).first()
        if r:
            res_name = f"{r.code} - {r.name}"

    return DisruptionOut(
        id=d.id,
        title=d.title,
        description=d.description,
        category=d.category,
        affected_resource_type=d.affected_resource_type,
        affected_resource_id=d.affected_resource_id,
        day_of_week=d.day_of_week,
        date=d.date,
        start_time=d.start_time,
        end_time=d.end_time,
        severity=d.severity,
        status=d.status,
        reported_by=d.reported_by,
        created_at=d.created_at,
        updated_at=d.updated_at,
        affected_resource_name=res_name
    )
