# backend/agents/spaced_agent.py

from typing import List, Dict
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from ..models import Flashcard


class SpacedRepetitionAgent:
    """
    Very simple spaced repetition:
      - Each time user marks 'remembered', next_due pushed further.
      - Each 'forgot' keeps it sooner.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_due_flashcards(self, user_id: int, limit: int = 10) -> List[Flashcard]:
        now = datetime.utcnow()
        cards = (
            self.db.query(Flashcard)
            .filter(
                Flashcard.user_id == user_id,
                Flashcard.next_due <= now,
            )
            .order_by(Flashcard.next_due.asc())
            .limit(limit)
            .all()
        )
        return cards

    def grade_flashcard(self, card_id: int, remembered: bool) -> Dict:
        card = self.db.query(Flashcard).filter(Flashcard.id == card_id).first()
        if not card:
            return {"ok": False, "error": "Flashcard not found"}

        card.times_seen = (card.times_seen or 0) + 1
        card.last_seen = datetime.utcnow()

        # Simple scheduling: if remembered -> push further, else sooner
        if remembered:
            # Increase ease + push by (times_seen * 12 hours)
            card.ease_factor = min(3.0, (card.ease_factor or 2.5) + 0.1)
            hours = min(72, card.times_seen * 12)  # up to 3 days
        else:
            # Decrease ease + review in 1 hour
            card.ease_factor = max(1.3, (card.ease_factor or 2.5) - 0.2)
            hours = 1

        card.next_due = datetime.utcnow() + timedelta(hours=hours)

        self.db.commit()
        return {"ok": True}
