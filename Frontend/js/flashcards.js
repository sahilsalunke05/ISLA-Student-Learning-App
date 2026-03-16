// frontend/js/flashcards.js

const root = document.getElementById("flashcards-root");
const USER_ID = 1;

async function loadFlashcards() {
  root.innerHTML = "<p>Loading flashcards...</p>";

  try {
    const res = await fetch(
      `http://127.0.0.1:8000/api/flashcards/due/${USER_ID}`
    );
    const cards = await res.json();

    if (!Array.isArray(cards) || cards.length === 0) {
      root.innerHTML =
        "<p>No flashcards due right now. Finish a quiz with some mistakes to generate more.</p>";
      return;
    }

    renderFlashcards(cards);
  } catch (err) {
    console.error(err);
    root.innerHTML = "<p>Error loading flashcards from backend.</p>";
  }
}

function renderFlashcards(cards) {
  root.innerHTML = "";

  cards.forEach((c) => {
    const cardDiv = document.createElement("div");
    cardDiv.classList.add("summary-card");

    const q = document.createElement("p");
    q.innerHTML = `<b>Q:</b> ${c.question}`;
    cardDiv.appendChild(q);

    const a = document.createElement("p");
    a.innerHTML = `<b>Answer:</b> <span class="hidden-answer">[click 'Show Answer']</span>`;
    const trueAnswerSpan = document.createElement("span");
    trueAnswerSpan.textContent = ` ${c.answer}`;
    trueAnswerSpan.style.display = "none";
    a.appendChild(trueAnswerSpan);
    cardDiv.appendChild(a);

    const meta = document.createElement("p");
    meta.style.fontSize = "12px";
    meta.textContent = `Subject: ${c.subject} | Topic: ${c.topic} | Seen: ${
      c.times_seen || 0
    } times`;
    cardDiv.appendChild(meta);

    const btnRow = document.createElement("div");
    btnRow.style.marginTop = "8px";

    const showBtn = document.createElement("button");
    showBtn.classList.add("btn", "btn-secondary");
    showBtn.textContent = "Show Answer";
    showBtn.addEventListener("click", () => {
      trueAnswerSpan.style.display = "inline";
      showBtn.disabled = true;
    });

    const remBtn = document.createElement("button");
    remBtn.classList.add("btn", "btn-primary");
    remBtn.style.marginLeft = "6px";
    remBtn.textContent = "I remembered";
    remBtn.addEventListener("click", () => {
      gradeCard(c.id, true, cardDiv);
    });

    const forgotBtn = document.createElement("button");
    forgotBtn.classList.add("btn");
    forgotBtn.style.marginLeft = "6px";
    forgotBtn.textContent = "I forgot";
    forgotBtn.addEventListener("click", () => {
      gradeCard(c.id, false, cardDiv);
    });

    btnRow.appendChild(showBtn);
    btnRow.appendChild(remBtn);
    btnRow.appendChild(forgotBtn);

    cardDiv.appendChild(btnRow);

    root.appendChild(cardDiv);
  });
}

async function gradeCard(cardId, remembered, cardElement) {
  try {
    await fetch(
      `http://127.0.0.1:8000/api/flashcards/grade?card_id=${cardId}&remembered=${remembered}`,
      { method: "POST" }
    );
    cardElement.style.opacity = "0.5";
    cardElement.style.pointerEvents = "none";
  } catch (err) {
    console.error(err);
    alert("Error grading flashcard.");
  }
}

loadFlashcards();
