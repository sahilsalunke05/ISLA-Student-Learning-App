# backend/agents/recommendation_agent.py

from typing import Dict, List, Optional
from sqlalchemy.orm import Session

from .memory_agent import MemoryAgent


class RecommendationAgent:
    """
    Uses MemoryAgent's profile summary to suggest:
      - Next topics
      - Study plan
      - Example video/resources (mock data for now)
    """

    def __init__(self, db: Session):
        self.db = db
        self.memory_agent = MemoryAgent(db)

        # Mock resource library – you can extend later or load from DB
        self.resource_library = {
            "DSA": {
                "recursion": {
                    "videos": [
                        "https://www.youtube.com/watch?v=IJDJ0kBx2LM",
                        "https://www.youtube.com/watch?v=Mv9NEXX1VHc",
                    ],
                    "topics_after": ["backtracking", "dynamic programming"],
                },
                "arrays": {
                    "videos": [
                        "https://www.youtube.com/watch?v=thL70BR3t5M",
                    ],
                    "topics_after": ["two pointers", "sliding window"],
                },
                "dynamic programming": {
                    "videos": [
                        "https://www.youtube.com/watch?v=nqowUJzG-iM",
                    ],
                    "topics_after": ["advanced DP patterns"],
                },
            }
        }

    def get_recommendation(self, user_id: int, subject: str = "DSA") -> Dict:
        """
        Returns a high-level recommendation based on profile.
        """
        profile = self.memory_agent.get_profile_summary(user_id, subject)

        if not profile:
            # No history yet
            return {
                "has_history": False,
                "message": (
                    "You don't have enough history yet. "
                    "Start with basic recursion and arrays. "
                    "Try: 'start quiz on recursion'."
                ),
                "suggested_topics": ["recursion", "arrays"],
                "suggested_videos": self._collect_videos(subject, ["recursion", "arrays"]),
            }

        weak_topics: List[str] = profile["weak_topics"]
        preferred_difficulty: str = profile["preferred_difficulty"]
        avg_score: float = profile["avg_score"]
        total_quizzes: int = profile["total_quizzes"]

        if weak_topics:
            # Focus on weakest topics first
            focus_topic = weak_topics[0]
        else:
            # If no weak topics, suggest progression topics
            focus_topic = "recursion"

        # Suggested follow-up topics from resource library (if available)
        progression_topics = self._get_progression_topics(subject, focus_topic)

        message_lines = [
            f"Your average score in {subject} is {avg_score:.1f}% over {total_quizzes} quizzes.",
            f"Current preferred difficulty: {preferred_difficulty}.",
        ]

        if weak_topics:
            weak_str = ", ".join(weak_topics)
            message_lines.append(f"Your weak topics are: {weak_str}.")
            message_lines.append(
                f"For now, let's focus on strengthening '{focus_topic}' before moving ahead."
            )
        else:
            message_lines.append(
                "You don't have clearly weak topics yet. That’s great! We'll move you gradually to more challenging topics."
            )

        if progression_topics:
            prog_str = ", ".join(progression_topics)
            message_lines.append(f"Once '{focus_topic}' is comfortable, a good next step is: {prog_str}.")

        videos = self._collect_videos(subject, [focus_topic] + progression_topics)

        return {
            "has_history": True,
            "message": "\n".join(message_lines),
            "focus_topic": focus_topic,
            "next_topics": progression_topics,
            "suggested_videos": videos,
        }

    # ----------------- helpers -----------------

    def _get_progression_topics(self, subject: str, topic: str) -> List[str]:
        subj_data = self.resource_library.get(subject, {})
        info = subj_data.get(topic, {})
        return info.get("topics_after", [])

    def _collect_videos(self, subject: str, topics: List[str]) -> List[str]:
        videos: List[str] = []
        subj_data = self.resource_library.get(subject, {})
        for t in topics:
            info = subj_data.get(t, {})
            for v in info.get("videos", []):
                if v not in videos:
                    videos.append(v)
        return videos
