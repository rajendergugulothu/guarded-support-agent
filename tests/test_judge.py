from support_eval.judge import run_judge
from support_eval.models import Ticket, ToolCall, Trajectory

T = Ticket("T", "refund", "refund", order_id="O1", amount=30)
TR = Trajectory([ToolCall("issue_refund", {"order_id": "O1", "amount": 30})])


def test_judge_dev_fail_open(policy, mock_client):
    findings = run_judge(policy, T, TR, "", client=mock_client, fail_closed=False)
    assert findings and all(f.passed for f in findings)


def test_judge_prod_fail_closed(policy, mock_client):
    findings = run_judge(policy, T, TR, "", client=mock_client, fail_closed=True)
    assert findings and all(not f.passed for f in findings)
