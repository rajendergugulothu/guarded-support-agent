# Project spec — Guarded Support Agent

## Problem
An AI agent that resolves support tickets by taking actions (refunds, account
changes) can cause real financial and security harm if a single decision is
manipulated, ungrounded, or over its authority. The product must let the agent act
autonomously on safe tickets while making unauthorized actions impossible to
execute.

## Users
Support / operations teams deploying action-taking AI agents, plus the risk and
compliance owners who must trust that autonomy.

## The core idea — trajectory evaluation
The unit of evaluation is the **plan of tool actions**, not the final message. The
agent proposes a trajectory (ordered tool calls + reply); the harness evaluates it
before any tool executes.

## Policy (v0.1)
- `auto_refund_max`: refunds above the cap must escalate, not auto-execute.
- `prohibited_actions`: delete_account, disable_security, export_all_data — never autonomous.
- `allowed_actions_by_category`: least privilege per ticket type.
- `require_prior_step`: identity verification must precede an account change.
- Judge rules (semantic): action justified by ticket+KB; correct escalation; injection resisted.

## Decision mapping
S4 (prohibited / over-limit / unjustified / injection) → **ESCALATE**; S2–S3 →
**BLOCK** (revise the plan); none → **APPROVE** (execute). Fail-closed in prod.

## Metrics
- **Unauthorized-action rate** (headline safety metric): a state-changing action
  executed on a ticket that should have escalated. Target 0.
- Violation catch rate, attack-success rate, false-positive rate, auto-resolution
  rate, latency, cost.

## Non-goals
Not a ticketing product; not legal compliance certification; not a replacement for
human judgment on high-risk actions.
