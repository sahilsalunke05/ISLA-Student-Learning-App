// frontend/js/dashboard.js (BACKEND + CHARTS)

const dashRoot = document.getElementById("dashboard-root");
const USER_ID = 1;

async function loadDashboard() {
  try {
    const [dashRes, histRes] = await Promise.all([
      fetch(`http://127.0.0.1:8000/api/dashboard/${USER_ID}`),
      fetch(`http://127.0.0.1:8000/api/history/${USER_ID}`),
    ]);

    const data = await dashRes.json();
    const history = await histRes.json();

    if (!data || data.total_quizzes === 0) {
      dashRoot.innerHTML =
        "<p>No quiz data yet. Start a quiz from the <a href='quiz.html'>Quiz</a> page.</p>";
      return;
    }

    const summary = document.createElement("div");
    summary.classList.add("summary-card");

    summary.innerHTML = `
      <h3>Overall Summary</h3>
      <p><b>Total quizzes taken:</b> ${data.total_quizzes}</p>
      <p><b>Average score:</b> ${data.avg_score.toFixed(1)}%</p>
      <p><b>Preferred difficulty:</b> ${data.preferred_difficulty}</p>
      <p><b>Weak topics:</b> ${
        data.weak_topics && data.weak_topics.length
          ? data.weak_topics.join(", ")
          : "None"
      }</p>
    `;
    dashRoot.appendChild(summary);

    // Difficulty distribution
    const diff = data.difficulty_distribution || {};
    const diffCard = document.createElement("div");
    diffCard.classList.add("summary-card");
    diffCard.innerHTML = `
      <h3>Difficulty Distribution (Summary)</h3>
      <p>Easy: ${diff.easy || 0}</p>
      <p>Medium: ${diff.medium || 0}</p>
      <p>Hard: ${diff.hard || 0}</p>
    `;
    dashRoot.appendChild(diffCard);

    // Draw charts
    drawScoreChart(history);
    drawDifficultyChart(diff);
  } catch (err) {
    console.error(err);
    dashRoot.innerHTML = "<p>Error loading dashboard from backend.</p>";
  }
}

function drawScoreChart(history) {
  if (!Array.isArray(history) || history.length === 0) return;

  const ctx = document.getElementById("scoreChart").getContext("2d");

  const labels = history
    .slice()
    .reverse()
    .map((h) => new Date(h.created_at).toLocaleString());
  const scores = history
    .slice()
    .reverse()
    .map((h) => h.score);

  new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "Score (%)",
          data: scores,
        },
      ],
    },
    options: {
      responsive: true,
      scales: {
        y: {
          min: 0,
          max: 100,
        },
      },
    },
  });
}

function drawDifficultyChart(diff) {
  const ctx = document.getElementById("difficultyChart").getContext("2d");
  const labels = ["easy", "medium", "hard"];
  const values = labels.map((k) => diff[k] || 0);

  new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [
        {
          label: "Number of quizzes",
          data: values,
        },
      ],
    },
    options: {
      responsive: true,
    },
  });
}

loadDashboard();
