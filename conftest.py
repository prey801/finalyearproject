import os
import pytest


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "heavy: marks tests that load large ML models (deselect with -m 'not heavy')"
    )


def pytest_collection_modifyitems(config, items):
    """
    When TESTING=true is set, automatically skip any test whose module
    triggers a heavy ML import at the point it is first collected.
    This prevents OOM kills in memory-constrained environments.
    """
    if os.environ.get("TESTING") == "true":
        skip_heavy = pytest.mark.skip(reason="Skipping heavy ML test in TESTING mode")
        for item in items:
            if "heavy" in item.keywords:
                item.add_marker(skip_heavy)
