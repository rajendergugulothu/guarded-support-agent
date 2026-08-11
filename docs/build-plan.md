# Build plan / status

## Done
- ✅ Trajectory compliance pre-filter — deterministic graders (prohibited action,
  refund threshold, **default-deny** least privilege, required prior step) + LLM
  judge (action justified, correct escalation, injection resisted), fail-closed.
- ✅ **Runtime authorization outside the model** — trusted systems (orders /
  customers / refund history / payment / identity) + `authorize()` enforcing
  object-level ownership, payment, prior-refund, eligibility, cap, and identity-
  verification *result*. Holds even if the model is compromised.
- ✅ **Stepwise authorized executor** — prerequisites' results gate later actions.
- ✅ Support agent (mock + real planner), guardrail control loop.
- ✅ Evaluation suite that *executes* plans through authorization; reports
  unauthorized-execution rate, unsafe-approval rate, false-positive rate; held-out
  `--split` (dev/test) supported.
- ✅ Real LLM planner + judge run measured (sonnet-4-5); numbers published via `make publish`.
- ✅ 35 unit tests (verdict, deterministic, judge, judge-contract, authorizer,
  executor, guardrail) + GitHub Actions CI.
- ✅ Cumulative cost accounting; hardened response parser.

## Next (deferred, scoped)
- ⏳ Expand the dataset toward 100–200 natural-language cases (encoded/indirect
  injection, retrieved-content injection, multi-turn, more benign edge cases).
- ⏳ Human-labeled gold set (30–50) to calibrate the LLM judge (measure agreement).
- ⏳ Post-deployment-style monitoring: override rate, retries, drift by category,
  model/policy version.
- ⏳ Real ticketing/CRM integration and real order/identity service clients.

## Reuse from Project A (Compliant AI SDR)
Same harness pattern (deterministic + judge + fail-closed), extended from text
compliance to **action/trajectory compliance and runtime authorization**.
