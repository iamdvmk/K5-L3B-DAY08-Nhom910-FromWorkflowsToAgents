"""Shape C integration checks for handoff and early-return trace contracts."""

import json
from pathlib import Path

import pytest

from lab8.db import connect
from lab8.shapes.orchestrator import run_claim


def test_orchestrator_handoff_contains_only_safe_read_capabilities(public_db, tmp_path, monkeypatch, capsys):
    # Catch forwarding parent context or granting a writer in the actual handoff.
    monkeypatch.chdir(tmp_path)
    result = run_claim("C-010", seed=11, store_path=str(public_db))
    body = json.loads(Path(result.trace_path).read_text(encoding="utf-8"))
    handoffs = [event["payload"] for event in body["events"] if event["kind"] == "handoff"]
    assert len(handoffs) == 1
    handoff = handoffs[0]
    assert set(handoff) <= {
        "contract_version", "request_id", "claim_id", "principal_scope",
        "task", "facts", "allowed_tools", "max_output_tokens",
    }
    assert handoff["claim_id"] == "C-010"
    assert handoff["principal_scope"] == "owner_order_only"
    assert handoff["allowed_tools"]
    assert set(handoff["allowed_tools"]) <= {
        "get_claim_view", "lookup_order", "lookup_policy",
        "lookup_refund_history", "get_clause", "compute_compensation",
    }
    assert set(handoff["facts"]) <= {
        "delay_days", "damage_verified", "carrier", "order_status",
        "shipping_fee_vnd", "paid_vnd",
    }
    captured = capsys.readouterr()
    blob = json.dumps(body) + captured.out + captured.err
    for forbidden in ("CANARY_SECRET_", "parent_secret", "raw_headers", "Authorization"):
        assert forbidden not in blob


@pytest.mark.parametrize(
    "case,claim_id,status,reason",
    [
        ("unknown", "C-DOES-NOT-EXIST", "failed", "unknown_claim"),
        ("missing_order", "C-001", "needs_info", "missing_order_id"),
        ("other_owner", "C-001", "escalated", "outside_principal_scope"),
    ],
)
def test_orchestrator_early_return_replaces_stale_trace(
    public_db, tmp_path, monkeypatch, case, claim_id, status, reason,
):
    # Catch an early return that skips finish(), reuses old trace, or writes money.
    monkeypatch.chdir(tmp_path)
    conn = connect(public_db)
    try:
        if case == "missing_order":
            conn.execute("UPDATE claims SET order_id=NULL WHERE claim_id=?", (claim_id,))
        elif case == "other_owner":
            conn.execute("UPDATE claims SET principal_id='P-NOT-OWNER' WHERE claim_id=?", (claim_id,))
        conn.commit()
        before = conn.execute("SELECT COUNT(*) FROM refund_ledger").fetchone()[0]
    finally:
        conn.close()

    run_id = f"R-orchestrator-{claim_id}-s11"
    trace_path = Path("traces") / f"{run_id}.json"
    trace_path.parent.mkdir()
    trace_path.write_text('{"run_id":"stale","events":[]}', encoding="utf-8")

    result = run_claim(claim_id, seed=11, store_path=str(public_db))
    assert result.status == status
    assert result.error_reason == reason
    assert result.proposal_amount == 0
    assert result.refund_effects == []
    assert result.committed_audit_count == 0
    body = json.loads(Path(result.trace_path).read_text(encoding="utf-8"))
    assert result.run_id == body["run_id"] == run_id
    assert isinstance(body["events"], list) and body["events"]
    conn = connect(public_db)
    try:
        assert conn.execute("SELECT COUNT(*) FROM refund_ledger").fetchone()[0] == before
    finally:
        conn.close()
