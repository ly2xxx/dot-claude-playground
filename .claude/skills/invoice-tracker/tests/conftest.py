"""Shared fixtures for BDD tests."""

import asyncio
import pytest
from typing import Dict, Any

@pytest.fixture(scope="session", autouse=True)
def setup_event_loop():
    """Setup event loop to avoid deepeval's asyncio.get_event_loop deprecation warning."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()

@pytest.fixture
def scenario_ctx() -> Dict[str, Any]:
    """Per-scenario mutable bag for sharing state between steps."""
    return {}
