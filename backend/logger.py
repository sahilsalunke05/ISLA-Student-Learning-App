# backend/logger.py
from sqlalchemy.orm import Session
from .models import AgentLog
from datetime import datetime


def log_event(
    db: Session,
    agent_name: str,
    event_type: str,
    message: str,
    user_id: int | None = None,
    extra: dict | None = None,
):
    log = AgentLog(
        timestamp=datetime.utcnow(),
        user_id=user_id,
        agent_name=agent_name,
        event_type=event_type,
        message=message,
        extra=extra or {},
    )
    db.add(log)
    db.commit()
