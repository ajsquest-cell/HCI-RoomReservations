/*

*/

const API = "http://localhost:8004";

// helpers

// get
async function getJSON(path) {
    try {
        const resp = await fetch(API + path);
        if (!resp.ok) {
            showMessage("Error: " + resp.status);
            return [];
        }
        return await resp.json();
    } catch (e) {
        showMessage("Could not reach API");
        return [];
    }
}

// book
async function book(roomId, slot) {
    const resp = await fetch(API + "/reservations/book", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ room_id: roomId, slot: slot }),
    });
    if (resp.ok) {
        showMessage("Booked " + slot);
        return true
    } 
    showMessage("Could not book " + slot);
    return false
}

async function bookSlots(roomId, slots, refresh) {
    for (const slot of slots) {
        if (!(await book(roomId, slot))) {
            break;
        }
    }
    refresh();
    if (typeof renderContent === "function") {
        renderContent();
    }
}

// notifications
function showMessage(text) {
    document.getElementById("message").textContent = text;
}

// toggle
function toggle(id) {
    const section = document.getElementById(id);
    section.hidden = !section.hidden;
}

// attendance
function getAttendance(id) {
    return parseInt(document.getElementById(id).value) || 0;
}

// make element
function make(tag, className, text = "") {
    const element = document.createElement(tag);
    element.className = className;
    element.textContent = text;
    return element;
}

// show Rooms
async function showRooms(resultsId, rooms, start, end, refresh) {
    const results = document.getElementById(resultsId);
    results.innerHTML = "";

    if (rooms.length === 0) {
        results.textContent = "No rooms found";
        return;
    }

    for (const room of rooms) {
        const slots = await getJSON(`/availability/by-room?room_id=${room.id}&start=${start}&end=${end}`);

        const card = make("div", "room-card");

        const link = make("a", "room-link", room.name);
        link.href = "#";
        link.onclick = (e) => { e.preventDefault(); showDetails(room); };
        card.appendChild(link);
        card.appendChild(make("div", "room-info", `${room.building} - capacity ${room.capacity}`));

        const slotRow = make("div", "slot-row");

        for (const slot of slots) {
            const button = make("button", "slot-btn", slot);
            button.onclick = () => bookSlots(room.id, [slot], refresh);
            slotRow.appendChild(button);
        }
        card.appendChild(slotRow);

        // book all
        if (slots.length > 1) {
            const bookAll = make("button", "book-all-btn", "Book all");
            bookAll.onclick = () => bookSlots(room.id, slots, refresh);
            card.appendChild(bookAll);
        }
        results.appendChild(card);
    }
}

// search by time
async function searchByTime() {
    showMessage("");
    const start = document.getElementById("start").value;
    const end = document.getElementById("end").value;
    if (!start || !end) {
        showMessage("Please select both start and end times");
        return;
    }
    const attendance = getAttendance("time-attendance");
    const rooms = await getJSON(`/availability/by-time?start=${start}&end=${end}&min_capacity=${attendance}`);
    showRooms("time-results", rooms, start, end, searchByTime);
    }

// search by building
async function searchByBuilding() {
    showMessage("");
    const building = document.getElementById("building").value;
    if (!building) {
        showMessage("Please select a building");
        return;
    }
    const attendance = getAttendance("building-attendance");
    const rooms = await getJSON(`/availability/by-building?building=${encodeURIComponent(building)}&min_capacity=${attendance}`);
    showRooms("building-results", rooms, 9, 17, searchByBuilding);
}

// Room details
function showDetails(room) {
    document.getElementById("details-name").textContent = room.name;
    document.getElementById("details-building").textContent = room.building;
    document.getElementById("details-capacity").textContent = room.capacity;
    document.getElementById("details-type").textContent = room.type;
    document.getElementById("details-equipment").textContent = room.equipment;
    document.getElementById("room-dialog").showModal();
}

function closeDetails() {
    document.getElementById("room-dialog").close();
}

// load buildings
async function loadBuildings() {
    const select = document.getElementById("building");
    for (const name of await getJSON("/buildings")) {
        select.add(new Option(name, name));
    }
}

loadBuildings();
