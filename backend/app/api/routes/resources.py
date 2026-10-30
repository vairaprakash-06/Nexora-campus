from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.entities import Room
from backend.app.schemas.api import RoomOut, RoomCreate, RoomUpdate
from backend.app.services.audit_service import log_audit_event

router = APIRouter(prefix="/resources", tags=["Resources"])

@router.get("", response_model=List[RoomOut])
def get_all_resources(
    room_type: Optional[str] = Query(None),
    building: Optional[str] = Query(None),
    is_available: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Room)
    if room_type:
        query = query.filter(Room.room_type == room_type)
    if building:
        query = query.filter(Room.building == building)
    if is_available is not None:
        query = query.filter(Room.is_available == is_available)
    if search:
        search_fmt = f"%{search}%"
        query = query.filter((Room.code.ilike(search_fmt)) | (Room.name.ilike(search_fmt)))

    rooms = query.order_by(Room.building, Room.code).all()
    return rooms

@router.get("/{room_id}", response_model=RoomOut)
def get_resource_by_id(room_id: int, db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room resource not found")
    return room

@router.put("/{room_id}", response_model=RoomOut)
def update_resource(
    room_id: int,
    payload: RoomUpdate,
    db: Session = Depends(get_db)
):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room resource not found")

    update_dict = payload.dict(exclude_unset=True)
    for field, val in update_dict.items():
        setattr(room, field, val)

    db.commit()
    db.refresh(room)

    log_audit_event(
        db=db,
        entity_type="Room",
        entity_id=room.id,
        action="UPDATE",
        details=update_dict,
        actor="Administrator"
    )
    return room
