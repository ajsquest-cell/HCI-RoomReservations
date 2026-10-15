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
# global filtered reservations list
current_filter_reservations = []


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
    room_id = state["room_id"]
    if room_id is None:
        ui.label("No room selected")
        return

    render_filter()
    ui.separator()

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


def render_filter():
    global current_filter_reservations
    current_parameters = {
        "reserved_by": [],
        "room_name": [],
        "building": [],
        # TODO
    }

    # Filter needs to collect a set of reservations to give to calendar view
    def _get_reservations(parameters: dict = None):
        all_reservations = api_get("/all-reservations")
        if not parameters:
            return all_reservations

        # Check if we have parameters for reservations or not
        has_params = False
        for params in parameters.values():
            if params:
                has_params = True
                break
        if not has_params:
            return all_reservations

        # """
        # Create list of reservations based on parameters (||)
        reservations = []
        for param, vals in parameters.items():
            for val in vals:
                r_meets_requirement = [
                    r for r in all_reservations if r[param] == val]
                print("\nALL RESERVATIONS THAT MEET REQUIREMENT:" +
                      f"{param} == {val}: {r_meets_requirement}")
                # don't add duplicate reservations if reservations fulfill multiple filters.
                for r in r_meets_requirement:
                    if r not in reservations:
                        reservations.append(r)
        return reservations
        # """

        """
        # Create list of reservations based on parameters (&&)
        separate_filtered_reservations: list(list(dict)) = []
        for param, vals in parameters.items():
            for val in vals:
                parameter_reservations = [r for r in all_reservations if r[param]]
            separate_filtered_reservations.append([r for r in parameter_reservations])
        final_reservations = []
        for i, reservations in enumerate(separate_filtered_reservations):
            if i == 0:
                final_reservations.append()
        """

    def _update_filter_output(param: str, values: list[str]):
        print(values)
        # check to make sure values are not None
        current_parameters[param] = [v for v in values if v]
        print(f"\nCurrent Parameters: {current_parameters}")
        current_filter_reservations = _get_reservations(current_parameters)
        print(f"\nfilter reservations: {current_filter_reservations}")

    all_reservations = _get_reservations()
    # print(f"Current parameters: {list(current_parameters.items())}")
    # print(f"Current reservations: {
    #       list(_get_reservations(current_parameters))}")

    with ui.card():
        ui.label("Filter")
        with ui.row(align_items="center"):
            ui.label("User:")
            ui.select(sorted(
                set([r["reserved_by"] for r in all_reservations])),
                on_change=lambda e: _update_filter_output(
                    "reserved_by", e.value),
                clearable=True, multiple=True)
        with ui.row(align_items="center"):
            ui.label("Room:")
            ui.select(sorted(
                set([r["room_name"] for r in all_reservations])),
                on_change=lambda e: _update_filter_output(
                    "room_name", e.value),
                clearable=True, multiple=True)
        with ui.row(align_items="center"):
            ui.label("Building:")
            ui.select(sorted(
                set([r["building"] for r in all_reservations])),
                on_change=lambda e: _update_filter_output(
                    "building", e.value),
                clearable=True, multiple=True)

        # with ui.row(align_items="center"):
        #     ui.label("User:")
        #     ui.select(sorted([r["reserved_by"] for r in all_reservations]))

        # for r in _get_reservations():
        #     with ui.row().classes("items-center"):
        #         ui.label(
        #             f'{r["room_name"]} ({r["building"]}) - {r["date"]} {r["slot"]}')
        #         ui.button(
        #             "Cancel",
        #             on_click=lambda rid=r["id"]: cancel_reservation(rid),
        #         )


ui.run(port=8083, title="Mock Room Reservations")
