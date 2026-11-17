# Research card

File này nằm cố định ở `report/team/research_card.md`; `python -m lab8.check_submission` đọc cột "Nhóm điền" bằng máy.

Phần này nối tiếp phần mini research ở buổi lý thuyết (slide 62–63). Chọn **một** câu R1–R4, điền 6 dòng, rồi biến nó thành **một ablation** chạy được trong lab: giữ nguyên model (MockLLM), tool, seed, corpus và giá, chỉ thay đổi một biến.

| Câu | Nguồn (thư viện tham khảo, slide 68–69) | Câu hỏi gợi ý cho lab |
| --- | --- | --- |
| R1 · Scaling | Google Research 2026, *Towards a Science of Scaling Agent Systems* | Task claims chủ yếu tuần tự hay song song được? Dự đoán thêm investigator sẽ làm pass rate và cost/success thay đổi thế nào. |
| R2 · Failure taxonomy | MAST, NeurIPS 2025, *Why Do Multi-Agent LLM Systems Fail?* | Các trial fail của swarm (seed 55) thuộc nhóm nào: lỗi giao việc, lệch mục tiêu, hay lỗi kiểm chứng? |
| R3 · Architecture choices | AgentArch, AACL 2026 | Nếu đổi topology mà giữ nguyên mọi thứ khác, biến nào phải cố định để kết luận còn đúng? |
| R4 · Evaluation confounders | EMNLP 2026, *Rethinking Evaluation of MAS Efficiency* | Làm sao chứng minh chênh lệch giữa A/B/C/D là do topology, không phải do prompt, tool hay seed? |

## Phiếu của nhóm

Điền vào cột cuối. Không xóa hai cột đầu.

| Field | Hướng dẫn | Nhóm điền |
| --- | --- | --- |
| CÂU | R1 / R2 / R3 / R4 | R2 · Failure taxonomy |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | Cemri et al., *Why Do Multi-Agent LLM Systems Fail?*, NeurIPS 2025, https://arxiv.org/abs/2503.13657 . Loại bằng chứng: phân tích thực nghiệm trên trace có gán nhãn (MAST-Data, hơn 1600 trace, 7 framework MAS), có nghiên cứu can thiệp nhỏ |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | Lỗi của hệ multi-agent gom được vào 14 failure mode thuộc 3 nhóm: FC1 Specification issues, FC2 Inter-agent misalignment, FC3 Task verification. Kiểm chứng sai hoặc thiếu (FM-3.2, FM-3.3) là một nhóm lỗi đáng kể, và có verifier không phải là cách chữa tất cả: verifier hiện có thường chỉ kiểm bề mặt |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Kết luận rút ra từ framework MAS mã nguồn mở (ChatDev, MetaGPT, AG2…) trên task coding, toán, agent tổng quát, với model GPT-4/Claude 3/Qwen2.5/CodeLlama và nhãn của người + LLM-as-judge. Không đo trên bài claims hoàn tiền, không dùng model cố định theo seed như MockLLM, nên tỉ lệ từng nhóm lỗi không chuyển thẳng sang lab này; nhóm chỉ mượn cách phân loại |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Trial fail duy nhất của swarm trên public (C-002 seed 55) thuộc FC3, cụ thể FM-3.3 Incorrect verification: swarm có bước đối chiếu số ngày trễ nhưng lấy số trong ticket (5) thay cho cột `delay_days` (2) rồi tính lại quote, nên trả `resolved` thay vì `denied`. Dự đoán khi thay swarm bằng workflow (luôn lấy `delay_days` từ order, không có nhánh ghi đè): pass rate tăng từ ≈0.986 lên 1.000, pass^5 từ ≈0.929 lên 1.000, seed variance từ >0 về 0, cost/success giảm vì không còn trial fail. Dự đoán phụ: với seed chia hết cho 5, lỗi lặp lại ở đúng C-002 trên mọi seed (pass ≈ 13/14 ≈ 0.929 mỗi seed) |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Giữ cố định: MockLLM, tool registry, corpus `data/public_claims.jsonl` (14 claim), world `data/public_world_state.json`, bảng giá `config/pricing.yaml`, `as_of` 2026-11-15, evaluator `lab8.metrics.trial_pass`, mỗi trial một SQLite mới. Biến duy nhất được thay đổi ở ablation chính: shape (swarm → workflow) trên seed `11,22,33,44,55`. Ablation phụ (để tách nguyên nhân): giữ shape swarm và workflow, chỉ đổi tập seed sang `5,10,15,20,25` |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Lỗi dự kiến: swarm tin số ngày trễ do khách tự ghi trong ticket thay vì dữ liệu order (FM-3.3), dẫn tới refund sai. Đo bằng: pass rate, pass^5, seed min–max và variance, cost/success từ `lab8.benchmark`; xác nhận nguyên nhân bằng `reason` của trial fail (`status resolved != denied`) và event `model_override` trong trace của run id fail |

