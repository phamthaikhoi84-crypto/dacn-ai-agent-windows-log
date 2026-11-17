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

(Điền cuối tuần.)
