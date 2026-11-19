const API_BASE = "http://localhost:8004";

const state = {
  roomId: null,
  announcements: [],
};

async function apiGet(path, fallback = []) {
  try {
    const resp = await fetch(API_BASE + path);
    if (!resp.ok) throw new Error(resp.status + " " + resp.statusText);
    return await resp.json();
  } catch (e) {
    showError("Could not reach API: " + e.message);
    return fallback;
  }
}

async function apiPost(path, body) {
  try {
    const resp = await fetch(API_BASE + path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!resp.ok) {
      let detail = "";
      try { detail = (await resp.json()).detail; } catch (_) { }
      showError(detail || "Request failed: " + resp.status);
      return false;
    }
    clearError();
    return true;
  } catch (e) {
    showError("Could not reach API: " + e.message);
    return false;
  }
}

function showError(msg) { document.getElementById("error").textContent = msg; }
function clearError() { document.getElementById("error").textContent = ""; }

function el(tag, text, className) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
}

async function bookSlot(roomId, slot) {
  if (await apiPost("/reservations/book", { room_id: roomId, slot })) {
    renderContent();
  }
}

async function cancelReservation(reservationId) {
  if (await apiPost("/reservations/cancel", { reservation_id: reservationId })) {
    renderContent();
  }
}

function selectRoom(roomId) {
  state.roomId = roomId;
  renderSidebar();
  renderContent();
}

async function updateState() {
  // TODO: Put all state updates here...
  state.announcements = await apiGet("/announcements");
}

async function renderSidebar() {
  const container = document.getElementById("room-list");
  const rooms = await apiGet("/rooms");
  container.replaceChildren();

  if (rooms.length && state.roomId === null) {
    state.roomId = rooms[0].id;
  }

  for (const room of rooms) {
    const isActive = room.id === state.roomId;
    const link = el("a", undefined, "room-item" + (isActive ? " is-active" : ""));
    link.href = "#";
    link.append(
      el("span", room.name, "room-item__name"),
      el("span", room.building, "room-item__building"),
    );
    link.onclick = (e) => {
      e.preventDefault();
      selectRoom(room.id);
    };
    container.appendChild(link);
  }
}

async function renderContent() {
  if (state.roomId === null) return;

  await Promise.all([
    renderRoomHeader(),
    renderSlots(),
    renderMyReservations(),
    renderAnnouncements(),
  ]);
}

async function renderRoomHeader() {
  const room = await apiGet(`/rooms/${state.roomId}`, {});
  const header = document.getElementById("room-header");
  header.replaceChildren();
  header.appendChild(el("h1", room.name || "", "room-header__name"));

  const meta = el("div", undefined, "room-header__meta");
  if (room.building) meta.appendChild(el("span", room.building, "chip"));
  if (room.capacity) meta.appendChild(el("span", `capacity ${room.capacity}`, "chip"));
  if (room.equipment) meta.appendChild(el("span", room.equipment, "chip"));
  header.appendChild(meta);
}

async function renderSlots() {
  const container = document.getElementById("slots");
  const slots = await apiGet(`/rooms/${state.roomId}/slots`);
  container.replaceChildren();

  for (const s of slots) {
    const row = el("div", undefined, "slot-row");

    row.appendChild(el("span", s.slot, "slot-row__time"));

    const isOpen = s.status === "available";
    row.appendChild(el("span", s.status, "badge " + (isOpen ? "badge--open" : "badge--taken")));

    if (s.reserved_by) row.appendChild(el("span", s.reserved_by, "slot-row__who"));

    row.appendChild(el("span", undefined, "slot-row__spacer"));

    if (isOpen) {
      const btn = el("button", "Book", "btn btn--primary");
      btn.onclick = () => bookSlot(state.roomId, s.slot);
      row.appendChild(btn);
    } else if (s.reserved_by === "you") {
      const btn = el("button", "Cancel", "btn btn--danger");
      btn.onclick = () => cancelReservation(s.reservation_id);
      row.appendChild(btn);
    }
    container.appendChild(row);
  }
}

