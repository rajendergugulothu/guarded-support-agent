"""Shared LLM client with mock + Anthropic backends (captures latency + cost).

Set SDR_LLM=mock to force mock. Real backend used when ANTHROPIC_API_KEY is set.
"""
from __future__ import annotations

import os
import time

# Approx USD per 1M tokens (input, output). Override SUPPORT_MODEL for your account's models.
PRICES = {"claude-sonnet-4-5-20250929": (3.0, 15.0), "default": (3.0, 15.0)}
DEFAULT_MODEL = "claude-sonnet-4-5-20250929"


def cost_usd(usage, model: str):
    if usage is None:
        return None
    pin, pout = PRICES.get(model, PRICES["default"])
    it = getattr(usage, "input_tokens", 0) or 0
    ot = getattr(usage, "output_tokens", 0) or 0
    return (it / 1_000_000) * pin + (ot / 1_000_000) * pout


class MockBackend:
    name = "mock"

    def __init__(self):
        self.last_latency = 0.0
        self.last_usage = None
        self.model = "mock"

    def complete(self, system, user):
        return ""


class AnthropicBackend:
    name = "anthropic"

    def __init__(self):
        import anthropic
        self.client = anthropic.Anthropic()
        self.model = os.environ.get("SUPPORT_MODEL", DEFAULT_MODEL)
        self.last_latency = 0.0
        self.last_usage = None

    def complete(self, system, user):
        t0 = time.perf_counter()
        resp = self.client.messages.create(model=self.model, max_tokens=1024, system=system,
                                            messages=[{"role": "user", "content": user}])
        self.last_latency = time.perf_counter() - t0
        self.last_usage = getattr(resp, "usage", None)
        return resp.content[0].text


def _auto_backend():
    mode = os.environ.get("SDR_LLM", "").lower()
    if mode == "mock":
        return MockBackend()
    if mode == "anthropic" or os.environ.get("ANTHROPIC_API_KEY"):
        try:
            return AnthropicBackend()
        except Exception:
            return MockBackend()
    return MockBackend()


class LLMClient:
    def __init__(self, backend=None):
        self.backend = backend or _auto_backend()

    @property
    def is_mock(self):
        return isinstance(self.backend, MockBackend)

    @property
    def name(self):
        return self.backend.name

    @property
    def model(self):
        return getattr(self.backend, "model", "unknown")

    @property
    def last_latency(self):
        return getattr(self.backend, "last_latency", 0.0)

    @property
    def last_cost(self):
        return cost_usd(getattr(self.backend, "last_usage", None), self.model)

    def complete(self, system, user):
        return self.backend.complete(system, user)
