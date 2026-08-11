"""Fill the docs with real evaluation numbers from results.json.

Run `make suite` with a real key, then `make publish` (or python -m eval_suite.publish)
to replace the block between <!-- EVAL:START --> and <!-- EVAL:END --> in README.md
and docs/case-study.md. Refuses mock results.
"""
from __future__ import annotations

import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(ROOT, "eval_suite", "results.json")
TARGETS = [os.path.join(ROOT, "README.md"), os.path.join(ROOT, "docs", "case-study.md")]
PAT = re.compile(r"(<!-- EVAL:START -->)(.*?)(<!-- EVAL:END -->)", re.DOTALL)


def _block(r):
    def p(x):
        return f"{x*100:.1f}%" if x is not None else "n/a"
    cost = r.get("cost_per_ticket_usd")
    return (
        "\n"
        f"Measured with **{r.get('model','?')}** over {r.get('n','?')} tickets "
        f"({r.get('attacks','?')} adversarial):\n\n"
        "| Metric | Deterministic + LLM judge |\n|---|---|\n"
        f"| **Unauthorized-action rate (harm executed)** | **{p(r.get('unauthorized_action_rate'))}** |\n"
        f"| Adversarial escalated to a human | {p(r.get('adversarial_escalated_rate'))} |\n"
        f"| Adversarial safely auto-resolved (no harm) | {p(r.get('adversarial_safe_resolved_rate'))} |\n"
        f"| False-positive rate | {p(r.get('false_positive_rate'))} |\n"
        f"| Latency / ticket | {r.get('avg_latency_ms',0):.0f} ms |\n"
        f"| Cost / ticket | {('$'+format(cost,'.5f')) if cost else 'n/a'} |\n\n"
        "_Generated from `eval_suite/results.json` by `make publish`._\n"
    )


def main() -> int:
    if not os.path.exists(RESULTS):
        print("No results.json — run `make suite` first (with ANTHROPIC_API_KEY).")
        return 1
    r = json.load(open(RESULTS, encoding="utf-8"))
    if r.get("backend") == "mock":
        print("Refusing to publish MOCK results. Run `make suite` with ANTHROPIC_API_KEY.")
        return 1
    block = _block(r)
    for path in TARGETS:
        if not os.path.exists(path):
            continue
        text = open(path, encoding="utf-8").read()
        if PAT.search(text):
            open(path, "w", encoding="utf-8").write(PAT.sub(lambda m: m.group(1) + block + m.group(3), text))
            print(f"updated {os.path.basename(path)}")
    print("Done. Review the diff and commit.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
