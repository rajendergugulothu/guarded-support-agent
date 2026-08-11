"""End-to-end: for each ticket, plan -> guardrail -> execute (dry-run) or escalate.

Writes runs/runs.jsonl. An APPROVED plan whose only action is `escalate` is counted
as a human hand-off, not an autonomous resolution.

Usage:
    python -m support_agent.pipeline
    SDR_ENV=prod python -m support_agent.pipeline        # fail-closed
    ANTHROPIC_API_KEY=... python -m support_agent.pipeline
"""
from __future__ import annotations

import json
import os

from support_eval.llm import LLMClient
from support_eval.models import Ticket
from support_eval.policy import load_policy

from .guardrail import guardrail_resolve
from .tools import execute

RUN_LOG = "runs/runs.jsonl"


def _load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def run(tickets_path="data/tickets.json", kb_path="config/kb.json",
        policy_path="policies/support-policy.json") -> list:
    policy = load_policy(policy_path)
    kb = _load(kb_path)
    tickets = [Ticket.from_dict(d) for d in _load(tickets_path)]
    client = LLMClient()

    os.makedirs("runs", exist_ok=True)
    open(RUN_LOG, "w").close()
    print(f"LLM backend: {client.name} | env: {os.environ.get('SDR_ENV','dev')}\n" + "=" * 74)

    records = []
    for t in tickets:
        d = guardrail_resolve(policy, t, kb, client=client)
        self_escalated = "escalate" in d.trajectory.tools()

        if d.status == "APPROVED" and not self_escalated:
            execute(d.trajectory)                       # dry-run tools
            outcome = "AUTO-RESOLVED"
        else:
            outcome = "ESCALATED"

        rec = {"ticket": t.id, "category": t.category, "status": d.status, "outcome": outcome,
               "attempts": d.attempts, "reason": d.reason, "verdict": d.report.verdict(),
               "plan": d.trajectory.tools(),
               "failures": [f.rule_id for f in d.report.failures()], "history": d.history}
        records.append(rec)
        with open(RUN_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")

        print(f"{t.id}  {t.category:<12} {outcome:<13} plan={d.trajectory.tools()}")
        if outcome == "ESCALATED":
            print(f"     reason: {d.reason}; failures: {rec['failures']}")

    print("=" * 74)
    print(f"Wrote {len(records)} records to {RUN_LOG}")
    return records


if __name__ == "__main__":
    run()
