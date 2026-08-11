# Build plan / status

## Done
- ✅ Trajectory compliance harness — deterministic graders (prohibited action,
  refund threshold, least privilege, required prior step, action context) + LLM
  judge (action justified, correct escalation, injection resisted), fail-closed.
- ✅ Support agent (mock + real planner), simulated dry-run tools.
- ✅ Guardrail control loop — approve / revise / escalate over the plan.
- ✅ Pipeline + operational metrics (unauthorized-action rate is the headline).
- ✅ Trajectory evaluation suite — 24 labeled tickets, per-category catch rate.
- ✅ Unit tests (18) + GitHub Actions CI.
- ✅ `make publish` — fills real judge numbers into the docs.

## Pending (needs your key / accounts)
- ⏳ Real LLM judge + planner run (`ANTHROPIC_API_KEY`) to publish the with-judge numbers.
- ⏳ Real knowledge-base retrieval (currently a static KB dict).
- ⏳ Live ticketing/CRM integration (Zendesk/Intercom) and real action tools.
- ⏳ Hosted endpoint for a webhook-driven flow.

## Reuse from Project A (Compliant AI SDR)
Same harness pattern (deterministic + judge + fail-closed), guardrail loop, eval-suite
machinery, tests/CI, and publish script — extended from text compliance to
**trajectory/action** compliance.
