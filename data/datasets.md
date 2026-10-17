# Bộ dữ liệu log tấn công

> File log lưu trên máy, không đưa lên GitHub. Bảng này chỉ mô tả.

**Tình trạng: đã có dữ liệu cho 8/8 kỹ thuật** (cập nhật ngày 16/10/2026)

| Mã kỹ thuật | Bộ dữ liệu | Tên file | Loại log | Ghi chú |
|---|---|---|---|---|
| T1105 | Splunk Attack Data | T1105/atomic_red_team/windows-sysmon.log | Sysmon, XML-text | Kiểm tra sơ bộ bằng từ khóa: có certutil / DownloadFile... (190 dòng khớp) |
| T1059.001 | Splunk Attack Data | T1059.001/atomic_red_team/windows-sysmon.log | Sysmon, XML-text | Kiểm tra sơ bộ bằng từ khóa: có -enc / -w hidden (35 dòng khớp) |
| T1059.001 | Splunk Attack Data | T1059.001/atomic_red_team/windows-powershell.log | PowerShell 4104, text khóa=giá trị (nhiều dòng mỗi sự kiện) | Kiểm tra sơ bộ bằng từ khóa: IEX (13 dòng khớp), DownloadString (4), FromBase64String (14), Invoke-Expression (3). Có 320 sự kiện EventCode=4104, file còn lẫn sự kiện khác (ví dụ 4106). Mỗi sự kiện nhiều dòng nên số dòng khớp không bằng số sự kiện |
| T1053.005 | Splunk Attack Data | T1053.005/atomic_red_team/windows-sysmon.log | Sysmon, XML-text | Kiểm tra sơ bộ bằng từ khóa: có schtasks (61 dòng khớp) |
| T1547.001 | Splunk Attack Data | T1547.001/atomic_red_team/windows-sysmon.log | Sysmon, XML-text | Kiểm tra sơ bộ bằng từ khóa: có CurrentVersion\Run (16 dòng khớp) |
| T1136.001 | Splunk Attack Data | T1136.001/atomic_red_team/windows-sysmon.log | Sysmon, XML-text | Kiểm tra sơ bộ bằng từ khóa: có net user / New-LocalUser (10 dòng khớp). Trong Sysmon chỉ thấy qua dòng lệnh; dấu vết chính nằm ở Security log (4720) |
| T1003.001 | Splunk Attack Data | T1003.001/atomic_red_team/windows-sysmon.log | Sysmon, XML-text | Kiểm tra sơ bộ bằng từ khóa: có lsass (913 dòng khớp) |
| T1021.001 | EVTX-ATTACK-SAMPLES | Lateral Movement/LM_sysmon_3_12_13_1_SharpRDP.evtx | Sysmon, EVTX | File chính. 38 sự kiện Sysmon (ID 1, 3, 12, 13). Có 4 sự kiện Sysmon 3 tới cổng 3389 (svchost.exe, Initiated=false, tức đây là log của máy đích nhận kết nối từ 192.168.56.1). Không có mstsc.exe vì là phía nhận. Chỉ 68 KB |
| T1021.001 | Splunk Attack Data | T1021.001/mstsc_rdp_cmd/mstsc_sysmon.log | Sysmon + Security 4688, XML-text | Dự phòng. Chỉ 6 sự kiện: 3 Sysmon 1 có mstsc.exe và cổng 3389 trong dòng lệnh, 3 sự kiện Security 4688. Không có Sysmon 3 |
| T1070.001 | Splunk Attack Data | T1070.001/atomic_red_team/windows-sysmon.log | Sysmon, XML-text | Kiểm tra sơ bộ bằng từ khóa: có wevtutil / Clear-EventLog (6 dòng khớp). Trong Sysmon chỉ thấy qua dòng lệnh; dấu vết chính nằm ở Security log (1102) |

**Loại log** ghi rõ: Sysmon / PowerShell 4104 / Security, và định dạng file (EVTX / JSON / XML-text / text khóa=giá trị).

**Lưu ý T1021.001:** log chính (EVTX) là phía máy đích, có Sysmon 3 tới cổng 3389 nhưng không có mstsc.exe; log dự phòng (Splunk) là phía máy khởi tạo, có mstsc.exe nhưng không có Sysmon 3.
## Log bình thường

> Thu trên máy 3 thành viên, Sysmon dùng cấu hình chung `config/sysmonconfig-dacn.xml` và bật PowerShell Script Block Logging. Log lưu trên máy, xuất mỗi tuần, không đưa lên GitHub.

| Máy | Bắt đầu thu | Cấu hình | Tình trạng |
|---|---|---|---|
| Khôi | 17/10/2026 00:09 | sysmonconfig-dacn.xml | Đang thu |
| Thiên | | sysmonconfig-dacn.xml | Đang thu |
| Dũng | | sysmonconfig-dacn.xml | Đang thu |
