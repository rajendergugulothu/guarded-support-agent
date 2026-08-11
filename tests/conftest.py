import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from support_eval.llm import LLMClient, MockBackend  # noqa: E402
from support_eval.policy import load_policy  # noqa: E402


@pytest.fixture
def policy():
    return load_policy(os.path.join(ROOT, "policies", "support-policy.json"))


@pytest.fixture
def kb():
    with open(os.path.join(ROOT, "config", "kb.json"), encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def mock_client():
    return LLMClient(backend=MockBackend())
