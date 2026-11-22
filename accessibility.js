/* App-bar accessibility menu. Dark mode persists via localStorage and
   applies to every page (data-theme on <html>). High contrast and text
   size remain placeholders. */
(function () {
  const root = document.getElementById("a11y");
  if (!root) return;
  const btn = document.getElementById("a11y-btn");
  const menu = document.getElementById("a11y-menu");

  function close() {
    menu.hidden = true;
    btn.setAttribute("aria-expanded", "false");
    root.classList.remove("is-open");
  }

  btn.addEventListener("click", (e) => {
    e.stopPropagation();
    const open = menu.hidden;
    menu.hidden = !open;
    btn.setAttribute("aria-expanded", String(open));
    root.classList.toggle("is-open", open);
  });
  menu.addEventListener("click", (e) => e.stopPropagation());
  document.addEventListener("click", close);

  // Dark mode toggle (persisted).
  const darkBtn = root.querySelector('[data-a11y="dark"]');
  function applyDark(on) {
    document.documentElement.dataset.theme = on ? "dark" : "";
    if (darkBtn) darkBtn.textContent = on ? "On" : "Off";
    try { localStorage.setItem("theme", on ? "dark" : "light"); } catch (_) { }
  }
  if (darkBtn) {
    darkBtn.disabled = false;
    applyDark(document.documentElement.dataset.theme === "dark");
    darkBtn.addEventListener("click", () => {
      applyDark(document.documentElement.dataset.theme !== "dark");
    });
  }
})();
