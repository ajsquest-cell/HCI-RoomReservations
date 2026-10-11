
"""
Going to copy-paste current api code since I don't really have anything to 
go on with my implementation at the moment, then can adjust later.

"""

from datetime import datetime

NOW = datetime(2026, 8, 23, 9, 0, 0)
TODAY = NOW.date().isoformat()

SLOTS = [
    "9:00-10:00", "10:00-11:00", "11:00-12:00", "12:00-13:00",
    "13:00-14:00", "14:00-15:00", "15:00-16:00", "16:00-17:00",
]

ROOMS = [
    {"id": 1, "name": "Study Room 204", "building": "Library",
        "capacity": 4, "type": "study", "equipment": "whiteboard"},
    {"id": 2, "name": "Study Room 210", "building": "Library",
        "capacity": 6, "type": "study", "equipment": "whiteboard, TV"},
    {"id": 3, "name": "Conference Room A", "building": "Student Union", "capacity": 12,
        "type": "conference", "equipment": "projector, video conferencing"},
    {"id": 4, "name": "Media Lab 1", "building": "Arts Building",
        "capacity": 8, "type": "lab", "equipment": "editing workstations"},
    {"id": 5, "name": "Group Study Pod C", "building": "Library",
        "capacity": 2, "type": "study", "equipment": "none"},
]

RESERVATIONS = [
    {"id": 1, "room_id": 1, "date": TODAY,
        "slot": "10:00-11:00", "reserved_by": "you"},
    {"id": 2, "room_id": 3, "date": TODAY,
        "slot": "13:00-14:00", "reserved_by": "Dolly Parton"},
]
_next_reservation_id = 3

ANNOUNCEMENTS = [
    {
        "id": 1,
        "title": "Media Lab 1 closed for equipment upgrades",
        "posted": "2026-08-21T10:00:00",
        "body": "Media Lab 1 will be unavailable for booking next Tuesday while new editing workstations are installed.",
    },
    {
        "id": 2,
        "title": "New group study pods added",
        "posted": "2026-08-18T10:00:00",
        "body": "Three new two-person study pods are now bookable on the library's second floor, including Group Study Pod C.",
    },
]


def clean_string(string: str) -> str:
    return string.lower().strip()


def room_search_suggestions(search_term: str) -> list[str]:
    """
    Not ideal to load list of rooms every call, could compile list in memory on client-side as
    part of ui loading or something
    """
    suggestions: list[str] = []
    current_room_name: str = ""
    clean_search_term: str = clean_string(search_term)

    for room in ROOMS:
        current_room_name = room["name"]
        if clean_search_term in clean_string(current_room_name):
            suggestions.append(current_room_name)

    return suggestions


"""
Rooms:
"Study Room 204", "Study Room 210", "Conference Room A",
"Media Lab 1", "Group Study Pod C",
"""
STUDY_ROOM_204 = "Study Room 204"
STUDY_ROOM_210 = "Study Room 210"
CONFERENCE_ROOM_A = "Conference Room A"
MEDIA_LAB_1 = "Media Lab 1"
GROUP_STUDY_POD_C = "Group Study Pod C"


def _room_search_test(search_term: str, expected_suggestions: list[str]):
    suggestions = _room_search_test(search_term)
    for room in expected_suggestions:
        assert room in suggestions


def _all_room_search_suggestion_tests():
    _room_search_test(
        "ST", [STUDY_ROOM_204, STUDY_ROOM_210, GROUP_STUDY_POD_C])
    _room_search_test("M", [STUDY_ROOM_204, STUDY_ROOM_210,
                            CONFERENCE_ROOM_A, MEDIA_LAB_1])
    _room_search_test("\t\nMeDIA    ", [MEDIA_LAB_1])


if __name__ == "__main__":
    _all_room_search_suggestion_tests()
