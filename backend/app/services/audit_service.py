from datetime import datetime
from typing import Dict, Any
from sqlalchemy.orm import Session
from backend.app.models.entities import AuditLog

def log_audit_event(
    db: Session,
    entity_type: str,
    entity_id: int,
    action: str,
    details: Dict[str, Any],
    actor: str = "Administrator"
) -> AuditLog:
    audit = AuditLog(
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        details=details,
        actor=actor,
        timestamp=datetime.utcnow()
    )
    db.add(audit)
    db.commit()
    db.refresh(audit)
    return audit
