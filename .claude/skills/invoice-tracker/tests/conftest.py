"""Shared fixtures for BDD tests."""

import pytest
from typing import Dict, Any

@pytest.fixture
def scenario_ctx() -> Dict[str, Any]:
    """Per-scenario mutable bag for sharing state between steps."""
    return {}
