# backend/agents/evaluation_agent.py

from typing import List, Dict


class EvaluationAgent:
    def __init__(self):
        # Map question id -> explanation text
        self.explanations: Dict[int, str] = {
            # -------- DSA: recursion (1–5) --------
            1: "Recursion is when a function calls itself on a smaller subproblem until a base case is reached.",
            2: "The base case stops further recursive calls. Without it, the function keeps calling itself and causes infinite recursion / stack overflow.",
            3: "Function calls are managed using the call stack. Every recursive call pushes a new frame onto the stack.",
            4: "Without a valid base case or progress towards it, recursion never stops and leads to stack overflow.",
            5: "Problems like factorial, tree traversal, and divide-and-conquer are well-suited to recursion because they naturally break into smaller similar subproblems.",

            # -------- DSA: arrays (6–10) --------
            6: "Array indexing uses direct address calculation, so accessing arr[i] is O(1) time.",
            7: "Arrays store elements in contiguous memory locations. This allows constant-time indexing but fixed size.",
            8: "Inserting at the beginning of an array requires shifting all existing elements, which is O(n).",
            9: "The sliding window technique is used to efficiently find subarrays or subranges that satisfy a condition.",
            10: "Two-pointer technique on sorted arrays is commonly used to find pairs with a given sum in linear time.",

            # -------- DSA: stacks (11–15) --------
            11: "A stack follows LIFO (Last In First Out): the last pushed element is the first one popped.",
            12: "Pop removes the top element from a stack; push adds an element to the top.",
            13: "BFS uses a queue, not a stack. Stacks are used in function calls, DFS, expression evaluation, etc.",
            14: "Infix to postfix conversion uses a stack to temporarily hold operators and manage precedence.",
            15: "Both push and pop operations are O(1) on average for stack implementations.",

            # -------- DSA: general (16–20) --------
            16: "Binary search repeatedly halves the search space on a sorted array, giving O(log n) time.",
            17: "BFS explores neighbors level by level and uses a queue to store the frontier.",
            18: "Merge sort and other divide-and-conquer sorts generally run in O(n log n) time on average.",
            19: "Hash tables provide average O(1) time for insert, search, and delete using hashing.",
            20: "Inserting at the head of a singly linked list is O(1) because it only changes a couple of pointers.",

            # -------- OS: deadlocks (21–25) --------
            21: "The four necessary conditions are: mutual exclusion, hold and wait, no preemption, and circular wait. 'Maximum throughput' is not one of them.",
            22: "Circular wait means each process in a set holds a resource and waits for another resource held by the next process in a cycle.",
            23: "Deadlock prevention works by denying at least one of the four necessary conditions so that deadlock can never occur.",
            24: "Banker's algorithm is a classic deadlock avoidance algorithm that checks for safe states before resource allocation.",
            25: "Deadlock detection typically uses a resource-allocation graph or similar structure to check for cycles.",

            # -------- OS: scheduling (26–30) --------
            26: "Priority scheduling without aging can cause starvation because low-priority processes may never get CPU time.",
            27: "Round Robin scheduling is ideal for interactive time-sharing systems because every process gets a time slice.",
            28: "FCFS runs processes strictly in order of arrival; it is simple but can cause the convoy effect.",
            29: "The time quantum size in Round Robin heavily affects performance and context-switch overhead.",
            30: "Shortest Remaining Time First (SRTF) is the preemptive version of Shortest Job First.",

            # -------- OS: memory (31–35) --------
            31: "Spooling is a technique for managing I/O operations, not a primary memory management scheme like paging or segmentation.",
            32: "Internal fragmentation occurs when a fixed-size allocated block has unused space inside it.",
            33: "In paging, a logical address is split into page number and offset to index into the page table.",
            34: "Page replacement algorithms decide which page to evict from memory when a new page must be loaded.",
            35: "FIFO page replacement can suffer from Belady’s anomaly, where increasing frames unexpectedly increases page faults.",

            # -------- OS: general (36–40) --------
            36: "Windows, Linux, and macOS are operating systems. Oracle Database is a DBMS, not an OS.",
            37: "The process scheduler (CPU scheduler) is responsible for deciding which process gets the CPU next.",
            38: "A blocked process is waiting for some event like I/O completion or a resource becoming available.",
            39: "A context switch saves the state of the current process and loads the state of the next process to run.",
            40: "Operating systems aim to maximize utilization, minimize response time, and provide user convenience—so all of the above is correct.",
        }

    def evaluate_quiz(self, questions: List[Dict], user_answers: List[int]) -> Dict:
        total = len(questions)
        score = 0
        details = []

        for q, ua in zip(questions, user_answers):
            correct = q.get("correct_option", 0)
            is_correct = (ua == correct)
            if is_correct:
                score += 1

            qid = q.get("id")
            expl = self.explanations.get(
                qid,
                "This question tests the core concept shown in the correct option."
            )

            details.append(
                {
                    "question": q["question"],
                    "user_answer": ua,
                    "correct_answer": correct,
                    "is_correct": is_correct,
                    "explanation": expl,
                }
            )

        percentage = (score / total * 100.0) if total > 0 else 0.0

        return {
            "score": score,
            "total": total,
            "percentage": percentage,
            "details": details,
        }

    # NEW: expose explanation by question id (used for EXPLAIN_QUESTION)
    def get_explanation_for_question_id(self, qid: int) -> str:
        return self.explanations.get(
            qid,
            "I don't have a detailed explanation stored for this question yet."
        )