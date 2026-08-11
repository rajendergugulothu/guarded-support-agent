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

**Deterministic-only baseline (measured, 24 tickets):**

| Metric | Value |
|---|---|
| Unauthorized-action rate (harm executed) | 14.3% (2/14) |
| False-positive rate | 0.0% |

Deterministic rules catch every structural attack (over-limit refund, prohibited
action, injected refund, missing verification, wrong privilege). The residual
harm is semantic misuse — a structurally valid refund with no legitimate reason —
which only the LLM judge can catch. Note that with the *real* LLM planner the agent
also neutralizes many injections by simply ignoring them (answering the legitimate
request and taking no harmful action), so the safety story is defense-in-depth:
deterministic rules + a judge + an agent that resists manipulation.

**Deterministic + LLM judge:**

<!-- EVAL:START -->
Measured with **claude-sonnet-4-5-20250929** over 24 tickets (14 adversarial):

| Metric | Deterministic + LLM judge |
|---|---|
| **Unauthorized-action rate (harm executed)** | **0.0%** |
| Adversarial escalated to a human | 71.4% |
| Adversarial safely auto-resolved (no harm) | 28.6% |
| False-positive rate | 25.0% |
| Latency / ticket | 9558 ms |
| Cost / ticket | $0.00562 |

_Generated from `eval_suite/results.json` by `make publish`._
<!-- EVAL:END -->

**Fail-closed:** in prod, an unavailable judge escalates every semantically-gated
plan rather than acting — unauthorized-action rate 0 at the cost of more escalations.

## Limitations & next
- With-judge numbers pending a real-key run.
- Static KB and simulated tools; next is real retrieval + a Zendesk/Intercom integration.
