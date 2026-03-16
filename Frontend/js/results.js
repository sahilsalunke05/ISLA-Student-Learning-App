// frontend/js/results.js

document.addEventListener("DOMContentLoaded", () => {
  const root = document.getElementById("results-root");
  if (!root) {
    console.error("results-root element not found in DOM");
    return;
  }

  try {
    const raw = localStorage.getItem("isla_last_result");
    console.log("Loaded isla_last_result from localStorage:", raw);

    if (!raw) {
      root.innerHTML =
        "<p>No recent quiz result found. Go to <a href='quiz.html'>Quiz</a> to start one.</p>";
      return;
    }

    const payload = JSON.parse(raw);
    console.log("Parsed payload:", payload);

    const {
      result,
      quiz,
      timestamp,
      mode,
      exam_info,
      time_taken_seconds,
      time_limit_seconds,
    } = payload;

    if (!result || !result.details) {
      root.innerHTML =
        "<p>Result data is incomplete. Please take a new quiz.</p>";
      return;
    }

    const date = timestamp ? new Date(timestamp) : new Date();

    // ---------- Summary card ----------
    const summaryDiv = document.createElement("div");
    summaryDiv.classList.add("summary-card");

    // Safe defaults
    const subj = quiz?.subject || "Unknown";
    const topic = quiz?.topic || "Unknown";
    const diff = quiz?.difficulty || "easy";

    const score = result.score ?? 0;
    const total = result.total ?? result.details.length;
    const pct =
      typeof result.percentage === "number"
        ? result.percentage
        : total > 0
        ? (score / total) * 100
        : 0;

    summaryDiv.innerHTML = `
      <p><b>Subject:</b> ${subj} &nbsp; | &nbsp; <b>Topic:</b> ${topic} &nbsp; | &nbsp; <b>Difficulty:</b> ${diff}</p>
      <p><b>Mode:</b> ${(mode || "practice").toUpperCase()}</p>
      <p><b>Raw Score:</b> ${score}/${total} (${pct.toFixed(1)}%)</p>
      <p><b>Date:</b> ${date.toLocaleString()}</p>
    `;

    root.appendChild(summaryDiv);

    // ---------- Exam info card (if any) ----------
    if (mode === "exam" && exam_info) {
      const examDiv = document.createElement("div");
      examDiv.classList.add("summary-card");

      let timeLines = "";
      if (time_limit_seconds != null) {
        const mins = Math.floor(time_limit_seconds / 60);
        timeLines += `<p><b>Time limit:</b> ${mins} min</p>`;
      }
      if (time_taken_seconds != null) {
        const usedMin = Math.floor(time_taken_seconds / 60);
        const usedSec = time_taken_seconds % 60;
        timeLines += `<p><b>Time used:</b> ${usedMin}m ${usedSec}s</p>`;
      }

      examDiv.innerHTML = `
        <h3>Exam Evaluation (with Negative Marking)</h3>
        ${timeLines}
        <p><b>Correct:</b> ${exam_info.correct} &nbsp; | &nbsp; <b>Wrong:</b> ${exam_info.wrong}</p>
        <p><b>Negative marking:</b> -${exam_info.negative_per_wrong} per wrong answer</p>
        <p><b>Exam score:</b> ${exam_info.raw_exam_score.toFixed(
          2
        )} out of ${total}</p>
        <p><b>Exam percentage:</b> ${exam_info.exam_percentage.toFixed(1)}%</p>
      `;

      root.appendChild(examDiv);
    }

    // ---------- Question-wise table ----------
    const table = document.createElement("table");
    table.classList.add("table");

    const thead = document.createElement("thead");
    thead.innerHTML = `
      <tr>
        <th>#</th>
        <th>Question</th>
        <th>Your Answer</th>
        <th>Correct Answer</th>
        <th>Result</th>
        <th>Explanation</th>
      </tr>
    `;
    table.appendChild(thead);

    const tbody = document.createElement("tbody");

    result.details.forEach((d, idx) => {
      const tr = document.createElement("tr");

      const statusBadge = d.is_correct
        ? `<span class="badge badge-success">Correct</span>`
        : `<span class="badge badge-danger">Wrong</span>`;

      const userOpt =
        typeof d.user_answer === "number" ? d.user_answer + 1 : "-";
      const correctOpt =
        typeof d.correct_answer === "number" ? d.correct_answer + 1 : "-";

      tr.innerHTML = `
        <td>${idx + 1}</td>
        <td>${d.question}</td>
        <td>Option ${userOpt}</td>
        <td>Option ${correctOpt}</td>
        <td>${statusBadge}</td>
        <td>${d.explanation || ""}</td>
      `;

      tbody.appendChild(tr);
    });

    table.appendChild(tbody);
    root.appendChild(table);
  } catch (err) {
    console.error("Error in results.js:", err);
    root.innerHTML = `<p>Something went wrong while loading results. Check console for details.</p>`;
  }
});
