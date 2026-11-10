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
async function book(roomId, slot, button) {
    const resp = await fetch(API + "/reservations/book", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ room_id: roomId, slot: slot }),
  });
  if (resp.ok) {
    showMessage("Booked " + slot);
    button.remove();
    renderContent();
  } else {
    showMessage("Could not book " + slot);
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

// show Rooms
async function showRooms(resultsId, rooms, start, end) {
    const results = document.getElementById(resultsId);
    results.innerHTML = "";

    if (rooms.length === 0) {
        results.textContent = "No rooms found";
        return;
    }

    for (const room of rooms) {
        const slots = await getJSON(`/availability/by-room?room_id=${room.id}&start=${start}&end=${end}`);

        const line = document.createElement("div");
        line.textContent = `${room.name} (${room.building}, capacity ${room.capacity}): `;

        for (const slot of slots) {
            const button = document.createElement("button");
            button.textContent = slot;
            button.onclick = () => book(room.id, slot, button);
            line.appendChild(button);
        }
        results.appendChild(line);
    }
}

// search by time
async function searchByTime() {
    const start = document.getElementById("start").value;
    const end = document.getElementById("end").value;
    const rooms = await getJSON(`/availability/by-time?start=${start}&end=${end}`);
    showRooms("time-results", rooms, start, end);
}

// search by building
async function searchByBuilding() {
    const building = document.getElementById("building").value;
    const rooms = await getJSON(`/availability/by-building?building=${encodeURIComponent(building)}`);
    showRooms("building-results", rooms, 9, 17);
}

// Room details


// load buildings
async function loadBuildings() {
    const select = document.getElementById("building");
    for (const name of await getJSON("/buildings")) {
        select.add(new Option(name, name));
    }
}

loadBuildings();
