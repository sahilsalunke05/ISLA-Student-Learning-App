// frontend/js/quiz.js

// === Subject & Topic dynamic dropdowns ===

const TOPICS_BY_SUBJECT = {
  DSA: [
    { value: "recursion", label: "Recursion" },
    { value: "arrays", label: "Arrays" },
    { value: "stacks", label: "Stacks" },
    { value: "general", label: "General DSA" },
  ],
  OS: [
    { value: "deadlocks", label: "Deadlocks" },
    { value: "scheduling", label: "CPU Scheduling" },
    { value: "memory", label: "Memory Management" },
    { value: "general", label: "General OS" },
  ],
};

const BACKEND_BASE_URL = "http://127.0.0.1:8000";

document.addEventListener("DOMContentLoaded", () => {
  const subjectSelect = document.getElementById("subject-select");
  const topicSelect = document.getElementById("topic-select");
  const modeRadios = document.querySelectorAll("input[name='mode']");
  const examSettings = document.getElementById("exam-settings");
  const startBtn = document.getElementById("start-quiz-btn");
  const quizSetup = document.getElementById("quiz-setup");
  const quizContainer = document.getElementById("quiz-container");
  const questionsWrapper = document.getElementById("questions-wrapper");
  const quizTitle = document.getElementById("quiz-title");
  const quizMeta = document.getElementById("quiz-meta");
  const timerDisplay = document.getElementById("timer-display");
  const quizForm = document.getElementById("quiz-form");
  const quizMessage = document.getElementById("quiz-message");
  const cancelBtn = document.getElementById("cancel-quiz-btn");

  if (!subjectSelect || !topicSelect) return;

  // Fill subject dropdown
  subjectSelect.innerHTML = `
    <option value="DSA">DSA</option>
    <option value="OS">OS</option>
  `;

  function populateTopics(subject) {
    const topics = TOPICS_BY_SUBJECT[subject] || [];
    topicSelect.innerHTML = "";
    topics.forEach((t) => {
      const opt = document.createElement("option");
      opt.value = t.value;
      opt.textContent = t.label;
      topicSelect.appendChild(opt);
    });
  }

  // Initial load
  populateTopics(subjectSelect.value);

  // When subject changes → update topics
  subjectSelect.addEventListener("change", () => {
    populateTopics(subjectSelect.value);
  });

  // Toggle exam settings visibility
  modeRadios.forEach((radio) => {
    radio.addEventListener("change", () => {
      if (radio.checked && radio.value === "exam") {
        examSettings.classList.remove("hidden");
      } else if (radio.checked && radio.value === "practice") {
        examSettings.classList.add("hidden");
      }
    });
  });

  let examTimerId = null;
  let remainingSeconds = 0;

  function startTimer(minutes) {
    clearInterval(examTimerId);
    remainingSeconds = minutes * 60;

    function updateTimer() {
      const m = Math.floor(remainingSeconds / 60);
      const s = remainingSeconds % 60;
      timerDisplay.textContent = `Time left: ${m}m ${s}s`;
      remainingSeconds -= 1;
      if (remainingSeconds < 0) {
        clearInterval(examTimerId);
        quizMessage.textContent = "Time is up! Submitting your answers...";
        quizForm.requestSubmit();
      }
    }

    updateTimer();
    examTimerId = setInterval(updateTimer, 1000);
  }

  function stopTimer() {
    clearInterval(examTimerId);
    timerDisplay.textContent = "";
  }

  // ------ Start Quiz Button ------
  startBtn.addEventListener("click", async () => {
    quizMessage.textContent = "";

    const subject = subjectSelect.value;
    const topic = topicSelect.value;
    const numQuestions = parseInt(
      document.getElementById("num-questions").value,
      10
    );
    const mode = document.querySelector("input[name='mode']:checked").value;
    const examMinutes = parseInt(
      document.getElementById("exam-duration").value,
      10
    );

    // Build a natural language message for /api/chat
    let msg = `start quiz on ${topic}`;
    if (subject === "OS") {
      msg += " in os";
    }

    try {
      const res = await fetch(`${BACKEND_BASE_URL}/api/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_id: 1,
          message: msg, // for models expecting "message"
          text: msg,    // for models expecting "text"  (prevents 422)
        }),
      });

      if (!res.ok) {
        const errText = await res.text().catch(() => "");
        console.error(
          "Error starting quiz. Status:",
          res.status,
          res.statusText,
          "Body:",
          errText
        );
        quizMessage.textContent =
          "Error starting quiz from backend (status " + res.status + "). Check console for details.";
        return;
      }

      const data = await res.json();
      console.log("Start quiz response:", data);

      const quiz = data.quiz;
      if (!quiz || !quiz.questions || !quiz.questions.length) {
        quizMessage.textContent =
          data.reply || "No questions returned from backend.";
        return;
      }

      const questions = quiz.questions;

      // Show quiz UI
      quizSetup.classList.add("hidden");
      quizContainer.classList.remove("hidden");

      quizTitle.textContent = `Quiz on ${quiz.topic} (${quiz.subject})`;
      quizMeta.textContent = `Difficulty: ${quiz.difficulty} • Mode: ${mode.toUpperCase()}`;
      questionsWrapper.innerHTML = "";

      // Build question blocks
      questions.forEach((q, index) => {
        const qDiv = document.createElement("div");
        qDiv.className = "quiz-question-block";
        const qNumber = index + 1;

        let html = `<p><b>Q${qNumber}.</b> ${q.question}</p>`;
        html += `<div class="quiz-options">`;
        q.options.forEach((opt, optIndex) => {
          const inputName = `q_${index}`;
          const inputId = `q_${index}_opt_${optIndex}`;
          html += `
            <label for="${inputId}">
              <input type="radio" name="${inputName}" id="${inputId}" value="${optIndex}" />
              ${optIndex + 1}. ${opt}
            </label><br/>
          `;
        });
        html += `</div>`;

        qDiv.innerHTML = html;
        questionsWrapper.appendChild(qDiv);
      });

      // Start timer if exam mode
      if (mode === "exam") {
        startTimer(examMinutes);
      } else {
        stopTimer();
      }
    } catch (err) {
      console.error("Network or fetch error starting quiz:", err);
      quizMessage.textContent =
        "Error starting quiz. Is the backend running or reachable?";
    }
  });

  // ------ Submit Quiz Form ------
  quizForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    stopTimer();

    const answers = [];
    const questionBlocks =
      questionsWrapper.querySelectorAll(".quiz-question-block");
    questionBlocks.forEach((block, index) => {
      const picked = block.querySelector(`input[name='q_${index}']:checked`);
      if (picked) {
        answers.push(parseInt(picked.value, 10) + 1); // 1-based
      } else {
        answers.push(0); // unanswered
      }
    });

    if (answers.includes(0)) {
      if (!confirm("Some questions are unanswered. Submit anyway?")) {
        return;
      }
    }

    try {
      const answerText = "answers " + answers.join(" ");
      const res = await fetch(`${BACKEND_BASE_URL}/api/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_id: 1,
          message: answerText, // for "message"
          text: answerText,    // for "text"
        }),
      });

      if (!res.ok) {
        const errText = await res.text().catch(() => "");
        console.error(
          "Error submitting quiz. Status:",
          res.status,
          res.statusText,
          "Body:",
          errText
        );
        quizMessage.textContent =
          "Error submitting quiz to backend (status " + res.status + "). Check console for details.";
        return;
      }

      const data = await res.json();
      console.log("Submit quiz response:", data);

      if (data.result) {
        localStorage.setItem("last_quiz_result", JSON.stringify(data.result));
        window.location.href = "results.html";
      } else {
        quizMessage.textContent = data.reply || "Quiz evaluated.";
      }
    } catch (err) {
      console.error("Network or fetch error submitting quiz:", err);
      quizMessage.textContent =
        "Error submitting quiz. Is the backend running or reachable?";
    }
  });

  // ------ Cancel Quiz ------
  cancelBtn.addEventListener("click", () => {
    stopTimer();
    quizContainer.classList.add("hidden");
    quizSetup.classList.remove("hidden");
    questionsWrapper.innerHTML = "";
    quizMessage.textContent = "Quiz cancelled.";
  });
});
