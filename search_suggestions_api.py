
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


def _get_all_contexts() -> list[dict]:
    all_contexts = []
    for context in SEARCHABLE_CONTEXTS:
        all_contexts.append({"context": context.__name__, "searchables": [
                            item.value for item in context]})
    return all_contexts


@app.get("/searchables")
def list_searchables():
    """
    We're going to have this be a client-side thing I think to reduce network
    calls. Initially, we will grab all of the names from the api. Then we'll have
    them to work with.

    TODO: Might be bad practice, unsure - need input here.
    """
    return _get_all_contexts()


if __name__ == "__main__":
    print("All searchable contexts detected:")
    for context in SEARCHABLE_CONTEXTS:
        print(f"\t{context.__name__}:")
        for item in context:
            print(f"\t\t- {item.value}")

    # server
    import uvicorn
    print("Starting searchables server...")
    uvicorn.run(app, port=PORT)
