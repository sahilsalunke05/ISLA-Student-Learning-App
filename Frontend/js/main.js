// frontend/js/main.js

const chatBox = document.getElementById("chat-box");
const chatForm = document.getElementById("chat-form");
const userInput = document.getElementById("user-input");

function addMessage(text, sender = "bot") {
  const msg = document.createElement("div");
  msg.classList.add("message", sender);
  msg.textContent = text;
  chatBox.appendChild(msg);
  chatBox.scrollTop = chatBox.scrollHeight;
}

chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = userInput.value.trim();
  if (!text) return;

  // Show user message
  addMessage(text, "user");
  userInput.value = "";

  try {
    const url = `http://127.0.0.1:8000/api/chat?user_id=1&text=${encodeURIComponent(
      text
    )}`;

    const res = await fetch(url, {
      method: "POST",
    });

    const data = await res.json();

    if (data.reply) {
      addMessage(data.reply, "bot");
    } else {
      addMessage("I received your message but something went wrong.", "bot");
    }
  } catch (err) {
    console.error(err);
    addMessage("Error contacting server. Is backend running?", "bot");
  }
});
