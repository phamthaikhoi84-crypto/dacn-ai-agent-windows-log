# Tuần 5 (9/11 – 15/11/2026)

## Mục tiêu tuần

Dựng xong nền móng để trả lời câu hỏi của thầy: **mô hình ngôn ngữ nhỏ (SLM) có giúp agent phát hiện tốt hơn so với chỉ dùng luật + dấu vết bắt buộc không?** Cụ thể: một bộ thử cố định có nhãn từng phiên, một chế độ chạy không SLM để so sánh, và một script đo ra bảng hai dòng (có SLM / không SLM) gồm phát hiện, báo nhầm và độ sớm.

## Phân công và kết quả

| Người | Việc | Kết quả |
|---|---|---|
| Khôi | K1: bước 4 gửi các dòng log quanh dấu vết thay vì 40 dòng đầu phiên | Xong |
| Khôi | K2: tách loại "SLM lỗi" khỏi "chưa xác nhận" | Xong |
| Khôi | K3: đổi `--ban-tam` thành `--khong-slm` (tên cũ vẫn chạy) | Xong |
| Khôi | K4: `src/danh_gia.py` đo có/không SLM trên bộ thử | Xong, đã đo trên 24 file |
| Thiên | `data/bo-thu.csv`: 21 file tấn công (nhãn từng phiên, đọc từ lệnh thật) + log bình thường | Xong, 1 dòng (comsvcs) loại ra |
| Thiên | Gửi log bình thường máy Thiên tuần 3, tuần 4 | Xong |
| Dũng | Đo lại 4 SLM sau khi sửa bước 4 | Đang đo lại với `slm.py` mới (xem mục Lần đo 1–2) |
| Dũng | Gửi log bình thường máy Dũng | Chưa có, chưa đưa vào bảng |

## Những gì đã sửa trong agent

- **Bước 4 (K1):** agent chọn tối đa 40 dòng gửi SLM theo thứ tự ưu tiên: (1) chính các sự kiện làm bằng chứng ở bước 3, (2) sự kiện tạo ra tiến trình đó, tiến trình cha, tiến trình ông, (3) các sự kiện cách bằng chứng không quá 60 giây. Mỗi dòng có đường dẫn đầy đủ và tiến trình cha. Trước đây gửi 40 dòng đầu phiên, trong khi phiên trên máy thật có hàng nghìn sự kiện và dòng đáng ngờ thường không nằm ở đầu.
- **SLM lỗi (K2):** kết quả mỗi phiên giờ có 4 loại: bình thường / chưa xác nhận / kết luận / SLM lỗi. Trước đây khi Ollama lỗi, agent tự chuyển sang chế độ không SLM và vẫn có thể kết luận, làm lẫn số đo của hai chế độ. Giờ SLM lỗi thì không kết luận và được đếm riêng.
- **`--khong-slm` (K3):** bỏ bước hỏi SLM, chọn ứng viên điểm cao nhất có đủ dấu vết.
- **`slm.py`:**
  - SLM trả **số dòng** làm bằng chứng thay vì chép lại cả dòng (chép lại dòng dài làm JSON bị cắt). `slm.py` đổi số dòng về dòng log thật, nên bước 5 vẫn kiểm tra bằng chứng có thật như cũ.
  - Gửi kèm **khuôn JSON (JSON schema)** cho Ollama: bắt buộc đủ 3 trường, đúng kiểu, mã chỉ được là một ứng viên hoặc `CHUA_XAC_NHAN`. Khuôn chỉ ép hình thức câu trả lời, không gợi ý chọn mã nào.
  - Ollama lỗi 500 thì thử lại 1 lần. Mọi lần lỗi ghi prompt + câu trả lời thô vào `output/slm_loi.txt`.
- **`danh_gia.py` (K4):** đọc `data/bo-thu.csv`, chạy từng file ở hai chế độ, kiểm tra số phiên khớp với `SoPhien` trước khi đo (lệch thì bỏ file, không đo sai), tách file đã dùng để chỉnh agent ra khỏi bảng chính, lưu log đã nạp vào DuckDB để lần sau không phải đọc lại `.evtx`.

Ảnh kiểm tra Dumpert ở cả hai chế độ sau khi sửa: `docs/hinh/tuan5-dumpert-khong-slm.png`, `docs/hinh/tuan5-dumpert-co-slm.png`.

## Bộ thử

- **Tấn công:** 21 file từ EVTX-ATTACK-SAMPLES, nhãn từng phiên do Thiên đọc từ lệnh/sự kiện thật (không dựa vào agent).
  - Loại `sysmon_10_1_memdump_comsvcs_minidump.evtx`: đích là `notepad.exe`, không phải `lsass.exe`, và đã dùng để demo.
  - Tách riêng `sysmon_10_11_outlfank_dumpert_and_andrewspecial_memdump.evtx`: đã dùng để chạy thử và sửa code tuần 4–5. Vẫn đo nhưng không tính vào bảng chính.
  - Còn lại **31 phiên tấn công** thuộc 7 kỹ thuật.
- **Bình thường:** 3290 phiên.

