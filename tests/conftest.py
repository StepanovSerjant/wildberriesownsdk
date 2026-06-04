from typing import Dict

import pytest


@pytest.fixture
def invalid_json() -> Dict[int, str]:
    return {1: "string"}
