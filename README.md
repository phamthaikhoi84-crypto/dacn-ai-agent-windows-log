# Xây dựng AI Agent sử dụng mô hình ngôn ngữ nhỏ phát hiện mối đe dọa dựa trên log Windows

Đồ án chuyên ngành — Khoa Công nghệ Thông tin, HUTECH — Học kỳ 1, năm học 2026–2027

| Thành viên | MSSV | Vai trò |
|---|---|---|
| Phạm Thái Khôi | 2380601102 | Nhóm trưởng |
| Trần Trọng Thiên | 2380602102| Dữ liệu|
| Nguyễn Châu Anh Dũng | 2380600296 | Môi trường và mô hình|

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

## Cách chạy

Mọi lệnh dưới đây chạy trong **PowerShell**, đứng ở **thư mục gốc repo** (thư mục có `src\` và `README.md`):

```powershell
cd <đường dẫn tới>\dacn-ai-agent-windows-log
```

Tất cả chế độ đều chạy qua một lệnh `python src\dacn.py <chế độ> ...`. File này chỉ gọi lại `agent.py`, `theo_doi.py`, `danh_gia.py`, nên mọi tham số của các file đó vẫn dùng được.

### 1. Cài đặt (làm một lần)

1. **Python 3.10 trở lên.** Kiểm tra bằng `python --version`.
2. **Thư viện:**
   ```powershell
   pip install -r requirements.txt
   ```
   Lệnh này cài `evtx`, `duckdb`, và `pywin32` (`pywin32` dùng cho `theo-doi`; thiếu thì agent đọc log bằng `wevtutil`, chậm hơn).
3. **Ollama** (chỉ cần khi chạy có SLM). Cài từ https://ollama.com, rồi tải mô hình mặc định:
   ```powershell
   ollama pull phi4-mini
   ```
   Mở Ollama trước khi chạy có SLM. Kiểm tra bằng `ollama list`.
4. **Sysmon** (chỉ cần cho `theo-doi`): tải Sysmon của Microsoft Sysinternals, rồi trong PowerShell "Run as administrator" chạy `sysmon64.exe -accepteula -i config\sysmonconfig-dacn.xml` (cấu hình chung của nhóm). Kiểm tra bằng `Get-Service Sysmon*`.
5. **Hiện đuôi file:** File Explorer > View > Show > File name extensions. Nếu không bật, file tải về có thể bị thành `a.evtx.evtx`.

### 2. Xem trợ giúp

```powershell
python src\dacn.py --help            # 4 chế độ và tham số chung
python src\dacn.py quet --help       # tham số riêng của một chế độ
```

### 3. Bốn chế độ

| Chế độ | Làm gì | Lệnh mẫu |
|---|---|---|
| `quet` | Phân tích một file `.evtx` (hoặc cả thư mục) qua 5 bước của agent | `python src\dacn.py quet D:\log\a.evtx` |
| `phat-lai` | Đưa từng sự kiện của file vào agent theo thứ tự thời gian, để xem agent báo sớm tới đâu | `python src\dacn.py phat-lai D:\log\a.evtx` |
| `theo-doi` | Theo dõi trực tiếp log Sysmon và PowerShell của máy đang chạy. **Phải mở PowerShell bằng "Run as administrator".** Dừng bằng Ctrl + C | `python src\dacn.py theo-doi --khong-slm` |
| `danh-gia` | Chạy agent trên bộ thử `data/bo-thu.csv`, có và không có SLM, rồi xuất bảng so sánh | `python src\dacn.py danh-gia --thu-muc <thư mục log tấn công> <thư mục log bình thường>` |

**Thử nhanh:** chạy `quet` trên file `sysmon_10_11_outlfank_dumpert_and_andrewspecial_memdump.evtx` (trong thư mục log tấn công, lấy từ EVTX-ATTACK-SAMPLES):

```powershell
python src\dacn.py quet <thư mục log>\sysmon_10_11_outlfank_dumpert_and_andrewspecial_memdump.evtx --khong-slm
```

Kết quả phải có dòng `=> KẾT LUẬN: T1003.001`. Với `phat-lai` trên cùng file, sự kiện 1 ra CHƯA XÁC NHẬN, sự kiện 2 chuyển sang KẾT LUẬN.

### 4. Tham số hay dùng

Tham số chung (của `dacn.py`, dùng cho mọi chế độ):

| Tham số | Ý nghĩa |
|---|---|
| `--startup` | Bật luật thư mục Startup (T1547.001), thay cho `$env:LUAT_STARTUP = '1'` |
| `--model <tên>` | Chọn mô hình Ollama, vd `--model llama3.2:3b` (mặc định `phi4-mini:latest`) |
| `--prompt-moi` | Dùng cách hỏi SLM mới, thay cho `$env:SLM_PROMPT_MOI = '1'` |
| `--moi-dot N` | (`phat-lai`) số sự kiện mỗi đợt, mặc định 1 |

Tham số được chuyển cho script của chế độ:

| Tham số | Chế độ | Ý nghĩa |
|---|---|---|
| `--khong-slm` | `quet`, `phat-lai`, `theo-doi` | Không gọi SLM, chỉ dùng luật và dấu vết. Chạy nhanh, không cần Ollama |
| `--in-dong-slm` | `quet`, `phat-lai`, `theo-doi` | In các dòng log đã gửi cho SLM |
| `--chi-tiet` | `quet` | In cả các phiên điểm thấp |
| `--tre S` | `phat-lai` | Nghỉ S giây giữa 2 đợt (để demo dễ theo dõi) |
| `--an-ten` | `theo-doi` | Thay tên máy, tên người dùng. Bật khi chụp ảnh báo cáo |
| `--nap-truoc-phut M` | `theo-doi` | Lúc bật, nạp thêm M phút log gần nhất (mặc định 10) |
| `--thu-muc A B` | `danh-gia` | Các thư mục chứa log của bộ thử |
| `--che-do khong-slm` | `danh-gia` | Chỉ đo không SLM (nhanh, không cần Ollama) |

Ví dụ ghép nhiều tham số:

```powershell
python src\dacn.py theo-doi --khong-slm --startup --an-ten
python src\dacn.py quet D:\log\a.evtx --model gemma3:4b --in-dong-slm
python src\dacn.py phat-lai D:\log\a.evtx --khong-slm --moi-dot 5 --tre 0.5
```

### 5. Ghi kết quả ra file

PowerShell 5.1 làm lỗi chữ tiếng Việt khi ghi ra file, nên phải chạy dòng đầu tiên dưới đây trước:

```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
python src\dacn.py quet D:\log\a.evtx --khong-slm > output\ket-qua.txt
```

Dòng `[dacn] chạy: ...` chỉ hiện trên màn hình, không ghi vào file.

### 6. Kết quả nằm ở đâu

- `quet`, `phat-lai`: in ra màn hình (hoặc vào file nếu dùng `>`).
- `theo-doi`: `output\theo_doi\<ngày-giờ bắt đầu>\` gồm `canh_bao.csv`, `chi_tiet.txt`, `tong_ket.md`.
- `danh-gia`: `output\danh_gia\` gồm `bang.md`, `ket_qua_phien.csv`, chi tiết từng file trong `khong-slm\` và `co-slm\`.

Thư mục `output\` không được đưa lên GitHub.

### 7. Lỗi hay gặp

| Thấy gì | Làm gì |
|---|---|
| `[dacn] không thấy: ...` | Sai đường dẫn, hoặc file bị thành `.evtx.evtx` (xem mục 1.5) |
| `invalid choice` | Thiếu tên chế độ. Lệnh phải bắt đầu bằng `python src\dacn.py quet ...` |
| `[dacn] nên đứng ở thư mục gốc repo` | `cd` về thư mục repo rồi chạy lại |
| `Không đọc được kênh Sysmon` | Mở lại PowerShell bằng "Run as administrator"; kiểm tra `Get-Service Sysmon*` |
| Kết quả có `SLM lỗi` | Ollama chưa mở hoặc chưa tải mô hình. Chạy `ollama list` để kiểm tra |
| `ModuleNotFoundError` | Chưa cài thư viện: `pip install -r requirements.txt` |
| Chữ tiếng Việt trong file bị lỗi | Chưa chạy lệnh `[Console]::OutputEncoding` ở mục 5 |


## Tiến độ

- [ ] Tuần 1: tạo repo, thu thập dữ liệu 8 kỹ thuật, nạp EVTX vào DuckDB, cài và đo 4 mô hình
