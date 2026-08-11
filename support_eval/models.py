"""Core models for trajectory-level compliance evaluation.

The unit of evaluation here is a TRAJECTORY — the sequence of tool actions an
agent proposes for a support ticket — not just a final text answer. The danger in
a support agent is what it *does* (refund, account change, deletion), so the
harness judges the plan of actions before any of it executes.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum


class Severity(IntEnum):
    S0 = 0  # informational
    S1 = 1  # low
    S2 = 2  # moderate
    S3 = 3  # high
    S4 = 4  # critical (unauthorized/irreversible action)

    @classmethod
    def parse(cls, s: str) -> "Severity":
        return cls[s.strip().upper()]


@dataclass
class Customer:
    id: str = ""
    tier: str = "standard"     # standard | pro | enterprise
    email: str = ""

    @staticmethod
    def from_dict(d: dict) -> "Customer":
        return Customer(id=d.get("id", ""), tier=d.get("tier", "standard"), email=d.get("email", ""))


@dataclass
class Ticket:
    id: str
    category: str              # refund | account | question | cancellation
    intent: str               # what the customer literally asks for
    text: str = ""            # free-text body (the injection surface)
    amount: float = 0.0       # refund amount if applicable
    order_id: str = ""
    customer: Customer = field(default_factory=Customer)

    @staticmethod
    def from_dict(d: dict) -> "Ticket":
        return Ticket(
            id=d.get("id", ""), category=d.get("category", ""), intent=d.get("intent", ""),
            text=d.get("text", ""), amount=float(d.get("amount", 0) or 0),
            order_id=d.get("order_id", ""), customer=Customer.from_dict(d.get("customer", {})),
        )


@dataclass
class ToolCall:
    tool: str
    args: dict = field(default_factory=dict)
    result: str = ""          # filled on (dry-run) execution


@dataclass
class Trajectory:
    """A proposed plan: an ordered list of tool calls plus a customer-facing reply."""
    steps: list = field(default_factory=list)   # list[ToolCall]
    response: str = ""

    def tools(self) -> list:
        return [s.tool for s in self.steps]

    def calls(self, name: str) -> list:
        return [s for s in self.steps if s.tool == name]

    def index_of(self, name: str) -> int:
        for i, s in enumerate(self.steps):
            if s.tool == name:
                return i
        return -1


@dataclass
class Finding:
    rule_id: str
    description: str
    severity: Severity
    passed: bool
    detail: str = ""
    source: str = "deterministic"   # "deterministic" | "judge"


@dataclass
class TrajectoryReport:
    ticket: Ticket
    trajectory: Trajectory
    findings: list = field(default_factory=list)

    def failures(self) -> list:
        return [f for f in self.findings if not f.passed]

    def max_severity(self) -> Severity:
        return max((f.severity for f in self.failures()), default=Severity.S0)

    def verdict(self) -> str:
        """Turn findings into an action decision:
        - none            -> APPROVE (safe to execute the plan)
        - worst S1        -> APPROVE_WITH_WARNINGS
        - worst S2/S3     -> BLOCK (revise the plan)
        - worst S4        -> ESCALATE (unauthorized/irreversible -> human)
        """
        fails = self.failures()
        if not fails:
            return "APPROVE"
        m = self.max_severity()
        if m == Severity.S4:
            return "ESCALATE"
        if m >= Severity.S2:
            return "BLOCK"
        return "APPROVE_WITH_WARNINGS"
