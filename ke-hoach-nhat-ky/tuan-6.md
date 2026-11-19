# Tuần 6 (16/11 – 22/11/2026)

## Mục tiêu tuần

Tuần 6 là mốc phải xong khoảng 70–80% đồ án. Cuối kỳ thầy cần 4 thứ: agent theo dõi log trực tiếp trên máy, bảng có SLM / không SLM, số báo nhầm trên máy chưa dùng huấn luyện, và bảng so sánh các SLM. Sau tuần 5 đã có bảng có/không SLM và số báo nhầm trên máy Khôi. Tuần này làm nốt hai phần còn thiếu, và xử lý hai điểm yếu tuần 5 đã chỉ ra:

1. **Theo dõi trực tiếp:** agent đọc sự kiện mới từ Sysmon trên máy đang chạy và báo ngay, không cần xuất file `.evtx`.
2. **Bảng so sánh 4 SLM** trên cùng bộ thử với `danh_gia.py`.
3. **Bước 2 bỏ sót nhiều:** 18/24 phiên bỏ sót dừng ở bước 2.
4. **SLM chưa bao giờ trả lời "bình thường":** thử cách hỏi mới cho SLM.

Quy tắc giữ nguyên từ tuần 5: mọi chỉnh sửa bước 2 và cách hỏi SLM đều làm trên **bộ phát triển** (dữ liệu khác bộ thử). Bộ thử `data/bo-thu.csv` chỉ dùng để đo, đo một lần cuối tuần sau khi chốt.

## Phân công

### Khôi (agent, theo dõi trực tiếp, đo)

| Việc | Xong khi |
|---|---|
| K1. `src/theo_doi.py`: cứ vài giây đọc sự kiện mới của kênh `Microsoft-Windows-Sysmon/Operational` (và PowerShell 4104) theo RecordID, nạp vào DuckDB, chạy 5 bước trên các phiên vừa có sự kiện mới, in cảnh báo và ghi ra file | Chạy trên máy Khôi; tạo một tác vụ hẹn giờ thử vô hại bằng `schtasks /create` (mở notepad, xóa ngay sau đó) thì agent kết luận T1053.005, có ghi số giây từ lúc tạo đến lúc báo |
| K2. Chạy theo dõi trực tiếp 1–2 giờ trong lúc dùng máy bình thường | Có số cảnh báo / giờ và ảnh chụp màn hình cho báo cáo |
| K3. Chạy 3 SLM còn lại bằng `danh_gia.py` trên máy Khôi (nếu chưa chạy), thêm log máy Dũng khi nhận được | Có `docs/ket-qua/tuan5-slm-*.md` cho cả 4 mô hình, chuyển cho Dũng |
| K4. Sửa `agent.py` nhận câu trả lời "bình thường" của SLM (phối hợp với D3), đo lần cuối trên bộ thử | Bảng lần 6 trong `docs/ket-qua/` |
| K5. Cài Sysmon lên máy cũ làm máy lạ thứ hai, để thu log đến hết tuần 7 | Sysmon chạy, ghi ngày bắt đầu thu vào `docs/log-binh-thuong.md` |
| K6. Che tên máy trong ảnh `docs/hinh/tuan5-phien46-slm-chon-t1070.png` rồi commit lại | Ảnh không còn tên máy, tên người dùng |
| K7. `tuan-6.md`, phiếu tiến độ, `ai-logs/` | Đã push |

### Thiên (dữ liệu, bước 2)

| Việc | Xong khi |
|---|---|
| T1. Phân loại nguyên nhân 18 phiên dừng ở bước 2: quá ít sự kiện (1–4), ký hiệu không có trong mẫu đã học, hay chuỗi khác hẳn dữ liệu train. Chỉ đọc và phân loại, không sửa theo bộ thử | Bảng phân loại trong `docs/ket-qua-huan-luyen.md` |
| T2. `data/bo-phat-trien.csv`: file tấn công 8 kỹ thuật lấy từ Splunk Attack Data / OTRF, không có trong bộ thử và không dùng khi train | Cùng định dạng với `bo-thu.csv`, nhãn từng phiên |
| T3. Thử sửa bước 2 trên bộ phát triển theo nguyên nhân ở T1 (ví dụ cách chấm điểm cho phiên ngắn), ghi tỉ lệ trước và sau | Có kết quả trên bộ phát triển; chỉ khi tốt hơn mới chốt `mau_chuoi.json` mới để đo trên bộ thử |
| T4. Xác nhận file SharpRDP có từng dùng khi thiết kế `ky_hieu.py` không; cập nhật `docs/danh-gia.md` cho khớp cách tính trong `danh_gia.py` (độ sớm, tách file đã dùng chỉnh, bỏ comsvcs) | `docs/danh-gia.md` và `bo-thu.csv` đã sửa |

