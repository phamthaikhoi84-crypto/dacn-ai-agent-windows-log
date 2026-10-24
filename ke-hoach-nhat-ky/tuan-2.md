# Tuần 2 (18/10 – 24/10/2026)

## Chốt hướng sau góp ý tuần 1

- **Hành vi** = chuỗi hành động có thứ tự, cùng máy / phiên đăng nhập / cây tiến trình, trong một khoảng thời gian. Log Sysmon là đối tượng, chuỗi hành động mới là hành vi.
- **Phương pháp 5 bước:** chuẩn hóa log → gom phiên hành vi → rút gọn thành chuỗi ký hiệu → so khớp + dự đoán bước tiếp theo → kiểm chứng bằng dấu vết bắt buộc.
- **Phạm vi 2 tầng:** tầng rộng nhận diện các kỹ thuật Windows có log Sysmon/PowerShell trong Splunk Attack Data; tầng sâu là 8 kỹ thuật, kiểm chứng kỹ và demo chuỗi tấn công hoàn chỉnh.
- **Đo kết quả:** tỷ lệ phát hiện đúng, báo nhầm trên log bình thường, độ sớm, tỷ lệ dự đoán đúng bước tiếp theo.

Chi tiết: [docs/phuong-phap.md](../docs/phuong-phap.md).

## Kế hoạch và kết quả

| Người | Việc | Kết quả | File |
|---|---|---|---|
| Khôi | Viết phương pháp | Xong bản nháp | [docs/phuong-phap.md](../docs/phuong-phap.md) |
| Khôi | Demo gom chuỗi hành vi | Script nạp .evtx vào DuckDB, gom theo LogonId + cây tiến trình + thời gian, in chuỗi hành động; chạy trên 3 file EVTX-ATTACK-SAMPLES ra 8 phiên | [src/chuoi_hanh_vi.py](../src/chuoi_hanh_vi.py) |
| Khôi | Đưa danh sách kỹ thuật lên repo | Xong | [data/ky-thuat-splunk-sysmon-powershell.csv](../data/ky-thuat-splunk-sysmon-powershell.csv) |
| Thiên | Gửi file .evtx cho demo | 2 file dump bộ nhớ (comsvcs, Dumpert + AndrewSpecial) | Giữ trên máy, không đưa lên GitHub |
| Thiên | Kiểm tra lại độ phủ dữ liệu | Phát hiện đếm theo tên file bị thiếu; đếm lại theo nội dung 2.090 file: 144 kỹ thuật Windows, 79 kỹ thuật có ≥3 file (cách cũ: 68). Cả 8 kỹ thuật tầng sâu đều có ≥3 file | [data/do-phu.md](../data/do-phu.md), [src/dem_theo_noi_dung.ps1](../src/dem_theo_noi_dung.ps1), [data/do-phu-theo-noi-dung.csv](../data/do-phu-theo-noi-dung.csv) |
| Thiên | Chốt phiên bản ATT&CK | ATT&CK v20.0, bảng đối chiếu mã cũ/mới (vd T1070.001 → T1685.005) | [docs/attack-version.md](../docs/attack-version.md), [data/attack-v20-tra-ma.csv](../data/attack-v20-tra-ma.csv) |
| Dũng | So sánh Sysmon và log Windows mặc định | Bảng so sánh cho 8 kỹ thuật; thống kê 42.099 sự kiện log bình thường theo Event ID | [docs/sysmon-vs-windows.md](../docs/sysmon-vs-windows.md) |
| Dũng | Thử 4 mô hình với chuỗi 3 sự kiện | Đã chạy cả 4 mô hình, có bảng so sánh | [docs/sysmon-vs-windows.md](../docs/sysmon-vs-windows.md) mục 4–5 |

## Ảnh kết quả demo

Lệnh: `python src\chuoi_hanh_vi.py D:\DACN\log --phien <số>`

**Phiên 1:** dump bộ nhớ bằng comsvcs.dll. Chuỗi đi qua 2 cây tiến trình (script nhờ WMI chạy hộ), chỉ nối được nhờ cùng LogonId và cách nhau 0,6 giây.

![Phiên 1](../docs/hinh/phien1-comsvcs.png)

**Phiên 2:** kết nối RDP cổng 3389. Sysmon không cho biết kết nối tạo ra phiên đăng nhập nào, cần thêm Security 4624 để nối.

![Phiên 2](../docs/hinh/phien2-rdp.png)

**Phiên 3:** SharpRDP, 25 sự kiện gộp đúng vào 1 phiên; nhịp "ghi RunMRU → tạo tiến trình" lặp lại 4 lần.

![Phiên 3](../docs/hinh/phien3-sharprdp.png)

**Phiên 8:** 3 công cụ khác tên nhưng cùng mẫu `MO_BO_NHO:lsass.exe → TAO_FILE:*.dmp`; đủ nghi sau 2 sự kiện.

![Phiên 8](../docs/hinh/phien8-dumpert.png)

## Chỗ đang vướng

1. Đếm độ phủ theo tên file bị sai, đã đếm lại theo nội dung; nhưng mới kiểm tra "có Sysmon/4104", chưa kiểm tra file có đúng hành vi của kỹ thuật.
2. Sysmon không nối được kết nối RDP vào phiên đăng nhập, cần thêm Security log.
3. Ký hiệu `SUA_REGISTRY` quá thô, chưa phân biệt ghi RunMRU với ghi khóa Run (T1547.001).
4. Bước 4 (so khớp, dự đoán) và vai trò của mô hình ngôn ngữ nhỏ chưa chốt.

## Nội dung buổi báo cáo 24/10/2026 (điền sau buổi)

- Câu hỏi / góp ý của thầy:
- Cách giải quyết:

## Kế hoạch tuần sau (dự kiến, chốt sau buổi báo cáo)

- Đọc log XML của Splunk Attack Data (bước 1).
- Tách ký hiệu registry theo loại khóa; thêm Security log (4624, 4688, 4720, 1102).
- Làm bước 4 bản cơ sở: đếm cặp/bộ ba ký hiệu liên tiếp để so khớp và dự đoán bước tiếp theo.
- Kiểm tra nội dung các file thuộc 8 kỹ thuật tầng sâu; xem xét 65 kỹ thuật Windows ngoài danh sách.
