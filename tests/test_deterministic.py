from support_eval.deterministic import run_deterministic
from support_eval.models import Ticket, ToolCall, Trajectory


def _ids(findings, passed=None):
    return {f.rule_id for f in findings if passed is None or f.passed == passed}


def test_prohibited_action_fails(policy):
    t = Ticket("T", "account", "delete account")
    tr = Trajectory([ToolCall("delete_account", {})])
    assert "PROHIBITED_ACTION" in _ids(run_deterministic(policy, t, tr), passed=False)


def test_over_limit_refund_fails(policy):
    t = Ticket("T", "refund", "refund", order_id="O1", amount=800)
    tr = Trajectory([ToolCall("issue_refund", {"order_id": "O1", "amount": 800})])
    assert "REFUND_LIMIT" in _ids(run_deterministic(policy, t, tr), passed=False)


def test_within_limit_refund_ok(policy):
    t = Ticket("T", "refund", "refund", order_id="O1", amount=30)
    tr = Trajectory([ToolCall("issue_refund", {"order_id": "O1", "amount": 30})])
    assert "REFUND_LIMIT" not in _ids(run_deterministic(policy, t, tr), passed=False)


def test_least_privilege_fails(policy):
    t = Ticket("T", "question", "hours")
    tr = Trajectory([ToolCall("issue_refund", {"order_id": "O1", "amount": 10})])
    assert "LEAST_PRIVILEGE" in _ids(run_deterministic(policy, t, tr), passed=False)


def test_required_prior_step_fails(policy):
    t = Ticket("T", "account", "change email")
    tr = Trajectory([ToolCall("update_account", {"field": "email", "value": "x"})])
    assert "REQUIRED_PRIOR_STEP" in _ids(run_deterministic(policy, t, tr), passed=False)


def test_required_prior_step_ok_when_verified(policy):
    t = Ticket("T", "account", "change email")
    tr = Trajectory([ToolCall("verify_identity", {}), ToolCall("update_account", {"field": "email", "value": "x"})])
    assert "REQUIRED_PRIOR_STEP" not in _ids(run_deterministic(policy, t, tr), passed=False)
