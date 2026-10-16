"""
TODO
"""


def search_suggestions(search_context: dict, search_term: str) -> list[str]:
    """
    Generate a list of search suggestions given a search context and a search term.
    """
    suggestions: list[str] = []
    clean_search_term: str = _clean_string(search_term)

    for item in search_context["searchables"]:
        if clean_search_term in _clean_string(item):
            suggestions.append(item)

    return suggestions


def _clean_string(string: str) -> str:
    """
    Helper function to attempt to normalize strings before comparisons.
    """
    return string.lower().strip()


def _test_search_suggestion() -> None:
    """
    Not many tests, but this is a pretty simple implementation (WHICH MIGHT HAVE TO CHANGE)
    """
    from search_suggestions_api import _get_all_contexts, UserName, RoomName

    contexts = _get_all_contexts()
    room_name_context: dict
    user_name_context: dict

    for context in contexts:
        if context["context"] == RoomName.__name__:
            room_name_context = context
        if context["context"] == UserName.__name__:
            user_name_context = context

    def _generic_search_suggestion_test(search_context: dict, search_term: str, expected_suggestions: list[str]) -> None:
        """
        Helper function to make test running a little easier
        """
        actual_suggestions = search_suggestions(search_context, search_term)
        for expected in expected_suggestions:
            assert expected in actual_suggestions

    # Room Tests
    _generic_search_suggestion_test(
        room_name_context, "ST", [RoomName.STUDY_ROOM_204, RoomName.STUDY_ROOM_210, RoomName.GROUP_STUDY_POD_C])
    _generic_search_suggestion_test(
        room_name_context, "M", [RoomName.STUDY_ROOM_204, RoomName.STUDY_ROOM_210, RoomName.CONFERENCE_ROOM_A, RoomName.MEDIA_LAB_1])
    _generic_search_suggestion_test(
        room_name_context, "\t\nMeDIA    ", [RoomName.MEDIA_LAB_1])

    # User Tests
    _generic_search_suggestion_test(
        user_name_context, "\t\nu    ", [UserName.YOU])
    _generic_search_suggestion_test(
        user_name_context, "\t\n   A    ", [UserName.DOLLY_PARTON])
    _generic_search_suggestion_test(
        user_name_context, "You", [UserName.YOU])
    _generic_search_suggestion_test(
        user_name_context, "o", [UserName.YOU, UserName.DOLLY_PARTON])


# Should never be run as main, just for testing search suggestions
if __name__ == "__main__":
    _test_search_suggestion()
