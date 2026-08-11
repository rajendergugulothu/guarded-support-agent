"""Contract tests for the LLM-judge parsing/mapping, using a fake backend that
returns controlled responses — so the real parsing logic is tested deterministically
without spending API money."""
from support_eval.judge import run_judge
from support_eval.llm import LLMClient
from support_eval.models import Customer, Ticket, ToolCall, Trajectory

T = Ticket("T", "refund", "refund", order_id="ORD-5", amount=30, customer=Customer("C-1"))
TR = Trajectory([ToolCall("issue_refund", {"order_id": "ORD-5", "amount": 30})])


class FakeBackend:
    name = "fake"
    model = "fake"
    last_latency = 0.0
    last_usage = None
    total_cost = 0.0
    calls = 0

    def __init__(self, response):
        self._response = response

    def complete(self, system, user):
        return self._response


def _judge(policy, response, fail_closed=False):
    return run_judge(policy, T, TR, "", client=LLMClient(backend=FakeBackend(response)),
                     fail_closed=fail_closed)


def test_all_pass(policy):
    resp = '[{"rule_id":"ACTION_JUSTIFIED","passed":true},{"rule_id":"CORRECT_ESCALATION","passed":true},{"rule_id":"INJECTION_RESISTED","passed":true}]'
    assert all(f.passed for f in _judge(policy, resp))


def test_one_fail(policy):
    resp = '[{"rule_id":"ACTION_JUSTIFIED","passed":false,"detail":"unjustified"}]'
    findings = _judge(policy, resp)
    assert any(f.rule_id == "ACTION_JUSTIFIED" and not f.passed for f in findings)


def test_missing_rule_defaults_failsafe(policy):
    # a rule absent from the judge's reply must NOT default to pass
    resp = '[{"rule_id":"ACTION_JUSTIFIED","passed":true}]'
    findings = {f.rule_id: f for f in _judge(policy, resp)}
    assert findings["CORRECT_ESCALATION"].passed is False


def test_markdown_fenced_json_parses(policy):
    resp = '```json\n[{"rule_id":"ACTION_JUSTIFIED","passed":true},{"rule_id":"CORRECT_ESCALATION","passed":true},{"rule_id":"INJECTION_RESISTED","passed":true}]\n```'
    assert all(f.passed for f in _judge(policy, resp))


def test_malformed_json_fails_closed_in_prod(policy):
    findings = _judge(policy, "not json at all", fail_closed=True)
    assert findings and all(not f.passed for f in findings)
