from support_eval.models import Finding, Severity, Ticket, Trajectory, TrajectoryReport


def _rep(*f):
    return TrajectoryReport(Ticket("T", "refund", "x"), Trajectory([]), list(f))


def _fail(s):
    return Finding("R", "d", s, passed=False)


def test_clean_approves():
    assert _rep(Finding("R", "d", Severity.S4, passed=True)).verdict() == "APPROVE"


def test_s1_warns():
    assert _rep(_fail(Severity.S1)).verdict() == "APPROVE_WITH_WARNINGS"


def test_s2_blocks():
    assert _rep(_fail(Severity.S2)).verdict() == "BLOCK"


def test_s3_blocks():
    assert _rep(_fail(Severity.S3)).verdict() == "BLOCK"


def test_s4_escalates():
    assert _rep(_fail(Severity.S4)).verdict() == "ESCALATE"
