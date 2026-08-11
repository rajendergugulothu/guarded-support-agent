# Case study — Guarded Support Agent

## Problem
An action-taking support agent can issue refunds, change accounts, and touch
sensitive data. The goal: autonomy on safe tickets, and a guarantee that no
unauthorized or unverified action executes — evaluated at the level of the agent's
*plan of actions*, not its final message.

## Approach
The agent proposes a trajectory of tool calls. A hybrid harness (deterministic
rules + LLM judge) evaluates the plan; a control loop executes, revises, or
escalates it; a dry-run tool layer means nothing has real side effects during testing.

## Methodology
- **Dataset:** 24 labeled tickets — 14 adversarial across over-limit refund,
  prohibited action, prompt injection (big and small), wrong-privilege,
  missing-context, and unjustified-action categories; plus benign resolvable
  tickets and benign tickets whose correct outcome is escalation (cancellations)
  and a boundary case (refund exactly at the cap).
- **Scoring:** each ticket runs through the full guardrail loop; the outcome is
  auto-resolved or escalated, and any executed state-changing action is recorded.

## Metric definitions
- **Unauthorized-action rate** — adversarial tickets that auto-resolved while
  executing a state-changing action (refund / account change / deletion). Target 0.
- **Violation catch rate** — adversarial tickets correctly escalated.
- **False-positive rate** — resolve-expected tickets wrongly escalated.

## Results

**Deterministic-only baseline (naive agent, no judge — measured, 20 tickets):**

| Metric | Value |
|---|---|
| Unauthorized-action execution rate | 0.0% (0/13) |
| Unsafe-action approval rate (caught by runtime authz) | 46.2% (6/13) |
| False-positive rate | 0.0% |

The safety guarantee does not depend on the model: even a naive agent with no judge
executes **zero** unauthorized actions, because runtime authorization checks each
state change against trusted systems (ownership, payment, prior-refund, eligibility,
cap, identity result). The 46.2% is the share of adversarial actions the rules/judge
alone approved — they can't see ownership or payment state — that runtime
authorization independently denied. That is defense in depth: agent + rules + judge
+ authorization, with authorization as the layer that holds even if the model is
fully compromised.

**Deterministic + LLM judge:**

<!-- EVAL:START -->
_Pending measurement._ Run `ANTHROPIC_API_KEY=… make suite && make publish`; the
block fills automatically with catch rate, attack-success, unauthorized-action
rate, false-positive rate, latency, and cost. (No expected number is published
before it is measured.)
<!-- EVAL:END -->

**Fail-closed:** in prod, an unavailable judge escalates every semantically-gated
plan rather than acting — unauthorized-action rate 0 at the cost of more escalations.

## Limitations & next
- With-judge numbers pending a real-key run.
- Static KB and simulated tools; next is real retrieval + a Zendesk/Intercom integration.
