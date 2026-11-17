"""Regression checks for single-agent crash tracing and resume."""

import json
from pathlib import Path

import pytest

from lab8.db import connect
from lab8.durability import InjectedCrash
from lab8.schemas import make_run_id
from lab8.shapes.single import run_claim


@pytest.mark.parametrize(
    "crash_at",
    ["before_effect", "after_effect_before_checkpoint", "after_checkpoint"],
)
def test_single_crash_persists_trace_before_resume(public_db, tmp_path, monkeypatch, crash_at):
    # Isolate traces so an earlier run cannot satisfy the existence check.
    monkeypatch.chdir(tmp_path)
    claim_id = "C-012"
    run_id = make_run_id("single", claim_id, 11)
    trace_path = Path("traces") / f"{run_id}.json"

    with pytest.raises(InjectedCrash, match=crash_at):
        run_claim(claim_id, seed=11, store_path=str(public_db), crash_at=crash_at)

    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    assert trace["run_id"] == run_id
    assert trace["events"][-1] == {
        "kind": "refund_attempt",
        "payload": {"proposal_amount": 35000, "crash_at": crash_at},
    }

    conn = connect(public_db)
    try:
        count = conn.execute(
            "SELECT COUNT(*) FROM refund_ledger WHERE claim_id = ?", (claim_id,)
        ).fetchone()[0]
        assert count == (0 if crash_at == "before_effect" else 1)
    finally:
        conn.close()

    for _ in range(2):
        result = run_claim(claim_id, seed=11, store_path=str(public_db))
        assert result.status == "resolved"
        assert result.proposal_amount == 35000
        assert len(result.refund_effects) == 1
        assert result.refund_effects[0]["amount_vnd"] == 35000
        assert result.committed_audit_count == 1

    conn = connect(public_db)
    try:
        count = conn.execute(
            "SELECT COUNT(*) FROM refund_ledger WHERE claim_id = ?", (claim_id,)
        ).fetchone()[0]
        assert count == 1
    finally:
        conn.close()
