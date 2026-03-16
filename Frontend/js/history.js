// frontend/js/history.js (BACKEND VERSION)

const historyRoot = document.getElementById("history-root");
const USER_ID = 1;

async function loadHistory() {
  try {
    const res = await fetch(`http://127.0.0.1:8000/api/history/${USER_ID}`);
    const history = await res.json();

    if (!Array.isArray(history) || history.length === 0) {
      historyRoot.innerHTML =
        "<p>No quiz history yet. Take a quiz from the <a href='quiz.html'>Quiz</a> page.</p>";
      return;
    }

    const table = document.createElement("table");
    table.classList.add("table");

    const thead = document.createElement("thead");
    thead.innerHTML = `
      <tr>
        <th>#</th>
        <th>Date</th>
        <th>Subject</th>
        <th>Topic</th>
        <th>Difficulty</th>
        <th>Score</th>
      </tr>
    `;
    table.appendChild(thead);

    const tbody = document.createElement("tbody");

    history.forEach((item, idx) => {
      const date = new Date(item.created_at);

      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${idx + 1}</td>
        <td>${date.toLocaleString()}</td>
        <td>${item.subject}</td>
        <td>${item.topic}</td>
        <td>${item.difficulty}</td>
        <td>${item.score.toFixed(1)}%</td>
      `;
      tbody.appendChild(tr);
    });

    table.appendChild(tbody);
    historyRoot.appendChild(table);
  } catch (err) {
    console.error(err);
    historyRoot.innerHTML = "<p>Error loading history from backend.</p>";
  }
}

loadHistory();
