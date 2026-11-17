# Team

## Thông tin nhóm

- Tên nhóm: Nhóm 910
- Lớp: L3B
- Repo nhóm: `K5-L3B-DAY08-Nhom910-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt:

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Đào Vũ Minh Khánh | 2A202603878 | 26ai.khanhdvm@vinuni.edu.vn | iamdvmk | Ledger/Crash + Evaluation |
|   2 | Hồ An Lộc | 2A202603743 | 26ai.locha@vinuni.edu.vn | hal2332004 | Workflow + Integration |
|   3 | Trương Đức Phát | 2A202603757 | 26ai.phattd@vinuni.edu.vn | trdphat | Single agent |
|   4 | Đào Nguyễn Quang Thành | 2A202603754 | 26ai.thanhdnq@vinuni.edu.vn | ThanhDao11 | Orchestrator + Handoff |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Hồ An Lộc (hal2332004) | Workflow + integration | `8370855` feat(workflow): implement deterministic workflow shape; `7cbe5c7` test(workflow): add extra workflow tests and personal report | `src/tests/test_workflow_extra.py`: `test_workflow_trace_has_no_secret_or_pii`, `test_workflow_ignores_delay_written_in_ticket`, `test_workflow_crash_then_resume_keeps_single_refund`, `test_workflow_passes_full_quote_when_order_already_refunded` |
| Trương Đức Phát (trdphat) | Single agent (ReAct) | `b7c0960` Feat: complete CP2; `0abb7d3` Complete CP3 for single shape |  |
| Đào Nguyễn Quang Thanh | Orchestrator + handoff | `83cb1ce` Add orchestrator CP2+CP3; `e3a91a1` Add Personal Report | `src/tests/test_orchestrator_extra.py`: `test_orchestrator_handoff_contains_only_safe_read_capabilities`, `test_orchestrator_early_return_replaces_stale_trace` |
| Đào Vũ Minh Khánh | Ledger/crash + evaluation | `f442136` cp1 (test ledger/crash/secret); review PR #2–#4; benchmark, crash report, ADR, research card | `src/tests/test_p4_ledger_safety.py`: `test_full_quote_pays_difference_but_pre_subtracted_quote_underpays`, `test_order_already_refunded_is_denied_with_audit`, `test_borrowed_approval_from_other_claim_is_blocked`, `test_shape_crash_then_resume_pays_once`, `test_shape_trace_and_result_have_no_secret_or_pii` |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## 2A202603743_HoAnLoc

### Phần việc phụ trách

Shape A `workflow` (`src/lab8/shapes/workflow.py`) và vai tích hợp (chạy `check_submission`, ghi commit hash vào ADR).

### Đóng góp cụ thể

- Cài đặt `workflow.py` là luồng Python cố định: đọc claim qua `get_claim_view`, kiểm tra `order_id`, `lookup_order`, tính tiền bằng `compute_compensation`, rồi gọi `durability.issue_refund`.
- Quyết định kỹ thuật:
  - Tiền do code tính từ dòng order trong DB; số ngày trễ trong ticket bị bỏ qua. MockLLM chỉ soạn câu trả lời, không quyết số tiền.
  - Truyền **quote đầy đủ** vào `issue_refund` để host tự trừ phần đã hoàn của đơn (T13, T14).
  - Quote bằng 0 thì trả `denied` và không gọi host.
  - Truyền `crash_at` vào `issue_refund`; nếu bắt `InjectedCrash` để ghi trace thì `raise` lại (T12).
  - Mọi nhánh trả kết quả qua `common.finish()`. Trace chỉ ghi field đã lọc (không ghi claim row hay order row thô).
- Test đã thêm: `src/tests/test_workflow_extra.py` (9 test):
  - trace không lộ secret/PII (4 claim);
  - bỏ qua số ngày trễ ghi trong ticket (C-002);
  - crash ở 3 điểm rồi resume vẫn một refund;
  - giữ quote đầy đủ khi đơn đã hoàn trước (C-014).

### Bằng chứng

- Commit: <ĐIỀN HASH>
- `python -m pytest -q -m student -o addopts= -k workflow` → 62 passed.
- `python -m pytest -q tests/test_workflow_extra.py` → 9 passed.
- `python -m pytest -q` → 63 passed, 248 deselected (trước khi merge hai shape còn lại).

## 2A202603754_DaoNguyenQuangThanh

### Phần việc phụ trách

- Triển khai Shape C — orchestrator và investigator chỉ đọc trong `src/lab8/shapes/orchestrator.py`.
- Kiểm tra handoff, trace, retry, crash/resume, approval và trần hoàn tiền trong phạm vi Shape C.
- Bổ sung test tích hợp cho Shape C trong `src/tests/test_orchestrator_extra.py`.

### Đóng góp cụ thể

- Commit: `83cb1ceeecdb0f413f08f5c593b6e11f4c3216d2` — `Add orchestrator CP2+CP3`. Commit gồm file triển khai orchestrator và file test bổ sung.
- Dựng handoff bằng `make_handoff`, không chuyển parent context; cấp `lookup_order`, `lookup_policy`, `compute_compensation` cho investigator thông qua runner có sẵn.
- Thêm 4 ca test: một ca kiểm tra handoff thực tế và ba ca tham số hóa kiểm tra trace ở các nhánh trả về sớm.

### Bằng chứng

- [Code Shape C](../../src/lab8/shapes/orchestrator.py).
- [Test bổ sung Shape C](../../src/tests/test_orchestrator_extra.py):
  - `test_orchestrator_handoff_contains_only_safe_read_capabilities`: kiểm tra field và tool được cấp trong handoff thực tế, cùng marker secret trong trace và stdout/stderr.
  - `test_orchestrator_early_return_replaces_stale_trace`: ba ca `unknown`, `missing_order`, `other_owner`; kiểm tra status, reason, quote 0, không phát sinh refund và trace mới thay nội dung cũ.

## 2A202603878_DaoVuMinhKhanh

### Phần việc phụ trách

- Viết test an toàn cho ledger, approval, crash và trace (`src/tests/test_p4_ledger_safety.py`).
- Review PR và chạy kiểm tra cả ba shape nhóm viết (workflow, single, orchestrator) trước khi merge vào `main`.
- Chạy crash suite, benchmark 4 shape, rà must-pass; soạn `report/team/decision_adr.md` và `report/team/research_card.md`.

### Đóng góp cụ thể

- **Test đã thêm:** `src/tests/test_p4_ledger_safety.py`, gồm hai lớp:
  - *3 test host* (chạy trong cổng `python -m pytest -q`, luôn xanh):
    - `test_full_quote_pays_difference_but_pre_subtracted_quote_underpays`: với T14, truyền quote đầy đủ 150.000 thì host trả 120.000; nếu shape tự trừ trước (truyền 120.000) thì host trừ thêm lần nữa, chỉ còn 90.000. Test này cho thấy vì sao shape phải truyền quote đầy đủ.
    - `test_order_already_refunded_is_denied_with_audit`: C-013 bị từ chối với lý do `order_already_refunded`, không ghi ledger, có audit `policy_denied`.
    - `test_borrowed_approval_from_other_claim_is_blocked`: claim mượn approval A-001 của C-001 bị chặn với lý do `approval_claim_mismatch`, kể cả khi gọi lại lần hai.
  - *Test shape* (marker `student`, chạy cho cả 4 shape, swarm làm đối chứng):
    - `test_shape_crash_then_resume_pays_once`: crash ở cả 3 điểm `before_effect`, `after_effect_before_checkpoint`, `after_checkpoint`; sau khi resume chỉ có 1 dòng ledger và 1 audit `refund_committed`. T12 có sẵn chỉ kiểm 1 điểm crash.
    - `test_shape_trace_and_result_have_no_secret_or_pii`: quét trace và `RunResult` tìm `CANARY_SECRET_*` và giá trị SĐT, địa chỉ, `internal_note`, `item_name` lấy từ world public.
- **Review và tích hợp:** kiểm từng nhánh trước khi merge (PR #2 workflow, #3 orchestrator, #4 single). Mỗi lần đều thử gộp với `main` để kiểm conflict, chạy cổng host, ma trận student và test P4, đồng thời đọc code theo `docs/business_rules.md`: tiền do `compute_compensation` tính, truyền quote đầy đủ, truyền `crash_at` và không nuốt `InjectedCrash`, mọi nhánh return đều ghi trace.

### Bằng chứng

- Commit: `f442136` (thêm `test_p4_ledger_safety.py`, merge qua PR #1); <hash commit benchmark/crash>; <hash commit ADR>.
- `python -m pytest -q` → 70 passed (trên `main` `4c5a39c`, gồm 3 test host của P4).
- `python -m pytest -q -m student -o addopts=` → 276 passed, 0 failed (4 shape, ma trận T01–T14 và test P4).
- `python -m pytest -q -m student -o addopts= -k "C-007 or C-013 or C-009 or p4"` → 88 passed. `Select-String` trên `src/traces/` với mẫu `CANARY_SECRET_|parent_secret|raw_headers|internal_note` không có kết quả.
- `python -m lab8.crash_test --count 20 --out reports/crash.json` → `crash_safety 20/20`.
- `src/reports/benchmark.json`: workflow pass 1.000 / pass^5 1.000 / variance 0 / cost/success 28.79 VND; swarm 0.986 / 0.929 / 0.000816 / 49.57, trượt duy nhất ở `R-swarm-C-002-s55` (`status resolved != denied`).
- `python -m lab8.demo.buggy_workflow` → `unsafe refund rows: 2`, dùng để giải thích vì sao checkpoint đơn lẻ không thay được ledger.

## MSSV_HoTen

### Phần việc phụ trách

-

### Đóng góp cụ thể

-

### Bằng chứng

-