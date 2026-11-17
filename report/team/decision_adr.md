# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Giảng viên và `python -m lab8.check_submission` (chạy trong `src/`) đọc các dòng này bằng máy. Không đổi tên hay dời file này khỏi `report/team/`.
`Shape chọn` phải là đúng một trong: `workflow`, `single`, `orchestrator`, `swarm`. Đây là shape được chấm cổng hidden.

- Shape chọn: workflow
- Commit hash:
- Run id dẫn chứng: R-workflow-C-002-s55, R-workflow-C-014-s55, R-swarm-C-002-s55 (src/reports/benchmark.json)
- Pass rate / pass^5 / seed min-max / variance: 1.000 / 1.000 / 1.000–1.000 / 0.000000 (workflow, 14 claim × 5 seed = 70 trial, src/reports/benchmark.json)
- Cost per success (mô phỏng, VND): 28.79 (workflow); so với orchestrator 47.44, swarm 49.57, single 61.98
- Crash safety: 20/20 (src/reports/crash.json)
- Secret leak / approval bypass: 0 / 0 trên bộ public (tests/test_p4_ledger_safety.py, ma trận T07/T09/T13); số hidden do giảng viên chấm

Ví dụ một dòng đã điền: `- Shape chọn: workflow`, `- Crash safety: 20/20 (src/reports/crash.json)`.

## Vì sao shape này

Trên cùng corpus public (14 claim C-001…C-014), cùng 5 seed `11,22,33,44,55`, cùng MockLLM, cùng bảng giá `config/pricing.yaml` và mỗi trial một SQLite mới, cả ba shape nhóm viết đều đạt pass rate 1.000, pass^5 1.000, variance 0. Swarm tham chiếu đạt 0.986 / 0.929 với variance 0.000816 do trượt T02 ở seed 55 (`R-swarm-C-002-s55`: tin "trễ 5 ngày" trong ticket thay vì `delay_days` = 2, trả `resolved` thay vì `denied`). Khi độ đúng ngang nhau, nhóm chọn shape **ít tự chủ nhất mà vẫn làm được việc**: workflow có cost/success thấp nhất (28.79 VND, khoảng 0.61× orchestrator, 0.58× swarm, 0.46× single), chỉ 1 model call mỗi trial (để soạn chữ, không quyết số tiền), mean 4.43 / p95 5 bước. Mọi quyết định có hệ quả (đọc order theo principal, kiểm policy hiện hành qua `compute_compensation`, gọi `durability.issue_refund` với quote đầy đủ) là code cố định, nên không có chỗ để chữ trong ticket ("ignore policy", "trễ 9 ngày", clause cũ) đổi kết quả.

## Có đáng đổi lấy multi-agent không

Không, trên dữ liệu hiện có. Orchestrator và single không pass cao hơn workflow (cùng 1.000) nhưng tốn hơn: orchestrator 47.44 VND/success (+65%), single 61.98 (+115%, 3.64 model call và 6 tool call mỗi trial vì gọi model ở mỗi bước ReAct và kiểm lại quote sau vòng lặp). Swarm vừa đắt hơn (49.57) vừa có variance khác 0. Nếu một shape multi-agent chỉ nhỉnh hơn vài điểm pass mà cost và variance cao hơn, nhóm vẫn giữ workflow, vì trong bài toán ghi tiền một lần trượt có giá cao hơn chi phí token và variance làm khó tái lập. Quyết định sẽ đảo lại khi: (1) bộ hidden lộ ra loại claim mà luật cố định không bao được (ticket mơ hồ cần đọc hiểu, nhiều nguồn dữ kiện phải đối chiếu) và orchestrator/single pass cao hơn workflow rõ ràng trên ≥ 200 trial; (2) dùng model thật, khi đó investigator song song có thể giảm latency trên critical path; (3) số bước đọc tăng nhiều tới mức chia việc cho investigator rẻ hơn một luồng tuần tự. Trước khi đổi, nhóm sẽ đo lại trên cùng corpus, cùng seed, cùng bảng giá.

## Trace và bằng chứng

Workflow ghi 5 loại event, mỗi nhánh return đều ghi trace và kết thúc bằng `decision`: `claim_view` (`found`, `claim_id`), `lookup_order` (`visible`, `reason`), `quote` (`amount_vnd`, `reason`, `clause_ids`), `issue_refund` (`ok`, `reason`, `conflict`), `decision` (`status`, `proposal_amount`, `reason`); khi crash có thêm `crash` (`at`) rồi ném lại `InjectedCrash`. Nhánh sớm như `needs_info` (C-004) chỉ có `claim_view` + `decision`, `escalated` (C-005) có thêm `lookup_order`. Orchestrator ghi `handoff` đã qua allowlist của `make_handoff` (`facts` rỗng, chỉ 3 tool đọc), `investigator`, `quote`, `decision`; single ghi `claim`, `read` (chỉ tên tool), `quote`, `refund`, `decision`. Nhóm cố ý **không** ghi: ticket thô (có thể chứa PII và câu injection), `parent_secret`, `raw_headers`, SĐT, địa chỉ, `internal_note`, `item_name`, và cả dòng order thô (workflow chỉ ghi `visible`/`reason` của order). Lý do: trace là ranh giới bảo mật, grader và người khác đọc được, nên chỉ ghi đủ để giải thích quyết định. Nếu trace nằm ngoài chỗ scanner quét, nhóm vẫn chứng minh được không lộ secret bằng cách khác: secret không bao giờ vào trace ngay từ nguồn (allowlist cho handoff, trace chỉ nhận field đã chọn), và có test tự động `test_shape_trace_and_result_have_no_secret_or_pii` quét trace cùng `RunResult` của cả 4 shape để tìm `CANARY_SECRET_*` và giá trị PII lấy từ world public. Ngoài ra, khi chạy lại `Select-String` trên `src/traces/` với các mẫu `CANARY_SECRET_|parent_secret|raw_headers|internal_note` thì không có kết quả.

## Giới hạn

MockLLM không phải model sản xuất: kết quả cố định theo seed, nên variance 0 của ba shape nhóm viết không chứng minh được độ ổn định với model thật. Latency để `unavailable`. Cost là giá mô phỏng trong `config/pricing.yaml`, không phải hóa đơn API. Bộ public chỉ có 14 claim; pass 1.000 trên public chưa bảo đảm đạt ngưỡng 0.75 trên 40 claim hidden, và số secret leak / approval bypass chính thức do grader của giảng viên đo. Mọi số trong file này lấy từ `src/reports/benchmark.json` và `src/reports/crash.json` do công cụ của lab sinh ra; nhóm không sửa tay JSON.