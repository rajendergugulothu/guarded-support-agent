"""Stepwise execution: authorization gates each state change; a denied action
does not execute; verification RESULT (not ordering) gates account updates."""
from support_agent.tools import execute
from support_eval.models import Customer, Ticket, ToolCall, Trajectory
from support_eval.systems import TrustedSystems


def test_valid_refund_executes_and_marks_refunded():
    s = TrustedSystems()
    t = Ticket("T", "refund", "refund", order_id="ORD-5", amount=30, customer=Customer("C-1"))
    tr = Trajectory([ToolCall("issue_refund", {"order_id": "ORD-5", "amount": 30})])
    res = execute(t, tr, s)
    assert res.executed == ["issue_refund"] and not res.denied
    assert s.get_refund_history("ORD-5")["refunded"] is True   # idempotency guard set


def test_cross_customer_refund_not_executed():
    s = TrustedSystems()
    t = Ticket("T", "refund", "refund", order_id="ORD-OTHER", amount=40, customer=Customer("C-1"))
    tr = Trajectory([ToolCall("issue_refund", {"order_id": "ORD-OTHER", "amount": 40})])
    res = execute(t, tr, s)
    assert res.executed == [] and res.denied          # blocked at runtime
    assert s.get_refund_history("ORD-OTHER")["refunded"] is False


def test_account_update_blocked_when_verification_fails():
    s = TrustedSystems()
    # correct verify order, but WRONG provided secret -> verification returns not-verified
    t = Ticket("T", "account", "change email", provided_identity="wrong",
               customer=Customer("C-2"))
    tr = Trajectory([ToolCall("verify_identity", {}),
                     ToolCall("update_account", {"field": "email", "value": "x"})])
    res = execute(t, tr, s)
    assert "update_account" not in res.executed and res.denied   # ordering present, result failed


def test_account_update_executes_when_verified():
    s = TrustedSystems()
    t = Ticket("T", "account", "change email", provided_identity="pin-2",
               customer=Customer("C-2"))
    tr = Trajectory([ToolCall("verify_identity", {}),
                     ToolCall("update_account", {"field": "email", "value": "x"})])
    res = execute(t, tr, s)
    assert res.executed == ["update_account"] and not res.denied
