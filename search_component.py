# Where/When Search

import requests
from nicegui import ui

API_BASE = "http://localhost:8004"

def get(path, **params):
    try:
        resp = requests.get(f"{API_BASE}{path}", params=params, timeout=5)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        ui.notify(f"Could not reach API: {e}", type="negative")
        return []

def book(room_id, slot):
    r = requests.post(f"{API_BASE}/reservations/book", json={"room_id": room_id, "slot": slot})
    if r.ok:
        ui.notify(f"Booking confirmed for room {room_id} at slot {slot}")
    else:
        ui.notify(f"Failed to book room {room_id} at slot {slot}", type="negative")
    return r.ok


# helper to toggle visibility of a section
def toggle_selection(title):
    ui.button(title, on_click=lambda: body.set_visibility(not body.visible)).classes("search-toggle")
    body = ui.column()
    body.set_visibility(False)
    return body

# get attendence
def get_attendance(size):
    return int(size.value) if size.value else 0

# helper to show open slots
def show_results(room, booking, start=9, end=17):
    slots = get("/availability/by-room", room_id=room["id"], start=start, end=end)
    with ui.card().classes("room-card"):
        ui.label(room["name"]).classes("room-link").on("click", lambda: room_details(room))
        ui.label(f'{room["building"]} - capacity {room["capacity"]}')

        if not slots:
            ui.label("No available slots").classes("text-red-500")
            return

        with ui.row():
            for slot in slots:
                ui.button(slot, on_click=lambda slot=slot: book_slot(room["id"], [slot], booking)).classes("m-1 slot-btn").props("flat")

        if len(slots) > 1:
            ui.button("Book all", on_click=lambda: book_slot(room["id"], slots, booking)).classes("slot-btn")


# display pop up with room details
def room_details(room):
    with ui.dialog() as dialog, ui.card().tight().classes("min-w-80"):
        ui.label(room["name"]).classes("room-info-title w-full")

        with ui.card_section():
            ui.label(f'Building: {room["building"]}')
            ui.label(f'Capacity: {room["capacity"]}')
            ui.label(f'Type: {room["type"].capitalize()}')
            ui.label(f'Equipment: {room["equipment"]}')
    dialog.open()

# helper to book slot
def book_slot(room_id, slots, booking):
    all(book(room_id, slot) for slot in slots)
    booking()

# creates search component
def search_component(on_booked=None):
    with ui.column():
        time_search(on_booked)
        location_search(on_booked)


# Search by time
def time_search(on_booked):
    # display
    with toggle_selection("Search for available locations by time"):
        start = ui.select(list(range(9, 17)), label="Start hour").classes("w-40")
        end = ui.select(list(range(10, 18)), label="End hour").classes("w-40")
        attendance = ui.number("Expected attendance (optional)", min=1, precision=0).classes("w-64")
        ui.button("Search", on_click=lambda: display_results())
        results = ui.row().classes("flex-wrap")

    # helper
    def display_results():
        results.clear()
        if start.value is None or end.value is None:
            ui.notify("Please select both start and end times", type="negative")
            return
        rooms = get("/availability/by-time", start=start.value, end=end.value, min_capacity=get_attendance(attendance))
        with results:
            if not rooms:
                ui.notify("No available rooms for the selected time range", type="negative")
                return
            
            for room in rooms:
                show_results(room, lambda: booking(), start.value, end.value)

    def booking():
        display_results()
        if on_booked:
            on_booked()


# Search by location
def location_search(on_booked):
    # display
    with toggle_selection("Search for available locations by building"):
        building = ui.select(get("/buildings"), label="Building").classes("w-64")
        attendance = ui.number("Expected attendance (optional)", min=1, precision=0).classes("w-64")
        ui.button("Search", on_click=lambda: display_results())
        results = ui.row().classes("flex-wrap")

    # helper
    def display_results():
        results.clear()
        if building.value is None:
            ui.notify("Please select a building", type="negative")
            return
        rooms = get("/availability/by-building", building=building.value, min_capacity=get_attendance(attendance))
        with results:
            if not rooms:
                ui.notify("No available rooms in the selected building", type="negative")
            for room in rooms:
                show_results(room, lambda: booking())

    def booking():
        display_results()
        if on_booked:
            on_booked()
