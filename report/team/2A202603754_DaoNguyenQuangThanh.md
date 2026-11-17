# Báo cáo cá nhân — 2A202603754_DaoNguyenQuangThanh

## 1. Thông tin thành viên

- Họ tên: Đào Nguyễn Quang Thành
- MSSV: 2A202603754
- Email:
- GitHub:

## 2. Phần việc phụ trách

- Triển khai Shape C — orchestrator và investigator chỉ đọc trong `src/lab8/shapes/orchestrator.py`.
- Kiểm tra handoff, trace, retry, crash/resume, approval và trần hoàn tiền đến hết CP4 trong phạm vi Shape C.
- Bổ sung test tích hợp cho Shape C trong `src/tests/test_orchestrator_extra.py`.
- Báo cáo hiện dừng ở CP4; chưa bao gồm benchmark chung, hidden self-check, ablation và quyết định kiến trúc ở CP5.

## 3. Đóng góp cụ thể

- Commit: `83cb1ceeecdb0f413f08f5c593b6e11f4c3216d2` — `Add orchestrator CP2+CP3`. Commit gồm file triển khai orchestrator và file test bổ sung.
- Giữ nguyên chữ ký `run_claim`; xử lý claim không tồn tại, thiếu mã đơn, đơn không tìm thấy hoặc ngoài quyền sở hữu, quote bằng 0 và kết quả duyệt của host.
- Dựng handoff bằng `make_handoff`, không chuyển parent context; cấp `lookup_order`, `lookup_policy`, `compute_compensation` cho investigator thông qua runner có sẵn.
- Tiền được tính bằng code. Orchestrator truyền quote đầy đủ cho `issue_refund`; host xử lý approval, phần đã hoàn trước đó và idempotency.
- Truyền `crash_at` cho host và để `InjectedCrash` truyền ra ngoài. Đóng kết nối DB trong `finally`.
- Dùng `finish()` cho các nhánh trả kết quả để lấy ledger/audit thực tế và ghi trace. Model chỉ được gọi qua MockLLM để soạn chữ, không quyết số tiền.
- Thêm 4 ca test: một ca kiểm tra handoff thực tế và ba ca tham số hóa kiểm tra trace ở các nhánh trả về sớm.

## 4. Bằng chứng

- Commit `83cb1ce`: [code Shape C](../../src/lab8/shapes/orchestrator.py) và [test bổ sung](../../src/tests/test_orchestrator_extra.py).
- Test mới gồm 4 ca: handoff chỉ cấp tool đọc và trace mới hợp lệ ở ba nhánh trả về sớm.

Kết quả gần nhất đã ghi nhận trong phiên Codex, chạy từ `src/`:

| Lệnh | Kết quả |
| --- | --- |
| `python -m pytest -q tests/test_orchestrator_extra.py` | `4 passed` |
| `python -m pytest -q` | `70 passed, 276 deselected` |
| `python -m pytest -q -m student -o addopts= -k orchestrator` | `69 passed, 277 deselected` |

- CP3: T11/T12 pass; rà 62 trace và 57 handoff, không phát hiện vấn đề trong phạm vi kiểm tra.
- CP4: kiểm tra riêng Shape C tại ba điểm crash; sau resume/retry mỗi ca chỉ có một refund, một audit committed và một checkpoint.
- Bảy ca approval/trần hoàn tiền đạt kết quả dự kiến: ca từ chối có `policy_denied`; hoàn phần chênh 120.000 VND; approval thấp giới hạn refund còn 20.000 VND. Không phát hiện secret/PII đối chiếu từ DB; stdout/stderr rỗng trong các ca này.

Các kiểm tra trực tiếp CP3–CP4 dùng script/DB tạm, chưa lưu thành report riêng. Đây chưa phải kết quả hidden. Khi chạy qua Codex đã thêm `--basetemp` để tránh lỗi quyền thư mục tạm Windows.

## 5. Công cụ AI đã dùng

- Codex: hỗ trợ đọc tài liệu, tìm reference Shape C, triển khai orchestrator, rà code và viết/chạy test theo từng bước được duyệt.
- Cách kiểm chứng đã thực hiện trong phiên: đối chiếu `CHECKPOINTS.md`, luật nghiệp vụ và contract; chạy pytest có sẵn và test bổ sung; đối chiếu ledger, audit, checkpoint, trace và stdout/stderr trong các ca kiểm tra trực tiếp.
- Các kết quả ở mục 4 là output thực tế do Codex chạy. Phần xác nhận tự kiểm tra độc lập của cá nhân chưa được bổ sung ở thời điểm lập báo cáo.

## 6. Tự đánh giá

