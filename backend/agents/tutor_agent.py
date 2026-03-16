# backend/agents/tutor_agent.py

from typing import Dict, Tuple


class TutorAgent:
    """
    Simple step-by-step tutor.
    For each topic, we define a small "lesson" as ordered steps:
      - explanation steps
      - question/checkpoint steps
    """

    def __init__(self, db=None):
        self.db = db

        # You can extend this with more topics later
        self.lessons: Dict[str, list] = {
            "recursion": [
                {
                    "type": "explain",
                    "text": "Step 1/5: Recursion is when a function calls itself to solve a smaller version of the same problem. "
                            "Important: every recursive function must have a BASE CASE to stop the recursion."
                },
                {
                    "type": "question",
                    "question": "Checkpoint: Why do we need a base case in recursion?",
                    "expected_keywords": ["stop", "terminates", "end", "infinite"],
                    "hint": "Think about what happens if the function keeps calling itself forever."
                },
                {
                    "type": "explain",
                    "text": "Step 3/5: In recursion, each call is stored on the call stack. When the base case is reached, "
                            "the calls start returning one by one (unwinding the stack)."
                },
                {
                    "type": "question",
                    "question": "Checkpoint: Which data structure is used under the hood to manage recursive calls?",
                    "expected_keywords": ["stack"],
                    "hint": "It's the same structure used by function calls in general."
                },
                {
                    "type": "explain",
                    "text": "Step 5/5: A good recursive solution has:\n"
                            "1) A clear base case\n"
                            "2) A step that moves towards the base case\n"
                            "3) No extra repeated work (if needed, we optimize with memoization / DP)."
                },
            ],
            "arrays": [
                {
                    "type": "explain",
                    "text": "Step 1/3: An array is a collection of elements stored at contiguous memory locations. "
                            "You can access any element in O(1) time using its index."
                },
                {
                    "type": "question",
                    "question": "Checkpoint: What is the time complexity of accessing an element by index in an array?",
                    "expected_keywords": ["o(1)", "constant"],
                    "hint": "Think about direct indexing, like arr[5]."
                },
                {
                    "type": "explain",
                    "text": "Step 3/3: Common operations on arrays include traversal, searching, and sorting. "
                            "Advanced patterns use two pointers or sliding window on arrays."
                },
            ],
        }

    # ---------- public API ----------

    def start_session(self, topic: str) -> Tuple[Dict, str]:
        topic_key = topic.lower()
        if topic_key not in self.lessons:
            topic_key = "recursion"  # default fallback

        session = {
            "topic": topic_key,
            "step_index": 0,
        }

        first_step_text = self._format_step_text(topic_key, 0, is_first=True)
        return session, first_step_text

    def handle_message(self, session: Dict, user_message: str) -> Tuple[Dict, str, bool]:
        """
        Handles user's reply inside a tutor session.
        Returns: (updated_session, reply_text, done_flag)
        """
        topic = session["topic"]
        step_index = session["step_index"]
        steps = self.lessons.get(topic, [])
        if not steps:
            return session, "I don't have a prepared lesson for this topic yet.", True

        current_step = steps[step_index]
        lower_msg = user_message.lower()

        # If user just says "next" or "ok", move forward
        if any(word in lower_msg for word in ["next", "continue", "go on", "ok", "okay"]):
            next_index = step_index + 1
            if next_index >= len(steps):
                return session, "Great! You've completed this mini-lesson. 🎉", True
            session["step_index"] = next_index
            reply = self._format_step_text(topic, next_index)
            return session, reply, False

        # If this step is a question, try to check the answer
        if current_step["type"] == "question":
            expected_keywords = current_step.get("expected_keywords", [])
            if any(kw in lower_msg for kw in expected_keywords):
                # Correct (or close enough)
                next_index = step_index + 1
                if next_index >= len(steps):
                    reply = "✅ Correct! You've completed this mini-lesson. Great job! 🎉"
                    return session, reply, True
                else:
                    session["step_index"] = next_index
                    reply = "✅ Correct! Let's move to the next step.\n\n" + self._format_step_text(
                        topic, next_index
                    )
                    return session, reply, False
            else:
                # Not matching expected keywords
                hint = current_step.get("hint", "")
                reply = "That doesn't fully answer the question yet.\n"
                if hint:
                    reply += f"Hint: {hint}\n"
                reply += "You can try again, or say 'next' if you want me to explain and move on."
                return session, reply, False

        # If this step is explanation and user wrote anything else (like a doubt)
        if current_step["type"] == "explain":
            reply = (
                "If that explanation was confusing, you can ask a specific doubt, "
                "or say 'next' to continue to the next step."
            )
            return session, reply, False

        # Fallback
        return session, "Let's continue. Say 'next' when you're ready.", False

    # ---------- helpers ----------

    def _format_step_text(self, topic: str, index: int, is_first: bool = False) -> str:
        steps = self.lessons.get(topic, [])
        if index < 0 or index >= len(steps):
            return "I think this lesson is complete."

        step = steps[index]
        header = f"Tutor mode: {topic.capitalize()} (step {index + 1} of {len(steps)})"
        if step["type"] == "explain":
            body = step["text"] + "\n\nWhen you're ready, say 'next' to continue."
        else:
            body = "Let's check your understanding.\n\n" + step["question"]

        if is_first:
            intro = f"Starting step-by-step lesson on {topic.capitalize()}.\n\n"
        else:
            intro = ""

        return intro + header + "\n\n" + body
    