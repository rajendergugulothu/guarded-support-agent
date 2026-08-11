"""Runtime authorization: object-level, evidence-based, verification-result-based."""
from support_agent.authorize import authorize
from support_eval.models import Customer, Ticket, ToolCall
from support_eval.systems import TrustedSystems


def _t(cid, order_id="", amount=0.0, provided=""):
    return Ticket("T", "refund", "refund", order_id=order_id, amount=amount,
                  provided_identity=provided, customer=Customer(cid))


def _refund(order_id, amount):
    return ToolCall("issue_refund", {"order_id": order_id, "amount": amount})


def test_valid_refund_allowed():
    s = TrustedSystems()
    assert authorize(_t("C-1", "ORD-5", 30), s, _refund("ORD-5", 30), {}).allowed


def test_cross_customer_refund_denied():
    s = TrustedSystems()
    # ORD-OTHER belongs to C-999; C-1 must not be able to refund it
    r = authorize(_t("C-1", "ORD-OTHER", 40), s, _refund("ORD-OTHER", 40), {})
    assert not r.allowed and "belong" in r.reason


def test_already_refunded_denied():
    s = TrustedSystems()
    assert not authorize(_t("C-1", "ORD-AR", 25), s, _refund("ORD-AR", 25), {}).allowed


def test_unpaid_order_denied():
    s = TrustedSystems()
    assert not authorize(_t("C-1", "ORD-UNPAID", 40), s, _refund("ORD-UNPAID", 40), {}).allowed


def test_over_cap_denied():
    s = TrustedSystems()
    assert not authorize(_t("C-3", "ORD-77", 800), s, _refund("ORD-77", 800), {}).allowed


def test_ineligible_reason_denied():
    s = TrustedSystems()
    assert not authorize(_t("C-1", "ORD-CM", 30), s, _refund("ORD-CM", 30), {}).allowed


def test_update_account_requires_verified_result():
    s = TrustedSystems()
    call = ToolCall("update_account", {"field": "email", "value": "x"})
    assert not authorize(_t("C-2"), s, call, {"identity_verified": False}).allowed
    assert authorize(_t("C-2"), s, call, {"identity_verified": True}).allowed


def test_prohibited_denied():
    s = TrustedSystems()
    assert not authorize(_t("C-5"), s, ToolCall("delete_account", {}), {}).allowed
