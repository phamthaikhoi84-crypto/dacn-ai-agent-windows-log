# Xây dựng AI Agent sử dụng mô hình ngôn ngữ nhỏ phát hiện mối đe dọa dựa trên log Windows

Đồ án chuyên ngành — Khoa Công nghệ Thông tin, HUTECH — Học kỳ 1, năm học 2026–2027

| Thành viên | MSSV | Vai trò |
|---|---|---|
| Phạm Thái Khôi | 2380601102 | Nhóm trưởng |
| Trần Trọng Thiên | 2380602102| |
| Nguyễn Châu Anh Dũng | 2380600296 | |

Giảng viên hướng dẫn: ...

## Giới thiệu đề tài

Đề tài xây dựng một AI Agent tự viết bằng Python (không dùng LangChain/LangGraph), chạy mô hình ngôn ngữ nhỏ cục bộ qua Ollama, để phân tích log Windows và phát hiện chuỗi hành vi tấn công.

- **Nguồn log chính:** Sysmon (Microsoft-Windows-Sysmon/Operational) và PowerShell Script Block Logging (Event ID 4104).
- **Phạm vi:** 8 kỹ thuật MITRE ATT&CK tạo thành một chuỗi tấn công:

| Mã | Kỹ thuật |
|---|---|
| T1105 | Ingress Tool Transfer (tải công cụ) |
| T1059.001 | PowerShell |
| T1053.005 | Scheduled Task |
| T1547.001 | Registry Run Keys / Startup Folder |
| T1136.001 | Create Account: Local Account |
| T1003.001 | OS Credential Dumping: LSASS Memory |
| T1021.001 | Remote Services: RDP |
| T1070.001 | Clear Windows Event Logs |

- **Mô hình so sánh** (nhiều họ khác nhau): Qwen3 4B, Llama 3.2 3B, Gemma 3 4B, Phi-4-mini.
- **Dữ liệu:** bộ log tấn công công khai đã gán nhãn (EVTX-ATTACK-SAMPLES, OTRF Security Datasets, Splunk Attack Data) kết hợp log bình thường.

## Cấu trúc thư mục

```
data/      Bảng mô tả bộ dữ liệu (KHÔNG chứa file log)
src/       Mã nguồn
docs/      Đề cương, kết quả thử nghiệm mô hình, tài liệu
ai-logs/   Nhật ký sử dụng công cụ AI trong quá trình làm đồ án
```

File log (.evtx, .log, .json lớn) được lưu trên máy từng thành viên và bị chặn bởi `.gitignore`.

## Cài đặt và chạy thử

```bash
pip install -r requirements.txt
python src/evtx_to_duckdb.py duong_dan/toi/file.evtx
```

Kết quả được ghi vào `output/events.duckdb` (bảng `events`).

## Tiến độ

- [ ] Tuần 1: tạo repo, thu thập dữ liệu 8 kỹ thuật, nạp EVTX vào DuckDB, cài và đo 4 mô hình
