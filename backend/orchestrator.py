# backend/orchestrator.py
from typing import Dict, List
from sqlalchemy.orm import Session

from .agents.user_agent import UserAgent
from .agents.quiz_agent import QuizAgent
from .agents.evaluation_agent import EvaluationAgent
from .agents.emotion_agent import EmotionAgent
from .agents.memory_agent import MemoryAgent
from .agents.recommendation_agent import RecommendationAgent
from .agents.tutor_agent import TutorAgent  # NEW

# Simple in-memory storage for current quiz per user
ACTIVE_QUIZZES: Dict[int, Dict] = {}

# NEW: in-memory tutor sessions per user
ACTIVE_TUTOR_SESSIONS: Dict[int, Dict] = {}


class Orchestrator:
    def __init__(self, db: Session):
        self.db = db
        self.user_agent = UserAgent(db)
        self.quiz_agent = QuizAgent(db)
        # make sure EvaluationAgent __init__ accepts optional db (db=None)
        self.eval_agent = EvaluationAgent()
        self.emotion_agent = EmotionAgent(db)
        self.memory_agent = MemoryAgent(db)
        self.recommendation_agent = RecommendationAgent(db)
        self.tutor_agent = TutorAgent(db)  # NEW

    def handle_user_input(self, user_id: int, text: str) -> Dict:
        """
        Main entry for user messages.
        1) Emotion analysis
        2) If in tutor mode, route to TutorAgent
        3) Check if this is quiz answers
        4) Otherwise, detect intent and respond
        """
        # ---------- 1) Emotion detection ----------
        emo_result = self.emotion_agent.analyze(text)
        emo_message = emo_result.get("message", "")
        emotion_label = emo_result.get("emotion", "neutral")

        # ---------- 2) Active Tutor session handling ----------
        if user_id in ACTIVE_TUTOR_SESSIONS:
            session = ACTIVE_TUTOR_SESSIONS[user_id]
            new_session, tutor_reply, done = self.tutor_agent.handle_message(
                session, text
            )

            if done:
                ACTIVE_TUTOR_SESSIONS.pop(user_id, None)
            else:
                ACTIVE_TUTOR_SESSIONS[user_id] = new_session

            reply_text = tutor_reply
            if emo_message:
                reply_text = emo_message + "\n\n" + reply_text

            return {
                "user_id": user_id,
                "reply": reply_text,
                "intent": "TUTOR_STEP",
                "emotion": emotion_label,
                "tutor_session": None if done else new_session,
                "tutor_done": done,
            }

        # ---------- 3) Quiz answer handling ----------
        if user_id in ACTIVE_QUIZZES and self._looks_like_answers(text):
            base_response = self._handle_quiz_answers(user_id, text)
            # Attach emotion context if any
            if emo_message:
                base_response["reply"] = emo_message + "\n\n" + base_response["reply"]
            base_response["emotion"] = emotion_label
            return base_response

        # ---------- 4) Normal intent handling ----------
        intent_data = self.user_agent.understand_intent(user_id, text)
        intent = intent_data.get("intent")

        # --- NEW: start tutor mode ---
        if intent == "START_TUTOR":
            topic = intent_data.get("topic", "recursion")
            session, tutor_text = self.tutor_agent.start_session(topic)
            ACTIVE_TUTOR_SESSIONS[user_id] = session

            reply = tutor_text
            if emo_message:
                reply = emo_message + "\n\n" + reply

            return {
                "user_id": user_id,
                "reply": reply,
                "intent": intent,
                "emotion": emotion_label,
                "tutor_session": session,
                "tutor_done": False,
            }

        # --- NEW: explain a specific question (user pasted a question & said "explain") ---
        if intent == "EXPLAIN_QUESTION":
            q_text = intent_data.get("text", "")
            match = self.quiz_agent.find_question_by_text(q_text)
            if not match:
                reply = (
                    "I couldn't match this to any question from my quiz bank.\n\n"
                    "Please paste the exact question text from one of my quizzes, "
                    "or include the main sentence of the question."
                )
            else:
                q = match["question"]
                qid = q.get("id")
                subject = match["subject"]
                topic = match["topic"]
                correct_index = q.get("correct_option", 0)
                correct_option_text = q["options"][correct_index]
                expl = self.eval_agent.get_explanation_for_question_id(qid)

                lines = [
                    "Here's the explanation for this question:",
                    f"\nQuestion: {q['question']}",
                    f"Correct answer: option {correct_index + 1} → {correct_option_text}",
                    f"\nSubject: {subject}, Topic: {topic}",
                    f"\nExplanation:\n{expl}",
                ]
                reply = "\n".join(lines)

            if emo_message:
                reply = emo_message + "\n\n" + reply

            return {
                "user_id": user_id,
                "reply": reply,
                "intent": intent,
                "emotion": emotion_label,
            }

        # ---------- START_QUIZ ----------
        if intent == "START_QUIZ":
            subject = intent_data.get("subject", "DSA")
            topic = intent_data.get("topic")
            num_q = intent_data.get("num_questions", 3)

            quiz = self.quiz_agent.generate_quiz(user_id, subject, topic, num_q)

            # Store active quiz for this user
            ACTIVE_QUIZZES[user_id] = quiz

            # Build a simple text reply listing questions
            lines = [
                f"Starting a quiz on {quiz['topic']} ({subject})",
                f"Difficulty level: {quiz['difficulty']}",
            ]
            lines.append("Reply with your answers like: answers 1 2 3")
            for idx, q in enumerate(quiz["questions"], start=1):
                lines.append(f"\nQ{idx}. {q['question']}")
                for opt_index, opt in enumerate(q["options"], start=1):
                    lines.append(f"   {opt_index}. {opt}")

            reply_text = "\n".join(lines)

            response = {
                "user_id": user_id,
                "reply": reply_text,
                "intent": intent,
                "quiz": quiz,
            }

        elif intent == "REQUEST_RECOMMENDATION":
            rec = self.recommendation_agent.get_recommendation(user_id, subject="DSA")

            if not rec["has_history"]:
                reply = rec["message"]
            else:
                lines = [rec["message"]]
                if rec.get("focus_topic"):
                    lines.append(f"\nPrimary focus topic: {rec['focus_topic']}.")
                if rec.get("next_topics"):
                    next_str = ", ".join(rec["next_topics"])
                    lines.append(f"After that, you can move to: {next_str}.")
                if rec.get("suggested_videos"):
                    lines.append("\nHere are some video suggestions:")
                    for v in rec["suggested_videos"]:
                        lines.append(f"- {v}")

                reply = "\n".join(lines)

            response = {
                "user_id": user_id,
                "reply": reply,
                "intent": intent,
            }

        elif intent == "ASK_DOUBT":
            user_text = intent_data.get("text", "")
            response = {
                "user_id": user_id,
                "reply": f"It seems you have a doubt: '{user_text}'. For now, I can only acknowledge it. Later I'll explain deeply.",
                "intent": intent,
            }

        else:  # SMALL_TALK or unknown
            response = {
                "user_id": user_id,
                "reply": (
                    f"You said: {text}. You can also say:\n"
                    "- 'start quiz on recursion'\n"
                    "- 'start quiz on deadlocks in OS'\n"
                    "- 'teach me recursion step by step'\n"
                    "- 'explain <paste question> ?'\n"
                    "- 'recommend what to study next'"
                ),
                "intent": "SMALL_TALK",
            }

        # Add emotion info and prepend motivation if needed
        if emo_message:
            response["reply"] = emo_message + "\n\n" + response["reply"]
        response["emotion"] = emotion_label

        return response

    # ----------------- helpers -----------------

    def _looks_like_answers(self, text: str) -> bool:
        """
        Check if the message looks like: 'answers 1 2 3' or '1 2 3'
        """
        lower = text.lower().strip()
        if lower.startswith("answers"):
            return True
        # Or just digits and spaces
        parts = lower.split()
        return all(p.isdigit() for p in parts)

    def _parse_answers(self, text: str) -> List[int]:
        lower = text.lower().strip()
        if lower.startswith("answers"):
            lower = lower.replace("answers", "", 1).strip()

        parts = lower.replace(",", " ").split()
        answers = []
        for p in parts:
            if p.isdigit():
                # convert 1-based option to 0-based index
                answers.append(int(p) - 1)
        return answers

    def _handle_quiz_answers(self, user_id: int, text: str) -> Dict:
        quiz = ACTIVE_QUIZZES.get(user_id)
        if not quiz:
            return {
                "user_id": user_id,
                "reply": "I couldn't find an active quiz. Say 'start quiz on recursion' to begin a new one.",
                "intent": "NO_ACTIVE_QUIZ",
            }

        questions = quiz["questions"]
        user_answers = self._parse_answers(text)

        if len(user_answers) != len(questions):
            return {
                "user_id": user_id,
                "reply": f"You provided {len(user_answers)} answers for {len(questions)} questions. Please send all answers like: answers 1 2 3",
                "intent": "INVALID_ANSWER_COUNT",
            }

        result = self.eval_agent.evaluate_quiz(questions, user_answers)

        # Once evaluated, clear active quiz
        ACTIVE_QUIZZES.pop(user_id, None)

        # Save result in memory (DB)
        subject = quiz.get("subject", "DSA")
        topic = quiz.get("topic", "general")
        difficulty = quiz.get("difficulty", "easy")
        self.memory_agent.update_after_quiz(
            user_id=user_id,
            subject=subject,
            topic=topic,
            difficulty=difficulty,
            percentage_score=result["percentage"],
            total_questions=len(questions),
        )

        # ----------------- create flashcards for wrong questions -----------------
        from .models import Flashcard
        wrong_count = 0
        for q, detail in zip(questions, result["details"]):
            if not detail["is_correct"]:
                wrong_count += 1
                card = Flashcard(
                    user_id=user_id,
                    subject=subject,
                    topic=topic,
                    question=q["question"],
                    answer=q["options"][q["correct_option"]],
                )
                self.db.add(card)
        if wrong_count:
            self.db.commit()

        # ----------------- build reply text -----------------
        lines = [
            f"Your score: {result['score']}/{result['total']} ({result['percentage']:.1f}%)",
        ]
        for idx, detail in enumerate(result["details"], start=1):
            q = detail["question"]
            ua = detail["user_answer"]
            ca = detail["correct_answer"]
            status = "✅" if detail["is_correct"] else "❌"
            lines.append(
                f"\nQ{idx}. {q}\n   Your answer: option {ua+1}\n   Correct answer: option {ca+1} {status}"
            )

        if wrong_count:
            lines.append(
                f"\nI’ve created {wrong_count} flashcards from your mistakes. You can review them on the Flashcards page."
            )

        reply_text = "\n".join(lines)

        return {
            "user_id": user_id,
            "reply": reply_text,
            "intent": "QUIZ_EVALUATED",
            "result": result,
        }