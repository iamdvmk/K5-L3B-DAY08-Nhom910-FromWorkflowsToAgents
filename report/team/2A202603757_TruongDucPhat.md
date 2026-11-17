# Báo cáo cá nhân — 2A202603757_TruongDucPhat

## 1. Thông tin thành viên

- Họ tên Trương Đức Phát
- MSSV 2A202603757
- Email chờ bổ sung
- GitHub chờ bổ sung

## 2. Phần việc phụ trách

Phụ trách Shape B `single` trong `src/lab8/shapes/single.py`, hoàn thiện CP2, CP3 và thêm test hồi quy trong `src/tests/test_single_extra.py`.

## 3. Đóng góp cụ thể

- Hoàn thiện `run_claim` bằng `lab8.runtime.run_react` với `max_steps=8`. Hàm `decide` chọn tool đọc để tra cứu đơn, lịch sử hoàn tiền và tính quote. Các model call được ghi nhận qua `Budget`.
- Đọc claim qua `get_claim_view` và tra cứu đơn theo principal. Thiếu mã đơn trả `needs_info`, đơn không tìm thấy hoặc ngoài phạm vi principal trả `escalated`.
- Tính tiền bằng `compute_compensation` dựa trên order và policy hiện hành. Sau vòng ReAct, host đọc lại order và tính lại quote để kiểm tra kết quả đề xuất.
- Truyền quote đầy đủ vào `durability.issue_refund` để host kiểm tra approval và áp dụng trần hoàn tiền theo đơn. Quote bằng 0 trả `denied`; quote dương bị host từ chối giữ nguyên `proposal_amount` và có audit do host ghi.
- Truyền `crash_at` vào `issue_refund`, để `InjectedCrash` truyền ra ngoài. Ghi sự kiện `refund_attempt` và lưu trace trước khi gọi host để có nhật ký khi crash.
- Trả kết quả bằng `common.finish()` ở mọi nhánh return. Trace ghi các trường cần thiết và dữ liệu quote, tránh ghi ticket thô hoặc dữ liệu riêng tư của khách hàng.
- Thêm test `test_single_crash_persists_trace_before_resume`, tham số hóa tại ba điểm `before_effect`, `after_effect_before_checkpoint` và `after_checkpoint`. Test dùng thư mục trace riêng, kiểm tra trace ngay sau crash, kiểm tra trạng thái ledger tại thời điểm crash và chạy resume hai lần để xác nhận chỉ có một refund cùng một audit committed.

## 4. Bằng chứng

Các commit liên quan trong lịch sử repository gồm

| Commit | Nội dung |
| --- | --- |
| `b7c0960` | Hoàn thiện CP2 cho shape single |
| `0abb7d3` | Bổ sung lưu trace trước khi gọi host cho CP3 |
| `cf354bb` | Thêm test hồi quy trace và crash/resume cho single |

Các lệnh dưới đây chạy trong thư mục `src`. Kết quả được ghi nhận trong phiên phát triển với trợ lý AI.

```powershell
python -m pytest tests/test_public_matrix.py -q -m student -o addopts= -k "single and not workflow and not orchestrator and not swarm"
```

Kết quả `62 passed`, bao gồm T01–T14 trên single và các kịch bản retry T11, crash/resume T12.

```powershell
python -m pytest -q -m student -o addopts= -k "single and not workflow and not orchestrator and not swarm"
```

Kết quả `69 passed` tại lần rà soát CP2 và CP3, gồm 62 test ma trận public, ba test crash/resume và bốn test secret/PII của nhóm.

```powershell
python -m pytest tests/test_single_extra.py -q
```

Kết quả `3 passed`. Ba trường hợp kiểm tra trace tồn tại ngay sau crash và resume/retry giữ nguyên một refund trị giá 35.000 VND cho claim `C-012`, cùng một audit `refund_committed`.

## 5. Công cụ AI đã dùng

Sử dụng ChatGPT/Codex để đọc yêu cầu CP2, CP3, phân tích runtime và contract, hỗ trợ triển khai shape single, thêm test hồi quy và soạn báo cáo cá nhân.

Quá trình kiểm chứng gồm đối chiếu code với `CHECKPOINTS.md`, `docs/business_rules.md`, `docs/contracts.md` và docstring của `single.py`; chạy ma trận public của single và test bổ sung. Các kết quả trong báo cáo là kết quả kiểm tra cục bộ được công cụ thực thi trong phiên làm việc.

## 6. Tự đánh giá

Phần single đáp ứng CP2 và CP3 trên bộ test public đã chạy. Các test xác nhận xử lý claim theo order và policy, giới hạn tool đọc trong vòng ReAct, kiểm tra quote tại host, retry an toàn và crash/resume tại cả ba điểm được hỗ trợ.

Bộ hidden chưa được kiểm tra. Báo cáo crash chung của CP4 do lead chạy và tổng hợp. Benchmark, báo cáo nhóm và bảng đóng góp trong `TEAM.md` cần nhóm hoàn thiện ở CP5. Email và tài khoản GitHub trong báo cáo này cần bổ sung trước khi nộp.
