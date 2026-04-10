import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_router import load_config, compile_patterns


@pytest.fixture(scope="session", autouse=True)
def setup_config():
    config = load_config()
    compile_patterns(config)