| Log bình thường | Số phiên | Quan hệ với mô hình |
|---|---|---|
| Máy Thiên tuần 3 (2/11–4/11) | 807 | Cùng máy với log dùng học lớp bình thường, khác thời gian (log học là 17/10–27/10) |
| Máy Thiên tuần 4 (5/11–12/11) | 1704 | Như trên |
| Máy Khôi 7 ngày | 779 | Máy lạ, chưa dùng huấn luyện hay chỉnh |
| Máy Dũng | – | Đã dùng chỉnh dấu vết; chưa có file nên chưa đo |

## Kết quả chính

Mô hình mẫu chuỗi `mau_chuoi.json` (sha256 `4255be121581`), ngưỡng 0.5, 3 ứng viên, SLM `phi4-mini:latest` chạy Ollama 100% CPU trên laptop ThinkPad T16. Commit `0c96ba2`. Bảng gốc: `docs/ket-qua/tuan5-lan4-hai-che-do.md`, độ sớm: `docs/ket-qua/tuan5-lan5-do-som.md`.

| Chế độ | Phát hiện đúng (31 phiên tấn công) | Bỏ sót: dừng bước 2 / chưa xác nhận | Báo nhầm (3290 phiên bình thường) | Độ sớm (trung vị) | SLM lỗi |
|---|---|---|---|---|---|
| Không SLM | **7 (23%)** | 18 / 6 | **19 (0,58%)** | 2 sự kiện (7 phiên) | – |
| Có SLM | **6 (19%)** | 18 / 7 | **8 (0,24%)** | 2 sự kiện (6 phiên) | 0 |

Không có trường hợp kết luận sai mã ở cả hai chế độ.

### Báo nhầm theo từng máy

| Máy | Số phiên | Không SLM | Có SLM | Bị chặn khi có SLM |
|---|---|---|---|---|
| Thiên tuần 3 | 807 | 0 | 0 | 0 |
| Thiên tuần 4 | 1704 | 4 | 2 | 2 |
| Khôi 7 ngày (máy lạ) | 779 | 15 | 6 | 9 |

### Phát hiện theo kỹ thuật

| Kỹ thuật | Số phiên | Không SLM | Có SLM |
|---|---|---|---|
| T1003.001 LSASS | 6 | 5 | 4 |
| T1053.005 Scheduled Task | 4 | 2 | 2 |
| T1021.001 RDP | 5 | 0 | 0 |
| T1105 Ingress Tool Transfer | 4 | 0 | 0 |
| T1136.001 Local Account | 7 | 0 | 0 |
| T1547.001 Run Keys / Startup | 4 | 0 | 0 |
| T1059.001 PowerShell | 1 | 0 | 0 |

## Phân tích

### SLM chưa lần nào nói "không phải tấn công"

Trong 27 lần hỏi SLM ở lần đo chính, SLM **không lần nào** chọn `CHUA_XAC_NHAN`. Mọi lần đều chọn một kỹ thuật trong danh sách ứng viên.

- **11 báo nhầm bị chặn** (9 trên máy Khôi, 2 trên máy Thiên tuần 4) đều do SLM chọn **nhầm sang một ứng viên thiếu dấu vết bắt buộc**, rồi bước 5 (kiểm chứng) gạt lựa chọn đó đi. SLM không nhận ra đó là hoạt động bình thường.
- **1 phát hiện thật bị mất** theo đúng cách đó: `babyshark_mimikatz_powershell.evtx` (T1003.001). Không SLM thì agent kết luận đúng T1003.001; có SLM thì SLM chọn T1059.001, không đủ dấu vết, thành chưa xác nhận.
- Các báo nhầm còn lại (6 trên máy Khôi, 2 trên máy Thiên) thì SLM **đồng ý** với kết luận sai, chủ yếu T1547.001.
- Trên file tấn công, khi chỉ có một ứng viên đủ dấu vết (mimikatz, lsass memdump, schtasks), SLM luôn chọn đúng, nhưng cũng không làm được gì hơn chế độ không SLM.

**Ví dụ phiên #46 máy Khôi** (ảnh `docs/hinh/tuan5-phien46-slm-chon-t1070.png`): tài khoản SYSTEM, phần mềm Lenovo tạo 3 tác vụ hẹn giờ bằng `schtasks /Create /XML` (dấu vết thật của T1053.005), cùng lúc Windows Defender gọi `wevtutil.exe` để cấu hình kênh nhật ký của Defender. SLM bỏ qua 3 dòng `schtasks`, bám vào chữ `wevtutil` và chọn T1070.001 (xóa nhật ký) dù không có lệnh xóa nào (`wevtutil cl`). Bước 5 không thấy dấu vết xóa log nên không kết luận. SLM đang nhận diện theo từ khóa, chưa suy luận được hành vi có nguy hiểm hay không.

### Điểm yếu lớn nhất là bước 2, không phải SLM

18/24 phiên bỏ sót dừng ngay ở bước 2: mô hình mẫu chuỗi cho điểm dưới ngưỡng, không nhận ra hành vi. Bốn kỹ thuật T1021.001, T1105, T1136.001, T1547.001 phát hiện 0%. Nhiều file trong số này chỉ có 1–4 sự kiện (ví dụ một Event 13 ghi khóa Run duy nhất), không đủ để thành chuỗi.

