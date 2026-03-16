# backend/agents/user_agent.py

from typing import Dict


class UserAgent:
    def __init__(self, db=None):
        self.db = db

    def understand_intent(self, user_id: int, text: str) -> Dict:
        """
        Very simple rule-based intent detection.
        """
        lower = text.lower()

        # -------- tutor mode detection --------
        if any(word in lower for word in ["teach me", "explain step by step", "learn step by step", "step by step"]):
            topic = None
            if "recursion" in lower:
                topic = "recursion"
            elif "array" in lower or "arrays" in lower:
                topic = "arrays"
            elif "deadlock" in lower:
                topic = "deadlocks"

            return {
                "intent": "START_TUTOR",
                "topic": topic or "recursion",  # default topic
            }

        # -------- explain a specific question (EXPLAIN_QUESTION) --------
        # User usually pastes a question and says something like:
        # "explain this question", "why this answer?", "explain: <question>?"
        if "explain" in lower and "?" in lower:
            return {
                "intent": "EXPLAIN_QUESTION",
                "text": text,
            }

        # -------- quiz related --------
        if "start quiz" in lower or "quiz" in lower:
            subject = "DSA"
            topic = None

            # Detect OS subject
            if " os" in lower or "operating system" in lower:
                subject = "OS"

            if "recursion" in lower:
                topic = "recursion"
            elif "array" in lower:
                topic = "arrays"
            elif "stack" in lower:
                topic = "stacks"
            elif "deadlock" in lower:
                topic = "deadlocks"
            elif "scheduling" in lower:
                topic = "scheduling"
            elif "memory" in lower:
                topic = "memory"

            return {
                "intent": "START_QUIZ",
                "subject": subject,
                "topic": topic,
                "num_questions": 3,
            }

        # -------- recommendation related --------
        if (
            "what should i study" in lower
            or "recommend" in lower
            or "next topic" in lower
        ):
            return {
                "intent": "REQUEST_RECOMMENDATION",
            }

        # -------- doubt related --------
        if "i am confused" in lower or "i'm confused" in lower:
            return {
                "intent": "ASK_DOUBT",
                "text": text,
            }

        # Default small-talk / unknown
        return {
            "intent": "SMALL_TALK",
            "text": text,
        }