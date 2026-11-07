# Tuần 4 (02/11 – 08/11/2026)

Báo cáo gộp tuần 3 và tuần 4 theo yêu cầu thầy ngày 07/11: đưa lên GitHub việc đã làm và chỗ đang kẹt. Tuần 3 xem [tuan-3.md](tuan-3.md).

## Mục tiêu tuần

Không thêm tính năng lớn, tập trung vào 3 việc: (1) số liệu đánh giá, nhất là báo nhầm trên log bình thường; (2) demo thể hiện rõ vòng lặp agent; (3) xác định chỗ đang kẹt để hỏi thầy.

## Đã làm

| Người | Việc | Kết quả | File |
|---|---|---|---|
| Khôi | Chế độ phát lại `--phat-lai` | Nạp log theo thời gian từng đợt, chỉ in khi quyết định của một phiên thay đổi. File Dumpert: sự kiện 1 "chưa xác nhận" (chuỗi giống nhưng chưa có dấu vết), sự kiện 2 "kết luận T1003.001". `demo_nho.evtx`: 16 phiên, 0 kết luận, giống hệt chế độ thường | [src/agent.py](../src/agent.py) |
| Khôi | Sửa ghép nối agent và `slm.py` | Trước khi sửa, cả 3 model đều bỏ sót file Dumpert; sau khi sửa, cả 3 đều kết luận đúng (chi tiết bên dưới) | [src/slm.py](../src/slm.py), [src/agent.py](../src/agent.py) |
| Khôi | Đo báo nhầm trên máy chưa dùng để train hay chỉnh (máy Khôi) | 7 ngày, 779 phiên, 15 kết luận nhầm (1,9%), 3 nguyên nhân gốc | |
| Thiên | Bảng tỷ lệ đúng, đo log mới, khoảng tin cậy, kiểm tra `dau_vet.py` trên Splunk | Trung bình 64%; 0/807 phiên trên log mới máy Thiên | [docs/ket-qua-huan-luyen.md](../docs/ket-qua-huan-luyen.md) |
| Dũng | Thử agent trên CapAttack (dữ liệu chưa dùng khi train) | 429 sự kiện, 21 phiên; phát hiện T1003.001 ở 2 phiên (ProcDump, điểm 0,978); các phiên thiếu dấu vết giữ "chưa xác nhận" | chưa đưa lên repo |
| Dũng | Câu trả lời 99,99% log bình thường | Xong | [docs/log-binh-thuong.md](../docs/log-binh-thuong.md) |
| Dũng | So sánh model ở bước 4 | Chưa xong, chuyển sang tuần sau | [docs/models.md](../docs/models.md) |

## Sửa ghép nối bước 4 (mô hình ngôn ngữ)

Trước khi sửa, cả phi4-mini, llama3.2:3b và gemma3:4b đều trả "chưa xác nhận" cho file Dumpert. Nguyên nhân nằm ở phần ghép nối, không phải ở mô hình:

