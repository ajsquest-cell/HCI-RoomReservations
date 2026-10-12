
"""
WIP search suggestion code. May need to change depending on
future implementation.

Endpoints:
    Get /searchables
"""
from enum import StrEnum

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

PORT = 8005

app = FastAPI(title="Room Reservation Searchables API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


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


SEARCHABLE_CONTEXTS: list[StrEnum] = [
    UserName,
    BuildingName,
    RoomName,
    RoomType,
    EquipmentType,
]


def clean_string(string: str) -> str:
    return string.lower().strip()


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


@app.get("/searchables")
def list_searchables():
    """
    We're going to have this be a client-side thing I think to reduce network
    calls. Initially, we will grab all of the names from the api. Then we'll have
    them to work with.

    TODO: Might be bad practice, unsure - need input here.
    """
    searchables: list[dict] = []
    for context in SEARCHABLE_CONTEXTS:
        c = {"context": context.__name__, "search_items": []}
        for item in context:
            c["search_items"].append(item.value)
        searchables.append(c)

    return searchables


if __name__ == "__main__":
    # testing
    search_suggestion_tests()

    print("All searchable contexts detected:")
    for context in SEARCHABLE_CONTEXTS:
        print(f"\t{context.__name__}:")
        for item in context:
            print(f"\t\t- {item.value}")

    # server
    import uvicorn
    print("Starting searchables server...")
    uvicorn.run(app, port=PORT)
