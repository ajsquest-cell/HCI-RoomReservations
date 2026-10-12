
"""
Going to copy-paste current api code since I don't really have anything to
go on with my implementation at the moment, then can adjust later.

"""

from datetime import datetime
from enum import StrEnum


class UserName(StrEnum):
    YOU = "you"
    DOLLY_PARTON = "Dolly Parton"


class BuildingName(StrEnum):
    LIBRARY = "Library"
    STUDENT_UNION = "Student Union"
    ARTS_BUILDING = "Arts Building"


class RoomName(StrEnum):
    STUDY_ROOM_204 = "Study Room 204"
    STUDY_ROOM_210 = "Study Room 210"
    CONFERENCE_ROOM_A = "Conference Room A"
    MEDIA_LAB_1 = "Media Lab 1"
    GROUP_STUDY_POD_C = "Group Study Pod C"


class RoomType(StrEnum):
    STUDY = "study"
    CONFERENCE = "conference"
    LAB = "lab"


class EquipmentType(StrEnum):
    NONE = "none"

    PROJECTOR = "projector"
    EDITING_WORKSTATIONS = "editing workstations"
    WHITEBOARD = "whiteboard"
    TV = "TV"
    VIDEO_CONFERENCING = "video conferencing"


NOW = datetime(2026, 8, 23, 9, 0, 0)
TODAY = NOW.date().isoformat()

SLOTS = [
    "9:00-10:00", "10:00-11:00", "11:00-12:00", "12:00-13:00",
    "13:00-14:00", "14:00-15:00", "15:00-16:00", "16:00-17:00",
]

ROOMS = [
    {"id": 1, "name": RoomName.STUDY_ROOM_204, "building": BuildingName.LIBRARY,
        "capacity": 4, "type": RoomType.STUDY, "equipment": f"{EquipmentType.WHITEBOARD}"},
    {"id": 2, "name": RoomName.STUDY_ROOM_210, "building": BuildingName.LIBRARY,
        "capacity": 6, "type": RoomType.STUDY, "equipment": f"{EquipmentType.WHITEBOARD}, {EquipmentType.TV}"},
    {"id": 3, "name": RoomName.CONFERENCE_ROOM_A, "building": BuildingName.STUDENT_UNION,
        "capacity": 12, "type": RoomType.CONFERENCE, "equipment": f"{EquipmentType.PROJECTOR}, {EquipmentType.VIDEO_CONFERENCING}"},
    {"id": 4, "name": RoomName.MEDIA_LAB_1, "building": BuildingName.ARTS_BUILDING,
        "capacity": 8, "type": RoomType.LAB, "equipment": f"{EquipmentType.EDITING_WORKSTATIONS}"},
    {"id": 5, "name": RoomName.GROUP_STUDY_POD_C, "building": BuildingName.LIBRARY,
        "capacity": 2, "type": RoomType.STUDY, "equipment": f"{EquipmentType.NONE}"},
]

RESERVATIONS = [
    {"id": 1, "room_id": 1, "date": TODAY,
        "slot": "10:00-11:00", "reserved_by": UserName.YOU},
    {"id": 2, "room_id": 3, "date": TODAY,
        "slot": "13:00-14:00", "reserved_by": UserName.DOLLY_PARTON},
]
_next_reservation_id = 3

ANNOUNCEMENTS = [
    {
        "id": 1,
        "title": f"{RoomName.MEDIA_LAB_1} closed for equipment upgrades",
        "posted": "2026-08-21T10:00:00",
        "body": f"{RoomName.MEDIA_LAB_1} will be unavailable for booking next Tuesday while new editing workstations are installed.",
    },
    {
        "id": 2,
        "title": "New group study pods added",
        "posted": "2026-08-18T10:00:00",
        "body": f"Three new two-person study pods are now bookable on the library's second floor, including {RoomName.GROUP_STUDY_POD_C}.",
    },
]


def clean_string(string: str) -> str:
    return string.lower().strip()


# def room_search_suggestions(search_term: str) -> list[str]:
#     """
#     Return a list of rooms which contain the search term in their name.
#     """
#     suggestions: list[str] = []
#     clean_search_term: str = _clean_string(search_term)
#
#     for room in RoomName:
#         if clean_search_term in _clean_string(room):
#             suggestions.append(room)
#
#     return suggestions


def search_suggestions(search_context: StrEnum, search_term: str) -> list[str]:
    """
    Generate a list of search suggestions given a search context and a search term.
    """
    suggestions: list[str] = []
    clean_search_term: str = clean_string(search_term)

    for item in search_context:
        if clean_search_term in clean_string(item):
            suggestions.append(item)

    return suggestions


def generic_search_suggestion_test(search_context: StrEnum, search_term: str, expected_suggestions: list[str]) -> None:
    actual_suggestions = search_suggestions(search_context, search_term)
    for expected in expected_suggestions:
        assert expected in actual_suggestions


def search_suggestion_tests() -> None:
    """
    Not many tests, but this is a pretty simple implementation (WHICH MIGHT HAVE TO CHANGE)
    """
    # Room Tests
    generic_search_suggestion_test(
        RoomName, "ST", [RoomName.STUDY_ROOM_204, RoomName.STUDY_ROOM_210, RoomName.GROUP_STUDY_POD_C])
    generic_search_suggestion_test(
        RoomName, "M", [RoomName.STUDY_ROOM_204, RoomName.STUDY_ROOM_210, RoomName.CONFERENCE_ROOM_A, RoomName.MEDIA_LAB_1])
    generic_search_suggestion_test(
        RoomName, "\t\nMeDIA    ", [RoomName.MEDIA_LAB_1])

    # User Tests
    generic_search_suggestion_test(
        UserName, "\t\nu    ", [UserName.YOU])
    generic_search_suggestion_test(
        UserName, "\t\n   A    ", [UserName.DOLLY_PARTON])
    generic_search_suggestion_test(
        UserName, "You", [UserName.YOU])
    generic_search_suggestion_test(
        UserName, "o", [UserName.YOU, UserName.DOLLY_PARTON])


if __name__ == "__main__":
    search_suggestion_tests()
