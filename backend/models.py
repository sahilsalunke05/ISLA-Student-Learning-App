# backend/models.py
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Float,
    ForeignKey,
    JSON,
)
from sqlalchemy.orm import relationship
from datetime import datetime

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    learning_profiles = relationship("LearningProfile", back_populates="user")
    quiz_history = relationship("QuizHistory", back_populates="user")
    flashcards = relationship("Flashcard", back_populates="user")


class LearningProfile(Base):
    __tablename__ = "learning_profile"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    subject = Column(String, default="general")

    avg_score = Column(Float, default=0.0)
    total_quizzes = Column(Integer, default=0)
    preferred_difficulty = Column(String, default="easy")

    weak_topics = Column(JSON, default=list)
    strong_topics = Column(JSON, default=list)

    last_updated = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="learning_profiles")


class QuizHistory(Base):
    __tablename__ = "quiz_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    subject = Column(String)
    topic = Column(String)
    difficulty = Column(String)
    score = Column(Float)
    total_questions = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="quiz_history")


class Flashcard(Base):
    """
    One flashcard = usually a wrong question from a quiz.
    Spaced repetition acts on this table.
    """
    __tablename__ = "flashcards"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    subject = Column(String)
    topic = Column(String)
    question = Column(String)
    answer = Column(String)

    times_seen = Column(Integer, default=0)
    ease_factor = Column(Float, default=2.5)  # optional, for smarter scheduling
    next_due = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="flashcards")


class AgentLog(Base):
    """
    Simple observability log: who did what, when.
    """
    __tablename__ = "agent_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, nullable=True)
    agent_name = Column(String)
    event_type = Column(String)  # e.g. "INTENT", "QUIZ_START", "QUIZ_EVAL"
    message = Column(String)
    extra = Column(JSON, default=dict)
