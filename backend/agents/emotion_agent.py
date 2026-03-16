# backend/agents/emotion_agent.py

from typing import Dict


class EmotionAgent:
    def __init__(self, db=None):
        self.db = db

    def analyze(self, text: str) -> Dict:
        """
        Very simple keyword-based emotion detection.
        Later you can replace with ML/NLP.
        Returns:
          {
            "emotion": "tired" | "confused" | "stressed" | "motivated" | "neutral",
            "message": "<supportive text or empty>"
          }
        """
        lower = text.lower()

        # Tired / low-energy
        if any(word in lower for word in ["tired", "sleepy", "exhausted", "drained"]):
            return {
                "emotion": "tired",
                "message": "You seem a bit tired. Let’s keep things light for now, or take a short break if you need. 🌱"
            }

        # Confused / stuck
        if any(phrase in lower for phrase in ["confused", "don't understand", "dont understand", "stuck", "lost"]):
            return {
                "emotion": "confused",
                "message": "I can see you’re feeling confused. That’s totally normal while learning — we’ll go step by step. 💡"
            }

        # Stressed / anxious
        if any(word in lower for word in ["stressed", "anxious", "overwhelmed"]):
            return {
                "emotion": "stressed",
                "message": "It sounds like things feel overwhelming. Breathe. We’ll focus on one small thing at a time. 🧠"
            }

        # Positive / motivated
        if any(word in lower for word in ["excited", "motivated", "ready", "let's go", "lets go"]):
            return {
                "emotion": "motivated",
                "message": "Love the energy! Let’s push a bit further with your learning today. 🚀"
            }

        # Default
        return {
            "emotion": "neutral",
            "message": ""
        }
