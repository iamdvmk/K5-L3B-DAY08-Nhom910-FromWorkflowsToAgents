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
|   2 | Hồ An Lộc | 2A20260     |       | hal2332004 | Workflow + Integration |
|   3 | Trương Đức Phát | 2A20260     |       | trdphat | Single agent |
|   4 | Đào Nguyễn Quang Thành | 2A20260     |       | ThanhDao11 | Orchestrator + Handoff |

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

## MSSV_HoTen

### Phần việc phụ trách

-

### Đóng góp cụ thể

-

### Bằng chứng

-
