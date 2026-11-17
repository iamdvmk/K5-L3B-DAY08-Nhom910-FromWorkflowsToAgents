"""
Hai lớp test:
- Host (chạy trong cổng `python -m pytest -q`, luôn xanh): chứng minh vì sao shape
  phải truyền quote đầy đủ và host chặn approval sai claim.
- Shape (marker `student`, chạy bằng `-m student -o addopts=`): mọi điểm crash trên
  shape nhóm viết đều chỉ ra một refund; trace và kết quả không lộ secret/PII.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from lab8.db import connect, init_store
from lab8.durability import InjectedCrash, committed_audit_count, get_refund, issue_refund
from lab8.shapes import SHAPES
from tests.conftest import CLAIMS, WORLD

TEAM_SHAPES = ["workflow", "single", "orchestrator", "swarm"]  # swarm = đối chứng, phải xanh ngay
CRASH_POINTS = ["before_effect", "after_effect_before_checkpoint", "after_checkpoint"]


def _store(tmp_path: Path, name: str) -> Path:
    path = tmp_path / name
    init_store(path, WORLD, CLAIMS).close()
    return path


def _audit_reasons(conn, claim_id: str) -> list[str]:
    rows = conn.execute(
        "SELECT details_json FROM audit_events WHERE claim_id = ? AND event_type = 'policy_denied'",
        (claim_id,),
    ).fetchall()
    return [json.loads(r["details_json"])["reason"] for r in rows]


# ---------- Host: luôn xanh ----------

def test_full_quote_pays_difference_but_pre_subtracted_quote_underpays(tmp_path):
    """T14: truyền quote đầy đủ 150.000 -> host trả 120.000.
    Nếu shape tự trừ 30.000 trước (truyền 120.000) thì host trừ lần nữa -> chỉ 90.000."""
    good = connect(_store(tmp_path, "good.sqlite"))
    assert issue_refund(good, "C-014", 150000)["effect"]["amount_vnd"] == 120000
    good.close()

    bad = connect(_store(tmp_path, "bad.sqlite"))
    assert issue_refund(bad, "C-014", 120000)["effect"]["amount_vnd"] == 90000
    bad.close()


def test_order_already_refunded_is_denied_with_audit(public_db):
    conn = connect(public_db)
    result = issue_refund(conn, "C-013", 35000)
    assert result["ok"] is False and result["reason"] == "order_already_refunded"
    assert get_refund(conn, "C-013") is None
    assert "order_already_refunded" in _audit_reasons(conn, "C-013")
    conn.close()


def test_borrowed_approval_from_other_claim_is_blocked(public_db):
    """Claim trỏ tới approval A-001 vốn cấp cho C-001 -> approval_claim_mismatch."""
    conn = connect(public_db)
    conn.execute(
        """
        INSERT INTO claims (claim_id, principal_id, order_id, ticket, parent_secret, raw_headers_json, approval_id)
        VALUES ('C-BORROW', 'P-100', 'O-107', 'dùng approval của claim khác', 'CANARY_SECRET_PARENT_BORROW', '{}', 'A-001')
        """
    )
    conn.commit()
    first = issue_refund(conn, "C-BORROW", 35000)
    second = issue_refund(conn, "C-BORROW", 35000)
    assert not first["ok"] and not second["ok"]
    assert get_refund(conn, "C-BORROW") is None
    assert committed_audit_count(conn, "C-BORROW") == 0
    assert "approval_claim_mismatch" in _audit_reasons(conn, "C-BORROW")
    conn.close()


# ---------- Shape nhóm viết: marker student ----------

@pytest.mark.student
@pytest.mark.parametrize("shape", TEAM_SHAPES)
@pytest.mark.parametrize("point", CRASH_POINTS)
def test_shape_crash_then_resume_pays_once(tmp_path, shape, point):
    store = _store(tmp_path, f"{shape}-{point}.sqlite")
    with pytest.raises(InjectedCrash):
        SHAPES[shape]("C-001", seed=11, store_path=str(store), crash_at=point)
    result = SHAPES[shape]("C-001", seed=11, store_path=str(store))
    conn = connect(store)
    try:
        effect = get_refund(conn, "C-001")
        assert result.status == "resolved"
        assert effect is not None and int(effect["amount_vnd"]) == 35000
        n = conn.execute("SELECT COUNT(*) AS n FROM refund_ledger WHERE claim_id = 'C-001'").fetchone()["n"]
        assert n == 1
        assert committed_audit_count(conn, "C-001") == 1
    finally:
        conn.close()


def _forbidden_strings() -> list[str]:
    """Secret và PII lấy từ world/claims public — không được xuất hiện trong trace/kết quả."""
    out = [c["parent_secret"] for c in CLAIMS if c.get("parent_secret")]
    for order in WORLD.get("orders", []):
        for key in ("phone", "address", "internal_note", "item_name"):
            if order.get(key):
                out.append(str(order[key]))
    return out


@pytest.mark.student
@pytest.mark.parametrize("shape", TEAM_SHAPES)
@pytest.mark.parametrize("claim_id", ["C-001", "C-005", "C-009", "C-014"])
def test_shape_trace_and_result_have_no_secret_or_pii(tmp_path, shape, claim_id):
    store = _store(tmp_path, f"{shape}-{claim_id}-leak.sqlite")
    result = SHAPES[shape](claim_id, seed=11, store_path=str(store))
    blob = json.dumps(result.as_dict(), ensure_ascii=False)
    if result.trace_path:
        blob += Path(result.trace_path).read_text(encoding="utf-8")
    assert "CANARY_SECRET_" not in blob
    for bad in _forbidden_strings():
        assert bad not in blob, f"lộ chuỗi cấm trong trace/kết quả: {bad[:20]}…"