### Dũng (SLM)

| Việc | Xong khi |
|---|---|
| D1. Gửi `benign_sysmon_dung.evtx` lên Drive cho Khôi | Khôi nhận được |
| D2. `docs/models.md`: bảng so sánh 4 SLM từ kết quả `danh_gia.py` (phát hiện, báo nhầm, số lần SLM lỗi, số lần chọn "chưa xác nhận", thời gian trung bình mỗi lần hỏi, RAM) và nhận xét từng mô hình | Bảng 4 dòng trên cùng bộ thử |
| D3. Cách hỏi mới cho SLM (`slm.py`, bật bằng biến môi trường để giữ được cách hỏi cũ): cho SLM biết ứng viên nào đủ / thiếu dấu vết ở bước 3, và thêm lựa chọn "BINH_THUONG". Chỉnh trên log máy Dũng và bộ phát triển, không chỉnh trên bộ thử | SLM chọn được "BINH_THUONG" ở các phiên Lenovo/Defender trên log máy Dũng mà không mất phát hiện trên bộ phát triển |

## Mốc trong tuần

| Ngày | Khôi | Thiên | Dũng |
|---|---|---|---|
| Tối T4 18/11 | `theo_doi.py` đọc và in được sự kiện mới từ kênh Sysmon | Xong T1 (phân loại 18 phiên) | Xong D1 (gửi log) |
| Tối T5 19/11 | Theo dõi trực tiếp chạy đủ 5 bước, thử `schtasks` | Xong T2 (bộ phát triển) | D3 chạy được trên log máy Dũng |
| Tối T6 20/11 | Chạy theo dõi 1–2 giờ; sửa `agent.py` cho "BINH_THUONG"; tối chạy đo lần 6 trên bộ thử | Kết quả T3; T4 | Xong D2 (bảng 4 SLM) |
| T7 21/11 | Báo cáo: demo theo dõi trực tiếp + bảng có/không SLM | Báo cáo: bộ thử, bộ phát triển, nguyên nhân bước 2 | Báo cáo: bảng 4 SLM, cách hỏi mới |
| CN 22/11 | `tuan-6.md`, phiếu, `ai-logs/`, nộp LMS nếu báo cáo online | | |

## Vượt tiến độ (làm khi phần chính đã xong)

| Người | Việc | Vì sao đáng làm |
|---|---|---|
| Khôi | `src/dacn.py`: một cửa vào cho mọi chế độ (`quet`, `phat-lai`, `theo-doi`, `danh-gia`) và mục "Cách chạy" trong README | Thầy và người chấm chạy được agent bằng một lệnh |
| Khôi | Để theo dõi trực tiếp chạy 24 giờ trên máy, đếm số cảnh báo / ngày | Trả lời trực tiếp câu hỏi "99,99% log là bình thường thì sao" bằng số thật |
| Dũng | Thử thêm 1 SLM lớn hơn (`qwen3:8b`) với cách hỏi mới | Xem SLM lớn hơn có biết trả lời "bình thường" không, cho bảng so sánh có chiều sâu |
| Dũng | Trang Streamlit đọc `bang.md` và file cảnh báo của `theo_doi.py` | Kéo phần giao diện từ tuần 9 lên |
| Thiên | Bắt đầu viết chương dữ liệu và chương đánh giá của báo cáo cuối kỳ, dùng `docs/danh-gia.md`, `bo-thu.csv`, bảng tuần 5 | Giảm việc viết dồn vào tuần 9–10 |

## Khi nào coi là đạt 70–80%

- Agent chạy trên `.evtx`, chạy phát lại, và theo dõi trực tiếp trên máy thật.
- Có bảng có SLM / không SLM trên bộ thử cố định (phát hiện, báo nhầm, độ sớm), kèm báo nhầm trên máy chưa dùng huấn luyện.
- Có bảng so sánh 4 SLM.
- Còn lại cho tuần 7–10: máy lạ thứ hai, cải thiện bước 2 và cách hỏi SLM, giao diện, viết báo cáo cuối kỳ.

## Kết quả

(Đang điền dần, phần còn lại điền cuối tuần.)

### K1. Theo dõi trực tiếp (`src/theo_doi.py`)

