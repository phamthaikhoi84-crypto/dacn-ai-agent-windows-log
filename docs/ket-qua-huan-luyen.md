# Kết quả huấn luyện và đo lường

Phần của Thiên (dữ liệu, nhãn, huấn luyện). Số liệu lấy từ các lần tự chạy `src/train.py`, `src/agent.py` và `src/dau_vet.py`, cập nhật ngày 6/11/2026 (có thêm kết quả trên máy Khôi). Mô hình: `models/mau_chuoi.json` (commit `5c8a3fa`, ký hiệu theo `ky_hieu.py` commit `6defe92`).

## 1. Dữ liệu và nhãn

- `data/nhan-file.csv`: 64 file Splunk Attack Data, 45 file có chuỗi có nhãn dùng được.
- 292 chuỗi có nhãn, còn **128 chuỗi** sau khi bỏ chuỗi trùng nhau trong cùng một file.
- Nhãn gán theo cây tiến trình: gốc là tiến trình có sự kiện khớp dấu hiệu của kỹ thuật, chuỗi gồm các sự kiện thuộc cây đó (Event 1, 3, 11, 12, 13, 14 và Event 10 vào lsass).

| Kỹ thuật | File | Chuỗi |
|---|---|---|
| T1003.001 | 3 | 15 |
| T1021.001 | 8 | 11 |
| T1053.005 | 7 | 15 |
| T1059.001 | 16 | 54 |
| T1070.001 | 2 | 3 |
| T1105 | 5 | 14 |
| T1136.001 | 1 | 3 |
| T1547.001 | 3 | 13 |

## 2. Cách học

- Mỗi sự kiện đổi thành một ký hiệu (ví dụ `TAO_TIEN_TRINH:certutil.exe`, `MO_BO_NHO:lsass.exe:DOC_BO_NHO`).
- Mô hình đếm các đoạn 1, 2, 3 ký hiệu liên tiếp trong chuỗi của từng kỹ thuật, cửa sổ trượt 6 ký hiệu.
- Điểm của một đoạn là xác suất kỹ thuật k khi gặp đoạn đó, có tính **tỉ lệ gốc 1e-2** (một cửa sổ tấn công hiếm hơn cửa sổ bình thường) và **lớp bình thường** học từ 60% đầu (603 phiên) log bình thường của máy Thiên. Điểm cửa sổ lấy đoạn cao nhất.
- Bảng "sau ký hiệu A thường là B" học riêng cho từng kỹ thuật, dùng để đoán bước kế tiếp.

## 3. Bảng tỉ lệ đoán đúng (bỏ lần lượt từng file ra thử)

Mỗi lần bỏ một file ra, học từ các file còn lại, rồi thử trên file bị bỏ. Kỹ thuật chỉ có một file thì bỏ lần lượt từng chuỗi. Mỗi kỹ thuật tính trọng số như nhau.

| Kỹ thuật | File | Chuỗi | Đoán đúng kỹ thuật | Không nhận ra | Đoán đúng bước kế (số mẫu) |
|---|---|---|---|---|---|
| T1003.001 | 3 | 15 | 47% | 7% | 13% (45) |
| T1021.001 | 8 | 11 | 55% | 18% | 0% (1) |
| T1053.005 | 7 | 15 | 93% | 0% | 18% (17) |
| T1059.001 | 16 | 54 | 83% | 0% | 39% (569) |
| T1070.001 | 2 | 3 | 67% | 0% | 50% (2), ít dữ liệu |
| T1105 | 5 | 14 | 43% | 7% | 31% (29) |
| T1136.001 | 1 | 3 | 67% | 0% | 86% (7), 1 file, ít dữ liệu |
| T1547.001 | 3 | 13 | 62% | 0% | 42% (97) |
| **Trung bình** | | | **64%** | | |

- "Đoán đúng kỹ thuật": kỹ thuật điểm cao nhất trùng nhãn, chưa áp ngưỡng. Khi áp ngưỡng 0,5 (ngưỡng agent dùng) thì tỉ lệ này là 55%.
- Nhầm lẫn hay gặp (nhãn thật sang dự đoán): T1105 sang T1059.001 (5 chuỗi), T1547.001 sang T1059.001 (5), T1003.001 sang T1059.001 (4), T1059.001 sang T1136.001 (4), T1059.001 sang T1003.001 (3).
- T1070.001 và T1136.001 chỉ có 3 chuỗi nên tỉ lệ của hai kỹ thuật này chưa đáng tin.
- Đoán bước kế còn yếu: T1003.001 13%, T1053.005 18%.

## 4. Báo động giả của bước 2 (khớp chuỗi) trên log bình thường

Log bình thường máy Thiên: 402 phiên cuối của tuần 2 (không dùng để học), 20.240 cửa sổ, khoảng 6,4 ngày.

