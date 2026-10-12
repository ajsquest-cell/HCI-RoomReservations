"""
reservations_ui.py

A very simple NiceGUI frontend that pulls data from
reservations_api.py and renders a room reservation portal:
browse rooms, see today's time slots, book/cancel a reservation, and
read announcements.

Run with:
    pip install nicegui requests
    python reservations_api.py    # in one terminal
    python reservations_ui.py     # in another terminal

Then http://localhost:8083 will open automatically
"""

import requests
from nicegui import ui

API_BASE = "http://localhost:8004"

# global state for "which room is selected"
state = {"room_id": None}


def api_get(path: str):
    try:
        resp = requests.get(f"{API_BASE}{path}", timeout=5)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        ui.notify(f"Could not reach API: {e}", type="negative")
        return []


def api_post(path: str, json: dict):
    try:
        resp = requests.post(f"{API_BASE}{path}", json=json, timeout=5)
        resp.raise_for_status()
        return True
    except requests.RequestException as e:
        detail = ""
        try:
            detail = e.response.json().get("detail", "")
        except Exception:
            pass
        ui.notify(detail or f"Request failed: {e}", type="negative")
        return False


def book_slot(room_id: int, slot: str):
    if api_post("/reservations/book", {"room_id": room_id, "slot": slot}):
        ui.notify("Room booked", type="positive")
        render_content.refresh()


def cancel_reservation(reservation_id: int):
    if api_post("/reservations/cancel", {"reservation_id": reservation_id}):
        ui.notify("Reservation cancelled", type="warning")
        render_content.refresh()


def select_room(room_id: int):
    state["room_id"] = room_id
    render_content.refresh()


def render_room_details(rooms: list(dict), room_id: int) -> None:
    def _clean_dialog(dialog):
        """
        Dialogs must be cleared before closing or reused.
        """
        dialog.clear()
        dialog.close()

    room: dict = {}
    for r in rooms:
        if r["id"] == room_id:
            room = r
            break

    if not room:  # Did not successfully find room to display details for.
        print(f"render_room_details() - Warning: room_id {
              room_id} invalid. Room does not exist in given set of rooms.")

        with ui.dialog() as dialog, ui.card(align_items="center"):
            ui.label("Whoops...").style("font-size:150%")
            ui.label("Details for the requested room are currently unavailable...")
            ui.button('Close', on_click=lambda: _clean_dialog(dialog))
        dialog.open()
        return

    with ui.dialog() as dialog, ui.card(align_items="center"):
        ui.label(f'{room["name"]}').style(
            "font-size:150%;font-weight:bold;text-align:center")
        ui.separator()
        with ui.grid(columns='auto 1fr'):
            ui.label("Capacity:").style("font-weight:bold")
            ui.label(f'{room["capacity"]}')

            ui.label('Type:').style("font-weight:bold")
            ui.label(f'{room["type"].title()}')

            ui.label('Equipment:').style("font-weight:bold")
            ui.label(f'{room["equipment"].title()}')

            ui.label('Building:').style("font-weight:bold")
            ui.label(f'{room["building"].title()}')

        ui.button('Close', on_click=lambda: _clean_dialog(dialog))
    dialog.open()


@ui.page("/")
def main_page():
    rooms = api_get("/rooms")
    if rooms and state["room_id"] is None:
        state["room_id"] = rooms[0]["id"]

    with ui.card():
        ui.button("More Details", on_click=lambda: render_room_details(rooms, 10))

    with ui.row().classes("w-full no-wrap"):
        with ui.column().classes("w-1/4 p-2"):
            ui.label("Rooms").classes("text-lg")
            for room in rooms:
                ui.link(f'{room["name"]} ({room["building"]})', "#").on(
                    "click", lambda room=room: select_room(room["id"])
                )

        with ui.column().classes("w-3/4 p-4"):
            render_content()


@ui.refreshable
def render_content():
    room_id = state["room_id"]
    if room_id is None:
        ui.label("No room selected")
        return

    room = api_get(f"/rooms/{room_id}")
    ui.label(f'{room.get("name", "")}').classes("text-2xl")
    ui.label(
        f'{room.get("building", "")} - capacity {room.get("capacity", "")} '
        f'- {room.get("equipment", "")}'
    ).classes("text-2xl")

    ui.label("Today's availability").classes("text-lg")
    slots = api_get(f"/rooms/{room_id}/slots")
    for s in slots:
        with ui.row().classes("items-center"):
            label = f'{s["slot"]} - {s["status"]}'
            if s["reserved_by"]:
                label += f' ({s["reserved_by"]})'
            ui.label(label)
            if s["status"] == "available":
                ui.button(
                    "Book",
                    on_click=lambda room_id=room_id, slot=s["slot"]: book_slot(
                        room_id, slot),
                )
            elif s["reserved_by"] == "you":
                ui.button(
                    "Cancel",
                    on_click=lambda rid=s["reservation_id"]: cancel_reservation(
                        rid),
                )

    ui.separator()
    render_my_reservations()
    ui.separator()
    render_announcements()


def render_my_reservations():
    ui.label("My Reservations").classes("text-lg")
    reservations = api_get("/my-reservations")
    if not reservations:
        ui.label("You don't have any reservations yet.")
        return
    for r in reservations:
        with ui.row().classes("items-center"):
            ui.label(
                f'{r["room_name"]} ({r["building"]}) - {r["date"]} {r["slot"]}')
            ui.button(
                "Cancel",
                on_click=lambda rid=r["id"]: cancel_reservation(rid),
            )


def render_announcements():
    ui.label("Announcements").classes("text-lg")
    announcements = api_get("/announcements")
    for a in announcements:
        ui.label(a["title"])
        ui.label(a["body"])
        ui.separator()


ui.run(port=8083, title="Mock Room Reservations")
