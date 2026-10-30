from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from backend.app.models.entities import Room, TimetableSchedule

def time_str_to_minutes(t_str: str) -> int:
    parts = t_str.strip().split(":")
    return int(parts[0]) * 60 + int(parts[1])

def slots_overlap(start1: str, end1: str, start2: str, end2: str) -> bool:
    s1, e1 = time_str_to_minutes(start1), time_str_to_minutes(end1)
    s2, e2 = time_str_to_minutes(start2), time_str_to_minutes(end2)
    return max(s1, s2) < min(e1, e2)

def evaluate_rooms_for_recovery(
    db: Session,
    required_type: str,
    min_capacity: int,
    required_equipment: List[str],
    day_of_week: str,
    start_time: str,
    end_time: str,
    preferred_building: str = None,
    exclude_room_ids: List[int] = None
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Deterministically evaluates all campus rooms against hard constraints and soft preferences.
    Returns: (suitable_rooms, rejected_rooms)
    """
    if exclude_room_ids is None:
        exclude_room_ids = []

    all_rooms = db.query(Room).all()
    suitable = []
    rejected = []

    # Get all active schedules for the day to check room occupation
    day_schedules = db.query(TimetableSchedule).filter(
        TimetableSchedule.day_of_week == day_of_week,
        TimetableSchedule.status.in_(["Scheduled", "Rescheduled"])
    ).all()

    occupied_room_ids = set()
    for sch in day_schedules:
        if slots_overlap(start_time, end_time, sch.start_time, sch.end_time):
            occupied_room_ids.add(sch.room_id)

    req_eq_set = set(e.strip().lower() for e in (required_equipment or []))

    for room in all_rooms:
        if room.id in exclude_room_ids:
            rejected.append({
                "room_id": room.id,
                "room_code": room.code,
                "room_name": room.name,
                "building": room.building,
                "capacity": room.capacity,
                "room_type": room.room_type,
                "equipment": room.equipment or [],
                "is_available_in_slot": False,
                "capacity_sufficient": room.capacity >= min_capacity,
                "equipment_match": True,
                "room_type_match": True,
                "suitability_score": 0.0,
                "rejection_reason": "Room is under active disruption / maintenance."
            })
            continue

        # Check room availability flag
        if not room.is_available:
            rejected.append({
                "room_id": room.id,
                "room_code": room.code,
                "room_name": room.name,
                "building": room.building,
                "capacity": room.capacity,
                "room_type": room.room_type,
                "equipment": room.equipment or [],
                "is_available_in_slot": False,
                "capacity_sufficient": room.capacity >= min_capacity,
                "equipment_match": True,
                "room_type_match": True,
                "suitability_score": 0.0,
                "rejection_reason": f"Room is flagged unavailable: {room.maintenance_notes or 'Maintenance'}"
            })
            continue

        # Check occupation in slot
        is_occupied = room.id in occupied_room_ids
        if is_occupied:
            rejected.append({
                "room_id": room.id,
                "room_code": room.code,
                "room_name": room.name,
                "building": room.building,
                "capacity": room.capacity,
                "room_type": room.room_type,
                "equipment": room.equipment or [],
                "is_available_in_slot": False,
                "capacity_sufficient": room.capacity >= min_capacity,
                "equipment_match": True,
                "room_type_match": True,
                "suitability_score": 10.0,
                "rejection_reason": f"Room is already occupied by another class on {day_of_week} between {start_time}-{end_time}."
            })
            continue

        # Check room type match
        type_match = (room.room_type.lower() == required_type.lower())
        if not type_match:
            rejected.append({
                "room_id": room.id,
                "room_code": room.code,
                "room_name": room.name,
                "building": room.building,
                "capacity": room.capacity,
                "room_type": room.room_type,
                "equipment": room.equipment or [],
                "is_available_in_slot": True,
                "capacity_sufficient": room.capacity >= min_capacity,
                "equipment_match": False,
                "room_type_match": False,
                "suitability_score": 15.0,
                "rejection_reason": f"Room type mismatch: Required '{required_type}', found '{room.room_type}'."
            })
            continue

        # Check capacity
        cap_sufficient = (room.capacity >= min_capacity)
        if not cap_sufficient:
            rejected.append({
                "room_id": room.id,
                "room_code": room.code,
                "room_name": room.name,
                "building": room.building,
                "capacity": room.capacity,
                "room_type": room.room_type,
                "equipment": room.equipment or [],
                "is_available_in_slot": True,
                "capacity_sufficient": False,
                "equipment_match": True,
                "room_type_match": True,
                "suitability_score": 25.0,
                "rejection_reason": f"Insufficient capacity: Room capacity ({room.capacity}) < Cohort size ({min_capacity})."
            })
            continue

        # Check equipment requirements
        room_eq_set = set(e.strip().lower() for e in (room.equipment or []))
        missing_eq = req_eq_set - room_eq_set
        if missing_eq:
            missing_str = ", ".join(m.title() for m in missing_eq)
            rejected.append({
                "room_id": room.id,
                "room_code": room.code,
                "room_name": room.name,
                "building": room.building,
                "capacity": room.capacity,
                "room_type": room.room_type,
                "equipment": room.equipment or [],
                "is_available_in_slot": True,
                "capacity_sufficient": True,
                "equipment_match": False,
                "room_type_match": True,
                "suitability_score": 35.0,
                "rejection_reason": f"Missing mandatory equipment: {missing_str}."
            })
            continue

        # Calculate Suitability Score (0 - 100)
        # 100 max:
        # Base 60 for meeting all hard constraints
        # +20 if in preferred building
        # +10 for optimal capacity slack (e.g. within 10 seats of cohort size)
        # +10 for matching extra equipment
        score = 60.0
        if preferred_building and room.building.lower() == preferred_building.lower():
            score += 25.0
        else:
            score += 10.0

        slack = room.capacity - min_capacity
        if 0 <= slack <= 10:
            score += 15.0  # Perfect fit
        elif slack <= 25:
            score += 10.0
        else:
            score += 5.0  # oversized room, slight penalty

        suitable.append({
            "room_id": room.id,
            "room_code": room.code,
            "room_name": room.name,
            "building": room.building,
            "capacity": room.capacity,
            "room_type": room.room_type,
            "equipment": room.equipment or [],
            "is_available_in_slot": True,
            "capacity_sufficient": True,
            "equipment_match": True,
            "room_type_match": True,
            "suitability_score": round(score, 1),
            "rejection_reason": None
        })

    # Sort suitable rooms by suitability score descending
    suitable.sort(key=lambda x: x["suitability_score"], reverse=True)
    return suitable, rejected
