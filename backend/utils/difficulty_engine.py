# backend/utils/difficulty_engine.py

from sqlalchemy.orm import Session
from ..models import LearningProfile


def get_next_difficulty(
    db: Session, user_id: int, subject: str, topic: str | None
) -> str:
    """
    Decide next quiz difficulty for this user + subject.
    Uses LearningProfile.preferred_difficulty as base.
    """
    profile = (
        db.query(LearningProfile)
        .filter(
            LearningProfile.user_id == user_id,
            LearningProfile.subject == subject,
        )
        .first()
    )

    if not profile:
        # New user → start easy
        return "easy"

    # You can make this more advanced later (e.g., topic-based)
    return profile.preferred_difficulty or "easy"
