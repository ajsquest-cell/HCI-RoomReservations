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
from nicegui import ui
import requests
from pathlib import Path

from calendar_view import calendar_view
from search_component import search_component

API_BASE = "http://localhost:8004"

# global state
state = {
    "room_id": None,
    "page": 1,
    "month": 10,
    "year": 2026,
    "current_filter_reservations": [],
    "current_parameters": {
        "reserved_by": [],
        "room_name": [],
        "building": [],
        # TODO
    },
    "announcements": [],
}


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

    ui.colors(primary="#003591", secondary="#003591")
    ui.add_css(Path(__file__).with_name("style.css").read_text())
    with ui.row().classes("w-full no-wrap gap-2"):
        ui.label("Room Reservation System").classes("text-3xl font-bold pr-10")
        ui.button("Dashboard", on_click=lambda: set_page(1)
                  ).classes("rounded-lg")
        ui.button("Search Rooms", on_click=lambda: set_page(2)
                  ).classes("rounded-lg")

    rooms = api_get("/rooms")
    if rooms and state["room_id"] is None:
        state["room_id"] = rooms[0]["id"]

    state["announcements"] = api_get("/announcements")

    with ui.column().classes("w-3/4 p-4"):
        render_content()


@ui.refreshable
def render_content():
    if state["page"] == 1:
        with ui.row().classes("w-full no-wrap"):
            render_filter()
            calendar_view(state["current_filter_reservations"], change_month_callback=change_month,
                          month=state["month"], year=state["year"])
    elif state["page"] == 2:
        with ui.row().classes("w-full"):
            search_component(on_booked=render_content.refresh)

    ui.separator()
    render_my_reservations()
    ui.separator()
    render_announcements()


def change_month(delta: int):

    state["month"] += delta

    if state["month"] > 12:
        state["month"] = 1
        state["year"] += 1
    elif state["month"] < 1:
        state["month"] = 12
        state["year"] -= 1

    render_content.refresh()


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


def render_filter():
    global state

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

        """
        # Create list of reservations based on parameters (||)
        reservations = []
        for param, vals in parameters.items():
            for val in vals:
                r_meets_requirement = [
                    r for r in all_reservations if r[param] == val]
                # print("\nALL RESERVATIONS THAT MEET REQUIREMENT:" +
                #       f"{param} == {val}: {r_meets_requirement}")
                # don't add duplicate reservations if reservations fulfill multiple filters.
                for r in r_meets_requirement:
                    if r not in reservations:
                        reservations.append(r)
        return reservations
        """

        # """
        # Create list of reservations based on parameters (&&)
        separate_filtered_reservations: list[list[dict]] = []
        for param, vals in parameters.items():
            if len(vals) == 0:
                continue
            r_meets_requirement = []
            for val in vals:
                r_meets_requirement.extend(
                    [r for r in all_reservations if r[param] == val])
                # print(f"\tMeets requirements: {list(r_meets_requirement)}")
            separate_filtered_reservations.append(r_meets_requirement)

        # print(f"\tall lists of reservations that meet requirements {
        #       separate_filtered_reservations}")

        final_reservations = []
        for i, reservations in enumerate(separate_filtered_reservations):
            if i == 0:
                # print(f"\n\tfirst list: {
                #       list(reservations)} getting added to final reservations")
                final_reservations = reservations
                continue

            # print(f"\n\tlist {i}: {list(reservations)} getting combined with final list {
            #       list(final_reservations)}")
            final_reservations = [
                r for r in final_reservations if r in reservations]
            # print(f"\n\tfinal list state: {list(final_reservations)}")

        # print(f"\tfinal reservations: {final_reservations}")
        return final_reservations
        # """

    def _update_filter_output(param: str, values: list[str]):
        # print(f"Param: '{param}'\nValues: {list(values)}")
        # check to make sure values are not None
        state["current_parameters"][param] = [v for v in values if v]
        # print(f"\nCurrent Parameters: {state["current_parameters"]}")
        current_filter_reservations = _get_reservations(
            state["current_parameters"])
        state["current_filter_reservations"] = current_filter_reservations
        render_content.refresh()

    all_reservations = _get_reservations()
    state["current_filter_reservations"] = _get_reservations(
        state["current_parameters"])

    current_params = state["current_parameters"]

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
                clearable=True, multiple=True,
                value=current_params["reserved_by"])
        with ui.row(align_items="center"):
            ui.label("Room:")
            ui.select(sorted(
                set([r["room_name"] for r in all_reservations])),
                on_change=lambda e: _update_filter_output(
                    "room_name", e.value),
                clearable=True, multiple=True,
                value=current_params["room_name"])
        with ui.row(align_items="center"):
            ui.label("Building:")
            ui.select(sorted(
                set([r["building"] for r in all_reservations])),
                on_change=lambda e: _update_filter_output(
                    "building", e.value),
                clearable=True, multiple=True,
                value=current_params["building"])

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


def render_announcements():
    """
    Render announcement card. Announcements can be clicked to be removed
    (placeholder for reading/acknowledging an announcement).

    TODO: Does not support announcement insertion at the moment. Currently
    when there are no announcements left, a new "item" label gets inserted
    into the list which says there are no items left. This is not counted
    by the expansion menu because that renders before the insertion. Should
    get fixed...
    """
    def _num_announcements() -> int:
        return len(state["announcements"])

    def _create_announcement_item(announcement: dict):
        """
        Create announcement item for the announcements list
        """
        with ui.item(on_click=lambda a=announcement: _remove_announcement(a)):
            with ui.item_section().props('avatar'):
                ui.icon('mail')
            with ui.item_section():
                ui.item_label(announcement["title"])
                ui.item_label(
                    announcement["body"]).props('caption')
            with ui.item_section().props('side top'):
                ui.item_label(announcement["posted_datetime"].strftime(
                    "%x")).props('caption')

    def _remove_announcement(announcement: dict):
        state["announcements"].remove(announcement)
        render_content.refresh()

    def _clear_list():
        state["announcements"].clear()
        render_content.refresh()

    def _render_no_messages_label():
        with announcement_list:
            with ui.card().classes('items-center no-shadow'):
                ui.label("No new announcements...")

    # Sort announcements from newest to oldest before listing
    announcements = state['announcements']
    for a in announcements:
        a["posted_datetime"] = datetime.strptime(
            a["posted"], "%Y-%m-%dT%H:%M:%S")
    announcements.sort(key=lambda item: item["posted_datetime"], reverse=True)

    # Render announcements card
    with ui.card().classes('w-full'):
        with ui.row().classes("w-full items-center").props('bordered'):
            with ui.expansion(f"Announcements ({_num_announcements()} unread)", value=_num_announcements() > 0).classes('w-full text-lg') as expansion:
                with ui.scroll_area().classes('border border-gray-300 rounded min-h-[200px]') as scroll:
                    with ui.list().props('separator').classes('w-full') as announcement_list:
                        for announcement in announcements:
                            _create_announcement_item(announcement)
                        if (_num_announcements() == 0):
                            _render_no_messages_label()

            ui.button("Clear All", on_click=lambda: _clear_list())

ui.run(port=8083, title="Mock Room Reservations")
