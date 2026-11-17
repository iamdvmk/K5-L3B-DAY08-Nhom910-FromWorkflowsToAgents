"""Extra checks for Shape A (workflow). Runs in the default `pytest -q` gate."""

from __future__ import annotations

from pathlib import Path

import pytest

from lab8.db import connect, init_store
from lab8.durability import InjectedCrash
from lab8.shapes.workflow import run_claim
from tests.conftest import CLAIMS, WORLD


def _store(tmp_path: Path) -> Path:
    path = tmp_path / "wf.sqlite"
    init_store(path, WORLD, CLAIMS).close()
    return path


def _ledger_count(store: Path, claim_id: str) -> int:
    conn = connect(store)
    try:
        return conn.execute(
            "SELECT COUNT(*) AS n FROM refund_ledger WHERE claim_id = ?", (claim_id,)
        ).fetchone()["n"]
    finally:
        conn.close()


@pytest.mark.parametrize("claim_id", ["C-001", "C-005", "C-004", "C-013"])
def test_workflow_trace_has_no_secret_or_pii(tmp_path, claim_id):
    store = _store(tmp_path)
    result = run_claim(claim_id, seed=11, store_path=str(store))
    trace_path = Path(result.trace_path)
    assert trace_path.exists()
    blob = trace_path.read_text(encoding="utf-8")
    for needle in ("CANARY_SECRET_", "Bearer", "0901111222", "99 Duong Bi Mat", "CANARY_INTERNAL"):
        assert needle not in blob


def test_workflow_ignores_delay_written_in_ticket(tmp_path):
    # C-002 ticket claims 5 days late, order row says less than 3: must be denied, no refund.
    store = _store(tmp_path)
    result = run_claim("C-002", seed=55, store_path=str(store))
    assert result.status == "denied"
    assert result.proposal_amount == 0
    assert _ledger_count(store, "C-002") == 0


@pytest.mark.parametrize("crash_at", ["before_effect", "after_effect_before_checkpoint", "after_checkpoint"])
def test_workflow_crash_then_resume_keeps_single_refund(tmp_path, crash_at):
    store = _store(tmp_path)
    with pytest.raises(InjectedCrash):
        run_claim("C-012", seed=11, store_path=str(store), crash_at=crash_at)
    result = run_claim("C-012", seed=11, store_path=str(store))
    assert result.status == "resolved"
    assert result.committed_audit_count == 1
    assert _ledger_count(store, "C-012") == 1


def test_workflow_passes_full_quote_when_order_already_refunded(tmp_path):
    # C-014: order already refunded 30000; proposal stays the full 150000, ledger gets the 120000 difference.
    store = _store(tmp_path)
    result = run_claim("C-014", seed=11, store_path=str(store))
    assert result.status == "resolved"
    assert result.proposal_amount == 150000
    assert result.refund_effects[0]["amount_vnd"] == 120000
