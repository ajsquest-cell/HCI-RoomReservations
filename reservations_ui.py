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

from ast import Lambda

from search_component import search_component

import requests
from nicegui import ui

from calendar_view import calendar_view

API_BASE = "http://localhost:8004"

# global state for "which room is selected"
state = {"room_id": None, "page": 1}

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

def set_page(page: int):
    state["page"] = page
    render_content.refresh()

@ui.page("/")
def main_page():

    with ui.row().classes("w-full no-wrap gap-2"):
        ui.label("Room Reservation System").classes("text-3xl font-bold pr-10")
        ui.button("Dashboard", on_click=lambda: set_page(1)).classes("rounded-lg")
        ui.button("Search Rooms", on_click=lambda: set_page(2)).classes("rounded-lg")

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


    if state["page"] == 1: 
        with ui.row().classes("w-full"):
            calendar_view(api_get("/my-reservations"))
    elif state["page"] == 2:
        with ui.row().classes("w-full"):
            search_component(on_booked=render_content.refresh)

    
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
            ui.label(f'{r["room_name"]} ({r["building"]}) - {r["date"]} {r["slot"]}')
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