1. `slm.py` tìm dòng dạng `EventID=10 GrantedAccess=...`, còn agent gửi dạng `07:35:37 [10] ... (quyền 0x1fffff)`, nên phần tự kiểm tra lsass luôn trả False rồi ép kết quả thành "chưa xác nhận".
2. Dòng log bị nối bằng `json.dumps` nên dấu `\` bị nhân đôi; bằng chứng chép đúng vẫn không khớp.
3. Prompt bị lặp 2 bản, có quy tắc sai (bắt buộc có quyền 0x0400, trong khi Mimikatz dùng 0x1010); `num_ctx: 2048` làm prompt bị cắt mất phần đầu.
4. Mô hình gọi sai tên kỹ thuật (T1003.001 bị gọi là "Process Injection").

Cách sửa theo một nguyên tắc: **cái gì tính chắc chắn được bằng code thì code tính sẵn rồi đưa cho mô hình** (ý nghĩa quyền ghi ngay trong dòng log, tên chính thức của 8 kỹ thuật ghi trong prompt). Mô hình chỉ đọc hiểu và giải thích. Sau khi sửa, với file Dumpert:

| Model | Kết quả | Bằng chứng có thật trong log |
|---|---|---|
| phi4-mini | KẾT LUẬN T1003.001 | 3/3 |
| llama3.2:3b | KẾT LUẬN T1003.001 | 3/3 |
| gemma3:4b | KẾT LUẬN T1003.001 | 1/1 |

<!-- ![Dumpert với SLM thật](../docs/hinh/tuan4-dumpert-slm.png) -->

## Demo phát lại

Lệnh: `python src\agent.py <file Dumpert> --phat-lai --ban-tam --tre 1`

Sự kiện đầu tiên (`Outflank-Dumpert.exe` khởi chạy) cho điểm khớp 0,898 với T1003.001 nhưng chưa có dấu vết đọc bộ nhớ lsass, nên agent ghi "chưa xác nhận" và chờ. Sự kiện thứ hai (mở lsass với quyền 0x1fffff) đủ dấu vết, agent chuyển sang "kết luận" và dự đoán bước tiếp theo là tạo file `.dmp`, đúng với sự kiện tiếp theo trong log.

<!-- ![Phát lại file Dumpert](../docs/hinh/tuan4-phat-lai.png) -->

## Báo nhầm trên log bình thường

Chạy với `--ban-tam` (bước 4 luôn đồng ý), tức là đo trường hợp xấu nhất của bước 2, 3 và 5.

| Log | Quan hệ với mô hình | Số phiên | Kết luận nhầm |
|---|---|---|---|
| Máy Dũng | Đã dùng để chỉnh dấu vết | 2.573 | 10 (0,39%) |
| Máy Thiên, 02/11–04/11 | Log mới, nhưng cùng máy với dữ liệu dạy lớp bình thường | 807 | 0 (0%) |
| Máy Khôi, 7 ngày (31/10–07/11) | Máy chưa từng dùng để train hay chỉnh; cùng cấu hình Sysmon của nhóm | 779 | 15 (1,9%; khoảng tin cậy 95% khoảng 1,2%–3,2%) |

Trên máy Khôi, 735/779 phiên (94%) dừng ngay ở bước 2 vì điểm khớp thấp; chỉ 44 phiên đi tiếp sang bước kiểm tra dấu vết. Báo nhầm tăng khi dữ liệu càng "lạ" với mô hình. 15 phiên báo nhầm chỉ đến từ **3 nguyên nhân gốc**, đều là phần mềm hợp lệ:

| Nguyên nhân gốc | Kỹ thuật | Số phiên |
|---|---|---|
| Phần mềm Lenovo chạy dưới SYSTEM sau mỗi lần khởi động, tạo tác vụ `LvfDriverRemoval` bằng `schtasks /Create /XML` từ `C:\Windows\TEMP` | T1053.005 | 9 |
| Edge (và UniKey) ghi khóa Run để tự chạy khi đăng nhập | T1547.001 | 4 |
| Một ứng dụng chạy PowerShell ẩn (`-WindowStyle Hidden -ExecutionPolicy Bypass -NoProfile -NonInteractive`) chỉ để kiểm tra VS Code đã cài chưa | T1059.001 | 2 |

Nguồn thứ ba dùng đúng bộ cờ lệnh kẻ tấn công hay dùng để che giấu, nhưng nội dung lệnh vô hại; chỉ dựa vào cờ lệnh thì không phân biệt được. Ngược lại, trình cài driver Realtek chạy `wevtutil um` nhưng agent không báo T1070.001, vì dấu vết bắt buộc chỉ khớp `wevtutil cl`.

<!-- ![Log máy Khôi 7 ngày](../docs/hinh/tuan4-may-khoi.png) -->

Chi tiết câu trả lời cho câu hỏi 99,99% log bình thường: [docs/log-binh-thuong.md](../docs/log-binh-thuong.md).

## Thử mô hình ngôn ngữ trên các phiên báo nhầm (máy Khôi, 6 phiên của 2 ngày đầu)

| Kết quả | Số phiên |
|---|---|
| Mô hình trả lời nhưng chọn sai T1070.001, bước 5 chặn vì không có dấu vết | 3 |
| Phản hồi bị cắt độ dài | 2 |
| Ollama lỗi HTTP 500 | 1 |
| Mô hình nhận ra là hoạt động bình thường | **0** |

Trên log máy thật, mô hình ngôn ngữ chưa chứng minh được tác dụng giảm báo nhầm. Bước 5 vẫn hoạt động đúng: 3 lần mô hình chọn sai kỹ thuật đều bị chặn.

## Chỗ đang kẹt

1. **Phiên quá dài.** Trên máy thật, một phiên có thể kéo dài hơn 4 tiếng, hơn 6.000 sự kiện. Bước 3 tìm dấu vết trên toàn phiên nên dễ tìm thấy dấu vết không liên quan đến đoạn khớp ở bước 2 (ví dụ đoạn khớp là winget, nhưng dấu vết lại là Edge, UniKey).
2. **Bước 4 chỉ gửi 40 dòng đầu.** Với phiên dài, mô hình không thấy dòng gây nghi ngờ, nên chọn sai hoặc phản hồi bị cắt.
3. **Hoạt động hợp lệ tạo đúng dấu vết tấn công.** Tạo tác vụ từ file XML trong `C:\Windows\TEMP`, chạy PowerShell ẩn với `-ExecutionPolicy Bypass`, ghi khóa Run đều là cách kẻ tấn công hay làm; chỉ nhìn dòng lệnh thì không phân biệt được.
4. **Lớp bình thường học từ 1 máy**, nên trên máy lạ báo nhầm cao hơn rõ rệt.
5. **Agent gộp "SLM lỗi" vào "chưa xác nhận".** An toàn nhưng làm thống kê dễ thổi phồng tác dụng của SLM.
6. **Dự đoán bước tiếp theo** đang lấy ký hiệu cuối của cả phiên, không phải cuối đoạn khớp.
7. Các hạn chế từ tuần 3 vẫn còn: một vụ tấn công RDP bị chia thành nhiều phiên; chưa dùng Security log.

## Câu hỏi cho thầy

1. Hoạt động hợp lệ tạo đúng dấu vết tấn công (Lenovo tạo tác vụ từ `C:\Windows\TEMP`, ứng dụng chạy PowerShell ẩn với `-ExecutionPolicy Bypass`, UniKey ghi khóa Run): nên xử lý bằng danh sách trắng (chữ ký, đường dẫn, tiến trình cha) hay học thêm từ log bình thường?
2. Phiên trên máy thật vừa có lúc quá dài (hàng nghìn sự kiện), vừa có lúc một vụ tấn công bị chia nhỏ: nên chia lại phiên theo cách nào?
3. Sản phẩm cuối thầy kỳ vọng là công cụ phân tích file log, hay agent theo dõi trực tiếp trên máy? Nhóm dự định làm chế độ theo dõi trực tiếp dựa trên chế độ phát lại hiện có.
4. Nhóm cần log bình thường từ nhiều máy khác nhau để đo khách quan. Thầy có gợi ý nguồn nào không?

## Kế hoạch tuần sau (dự kiến)

- Khôi: bước 3 chỉ tìm dấu vết gần đoạn khớp; bước 4 gửi các dòng quanh dấu vết thay vì 40 dòng đầu; tách loại "SLM lỗi" khi thống kê; dự đoán bước tiếp theo theo đoạn khớp.
- Thiên: huấn luyện lớp bình thường từ nhiều máy, đánh giá kiểu "bỏ một máy ra, học trên các máy còn lại, thử trên máy bỏ ra".
- Dũng: hoàn thiện bảng so sánh model ở bước 4 (Dumpert, CapAttack, các phiên báo nhầm).

## Nội dung buổi báo cáo (điền sau khi thầy phản hồi)

- Câu hỏi / góp ý của thầy:
- Cách giải quyết: