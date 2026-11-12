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

// notifications
let messageTimer;
function showMessage(text) {
    const popup = document.getElementById("message");
    clearTimeout(messageTimer);

    if (!text) {
        popup.classList.remove("show");
        return;
    }

    popup.textContent = text;
    popup.classList.add("show");

    const time = Math.max(3000, text.length * 50);
    messageTimer = setTimeout(() => popup.classList.remove("show"), time);
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

function getHour(slot) {
    return parseInt(slot.split(":")[0])
}

function rangeLabel(firstSlot, lastSlot) {
    return firstSlot.split("-")[0] + "-" + lastSlot.split("-")[1];
}

function cloneTemplate(id) {
    return document.getElementById(id).content.firstElementChild.cloneNode(true);
}

// booking slot range 

async function bookRange(room, picked, refresh) {
    const booked = [];
    const skipped = [];

    for (const s of picked) {
        if (s.status == "available") {
            if (await book(room.id, s.slot)) {
                booked.push(s.slot);
            } else {
                skipped.push(`${s.slot} (request failed)`);
            }
        } else if (s.reserved_by === "you") {
            skipped.push(`${s.slot} (you already booked it)`);
        } else {
            skipped.push(`${s.slot} (booked by someone else)`);
        }
    }

    await refresh();

    let message = `${room.name}: `;
    message += booked.length ? `booked ${booked.join(", ")}.` : "nothing booked.";
    if (skipped.length) {
        message += ` Could not book ${skipped.join(", ")}.`;
    }
    showMessage(message);
    
    if (typeof renderContent === "function") {
        renderContent();
    }
}

function makeCard(room, slots, refresh) {
    const card =  cloneTemplate("room-card-template");

    const link = card.querySelector(".room-link");
    const bar = card.querySelector(".timeline");
    const selection = card.querySelector(".selection");
    const bookButton = card.querySelector(".book-all-btn");

    link.textContent = room.name;
    link.onclick = (e) => { e.preventDefault(); showDetails(room); };
    card.querySelector(".room-info").textContent = `${room.building} - capacity ${room.capacity}`;

    const blocks = [];
    slots.forEach((s, i) => {
        const block =  cloneTemplate("slot-template");
        block.querySelector(".seg-hour").textContent = getHour(s.slot);
        const icon = block.querySelector(".seg-icon");

        if (s.status === "available") {
            block.classList.add("seg-open");
            block.title = `${s.slot}: open`;
        } else if (s.reserved_by === "you") {
            block.classList.add("seg-mine");
            icon.textContent = "✓";
            block.title = `${s.slot}: booked by you`;
        } else {
            block.classList.add("seg-taken");
            icon.textContent = "✗";
            block.title = `${s.slot}: booked by someone else`;
        }

        block.onclick = () => pick(i);
        blocks.push(block);
        bar.appendChild(block);
    });

    let first = null;
    let last = null;

    function selectedRange() {
        const end = last === null ? first : last;
        return [Math.min(first, end), Math.max(first, end)];
    }

    function pick(i) {
        if (first === null || last != null) {
            first = i;
            last = null;
        } else {
            last = i;
        }

        const [lo, hi] = selectedRange();
        blocks.forEach((b, j) => b.classList.toggle("seg-selected", j >= lo && j <= hi));
        selection.textContent = "Selected " + rangeLabel(slots[lo].slot, slots[hi].slot);
        bookButton.disabled = false;
    }

    bookButton.onclick = () => {
        const [lo, hi] = selectedRange();
        bookRange(room, slots.slice(lo, hi + 1), refresh);
    };

    return card;
}

// show Rooms
async function showRooms(resultsId, rooms, start, end, refresh) {
    const results = document.getElementById(resultsId);
    results.innerHTML = "";

    const legend = results.parentElement.querySelector(".legend");

    if (rooms.length === 0) {
        results.textContent = "No rooms found";
        legend.hidden = true;
        return;
    }

    legend.hidden = false;

    for (const room of rooms) {
        
        const allSlots = await getJSON(`/rooms/${room.id}/slots`);
        const slots = allSlots.filter(s =>
            getHour(s.slot) >= Number(start) && getHour(s.slot) < Number(end));
 
        results.appendChild(makeCard(room, slots, refresh));
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
    await showRooms("time-results", rooms, start, end, searchByTime);
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
    await showRooms("building-results", rooms, 9, 17, searchByBuilding);
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