| Ngưỡng | Đoán đúng (có áp ngưỡng) | Cảnh báo giả | Cảnh báo giả mỗi ngày |
|---|---|---|---|
| 0,3 | 55% | 62 | 9,7 |
| **0,5** | **55%** | **39** | **6,1** |

Trước khi thêm lớp bình thường và tỉ lệ gốc (bản 5), cùng log này cho khoảng 56 đến 61 cảnh báo giả mỗi ngày.

## 5. Dấu vết bắt buộc (bước 3, `src/dau_vet.py`)

Chạy trên 45 file Splunk **trước khi Khôi sửa** (commit `e079e87`): đủ dấu vết của kỹ thuật đúng ở **36/45 file (80%)**, trung bình theo kỹ thuật 84%.

| Kỹ thuật | Đủ dấu vết |
|---|---|
| T1053.005, T1070.001, T1136.001, T1547.001 | 7/7, 2/2, 1/1, 3/3 |
| T1059.001 | 14/16 |
| T1105 | 4/5 |
| T1003.001 | 2/3 |
| T1021.001 | 3/8 |

9 file thiếu vì: file RDP chỉ có dấu vết trên đĩa (5 file), lệnh `curl.exe"` có ngoặc kép (1 file), và 3 file mà nhãn đáng nghi (`createdump` dump tiến trình .NET, `soaphound` không dùng PowerShell, `trickbot` chưa rõ). Khôi đã sửa dấu vết T1003.001, T1021.001, T1053.005, T1105.

Số sự kiện khớp dấu vết trong log bình thường máy Thiên (trước khi sửa): T1547.001 333, T1053.005 62, T1059.001 36, T1003.001 4 (đều là `wininit.exe`, `csrss.exe` lúc khởi động), các kỹ thuật còn lại 0.

## 6. Agent đầu-cuối (5 bước, ngưỡng 0,5)

| Log | Số phiên | Qua bước 2 | Bị kết luận tấn công (đều là báo giả) |
|---|---|---|---|
| Máy Dũng, trước khi sửa dấu vết | 2.573 | 91 (3,5%) | 46 (1,79%) |
| Máy Dũng, sau khi sửa | 2.573 | 91 (3,5%) | **10 (0,39%)** |
| Máy Thiên, log mới 2/11 đến 4/11 | 807 | 12 (1,5%) | **0** |
| **Máy Khôi, log 7 ngày (cấu hình Sysmon chung, theo Khôi không chạy công cụ tấn công)** | 779 | 44 (5,6%) | **15 (1,9%)** |
| `demo_nho.evtx` (đoạn nhỏ của Dũng) | 16 | 3 | **0** |

- 10 phiên còn lại trên máy Dũng: 4 T1547.001 (`browser.exe`, `runonce.exe` ghi khóa Run), 4 T1059.001 (PowerShell bộ cài `-ExecutionPolicy Bypass`), 2 T1053.005 (Office `schtasks /Create ... Office Feature Updates`).
- 0 trên 807 phiên nghĩa là tỉ lệ báo giả khoảng 0 với cận trên 95% khoảng 0,4%. Nhưng log này cùng máy với dữ liệu học lớp bình thường.
- **Máy Khôi (máy lạ, chưa nằm trong dữ liệu học hay chỉnh dấu vết nào):** 15 phiên bị kết luận nhầm trên 779 phiên (1,9%, khoảng tin cậy 95% xấp xỉ 1,2% đến 3,2%). Ba nguyên nhân gốc, đều là phần mềm hợp lệ: (1) Lenovo chạy dưới SYSTEM sau mỗi lần khởi động, `schtasks /Create /TN "LvfDriverRemoval" /XML C:\Windows\TEMP\...` (T1053.005); (2) Edge và UniKey ghi khóa Run (T1547.001); (3) PowerShell chạy ẩn để kiểm tra VS Code (T1059.001). Lần đo đầu trên 2 ngày đầu của log này cho 6/242 (2,5%), cùng khoảng tin cậy, và không cộng dồn với số 779.
- Tỉ lệ phiên qua bước 2 tăng theo độ xa so với dữ liệu học: máy Thiên 1,5%, máy Dũng 3,5%, máy Khôi 5,6% (lần đo 2 ngày đầu là 8,3%).

Phép thử mô hình ngôn ngữ trên 6 phiên của máy Khôi (phi4-mini, chạy ngày 6/11): 3 phiên mô hình chọn sai T1070.001 và bước 5 chặn, 2 phiên phản hồi bị cắt, 1 phiên Ollama báo lỗi 500. **Không phiên nào được mô hình nhận ra là bình thường**, nên chưa có bằng chứng bước 4 giúp loại báo giả (bước 5 chặn kết luận sai là việc của bước kiểm chứng, không phải của mô hình). Nguyên nhân Khôi nêu: phiên trên máy thật rất dài (phiên 41 hơn 3 giờ, 5.604 sự kiện), bước 4 chỉ gửi 40 dòng đầu nên mô hình không thấy dòng đáng ngờ; và bước 3 tìm dấu vết trong cả phiên nên phiên dài dễ tìm thấy dấu vết không liên quan đoạn khớp ở bước 2. Hướng sửa: chỉ tìm dấu vết gần đoạn khớp (để tuần sau).

