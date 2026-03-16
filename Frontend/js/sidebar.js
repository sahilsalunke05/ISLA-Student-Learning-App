// frontend/js/sidebar.js

async function loadSidebar(activePage) {
  try {
    const res = await fetch("components/sidebar.html");
    const html = await res.text();

    const container = document.getElementById("sidebar-container");
    if (!container) return;

    container.innerHTML = html;

    // Highlight active link
    document.querySelectorAll(".sidebar a").forEach((link) => {
      if (link.dataset.page === activePage) {
        link.classList.add("active");
      }
    });
  } catch (err) {
    console.error("Failed to load sidebar:", err);
  }
}
