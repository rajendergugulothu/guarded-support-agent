"""Combine deterministic + judge findings into one TrajectoryReport."""
from __future__ import annotations

from .deterministic import run_deterministic
from .judge import run_judge
from .llm import LLMClient
from .models import Ticket, Trajectory, TrajectoryReport


def evaluate(policy: dict, ticket: Ticket, traj: Trajectory, kb: str = "",
             client: LLMClient | None = None, fail_closed: bool | None = None) -> TrajectoryReport:
    findings = (
        run_deterministic(policy, ticket, traj)
        + run_judge(policy, ticket, traj, kb, client=client, fail_closed=fail_closed)
    )
    return TrajectoryReport(ticket=ticket, trajectory=traj, findings=findings)
