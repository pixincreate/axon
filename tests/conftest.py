import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_router import compile_patterns, load_config


@pytest.fixture(scope="session", autouse=True)
def setup_config():
    config = load_config()
    compile_patterns(config)
