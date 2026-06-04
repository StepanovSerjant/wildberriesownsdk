from wildberriesownsdk.core.http import log_response


def test_log_response_with_invalid_json(invalid_json) -> None:
    response = ...
    assert log_response(response) is None