### Thời gian

| Trường hợp | Thời gian mỗi lần hỏi SLM |
|---|---|
| Phiên trên máy thật, gửi 24–40 dòng | 35–125 giây, khoảng 70 giây trung bình |
| Phiên trong file tấn công, gửi 1–10 dòng | 9–17 giây |

Laptop chạy Ollama hoàn toàn bằng CPU. Đo trên toàn bộ bộ thử: không SLM 42 phút, có SLM 35 phút, trong đó 26 lần hỏi SLM chiếm 24 phút. (Phần lớn thời gian còn lại là nạp file `.evtx` lớn của máy Thiên; lần chạy có SLM dùng lại dữ liệu đã nạp.)

## Quá trình đo (ghi đủ để không bỏ sót lần nào)

| Lần | Dữ liệu | Thay đổi | Kết quả |
|---|---|---|---|
| 1 | Máy Khôi | `slm.py` dùng `"format": "json"` | 13 lần hỏi (dừng giữa chừng): 3 kết luận, 2 chưa xác nhận, **8 SLM lỗi** (4 JSON sai cấu trúc, 2 bị cắt, 2 Ollama lỗi 500) |
| 2 | Máy Khôi | Thêm khuôn JSON + thử lại khi lỗi 500 | 15 lần hỏi, **0 lỗi**, báo nhầm 15 → 6 |
| 3 | Máy Khôi + Thiên, không SLM | – | Báo nhầm 19/3290; khớp số Thiên ghi (4 trên máy Thiên tuần 4) |
| 4 | Toàn bộ bộ thử, hai chế độ | – | Bảng chính ở trên |
| 5 | File tấn công, hai chế độ | Đo độ sớm | Trung vị 2 sự kiện ở cả hai chế độ |

Giữa lần 1 và lần 2 chỉ sửa **định dạng đầu ra** của SLM (lỗi kỹ thuật), không sửa prompt hay cách chọn. Lần 2 và lần 4 cho cùng kết quả trên máy Khôi (15 → 6), vì SLM chạy temperature 0.

## Kết luận tạm

- Với `phi4-mini` và cách hỏi hiện tại, SLM **chưa giúp được** theo nghĩa thầy hỏi. Báo nhầm giảm 19 → 8 là nhờ bước kiểm chứng gạt bỏ lựa chọn sai của SLM, và chính cơ chế đó làm mất 1/7 phát hiện thật.
- Phần đóng góp chính đang nằm ở **luật + dấu vết bắt buộc + bước kiểm chứng**. Bước kiểm chứng cũng là thứ giữ cho SLM không làm agent kết luận bừa.
- Bộ thử còn nhỏ (31 phiên tấn công, 1 phiên T1059.001) nên các tỉ lệ theo kỹ thuật chỉ mang tính tham khảo.

## Hạn chế cần ghi rõ

- Log máy Dũng chưa có. Theo `bo-thu.csv` máy này đã dùng để chỉnh dấu vết, nên khi có cũng không tính vào báo nhầm chính thức.
- Máy Thiên là cùng máy với log dùng học lớp bình thường (khác thời gian), nên chỉ máy Khôi là "máy chưa dùng huấn luyện" đúng nghĩa.
- Cần xác nhận file `LM_sysmon_3_12_13_1_SharpRDP.evtx` có từng được dùng khi thiết kế `ky_hieu.py` (ghi chú RunMRU) không. Nếu có thì phải tách ra như Dumpert.

## Việc tuần 6

1. **Bước 2 (quan trọng nhất):** tìm vì sao 18 phiên dừng ở bước 2, nhất là các file 1–4 sự kiện. Mọi chỉnh sửa phải làm trên dữ liệu khác (Splunk Attack Data, OTRF), **không chỉnh theo bộ thử này**, rồi mới đo lại trên bộ thử.
2. **SLM:** thử cho SLM biết kết quả bước 3 (ứng viên nào thiếu dấu vết) và cho phép trả lời "hoạt động bình thường". Chỉnh trên log máy Dũng, đo trên bộ thử.
3. Dũng: bảng so sánh 4 SLM với `slm.py` mới, gồm số lần SLM lỗi, số lần chọn `CHUA_XAC_NHAN`, thời gian mỗi lần hỏi.
4. Thiên: bổ sung phiên tấn công cho các kỹ thuật ít mẫu (T1059.001 mới có 1 phiên), từ nguồn chưa dùng.
5. Độ sớm ở chế độ phát lại (agent xem log dần theo thời gian), để đúng với yêu cầu "nhận ra sớm từ vài sự kiện đầu".

## Dùng AI

Claude hỗ trợ sửa `agent.py`, `slm.py`, `dau_vet.py` (K1–K3), viết `danh_gia.py` (K4) và phân tích kết quả. Khôi chạy kiểm tra trên máy trước mỗi lần commit. Nội dung trao đổi lưu trong `ai-logs/`.
