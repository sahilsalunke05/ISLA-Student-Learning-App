# backend/main.py

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .database import engine, Base, get_db
from .orchestrator import Orchestrator
from .models import QuizHistory, LearningProfile, Flashcard, AgentLog
from .agents.spaced_agent import SpacedRepetitionAgent

# Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="ISLA - Intelligent Student Learning Assistant")

# CORS (so frontend JS can call backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # in production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/ping")
def ping():
    return {"status": "ok", "message": "ISLA backend is running ✅"}


# ---------- Chat request model ----------

class ChatRequest(BaseModel):
    user_id: int = 1
    # we accept BOTH fields so different frontends can use either
    message: str | None = None
    text: str | None = None


# ---------- Main chat endpoint (used by chat page + quiz page) ----------

@app.post("/api/chat")
def chat(payload: ChatRequest, db: Session = Depends(get_db)):
    """
    Unified chat endpoint.

    Frontend can send:
      { "user_id": 1, "message": "start quiz on recursion" }
      or
      { "user_id": 1, "text": "start quiz on recursion" }
      or both.

    We just pick whichever is non-empty.
    """
    user_id = payload.user_id
    msg = payload.text or payload.message or ""

    orchestrator = Orchestrator(db)
    result = orchestrator.handle_user_input(user_id=user_id, text=msg)
    return result


# ---------- History & Dashboard ----------

@app.get("/api/history/{user_id}")
def get_quiz_history(user_id: int, db: Session = Depends(get_db)):
    history = (
        db.query(QuizHistory)
        .filter(QuizHistory.user_id == user_id)
        .order_by(QuizHistory.created_at.desc())
        .all()
    )

    result = []
    for h in history:
        result.append(
            {
                "subject": h.subject,
                "topic": h.topic,
                "difficulty": h.difficulty,
                "score": h.score,
                "total_questions": h.total_questions,
                "created_at": h.created_at.isoformat(),
            }
        )

    return result


@app.get("/api/dashboard/{user_id}")
def get_dashboard(user_id: int, db: Session = Depends(get_db)):
    profile = (
        db.query(LearningProfile)
        .filter(LearningProfile.user_id == user_id)
        .first()
    )

    history = (
        db.query(QuizHistory)
        .filter(QuizHistory.user_id == user_id)
        .all()
    )

    if not profile:
        return {
            "total_quizzes": 0,
            "avg_score": 0,
            "preferred_difficulty": "easy",
            "weak_topics": [],
            "difficulty_distribution": {},
        }

    # Difficulty distribution
    diff_dist: dict[str, int] = {}
    for h in history:
        d = h.difficulty or "easy"
        diff_dist[d] = diff_dist.get(d, 0) + 1

    return {
        "total_quizzes": profile.total_quizzes,
        "avg_score": profile.avg_score,
        "preferred_difficulty": profile.preferred_difficulty,
        "weak_topics": profile.weak_topics,
        "difficulty_distribution": diff_dist,
    }


# ---------- Flashcards (Spaced Repetition) ----------

@app.get("/api/flashcards/due/{user_id}")
def get_due_flashcards(user_id: int, db: Session = Depends(get_db)):
    agent = SpacedRepetitionAgent(db)
    cards = agent.get_due_flashcards(user_id=user_id, limit=10)
    return [
        {
            "id": c.id,
            "subject": c.subject,
            "topic": c.topic,
            "question": c.question,
            "answer": c.answer,
            "times_seen": c.times_seen,
        }
        for c in cards
    ]


class GradeFlashcardRequest(BaseModel):
    card_id: int
    remembered: bool


@app.post("/api/flashcards/grade")
def grade_flashcard(payload: GradeFlashcardRequest, db: Session = Depends(get_db)):
    agent = SpacedRepetitionAgent(db)
    return agent.grade_flashcard(card_id=payload.card_id, remembered=payload.remembered)


# ---------- Admin / Observability ----------

@app.get("/api/admin/metrics")
def get_admin_metrics(db: Session = Depends(get_db)):
    total_quizzes = db.query(QuizHistory).count()
    total_users = db.query(LearningProfile.user_id).distinct().count()
    total_flashcards = db.query(Flashcard).count()
    total_logs = db.query(AgentLog).count()

    return {
        "total_users": total_users,
        "total_quizzes": total_quizzes,
        "total_flashcards": total_flashcards,
        "total_logs": total_logs,
    }


@app.get("/api/admin/logs")
def get_admin_logs(limit: int = 50, db: Session = Depends(get_db)):
    logs = (
        db.query(AgentLog)
        .order_by(AgentLog.timestamp.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "timestamp": l.timestamp.isoformat(),
            "user_id": l.user_id,
            "agent_name": l.agent_name,
            "event_type": l.event_type,
            "message": l.message,
            "extra": l.extra,
        }
        for l in logs
    ]
