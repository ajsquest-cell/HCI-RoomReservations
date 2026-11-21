const API_BASE = "http://localhost:8004";

const state = {
  roomId: null,
  announcements: [],
  myReservations: [],
};

let currentDate = new Date();
let events = [];

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

function el(tag, text) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
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

async function cancelAllReservations() {
  if (await apiPost("/reservations/cancel-all", {})) {
    renderContent();
  }
}

function selectRoom(roomId) {
  state.roomId = roomId;
  renderContent();
}

async function renderSidebar() {
  const container = document.getElementById("room-list");
  const rooms = await apiGet("/rooms");
  container.replaceChildren();

  if (rooms.length && state.roomId === null) {
    state.roomId = rooms[0].id;
  }

  for (const room of rooms) {
    const link = el("a", `${room.name} (${room.building})`);
    link.href = "#";
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
  header.appendChild(el("h1", room.name || ""));
  header.appendChild(el("h1",
    `${room.building || ""} - capacity ${room.capacity || ""} - ${room.equipment || ""}`));
}

//equivalent to python's calendar.monthcalendar(year, month)
function getMonthCalendar(year, month) {
  const firstDay = new Date(year, month, 1).getDay();
  const daysInMonth = new Date(year, month + 1, 0).getDate();

  let calendar = [];
  let week = [];

  //add empty days
  for (let i = 0; i < firstDay; i++) {
    week.push(null);
  }

  // days of the month
  for (let day = 1; day <= daysInMonth; day++) {
    week.push(day);

    if (week.length === 7) {
      calendar.push(week);
      week = [];
    }
  }

  // fill the last week with empty days
  if (week.length > 0) {
    while (week.length < 7) {
      week.push(null);
    }

    calendar.push(week);
  }

  return calendar;
}

// Render the calendar
function renderCalendar() {
  const year = currentDate.getFullYear();
  const month = currentDate.getMonth();

  const calendar = getMonthCalendar(year, month);

  const container = document.getElementById('calendar-body');
  const title = document.getElementById('calendar-title');

  title.textContent = currentDate.toLocaleDateString('en-US', {
    month: 'long',
    year: 'numeric'
  });

  container.innerHTML = '';

  calendar.forEach(week => {

    week.forEach(day => {

      const dayElement = document.createElement('div');
      dayElement.classList.add('calendar-day');

      if (day === null) {
        dayElement.classList.add('empty-day');
      } else {

        const dayNumber = document.createElement('div');
        dayNumber.classList.add('day-number');
        dayNumber.textContent = day;

        dayElement.appendChild(dayNumber);

        // Add events for this date
        const dateString = new Date(year, month, day).toLocaleDateString('en-CA');

        const dayEvents = events.filter(event => event.date === dateString);

        dayEvents.forEach(event => {

          const eventElement = document.createElement('div');
          eventElement.classList.add('calendar-event');
          eventElement.textContent = `${event.building}) - ${event.slot} -- reserved by :${event.reserved_by}`;

          dayElement.appendChild(eventElement);
        });

        // Clicking a day
        dayElement.addEventListener('click', () => {
          console.log('Selected date:', dateString);
        });
      }

      container.appendChild(dayElement);
    });
  });
}

// Navigate between months
function changeMonth(offset) {
  currentDate.setMonth(currentDate.getMonth() + offset);

  renderCalendar();
}

// Add an event
function addEvent(event) {
  events.push(event);

  renderCalendar();
}

// Initialize calendar
function initializeCalendar(reservations) {

  console.log("Calling initializeCalendar...");

  document.getElementById('prev-month').addEventListener('click', () => {
    changeMonth(-1);
  });

  document.getElementById('next-month').addEventListener('click', () => {
    changeMonth(1);
  });

  events = reservations
  renderCalendar();
}

async function renderSlots() {
  const container = document.getElementById("slots");
  const slots = await apiGet(`/rooms/${state.roomId}/slots`);
  container.replaceChildren();

  for (const s of slots) {
    const row = el("div");
    row.className = "row";

    let label = `${s.slot} - ${s.status}`;
    if (s.reserved_by) label += ` (${s.reserved_by})`;
    row.appendChild(el("span", label));

    if (s.status === "available") {
      const btn = el("button", "Book");
      btn.onclick = () => bookSlot(state.roomId, s.slot);
      row.appendChild(btn);
    } else if (s.reserved_by === "you") {
      const btn = el("button", "Cancel");
      btn.onclick = () => cancelReservation(s.reservation_id);
      row.appendChild(btn);
    }
    container.appendChild(row);
  }
}

async function renderMyReservations() {
  // Reservations can change outside of rendering (booking), so a fetch is necessary here...
  state.myReservations = await apiGet("/my-reservations");

  const headerText = document.getElementById("reservations-header-text");
  const list = document.getElementById("reservations-list");
  const noReservations = document.getElementById("reservations-none");

  list.replaceChildren();

  // Create reservation cards from user's reservations
  function _slotStartHour(slot) {
    return parseInt(slot.split(":")[0], 10);
  }

  function _createReservation(reservation) {
    const reservationTemplate = document.getElementById("reservation-template");
    const card = reservationTemplate.content.cloneNode(true);

    card.querySelector(".reservation-room").textContent = reservation.room_name;
    card.querySelector(".reservation-building").textContent = reservation.building;
    const reservationDate = card.querySelector(".reservation-date");
    reservationDate.dateTime = reservation.date;
    // Parse as local time; a bare "YYYY-MM-DD" is parsed as UTC and can display as the previous day.
    reservationDate.textContent = new Date(reservation.date + "T00:00:00").toLocaleDateString("en-US", {
      weekday: "long",
      month: "long",
      day: "numeric",
      year: "numeric",
    });
    card.querySelector(".reservation-slot").textContent = reservation.slot;

    // Cancel reservation
    const cancelConfirmationDialog = card.querySelector(".reservation-cancel-confirmation-dialog");
    card.querySelector(".reservation-cancel-confirmation-dialog-yes-button").onclick = () => {
      cancelConfirmationDialog.close();
      cancelReservation(reservation.id);
    };
    card.querySelector(".reservation-cancel-confirmation-dialog-no-button").onclick = () => {
      cancelConfirmationDialog.close();
    };

    card.querySelector(".reservation-cancel-button").onclick = () => {
      cancelConfirmationDialog.showModal();
    };

    return card;
  }

  // Display reservations in ascending order (soonest first)
  // Sort by date, then by time, then by room name
  const reservationsAscending = state.myReservations.sort((a, b) =>
    a.date.localeCompare(b.date) ||
    _slotStartHour(a.slot) - _slotStartHour(b.slot) ||
    a.room_name.localeCompare(b.room_name));
  for (const r of reservationsAscending) {
    list.appendChild(_createReservation(r));
  }

  const numReservations = state.myReservations.length;
  headerText.textContent = "My Reservations (" + numReservations + ")";
  noReservations.hidden = numReservations > 0;

  // Cancel all reservations
  const cancelAllReservationsContainer = document.getElementById("reservation-cancel-all");
  const cancelAllReservationsButton = document.getElementById("reservation-cancel-all-button");
  const cancelAllReservationsConfirmationDialog = cancelAllReservationsContainer.querySelector(".reservation-cancel-confirmation-dialog");
  cancelAllReservationsButton.disabled = numReservations === 0;
  cancelAllReservationsButton.onclick = () => {
    cancelAllReservationsConfirmationDialog.showModal();
  };
  cancelAllReservationsConfirmationDialog.querySelector(".reservation-cancel-confirmation-dialog-yes-button").onclick = () => {
    cancelAllReservationsConfirmationDialog.close();
    cancelAllReservations();
  };
  cancelAllReservationsConfirmationDialog.querySelector(".reservation-cancel-confirmation-dialog-no-button").onclick = () => {
    cancelAllReservationsConfirmationDialog.close();
  };
}

async function renderAnnouncements() {
  const headerText = document.getElementById("announcements-header-text");
  const unread = document.getElementById("announcements-unread");
  const noNewMessages = document.getElementById("announcements-no-new-messages");

  unread.replaceChildren();

  // ~~~Create messages from available announcements~~~ //

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
  // TODO: Announcements are only fetched once on init. If we wanted persistent
  //       announcements, then we would need user accounts or something similar
  //       on the api-side (similarly to reservations).
  state.announcements = await apiGet("/announcements");

  const reservations = await apiGet("/all-reservations");
  // console.log("Reservations:", reservations);
  // console.log("Is array:", Array.isArray(reservations));

  // Initialize actual page
  await renderSidebar();
  await renderContent();

  initializeCalendar(reservations);
}

// document.addEventListener('DOMContentLoaded', init);

init();
