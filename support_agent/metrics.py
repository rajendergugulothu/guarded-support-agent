"""Operational metrics from the run log.

Key safety metric: UNAUTHORIZED-ACTION RATE — how often an auto-resolved
(executed) plan contained a prohibited action, an over-limit refund, or a
least-privilege / missing-approval violation. Target: 0.

Usage: python -m support_agent.metrics
"""
from __future__ import annotations

import json
import os
from collections import Counter

RUN_LOG = "runs/runs.jsonl"
UNSAFE_RULES = {"PROHIBITED_ACTION", "REFUND_LIMIT", "LEAST_PRIVILEGE", "REQUIRED_PRIOR_STEP"}


def load(path=RUN_LOG):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(x) for x in f if x.strip()]


def report(path=RUN_LOG) -> None:
    runs = load(path)
    if not runs:
        print("No runs. Run: python -m support_agent.pipeline")
        return
    total = len(runs)
    resolved = [r for r in runs if r["outcome"] == "AUTO-RESOLVED"]
    escalated = [r for r in runs if r["outcome"] == "ESCALATED"]
    # an executed plan that still carried an unsafe finding = an unauthorized action
    unauthorized = [r for r in resolved if set(r["failures"]) & UNSAFE_RULES]
    reasons = Counter()
    for r in runs:
        for h in r.get("history", []):
            for rule in h.get("failures", []):
                reasons[rule] += 1

    def pct(n):
        return f"{100*n/total:.0f}%"

    print("=" * 60)
    print("GUARDED SUPPORT AGENT — OPERATIONAL METRICS")
    print("=" * 60)
    print(f"Tickets ...................... {total}")
    print(f"Auto-resolved ................ {len(resolved)}  ({pct(len(resolved))})")
    print(f"Escalated to human ........... {len(escalated)}  ({pct(len(escalated))})")
    print(f"Unauthorized actions executed  {len(unauthorized)}  (target 0)")
    print("-" * 60)
    print("Policy violations caught (across attempts):")
    for rule, n in reasons.most_common():
        print(f"   {rule:<22} {n}")
    print("=" * 60)


if __name__ == "__main__":
    report()
