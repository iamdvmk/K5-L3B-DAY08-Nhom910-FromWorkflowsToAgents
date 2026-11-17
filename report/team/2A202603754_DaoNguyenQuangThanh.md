# Báo cáo cá nhân — 2A202603754_DaoNguyenQuangThanh

## 1. Thông tin thành viên

- Họ tên: Đào Nguyễn Quang Thành
- MSSV: 2A202603754
- Email: 26ai.thanhdnq@vinuni.edu.vn
- GitHub: [ThanhDao11](https://github.com/ThanhDao11)

## 2. Phần việc phụ trách

- Triển khai Shape C — orchestrator và investigator chỉ đọc trong `src/lab8/shapes/orchestrator.py`.
- Kiểm tra handoff, trace, retry, crash/resume, approval và trần hoàn tiền trong phạm vi Shape C.
- Bổ sung test tích hợp cho Shape C trong `src/tests/test_orchestrator_extra.py`.

## 3. Đóng góp cụ thể

- Commit: `83cb1ceeecdb0f413f08f5c593b6e11f4c3216d2` — `Add orchestrator CP2+CP3`. Commit gồm file triển khai orchestrator và file test bổ sung.
- Dựng handoff bằng `make_handoff`, không chuyển parent context; cấp `lookup_order`, `lookup_policy`, `compute_compensation` cho investigator thông qua runner có sẵn.
- Thêm 4 ca test: một ca kiểm tra handoff thực tế và ba ca tham số hóa kiểm tra trace ở các nhánh trả về sớm.

## 4. Bằng chứng

### Code và test trong commit

- [Code Shape C](../../src/lab8/shapes/orchestrator.py).
- [Test bổ sung Shape C](../../src/tests/test_orchestrator_extra.py):
  - `test_orchestrator_handoff_contains_only_safe_read_capabilities`: kiểm tra field và tool được cấp trong handoff thực tế, cùng marker secret trong trace và stdout/stderr.
  - `test_orchestrator_early_return_replaces_stale_trace`: ba ca `unknown`, `missing_order`, `other_owner`; kiểm tra status, reason, quote 0, không phát sinh refund và trace mới thay nội dung cũ.

## 5. Công cụ AI đã dùng

- Codex: hỗ trợ đọc tài liệu, triển khai orchestrator, rà code và viết/chạy test theo từng bước được duyệt.
- Cách kiểm chứng đã thực hiện trong phiên: đối chiếu `CHECKPOINTS.md`, luật nghiệp vụ và contract; chạy pytest có sẵn và test bổ sung; đối chiếu ledger, audit, checkpoint, trace và stdout/stderr trong các ca kiểm tra trực tiếp.

## 6. Tự đánh giá
- Đã hoàn thành phần phụ trách Shape C và 4 test bổ sung, tập trung vào handoff chỉ đọc và trace an toàn. Theo benchmark chung của nhóm ở CP5, orchestrator đạt pass rate và pass^5 bằng 1.000 trên 70 trial public, variance 0; đây là kết quả đánh giá của nhóm trên phần triển khai đã tích hợp.
- Từ kết quả nhóm, nhận thấy orchestrator chưa đem lại lợi ích về độ đúng so với workflow nhưng có cost/success mô phỏng cao hơn (47,44 so với 28,79 VND), phù hợp với quyết định chọn workflow trong ADR.
