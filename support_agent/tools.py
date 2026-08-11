"""Stepwise, authorized tool execution.

Actions execute one step at a time. Read tools fetch trusted evidence;
`verify_identity` produces a RESULT that gates later steps; every state-changing
action is checked by runtime `authorize()` against the trusted systems before it
runs. A denied action does NOT execute and halts further state changes.

This is where "authorization outside the model" actually bites: even a plan that
passed the pre-filter cannot perform an unauthorized state change here.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from support_eval.models import Trajectory
from support_eval.systems import TrustedSystems

from .authorize import STATE_CHANGING, authorize

READ_TOOLS = {"get_order", "get_customer", "get_refund_history", "get_payment_status"}


@dataclass
class ExecResult:
    executed: list = field(default_factory=list)     # state-changing tools that actually ran
    denied: list = field(default_factory=list)       # (tool, reason) blocked by runtime authorization
    context: dict = field(default_factory=dict)
    log: list = field(default_factory=list)

    @property
    def had_denial(self) -> bool:
        return bool(self.denied)


def execute(ticket, traj: Trajectory, systems: TrustedSystems | None = None) -> ExecResult:
    systems = systems or TrustedSystems()
    ctx: dict = {"identity_verified": False, "evidence": {}}
    res = ExecResult(context=ctx)

    for step in traj.steps:
        tool, args = step.tool, step.args

        if tool in READ_TOOLS:
            fetch = {
                "get_order": lambda: systems.get_order(args.get("order_id", "")),
                "get_customer": lambda: systems.get_customer(args.get("customer_id", ticket.customer.id)),
                "get_refund_history": lambda: systems.get_refund_history(args.get("order_id", "")),
                "get_payment_status": lambda: systems.get_payment_status(args.get("order_id", "")),
            }[tool]()
            ctx["evidence"][tool] = fetch
            step.result = f"evidence: {fetch}"
            res.log.append((tool, "read"))
            continue

        if tool == "verify_identity":
            outcome = systems.verify_identity(ticket.customer.id, ticket.provided_identity)
            ctx["identity_verified"] = outcome["verified"]
            step.result = f"verify_identity -> {outcome}"
            res.log.append((tool, "verified" if outcome["verified"] else "NOT verified"))
            continue

        if tool in STATE_CHANGING:
            decision = authorize(ticket, systems, step, ctx)
            if decision.allowed:
                if tool == "issue_refund":
                    systems.mark_refunded(args.get("order_id", ""))   # idempotent side effect
                step.result = f"executed: {tool}"
                res.executed.append(tool)
                res.log.append((tool, "executed"))
            else:
                step.result = f"DENIED: {decision.reason}"
                res.denied.append((tool, decision.reason))
                res.log.append((tool, f"denied: {decision.reason}"))
                break   # fail-safe: stop the plan on a denied state change
            continue

        # respond / escalate / anything else — no side effects
        step.result = f"{tool}: {args.get('text') or args.get('reason') or ''}"
        res.log.append((tool, "ok"))

    return res
