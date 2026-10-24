# Tuần 1 (16/10 – 17/10/2026)

## Kế hoạch

| Người | Việc |
|---|---|
| Khôi | Tạo repo GitHub (data/, src/, docs/, ai-logs/), mời thầy và thành viên; viết script nạp file .evtx vào DuckDB |
| Thiên | Thu thập log tấn công cho 8 kỹ thuật (EVTX-ATTACK-SAMPLES, OTRF, Splunk Attack Data); log không đưa lên GitHub |
| Dũng | Cài Sysmon + PowerShell Script Block Logging; cài và đo 4 mô hình qua Ollama |

## Kết quả

| Người | Kết quả | File |
|---|---|---|
| Khôi | Repo và khung tài liệu; script đọc .evtx nạp vào DuckDB, chạy thử thành công trên file SharpRDP | [src/evtx_to_duckdb.py](../src/evtx_to_duckdb.py) |
| Thiên | Bảng dữ liệu cho 8/8 kỹ thuật; cấu hình Sysmon dùng chung | [data/datasets.md](../data/datasets.md), [config/sysmonconfig-dacn.xml](../config/sysmonconfig-dacn.xml) |
| Dũng | Sysmon + Script Block Logging chạy trên máy; đo 4 mô hình (Qwen3 4B, Llama 3.2 3B, Gemma 3 4B, Phi-4-mini) bằng CPU | [docs/models.md](../docs/models.md) |
| Cả nhóm | Bắt đầu thu log bình thường trên máy 3 thành viên (từ 17/10) | Log giữ trên máy, không đưa lên GitHub |

## Góp ý của thầy (buổi 17/10/2026)

- Repo và mô hình chỉ là hạ tầng. Cốt lõi của đề tài là **phương pháp nhận diện hành vi tấn công**, nhóm chưa có.
- Hành vi là một chuỗi sự kiện có thứ tự của cùng người dùng / máy, cần nhận diện sớm từ vài sự kiện đầu và dự đoán được, đo độ chính xác trên dữ liệu có nhãn và cải thiện dần.
- Nguồn log chỉ là "đối tượng", không phải hành vi.
- 8 kỹ thuật là quá ít: vì sao không làm tất cả? Cần mở rộng hoặc giải thích lý do chọn, để chuỗi không bị đứt khi gặp kỹ thuật ngoài phạm vi.
- Thầy mở log Windows trên máy thầy và hỏi: vì sao phải dựa vào Sysmon?

## Kế hoạch tuần sau

Chốt hướng theo góp ý: định nghĩa hành vi, phương pháp, phạm vi 2 tầng, so sánh Sysmon với log Windows mặc định (chi tiết ở [tuan-2.md](tuan-2.md)).