Ca tấn công ngoài tập huấn luyện (EVTX-ATTACK-SAMPLES), chạy với `--ban-tam`:

| File | Kết luận |
|---|---|
| `rundll32_cmd_schtask` | T1053.005, 0,865, đúng |
| `babyshark_mimikatz_powershell` phiên 4 | T1003.001, 0,760, đúng (bước 2 xếp T1053.005 0,898, bước 3 loại vì thiếu `schtasks /create`) |
| `DE_timestomp_and_dll_sideloading_and_RunPersist` phiên 1 | T1547.001, 0,910, đúng |
| `CA_sysmon_hashdump_cmd_meterpreter` (chạy 30/10) | T1003.001, 0,760, đúng (chỉ 1 sự kiện lsass) |
| `CA_teamviewer-dumper_sysmon_10` (chạy 30/10), `sideloading_..._run_key` (chạy 30/10) | bỏ sót, log quá ngắn (1 và 7 sự kiện) |

## 7. Hạn chế

- Ký hiệu không có nội dung dòng lệnh (không phân biệt `net user /add` với `net use`), nên bước 2 chỉ là bộ lọc thô và dấu vết bắt buộc mới quyết định kết luận.
- Công cụ chưa gặp khi huấn luyện (ví dụ `createdump.exe`) không khớp được vì ký hiệu chứa tên tiến trình.
- T1070.001 và T1136.001 chỉ có 3 chuỗi.
- Lớp bình thường học từ một máy (máy Thiên). Log của Dũng đã được dùng để chỉnh dấu vết, nên 0,39% là số trên dữ liệu đã dùng để chỉnh. Log mới của máy Thiên (0 trên 807 phiên) cùng máy với dữ liệu học. **Chỉ có một log từ máy lạ (máy Khôi, 779 phiên trong 7 ngày): 15 phiên bị kết luận nhầm (1,9%).** Số này mới có một máy, nên chưa nói được tỉ lệ trên máy bất kỳ.
- Hoạt động hợp lệ tạo đúng dấu vết tấn công (Office, Lenovo, PowerShell bộ cài, ứng dụng ghi khóa Run) vẫn còn báo giả. Đây là điểm yếu chính của hai kỹ thuật T1053.005 và T1547.001: phần mềm hợp lệ làm đúng việc mà kẻ tấn công làm.
- Phiên rất dài (hàng nghìn sự kiện) làm bước 3 dễ thấy dấu vết ở chỗ không liên quan đoạn khớp ở bước 2, và bước 4 chỉ gửi 40 dòng đầu cho mô hình ngôn ngữ.
- Hai nhãn đáng nghi: `createdump_windows-sysmon.log` (T1003.001) và `sysmon_soaphound.log` (T1059.001).

## 8. Trả lời câu hỏi "log bình thường chiếm 99,99%"

Log bình thường nhiều hơn log tấn công rất nhiều, nên bộ lọc chỉ đoán "giống tấn công" sẽ báo giả nhiều. Agent xử lý bằng ba lớp:

1. **Lớp bình thường và tỉ lệ gốc trong điểm** (bước 2): đưa cảnh báo giả trên log của Thiên từ khoảng 56 xuống khoảng 6 mỗi ngày (ngưỡng 0,5).
2. **Dấu vết bắt buộc** (bước 3): kỹ thuật chỉ được xét tiếp khi tìm thấy dấu vết thật trong log (ví dụ `schtasks /create`, mở lsass có quyền đọc). Thiếu dấu vết thì "chưa xác nhận".
3. **Kiểm chứng** (bước 5): kỹ thuật chọn phải nằm trong ứng viên, đủ dấu vết, điểm đạt ngưỡng, và dòng log trích làm bằng chứng phải có thật.

Kết quả: máy Thiên (log mới) 0 phiên nhầm trên 807; máy Dũng 10 phiên nhầm trên 2.573 (0,39%); máy Khôi, máy lạ, 15 phiên nhầm trên 779 (1,9%, khoảng tin cậy 95% xấp xỉ 1,2% đến 3,2%, ba nguyên nhân gốc). Tức là tỉ lệ báo giả cuối cùng khoảng 0 đến vài phần trăm số phiên tùy máy, thấp hơn nhiều so với chỉ so khớp chuỗi (1,5% đến 5,6% phiên qua bước 2), nhưng chưa về 0 trên máy lạ. Phần còn lại chủ yếu là phần mềm hợp lệ tạo tác vụ hẹn giờ hay khóa Run.
