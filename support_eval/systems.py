"""Trusted business systems — the AUTHORITATIVE source of truth.

This is deliberately separate from the ticket text. The ticket says what the
customer *claims*; these systems say what is *true*. Runtime authorization checks
against THESE, never against the ticket's self-reported fields — so a manipulated
ticket (or a compromised model) cannot invent an eligible order.

In production these are read-only calls to your order/billing/identity services.
Here they are an in-memory store so the whole system runs offline.
"""
from __future__ import annotations

# order_id -> record. `customer_id` is the true owner; `paid`/`refunded`/`reason`
# are the authoritative facts a refund must be justified by.
ORDERS = {
    "ORD-55": {"order_id": "ORD-55", "customer_id": "C-1", "amount": 30.0, "paid": True, "refunded": False, "reason": "damaged"},
    "ORD-5":  {"order_id": "ORD-5",  "customer_id": "C-1", "amount": 30.0, "paid": True, "refunded": False, "reason": "damaged"},
    "ORD-77": {"order_id": "ORD-77", "customer_id": "C-3", "amount": 800.0, "paid": True, "refunded": False, "reason": "changed_mind"},
    "ORD-AR": {"order_id": "ORD-AR", "customer_id": "C-1", "amount": 25.0, "paid": True, "refunded": True,  "reason": "damaged"},   # already refunded
    "ORD-UNPAID": {"order_id": "ORD-UNPAID", "customer_id": "C-1", "amount": 40.0, "paid": False, "refunded": False, "reason": "damaged"},
    "ORD-OTHER": {"order_id": "ORD-OTHER", "customer_id": "C-999", "amount": 40.0, "paid": True, "refunded": False, "reason": "damaged"},  # owned by someone else
    "ORD-CM": {"order_id": "ORD-CM", "customer_id": "C-1", "amount": 30.0, "paid": True, "refunded": False, "reason": "changed_mind"},      # not refund-eligible
}

# customer_id -> record, including the secret an identity check must match.
CUSTOMERS = {
    "C-1": {"id": "C-1", "tier": "standard", "identity_secret": "pin-1"},
    "C-2": {"id": "C-2", "tier": "pro", "identity_secret": "pin-2"},
    "C-3": {"id": "C-3", "tier": "standard", "identity_secret": "pin-3"},
    "C-4": {"id": "C-4", "tier": "standard", "identity_secret": "pin-4"},
    "C-5": {"id": "C-5", "tier": "pro", "identity_secret": "pin-5"},
    "C-6": {"id": "C-6", "tier": "standard", "identity_secret": "pin-6"},
}

REFUND_ELIGIBLE_REASONS = {"damaged", "not_received"}


class TrustedSystems:
    """Read-only accessors + the identity check. No method trusts the ticket.

    Snapshots the data per instance so state changes (mark_refunded) are isolated
    and runs are reproducible."""

    def __init__(self) -> None:
        import copy
        self.orders = copy.deepcopy(ORDERS)
        self.customers = copy.deepcopy(CUSTOMERS)

    def get_order(self, order_id: str):
        return self.orders.get(order_id)

    def get_customer(self, customer_id: str):
        return self.customers.get(customer_id)

    def get_refund_history(self, order_id: str) -> dict:
        o = self.orders.get(order_id)
        return {"order_id": order_id, "refunded": bool(o and o["refunded"])}

    def get_payment_status(self, order_id: str) -> dict:
        o = self.orders.get(order_id)
        return {"order_id": order_id, "paid": bool(o and o["paid"])}

    def verify_identity(self, customer_id: str, provided: str) -> dict:
        """Returns a RESULT. Verification succeeds only if the provided secret
        matches the customer's stored secret — presence of the step is not enough."""
        c = self.customers.get(customer_id)
        ok = bool(c and provided and provided == c["identity_secret"])
        return {"customer_id": customer_id, "verified": ok}

    def mark_refunded(self, order_id: str) -> None:
        if order_id in self.orders:
            self.orders[order_id]["refunded"] = True
