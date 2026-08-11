"""The guardrail loop — evaluate the PLAN before any action executes.

plan -> evaluate trajectory -> decide:
  * APPROVE / APPROVE_WITH_WARNINGS -> execute (dry-run)
  * ESCALATE (an S4: prohibited/over-limit/unjustified/injection) -> human, no execution
  * BLOCK -> feed findings back, replan
  * still blocked after max_attempts -> escalate

This is what turns a trajectory *score* into *control* over what the agent may do.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from support_eval.evaluate import evaluate
from support_eval.llm import LLMClient
from support_eval.models import Ticket, Trajectory, TrajectoryReport

from .agent import SupportAgent


@dataclass
class Decision:
    status: str            # "APPROVED" | "ESCALATED"
    trajectory: Trajectory
    report: TrajectoryReport
    attempts: int
    reason: str = ""
    history: list = field(default_factory=list)


def guardrail_resolve(policy: dict, ticket: Ticket, kb: dict,
                      agent: SupportAgent | None = None, client: LLMClient | None = None,
                      max_attempts: int = 3) -> Decision:
    client = client or LLMClient()
    agent = agent or SupportAgent(client)
    kb_text = " ".join(f"{k}: {v}" for k, v in kb.items())
    history: list = []
    feedback = None
    traj = report = None

    for attempt in range(1, max_attempts + 1):
        traj = agent.plan(ticket, kb, feedback)
        report = evaluate(policy, ticket, traj, kb_text, client=client)
        verdict = report.verdict()
        history.append({"attempt": attempt, "verdict": verdict, "tools": traj.tools(),
                        "failures": [f.rule_id for f in report.failures()]})

        if verdict in ("APPROVE", "APPROVE_WITH_WARNINGS"):
            return Decision("APPROVED", traj, report, attempt, "safe plan", history)
        if verdict == "ESCALATE":
            return Decision("ESCALATED", traj, report, attempt, "critical (S4) failure", history)
        feedback = "; ".join(f"{f.rule_id}: {f.detail}" for f in report.failures())

    return Decision("ESCALATED", traj, report, max_attempts, "unresolved after retries", history)
