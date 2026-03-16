// frontend/js/admin.js

const metricsDiv = document.getElementById("admin-metrics");
const logsDiv = document.getElementById("admin-logs");

async function loadMetrics() {
  try {
    const res = await fetch("http://127.0.0.1:8000/api/admin/metrics");
    const data = await res.json();

    metricsDiv.innerHTML = `
      <h3>System Metrics</h3>
      <p><b>Total users with profiles:</b> ${data.total_users}</p>
      <p><b>Total quizzes taken:</b> ${data.total_quizzes}</p>
      <p><b>Total flashcards:</b> ${data.total_flashcards}</p>
      <p><b>Total agent log entries:</b> ${data.total_logs}</p>
    `;
  } catch (err) {
    console.error(err);
    metricsDiv.innerHTML = "<p>Error loading metrics.</p>";
  }
}

async function loadLogs() {
  try {
    const res = await fetch("http://127.0.0.1:8000/api/admin/logs?limit=50");
    const logs = await res.json();

    if (!Array.isArray(logs) || logs.length === 0) {
      logsDiv.innerHTML = "<p>No logs available.</p>";
      return;
    }

    const table = document.createElement("table");
    table.classList.add("table");

    const thead = document.createElement("thead");
    thead.innerHTML = `
      <tr>
        <th>Time</th>
        <th>User</th>
        <th>Agent</th>
        <th>Event</th>
        <th>Message</th>
      </tr>
    `;
    table.appendChild(thead);

    const tbody = document.createElement("tbody");

    logs.forEach((l) => {
      const tr = document.createElement("tr");
      const date = new Date(l.timestamp);
      tr.innerHTML = `
        <td>${date.toLocaleString()}</td>
        <td>${l.user_id ?? "-"}</td>
        <td>${l.agent_name}</td>
        <td>${l.event_type}</td>
        <td>${l.message}</td>
      `;
      tbody.appendChild(tr);
    });

    table.appendChild(tbody);
    logsDiv.appendChild(table);
  } catch (err) {
    console.error(err);
    logsDiv.innerHTML = "<p>Error loading logs.</p>";
  }
}

loadMetrics();
loadLogs();
