/* ==============================================================
 * dashboard-filter.js
 *
 * Reservation filter for the dashboard, mirroring the Python
 * version's render_filter() (reservations_ui.py):
 *   - three multi-selects: User / Room / Building
 *   - options are the sorted distinct values across all reservations
 *   - semantics: AND across fields, OR within a field
 *
 * Self-contained module. Loaded ONLY by index.html (never the
 * search page), so it cannot affect the shared script.js. It does
 * reuse two globals that script.js defines first: el() and
 * API_BASE — index.html loads script.js before this file.
 * ============================================================== */

/* The three filterable fields, in display order, with their labels. */
const FILTER_FIELDS = [
  { key: "reserved_by", label: "User" },
  { key: "room_name", label: "Room" },
  { key: "building", label: "Building" },
];

const filterState = {
  all: [],                                      // every reservation (/all-reservations)
  params: { reserved_by: [], room_name: [], building: [] }, // active selections
};

/* -------------------------------------------------------------- */
/* Data + filtering                                               */
/* -------------------------------------------------------------- */
async function loadFilter() {
  try {
    const resp = await fetch(API_BASE + "/all-reservations");
    filterState.all = resp.ok ? await resp.json() : [];
  } catch (_) {
    filterState.all = [];
  }

  const clearBtn = document.getElementById("filter-clear");
  if (clearBtn) clearBtn.onclick = clearFilter;

  buildFilterControls();
  applyFilter();
}

/* Distinct, sorted values for one field across all reservations. */
function distinctValues(key) {
  return [...new Set(filterState.all.map((r) => r[key]))].sort((a, b) =>
    String(a).localeCompare(String(b))
  );
}

/* AND across fields, OR within a field (matches the Python && version). */
function filterReservations() {
  return filterState.all.filter((r) =>
    FILTER_FIELDS.every(({ key }) => {
      const selected = filterState.params[key];
      return selected.length === 0 || selected.includes(r[key]);
    })
  );
}

function filtersActive() {
  return FILTER_FIELDS.some(({ key }) => filterState.params[key].length > 0);
}

function applyFilter() {
  renderFilterResults(filterReservations());
  const clearBtn = document.getElementById("filter-clear");
  if (clearBtn) clearBtn.disabled = !filtersActive();
}

function clearFilter() {
  for (const { key } of FILTER_FIELDS) filterState.params[key] = [];
  buildFilterControls();
  applyFilter();
}

function buildFilterControls() {
  for (const { key } of FILTER_FIELDS) {
    const host = document.getElementById("filter-" + key);
    if (!host) continue;
    buildMultiSelect(host, distinctValues(key), filterState.params[key], (selected) => {
      filterState.params[key] = selected;
      applyFilter();
    });
  }
}

/* -------------------------------------------------------------- */
/* Results list (stand-in for the calendar component)             */
/* -------------------------------------------------------------- */
function renderFilterResults(reservations) {
  const host = document.getElementById("filter-results");
  if (!host) return;
  host.replaceChildren();

  const total = filterState.all.length;
  host.appendChild(el(
    "div",
    filtersActive()
      ? `Showing ${reservations.length} of ${total} reservation(s).`
      : `Showing all ${total} reservation(s).`,
    "muted filter-results__count"
  ));

  if (reservations.length === 0) {
    host.appendChild(el("div", "No reservations match the current filter.", "muted"));
    return;
  }

  const sorted = [...reservations].sort(
    (a, b) => a.date.localeCompare(b.date) || a.slot.localeCompare(b.slot)
  );
  for (const r of sorted) {
    const row = el("div", undefined, "filter-row");
    row.appendChild(el("span", r.date, "filter-row__date"));
    row.appendChild(el("span", r.slot, "filter-row__slot"));
    row.appendChild(el("span", `${r.room_name} · ${r.building}`, "filter-row__room"));
    row.appendChild(el("span", undefined, "slot-row__spacer"));
    row.appendChild(el("span", r.reserved_by === "you" ? "You" : r.reserved_by, "filter-row__who"));
    host.appendChild(row);
  }
}

/* -------------------------------------------------------------- */
/* Multi-select component                                         */
/* A button showing the current selection + a checkbox popover.   */
/* -------------------------------------------------------------- */
function buildMultiSelect(container, options, selected, onChange) {
  container.replaceChildren();
  container.classList.remove("is-open");

  const btn = el("button", undefined, "ms-btn");
  btn.type = "button";
  const value = el("span", undefined, "ms-value");
  const caret = el("span", "▾", "ms-caret");
  btn.append(value, caret);

  const menu = el("div", undefined, "ms-menu");
  menu.hidden = true;

  function refreshLabel() {
    value.textContent =
      selected.length === 0 ? "Any" :
      selected.length === 1 ? selected[0] :
      selected.length + " selected";
    value.classList.toggle("is-empty", selected.length === 0);
  }

  if (options.length === 0) {
    menu.appendChild(el("div", "No options", "ms-empty"));
  }
  for (const opt of options) {
    const row = el("label", undefined, "ms-option");
    const cb = document.createElement("input");
    cb.type = "checkbox";
    cb.checked = selected.includes(opt);
    cb.onchange = () => {
      if (cb.checked) {
        if (!selected.includes(opt)) selected.push(opt);
      } else {
        const i = selected.indexOf(opt);
        if (i >= 0) selected.splice(i, 1);
      }
      refreshLabel();
      onChange([...selected]);
    };
    row.append(cb, el("span", String(opt)));
    menu.appendChild(row);
  }

  btn.onclick = (e) => {
    e.stopPropagation();
    const open = container.classList.toggle("is-open");
    menu.hidden = !open;
    closeOtherMenus(container);
  };
  menu.onclick = (e) => e.stopPropagation(); // keep clicks inside from closing it

  refreshLabel();
  container.append(btn, menu);
}

function closeOtherMenus(except) {
  for (const ms of document.querySelectorAll(".ms.is-open")) {
    if (ms === except) continue;
    ms.classList.remove("is-open");
    const menu = ms.querySelector(".ms-menu");
    if (menu) menu.hidden = true;
  }
}

// Clicking anywhere outside an open menu closes it.
document.addEventListener("click", () => closeOtherMenus(null));

loadFilter();
