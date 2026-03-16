# backend/agents/quiz_agent.py

from typing import List, Dict
from sqlalchemy.orm import Session

from ..utils.difficulty_engine import get_next_difficulty


class QuizAgent:
    def __init__(self, db: Session | None = None):
        self.db = db

        # Question bank: 20 questions per subject (DSA, OS)
        self.question_bank = {
            "DSA": {
                "recursion": [
                    {
                        "id": 1,
                        "question": "What is recursion?",
                        "options": [
                            "A function that calls itself",
                            "A function that never returns",
                            "A loop that runs forever",
                            "A function that calls multiple other functions",
                        ],
                        "correct_option": 0,
                        "difficulty": "easy",
                    },
                    {
                        "id": 2,
                        "question": "Why is a base case required in recursion?",
                        "options": [
                            "To make the algorithm faster",
                            "To stop the recursion and prevent infinite calls",
                            "To allocate more memory",
                            "To convert recursion to iteration",
                        ],
                        "correct_option": 1,
                        "difficulty": "easy",
                    },
                    {
                        "id": 3,
                        "question": "Which data structure is used by recursion internally?",
                        "options": [
                            "Queue",
                            "Stack",
                            "Heap",
                            "Graph",
                        ],
                        "correct_option": 1,
                        "difficulty": "easy",
                    },
                    {
                        "id": 4,
                        "question": "What happens if a recursive function has no valid base case?",
                        "options": [
                            "It returns 0",
                            "It runs faster",
                            "It leads to infinite recursion and stack overflow",
                            "It behaves like a loop",
                        ],
                        "correct_option": 2,
                        "difficulty": "medium",
                    },
                    {
                        "id": 5,
                        "question": "Which of the following problems is best suited for recursion?",
                        "options": [
                            "Finding maximum of two numbers",
                            "Factorial of a number",
                            "Swapping two numbers",
                            "Reading input from user",
                        ],
                        "correct_option": 1,
                        "difficulty": "medium",
                    },
                ],
                "arrays": [
                    {
                        "id": 6,
                        "question": "What is the time complexity of accessing an element by index in an array?",
                        "options": [
                            "O(n)",
                            "O(log n)",
                            "O(1)",
                            "O(n log n)",
                        ],
                        "correct_option": 2,
                        "difficulty": "easy",
                    },
                    {
                        "id": 7,
                        "question": "Which of the following is TRUE about arrays?",
                        "options": [
                            "Elements are stored in random memory locations",
                            "Elements are stored in contiguous memory locations",
                            "Arrays can only store integers",
                            "Array index always starts from 1",
                        ],
                        "correct_option": 1,
                        "difficulty": "easy",
                    },
                    {
                        "id": 8,
                        "question": "What is the time complexity of inserting an element at the beginning of an array (shifting required)?",
                        "options": [
                            "O(1)",
                            "O(log n)",
                            "O(n)",
                            "O(n log n)",
                        ],
                        "correct_option": 2,
                        "difficulty": "medium",
                    },
                    {
                        "id": 9,
                        "question": "Which technique is commonly used with arrays to optimize searching for subarrays?",
                        "options": [
                            "Recursion",
                            "Backtracking",
                            "Sliding window",
                            "Dynamic programming only",
                        ],
                        "correct_option": 2,
                        "difficulty": "medium",
                    },
                    {
                        "id": 10,
                        "question": "Which of the following is a valid use-case of two-pointer technique on arrays?",
                        "options": [
                            "Binary search tree traversal",
                            "Finding a pair with given sum in a sorted array",
                            "Depth-first search",
                            "Hash table lookup",
                        ],
                        "correct_option": 1,
                        "difficulty": "medium",
                    },
                ],
                "stacks": [
                    {
                        "id": 11,
                        "question": "Which principle does a stack follow?",
                        "options": [
                            "FIFO (First In First Out)",
                            "LIFO (Last In First Out)",
                            "LILO (Last In Last Out)",
                            "Random access",
                        ],
                        "correct_option": 1,
                        "difficulty": "easy",
                    },
                    {
                        "id": 12,
                        "question": "Which operation removes an element from the top of the stack?",
                        "options": [
                            "Push",
                            "Pop",
                            "Peek",
                            "Insert",
                        ],
                        "correct_option": 1,
                        "difficulty": "easy",
                    },
                    {
                        "id": 13,
                        "question": "Which of the following is NOT an application of stacks?",
                        "options": [
                            "Function call management",
                            "Expression evaluation",
                            "Undo operation in editors",
                            "Breadth-first search in graphs",
                        ],
                        "correct_option": 3,
                        "difficulty": "medium",
                    },
                    {
                        "id": 14,
                        "question": "Infix to postfix conversion commonly uses which data structure?",
                        "options": [
                            "Queue",
                            "Stack",
                            "Array",
                            "Linked List",
                        ],
                        "correct_option": 1,
                        "difficulty": "medium",
                    },
                    {
                        "id": 15,
                        "question": "What is the time complexity of push and pop operations in a stack (array or linked-list based)?",
                        "options": [
                            "O(1) average",
                            "O(log n)",
                            "O(n)",
                            "O(n log n)",
                        ],
                        "correct_option": 0,
                        "difficulty": "easy",
                    },
                ],
                "general": [
                    {
                        "id": 16,
                        "question": "What is the time complexity of binary search on a sorted array?",
                        "options": [
                            "O(n)",
                            "O(log n)",
                            "O(n^2)",
                            "O(1)",
                        ],
                        "correct_option": 1,
                        "difficulty": "easy",
                    },
                    {
                        "id": 17,
                        "question": "Which data structure is best suited for BFS (Breadth-First Search)?",
                        "options": [
                            "Stack",
                            "Queue",
                            "Priority queue",
                            "Set",
                        ],
                        "correct_option": 1,
                        "difficulty": "easy",
                    },
                    {
                        "id": 18,
                        "question": "Which of the following sorting algorithms has average time complexity O(n log n)?",
                        "options": [
                            "Bubble sort",
                            "Selection sort",
                            "Merge sort",
                            "Insertion sort",
                        ],
                        "correct_option": 2,
                        "difficulty": "medium",
                    },
                    {
                        "id": 19,
                        "question": "Which data structure provides average O(1) time complexity for search, insert, and delete?",
                        "options": [
                            "Binary search tree",
                            "Linked list",
                            "Array",
                            "Hash table",
                        ],
                        "correct_option": 3,
                        "difficulty": "medium",
                    },
                    {
                        "id": 20,
                        "question": "Which of the following is TRUE about a singly linked list?",
                        "options": [
                            "Random access of elements is O(1)",
                            "Insertion at head is O(1)",
                            "It uses contiguous memory",
                            "Deletion always takes O(n^2)",
                        ],
                        "correct_option": 1,
                        "difficulty": "easy",
                    },
                ],
            },

            # ================= OS SUBJECT (20 QUESTIONS) =================
            "OS": {
                "deadlocks": [
                    {
                        "id": 21,
                        "question": "Which of the following is NOT a necessary condition for deadlock?",
                        "options": [
                            "Mutual exclusion",
                            "Hold and wait",
                            "No preemption",
                            "Maximum throughput",
                        ],
                        "correct_option": 3,
                        "difficulty": "medium",
                    },
                    {
                        "id": 22,
                        "question": "Circular wait means:",
                        "options": [
                            "Processes wait in a straight queue",
                            "Each process holds a resource and waits for another in a cycle",
                            "Process waits only for I/O",
                            "Only one process is waiting",
                        ],
                        "correct_option": 1,
                        "difficulty": "medium",
                    },
                    {
                        "id": 23,
                        "question": "Deadlock prevention works by:",
                        "options": [
                            "Killing processes randomly",
                            "Denying at least one of the necessary conditions for deadlock",
                            "Ignoring deadlocks",
                            "Restarting the OS periodically",
                        ],
                        "correct_option": 1,
                        "difficulty": "medium",
                    },
                    {
                        "id": 24,
                        "question": "Which of the following strategies is related to deadlock avoidance?",
                        "options": [
                            "Banker’s algorithm",
                            "Round Robin",
                            "LRU page replacement",
                            "Shortest Job First",
                        ],
                        "correct_option": 0,
                        "difficulty": "hard",
                    },
                    {
                        "id": 25,
                        "question": "Deadlock detection involves:",
                        "options": [
                            "Checking resource-allocation graph for cycles",
                            "Killing all processes",
                            "Increasing CPU speed",
                            "Using only FCFS scheduling",
                        ],
                        "correct_option": 0,
                        "difficulty": "medium",
                    },
                ],
                "scheduling": [
                    {
                        "id": 26,
                        "question": "Which scheduling algorithm may lead to starvation without aging?",
                        "options": [
                            "First Come First Serve (FCFS)",
                            "Round Robin",
                            "Priority Scheduling",
                            "Shortest Job Next with aging",
                        ],
                        "correct_option": 2,
                        "difficulty": "medium",
                    },
                    {
                        "id": 27,
                        "question": "Round Robin scheduling is best suited for:",
                        "options": [
                            "Real-time systems with strict deadlines",
                            "Interactive time-sharing systems",
                            "Batch processing only",
                            "Single-user systems",
                        ],
                        "correct_option": 1,
                        "difficulty": "medium",
                    },
                    {
                        "id": 28,
                        "question": "In FCFS scheduling:",
                        "options": [
                            "Shortest job is always executed first",
                            "Jobs are executed in order of arrival",
                            "Priority decides the order",
                            "Jobs are chosen randomly",
                        ],
                        "correct_option": 1,
                        "difficulty": "easy",
                    },
                    {
                        "id": 29,
                        "question": "Which parameter is most critical for Round Robin scheduling?",
                        "options": [
                            "Arrival time",
                            "Time quantum",
                            "Priority",
                            "Number of processes",
                        ],
                        "correct_option": 1,
                        "difficulty": "medium",
                    },
                    {
                        "id": 30,
                        "question": "Shortest Remaining Time First (SRTF) is:",
                        "options": [
                            "Non-preemptive version of SJF",
                            "Preemptive version of SJF",
                            "Same as FCFS",
                            "Same as Round Robin",
                        ],
                        "correct_option": 1,
                        "difficulty": "hard",
                    },
                ],
                "memory": [
                    {
                        "id": 31,
                        "question": "Which of the following is NOT a memory management technique?",
                        "options": [
                            "Paging",
                            "Segmentation",
                            "Demand paging",
                            "Spooling",
                        ],
                        "correct_option": 3,
                        "difficulty": "medium",
                    },
                    {
                        "id": 32,
                        "question": "Internal fragmentation occurs when:",
                        "options": [
                            "Allocated memory may have unused space inside a partition",
                            "Total memory is insufficient",
                            "Processes are swapped out frequently",
                            "Memory is accessed out of bounds",
                        ],
                        "correct_option": 0,
                        "difficulty": "medium",
                    },
                    {
                        "id": 33,
                        "question": "In paging, the logical address is divided into:",
                        "options": [
                            "Frame number and offset",
                            "Page number and offset",
                            "Segment number and page number",
                            "Base and limit",
                        ],
                        "correct_option": 1,
                        "difficulty": "medium",
                    },
                    {
                        "id": 34,
                        "question": "Page replacement algorithms are used to:",
                        "options": [
                            "Decide which page to remove from memory",
                            "Allocate CPU time",
                            "Detect deadlocks",
                            "Increase disk speed",
                        ],
                        "correct_option": 0,
                        "difficulty": "easy",
                    },
                    {
                        "id": 35,
                        "question": "Which page replacement algorithm may suffer from Belady’s anomaly?",
                        "options": [
                            "LRU",
                            "Optimal",
                            "FIFO",
                            "Clock",
                        ],
                        "correct_option": 2,
                        "difficulty": "hard",
                    },
                ],
                "general": [
                    {
                        "id": 36,
                        "question": "Which of the following is NOT an operating system?",
                        "options": [
                            "Windows",
                            "Linux",
                            "Oracle Database",
                            "macOS",
                        ],
                        "correct_option": 2,
                        "difficulty": "easy",
                    },
                    {
                        "id": 37,
                        "question": "Which component of OS manages CPU scheduling?",
                        "options": [
                            "Memory manager",
                            "Process scheduler",
                            "Device driver",
                            "File system",
                        ],
                        "correct_option": 1,
                        "difficulty": "easy",
                    },
                    {
                        "id": 38,
                        "question": "A process in the blocked state is:",
                        "options": [
                            "Using the CPU",
                            "Waiting for some event (like I/O) to occur",
                            "Ready to run in main memory",
                            "Being terminated",
                        ],
                        "correct_option": 1,
                        "difficulty": "easy",
                    },
                    {
                        "id": 39,
                        "question": "Context switch refers to:",
                        "options": [
                            "Switching from user mode to kernel mode",
                            "Saving and restoring process state during scheduling",
                            "Changing file system type",
                            "Flushing cache memory",
                        ],
                        "correct_option": 1,
                        "difficulty": "medium",
                    },
                    {
                        "id": 40,
                        "question": "Which of the following is a valid goal of an operating system?",
                        "options": [
                            "Maximize CPU utilization",
                            "Minimize response time",
                            "Provide user convenience",
                            "All of the above",
                        ],
                        "correct_option": 3,
                        "difficulty": "easy",
                    },
                ],
            },
        }

    def generate_quiz(
        self,
        user_id: int,
        subject: str,
        topic: str | None,
        num_questions: int = 3,
    ) -> Dict:
        """
        Returns a small quiz for the given subject/topic and adaptive difficulty.
        """
        # Decide difficulty using engine
        if self.db is not None:
            difficulty = get_next_difficulty(self.db, user_id, subject, topic)
        else:
            difficulty = "easy"

        subject_bank = self.question_bank.get(subject, {})
        topic_key = topic if topic in subject_bank else "general"
        all_questions = subject_bank.get(topic_key, [])

        # Filter questions by difficulty level
        filtered = self._filter_by_difficulty(all_questions, difficulty)

        # Limit to num_questions
        questions = filtered[:num_questions] if filtered else all_questions[:num_questions]

        return {
            "subject": subject,
            "topic": topic or topic_key,
            "difficulty": difficulty,
            "questions": questions,
        }

    def _filter_by_difficulty(self, questions: List[Dict], difficulty: str) -> List[Dict]:
        """
        Simple rule:
          - easy   -> only 'easy'
          - medium -> 'easy' + 'medium'
          - hard   -> 'medium' + 'hard'
        """
        if not questions:
            return []

        if difficulty == "easy":
            return [q for q in questions if q.get("difficulty") == "easy"]
        elif difficulty == "medium":
            return [q for q in questions if q.get("difficulty") in ("easy", "medium")]
        else:  # hard
            return [q for q in questions if q.get("difficulty") in ("medium", "hard")]

    # NEW: find question by matching its text (used for EXPLAIN_QUESTION)
    def find_question_by_text(self, text: str) -> Dict | None:
        """
        Try to find a question in the bank that matches the given text.
        Returns: {
          "subject": ...,
          "topic": ...,
          "question": q_dict
        } or None
        """
        target = text.lower().strip()
        best_match = None
        best_len = 0

        for subject, topics in self.question_bank.items():
            for topic, questions in topics.items():
                for q in questions:
                    qtext = q["question"].lower()
                    # Simple matching heuristic
                    if target == qtext or qtext in target or target in qtext:
                        if len(qtext) > best_len:
                            best_len = len(qtext)
                            best_match = {
                                "subject": subject,
                                "topic": topic,
                                "question": q,
                            }
        return best_match