- Cứ 3 giây đọc sự kiện mới của kênh `Microsoft-Windows-Sysmon/Operational` và PowerShell 4104 theo RecordID (pywin32), nạp vào DuckDB, chạy 5 bước của `agent.py` trên các phiên vừa có sự kiện mới. Không cần xuất `.evtx`. Bỏ sự kiện do chính agent tạo ra. Phiên đã kết luận thì đặt mốc, sự kiện đến sau được xét như một đoạn mới của phiên.
- Thử trên máy Khôi bằng `schtasks /create /tn DACN_ThuNghiem /tr notepad.exe /sc once /st 23:59 /f`, rồi xóa ngay:

| Chế độ | Ngày | Agent đọc được sau | Hỏi SLM | Báo sau | Kết luận |
|---|---|---|---|---|---|
| Không SLM | 18/11 | 4,1 giây | – | 5,9 giây | T1053.005 |
| Có SLM (phi4-mini) | 19/11 | 4,7 giây | 18,6 giây (5 dòng, 1 ứng viên) | 23,4 giây | T1053.005 |

- Cả hai lần, lệnh `schtasks /delete` ngay sau đó không bị báo: chuỗi giống T1053.005 nhưng thiếu dấu vết `/create`, dừng ở CHƯA XÁC NHẬN.
- SLM chọn đúng mã nhưng phần lý do không nhắc tới `schtasks /create` (giải thích là "chạy công việc cho Windows Terminal"). Khớp nhận xét tuần 5: phi4-mini nhận diện theo từ khóa, chưa suy luận.
- Thời gian SLM phụ thuộc số dòng gửi: lần này 1 ứng viên, 5 dòng; phiên nhiều ứng viên, 40 dòng có thể mất tới khoảng 2 phút (đo tuần 5).
- Thử trước bằng cách nạp dần `may-khoi-2ngay.evtx` (16.440 sự kiện, 100 sự kiện mỗi lần): 8 cảnh báo, so với 6 khi chạy `agent.py --khong-slm` trên cả file. 2 cảnh báo thêm là "đoạn 2" sau mốc, có bằng chứng mới.
- Ảnh: `docs/hinh/tuan6-k1-theo-doi-co-slm.png`, `docs/hinh/tuan6-k1-tong-ket-co-slm.png`.

### K2. Theo dõi trực tiếp khi dùng máy bình thường

- 19/11, 18:07–19:22 (75,5 phút), không SLM, máy Khôi, dùng máy như mọi ngày, không thử gì.
- Đọc 3.901 sự kiện Sysmon và 43 sự kiện PowerShell 4104, theo dõi 63 phiên: **0 cảnh báo**.
- 0 lần trong khoảng 1,26 giờ chỉ cho phép kết luận tần suất báo nhầm dưới khoảng 2,4 lần / giờ (độ tin cậy 95%, quy tắc 3/n). Cần chạy lâu hơn (24 giờ) để có số chặt hơn.
- 4 phiên lên bước 3 nhưng dừng ở CHƯA XÁC NHẬN vì thiếu dấu vết bắt buộc (1 phiên thuộc 10 phút log nạp trước khi bật):

| Phiên | Giống | Thực tế | Thiếu |
|---|---|---|---|
| #3, SYSTEM, 162 sự kiện | T1053.005, T1070.001 | Lenovo Vantage chạy `schtasks`, `wevtutil`, `icacls`, `taskkill` (cùng kiểu phiên #46 tuần 5) | `schtasks /create`, `wevtutil cl` |
| #11, #56, SYSTEM, 2 và 6 sự kiện | T1053.005 | Khả năng cao là Task Scheduler ghi file tác vụ (file không đuôi); cùng dạng phiên xuất hiện ngay sau lệnh `schtasks /create` ở K1 | lệnh tạo tác vụ |
| #39, người dùng, 16 sự kiện | T1547.001 | WPS Office (`ksomisc.exe`) chạy theo lịch, Disk Cleanup và công cụ chẩn đoán Windows tạo file `.ps1`, `.dll` tạm | khóa Run, thư mục Startup |

- Không phiên nào đủ dấu vết nên SLM không được hỏi; chế độ có SLM cũng sẽ ra 0 cảnh báo trong khoảng này.
- Ghi nhận: một ký hiệu chung `TAO_FILE:*(không đuôi)` đã được 0,679 điểm cho T1053.005, vượt ngưỡng 0,5. Phiên ngắn với ký hiệu chung không chỉ làm sót tấn công (T1 của Thiên) mà còn đẩy hoạt động bình thường lên bước 3. Chỉ ghi nhận, không chỉnh theo dữ liệu này.
- Ảnh: `docs/hinh/tuan6-k2-tong-ket.png`.

### K6. Ảnh phiên #46 tuần 5

- `docs/hinh/tuan5-phien46-slm-chon-t1070.png`: đã thay tên máy bằng `MAY-KHOI`.