async function renderMyReservations() {
  const container = document.getElementById("my-reservations");
  const reservations = await apiGet("/my-reservations");
  container.replaceChildren();

  if (!reservations.length) {
    container.appendChild(el("div", "You don't have any reservations yet.", "muted"));
    return;
  }

  for (const r of reservations) {
    const row = el("div", undefined, "reservation-row");
    row.appendChild(el("span", `${r.room_name} (${r.building}) — ${r.date} ${r.slot}`, "reservation-row__text"));

    const btn = el("button", "Cancel", "btn btn--danger");
    btn.onclick = () => cancelReservation(r.id);
    row.appendChild(btn);

    container.appendChild(row);
  }
}

async function renderAnnouncements() {
  const headerText = document.getElementById("announcements-header-text");
  const unread = document.getElementById("announcements-unread");
  const noNewMessages = document.getElementById("announcements-no-new-messages");

  unread.replaceChildren();

  // Create messages from available announcements

  function _removeAnnouncement(announcement) {
    for (const [index, a] of state.announcements.entries()) {
      if (a.id === announcement.id) {
        state.announcements.splice(index, 1);
        break;
      }
    }
    renderAnnouncements()
  }

  function _removeAllAnnouncements() {
    state.announcements.length = 0;
    renderAnnouncements();
  }

  function _createMessage(announcement) {
    // Uses message template to form message element.
    const messageTemplate = document.getElementById("announcement-message-template");
    const message = messageTemplate.content.cloneNode(true);

    message.querySelector(".announcement-message-title").textContent = announcement.title;
    const messagePostedTime = message.querySelector(".announcement-message-posted-time");
    messagePostedTime.datetime = announcement.posted;
    messagePostedTime.textContent = new Date(announcement.posted);
    const messageBody = message.querySelector(".announcement-message-body");
    messageBody.textContent = announcement.body;
    // Open/Close announcement message
    message.querySelector(".announcement-message").onclick = () => {
      messageBody.hidden = !messageBody.hidden;
    };

    // Clear announcement
    const messageConfirmationDialog = message.querySelector(".announcement-message-clear-confirmation-dialog");
    message.querySelector(".announcement-message-clear-confirmation-dialog-yes-button").onclick = () => {
      messageConfirmationDialog.close();
      _removeAnnouncement(announcement);
    };
    message.querySelector(".announcement-message-clear-confirmation-dialog-no-button").onclick = () => {
      messageConfirmationDialog.close();
    };

    message.querySelector(".announcement-message-clear-button").onclick = (event) => {
      messageConfirmationDialog.showModal();
      event.stopPropagation(); // Don't toggle message body while trying to clear the message.
    };

    return message;
  }

  // Display announcements in descending order (most recent first)
  const announcementsDescendingDate = state.announcements.sort((a, b) => new Date(b.posted) - new Date(a.posted));
  for (const a of announcementsDescendingDate) {
    unread.appendChild(_createMessage(a));
  }

  const numAnnouncements = state.announcements.length;
  headerText.textContent = "Announcements (" + numAnnouncements + " unread)";
  noNewMessages.hidden = numAnnouncements > 0;

  // Clear all announcements
  const clearAllAnnouncementsContainer = document.getElementById("announcement-clear-all");
  const clearAllAnnouncementsButton = document.getElementById("announcement-clear-all-messages-button");
  const clearAllAnnouncementsConfirmationDialog = clearAllAnnouncementsContainer.querySelector(".announcement-message-clear-confirmation-dialog");
  clearAllAnnouncementsButton.onclick = () => {
    clearAllAnnouncementsConfirmationDialog.showModal();
  };
  clearAllAnnouncementsConfirmationDialog.querySelector(".announcement-message-clear-confirmation-dialog-yes-button").onclick = () => {
    clearAllAnnouncementsConfirmationDialog.close();
    _removeAllAnnouncements();
  };
  clearAllAnnouncementsConfirmationDialog.querySelector(".announcement-message-clear-confirmation-dialog-no-button").onclick = () => {
    clearAllAnnouncementsConfirmationDialog.close();
  };
}

async function init() {
  await updateState();
  await renderSidebar();
  await renderContent();
}

init();
