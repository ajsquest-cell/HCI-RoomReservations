/* App-bar accessibility menu. Controls are placeholders; each has a
   data-a11y hook so behavior can be wired up later. */
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
})();
