# Độ phủ dữ liệu log tấn công (Splunk Attack Data)

Cập nhật: 23/10/2026. Nguồn danh sách: data/ky-thuat-splunk-sysmon-powershell.csv. Bảng tra mã: ATT&CK v20.0 (xem docs/attack-version.md).

## 1. Quy tắc đếm "file"

Danh sách 161 kỹ thuật đếm số file theo quy tắc sau (Thiên tái tạo lại từ kho Splunk Attack Data, bản lấy ngày 23/10/2026, và khớp với danh sách):

- Duyệt các file trong thư mục datasets/attack_techniques/<mã kỹ thuật>/. Chỉ tính thư mục bắt đầu bằng chữ T hoa.
- Một file tính vào cột Sysmon nếu đường dẫn (tên thư mục con cộng tên file) chứa "sysmon", và vào cột PowerShell nếu chứa "powershell". Tổng file bằng hai cột cộng lại.

## 2. Kết quả

| Cách tính | Số kỹ thuật | ≥3 file | 2 file | 1 file |
|---|---|---|---|---|
| Theo danh sách (mã Splunk) | 161 | 71 | 34 | 56 |
| Gộp theo mã ATT&CK v20.0 | 160 | 71 | 33 | 56 |
| Gộp theo mã v20.0 và chỉ kỹ thuật có Windows | 144 | 68 | 31 | 45 |
| Chỉ đếm file dữ liệu (bỏ .yml và .md), mỗi file một lần | 161 | 68 | 32 | 61 |

## 3. Mã đã đổi trong ATT&CK v20.0

| Mã trong danh sách | Số file | Mã mới v20.0 |
|---|---|---|
| T1070.001 | 2 | T1685.005 |
| T1562.001 | 24 | T1685 |
| T1562.002 | 2 | T1685.001 |
| T1562.004 | 3 | T1686 |
| T1574.002 | 6 | T1574.001 |

T1574.001 đã có sẵn trong danh sách nên T1574.002 gộp vào đó, số kỹ thuật giảm từ 161 xuống 160.

## 4. Kỹ thuật không áp dụng cho Windows

ATT&CK không liệt kê Windows trong nền tảng của 16 kỹ thuật sau: T1003.008, T1053.003, T1053.006, T1059.004, T1098.004, T1546.004, T1547.006, T1548.001, T1548.003, T1574.006, T1587.002, T1588.002, T1590.002, T1590.005, T1595, T1598.002. Chưa kiểm tra từng kỹ thuật xem log của chúng đến từ máy nào (ví dụ Sysmon for Linux).

## 5. Tám kỹ thuật tầng sâu

| Mã | Tên | File Sysmon | File PowerShell | Tổng |
|---|---|---|---|---|
| T1003.001 | LSASS Memory | 3 | 1 | 4 |
| T1021.001 | Remote Desktop Protocol | 1 | 0 | 1 |
| T1053.005 | Scheduled Task | 9 | 2 | 11 |
| T1059.001 | PowerShell | 19 | 73 | 92 |
| T1070.001 | Clear Windows Event Logs (mã mới T1685.005) | 1 | 1 | 2 |
| T1105 | Ingress Tool Transfer | 5 | 0 | 5 |
| T1136.001 | Local Account | 2 | 2 | 4 |
| T1547.001 | Registry Run Keys / Startup Folder | 2 | 1 | 3 |

T1021.001 và T1070.001 dưới 3 file trong Splunk, cần bổ sung từ nguồn khác (phần này sẽ cập nhật).

## 6. Hạn chế

- Số "file" chưa phải số file log: quy tắc đếm cả file mô tả .yml, và một file có cả hai từ trong đường dẫn bị đếm hai lần.
- Đếm theo tên thư mục nên mọi file trong thư mục có chữ powershell đều thành "PowerShell", kể cả log Sysmon. Ví dụ T1059.001 có 73 "file PowerShell".
- Tên file và mô tả không đảm bảo nội dung: file mstsc_sysmon.log của T1021.001 có cả sự kiện Sysmon 1 và Security 4688.
- Hai thư mục viết thường (t1547.014, t1592) không được tính vì quy tắc chỉ nhận thư mục bắt đầu bằng chữ T hoa.
- Cột "áp dụng cho Windows" dựa vào nền tảng ghi trong ATT&CK, chưa kiểm tra nội dung log.
- Chưa đưa EVTX-ATTACK-SAMPLES và OTRF vào bản này.