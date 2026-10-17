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

from datetime import datetime
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


@ui.page("/")
def main_page():
    rooms = api_get("/rooms")
    if rooms and state["room_id"] is None:
        state["room_id"] = rooms[0]["id"]

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

    render_announcements()
    ui.separator()

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
    # ui.separator()
    # render_announcements()


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
    announcements = api_get("/announcements")

    # Sort announcements from newest to oldest
    for a in announcements:
        a["posted_datetime"] = datetime.strptime(
            a["posted"], "%Y-%m-%dT%H:%M:%S")
    announcements.sort(key=lambda item: item["posted_datetime"], reverse=True)

    def _create_announcement_item(announcement: dict):
        with ui.item() as announcement_item:
            announcement_item.on_click(
                lambda i=announcement_item: _remove_announcement_item(i))
            with ui.item_section().props('avatar'):
                ui.icon('mail')
            with ui.item_section():
                ui.item_label(announcement["title"])
                ui.item_label(
                    announcement["body"]).props('caption')
            with ui.item_section().props('side top'):
                ui.item_label(announcement["posted_datetime"].strftime(
                    "%x")).props('caption')

    def _remove_announcement_item(announcement_item):
        # ui.notify(f'Selected Announcement {announcement_item["id"]}')
        announcement_item.delete()

    # h-[30vh] min-h-[250px]'):  # TODO
    with ui.card().classes('w-full') as card:
        with ui.row().classes("items-center w-full").props('bordered'):
            ui.label('Announcements').props('header').classes('text-lg')
            ui.space()
            ui.button("Clear", on_click=lambda: announcement_list.clear())

        with ui.scroll_area() as scroll:
            with ui.list().props('bordered separator').classes('w-full') as announcement_list:
                for announcement in announcements:
                    _create_announcement_item(announcement)


ui.run(port=8083, title="Mock Room Reservations")
