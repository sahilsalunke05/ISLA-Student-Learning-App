# backend/agents/memory_agent.py

from typing import Optional
from sqlalchemy.orm import Session

from ..models import User, LearningProfile, QuizHistory
from datetime import datetime


class MemoryAgent:
    """
    Handles long-term memory:
      - LearningProfile per user + subject
      - QuizHistory insertion
      - Weak topics updates
    """

    def __init__(self, db: Session):
        self.db = db

    # ---------- basic helpers ----------

    def get_or_create_user(self, user_id: int) -> User:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            user = User(id=user_id, username=None)
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
        return user

    def get_or_create_profile(self, user_id: int, subject: str) -> LearningProfile:
        profile = (
            self.db.query(LearningProfile)
            .filter(
                LearningProfile.user_id == user_id,
                LearningProfile.subject == subject,
            )
            .first()
        )
        if not profile:
            profile = LearningProfile(
                user_id=user_id,
                subject=subject,
                avg_score=0.0,
                total_quizzes=0,
                preferred_difficulty="easy",
                weak_topics=[],
                strong_topics=[],
            )
            self.db.add(profile)
            self.db.commit()
            self.db.refresh(profile)
        return profile

    # ---------- update after each quiz ----------

    def update_after_quiz(
        self,
        user_id: int,
        subject: str,
        topic: str,
        difficulty: str,
        percentage_score: float,
        total_questions: int,
    ):
        """
        Called after a quiz is evaluated.
        Updates:
          - QuizHistory
          - LearningProfile (avg_score, total_quizzes, weak_topics, difficulty)
        """
        self.get_or_create_user(user_id)
        profile = self.get_or_create_profile(user_id, subject)

        # Insert history
        history = QuizHistory(
            user_id=user_id,
            subject=subject,
            topic=topic,
            difficulty=difficulty,
            score=percentage_score,
            total_questions=total_questions,
        )
        self.db.add(history)

        # Update profile averages
        old_total = profile.total_quizzes
        old_avg = profile.avg_score

        # new_avg = (old_avg * old_total + new_score) / (old_total + 1)
        new_total = old_total + 1
        new_avg = ((old_avg * old_total) + percentage_score) / new_total

        profile.total_quizzes = new_total
        profile.avg_score = new_avg
        profile.last_updated = datetime.utcnow()

        # Update weak topics based on threshold
        weak = set(profile.weak_topics or [])
        strong = set(profile.strong_topics or [])

        if percentage_score < 50:
            weak.add(topic)
            # if topic was strong before, remove it
            if topic in strong:
                strong.remove(topic)
        elif percentage_score >= 80:
            strong.add(topic)
            if topic in weak:
                weak.remove(topic)

        profile.weak_topics = list(weak)
        profile.strong_topics = list(strong)

        # Update preferred difficulty based on rolling average
        # Very simple rule:
        #   avg < 50  -> easy
        #   50–80     -> medium
        #   >80       -> hard
        if new_avg < 50:
            profile.preferred_difficulty = "easy"
        elif new_avg < 80:
            profile.preferred_difficulty = "medium"
        else:
            profile.preferred_difficulty = "hard"

        self.db.commit()

    # ---------- getters for use in other agents ----------

    def get_profile_summary(self, user_id: int, subject: str = "DSA") -> Optional[dict]:
        profile = (
            self.db.query(LearningProfile)
            .filter(
                LearningProfile.user_id == user_id,
                LearningProfile.subject == subject,
            )
            .first()
        )
        if not profile:
            return None

        return {
            "avg_score": profile.avg_score,
            "total_quizzes": profile.total_quizzes,
            "preferred_difficulty": profile.preferred_difficulty,
            "weak_topics": profile.weak_topics or [],
            "strong_topics": profile.strong_topics or [],
        }
