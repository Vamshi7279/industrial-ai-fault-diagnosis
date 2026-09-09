import json
import datetime
from typing import Optional, Any
from sqlalchemy.orm import Session
from src.models_orm import AuditLog

def log_audit_event(
    db: Session,
    user_id: Optional[str],
    action: str,
    entity_type: str,
    entity_id: str,
    previous_state: Optional[Any] = None,
    new_state: Optional[Any] = None,
    ip_address: Optional[str] = "127.0.0.1"
) -> AuditLog:
    """
    Records an immutable audit log entry in the database.
    """
    prev_str = json.dumps(previous_state) if isinstance(previous_state, (dict, list)) else (str(previous_state) if previous_state else None)
    new_str = json.dumps(new_state) if isinstance(new_state, (dict, list)) else (str(new_state) if new_state else None)
    
    audit_entry = AuditLog(
        user_id=user_id or "system_automator",
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        previous_state=prev_str,
        new_state=new_str,
        ip_address=ip_address,
        timestamp=datetime.datetime.utcnow()
    )
    
    try:
        db.add(audit_entry)
        db.commit()
        db.refresh(audit_entry)
    except Exception as e:
        db.rollback()
        print(f"[AuditLog Error] Failed to write audit event: {e}")
        
    return audit_entry