## Kết quả ablation

- Lệnh đã chạy (copy nguyên văn):
  - Ablation chính (đổi shape): `python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json`
  - Ablation phụ (đổi tập seed): `python -m lab8.benchmark --shapes swarm,workflow --cases data/public_claims.jsonl --seeds 5,10,15,20,25 --out reports/ablation_r2_seed_sweep.json`
- Run id / file report: `src/reports/benchmark.json` (commit `8413054`), trial fail `R-swarm-C-002-s55`, đối chứng `R-workflow-C-002-s55`; `src/reports/ablation_r2_seed_sweep.json`, trial fail `R-swarm-C-002-s5`, `R-swarm-C-002-s10`, `R-swarm-C-002-s15`, `R-swarm-C-002-s20`, `R-swarm-C-002-s25`.
- Kết quả so với hypothesis (đúng / sai / không kết luận được), kèm số liệu: **Đúng.** Ablation chính, cùng 70 trial: swarm pass 0.986, pass^5 0.929, seed min–max 0.929–1.000, variance 0.000816, cost/success 49.57 VND; workflow pass 1.000, pass^5 1.000, min–max 1.000–1.000, variance 0, cost/success 28.79 VND. Trial fail duy nhất của swarm là C-002 seed 55 với `status resolved != denied`, trace có event `model_override` (ghi đè `delay_days` bằng số trong ticket) — khớp FM-3.3 Incorrect verification trong nhóm FC3, không phải lỗi giao việc (FC1) hay lệch mục tiêu giữa agent (FC2). Ablation phụ xác nhận nguyên nhân: với seed `5,10,15,20,25`, swarm pass đúng 0.929 ở cả 5 seed (13/14 mỗi seed), cả 5 trial fail đều là C-002; workflow vẫn 1.000. Vậy lỗi gắn với nhánh ghi đè dữ liệu, không phải dao động ngẫu nhiên giữa seed.
- Giới hạn: MockLLM không phải model sản xuất, latency là `unavailable`. Lỗi của swarm là điểm yếu cài sẵn (`REFERENCE_WEAKNESS`, seed chia hết cho 5), nên ablation chứng minh cơ chế lỗi chứ không đo tần suất lỗi của model thật. Corpus public chỉ có 14 claim và chỉ một claim (C-002) có số ngày trong ticket khác order, nên mẫu lỗi rất nhỏ. Gán FM-3.3 là phán đoán của nhóm; cũng có thể lập luận đây là FM-1.1 (không tuân đặc tả "chữ trong ticket là dữ liệu"). Swarm và workflow khác nhau ở nhiều điểm ngoài bước kiểm chứng (số agent, số model call), nên chênh cost/success không chỉ do lỗi này.

Muốn đi xa hơn một ablation để lấy điểm cộng thì xem [docs/bonus_topics.md](../../docs/bonus_topics.md).