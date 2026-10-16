# Bảng mô tả bộ dữ liệu log tấn công

File log được lưu trên máy, không đưa lên GitHub.

|Mã kỹ thuật|Bộ dữ liệu|Tên file|Loại log|Ghi chú|
|-|-|-|-|-|
|T1003.001|Splunk Attack Data|atomic\_red\_team/windows-sysmon.log|Sysmon|Đã kiểm tra: có lsass (913 dòng khớp)|
|T1053.005|Splunk Attack Data|atomic\_red\_team/windows-sysmon.log|Sysmon|Đã kiểm tra: có schtasks (61 dòng khớp)|
|T1059.001|Splunk Attack Data|atomic\_red\_team/windows-sysmon.log|Sysmon|Đã kiểm tra: có -enc / -w hidden (35 dòng khớp)|
|T1070.001|Splunk Attack Data|atomic\_red\_team/windows-sysmon.log|Sysmon|Đã kiểm tra: có wevtutil / Clear-EventLog (6 dòng khớp)|
|T1105|Splunk Attack Data|atomic\_red\_team/windows-sysmon.log|Sysmon|Đã kiểm tra: có certutil / DownloadFile... (190 dòng khớp)|
|T1136.001|Splunk Attack Data|atomic\_red\_team/windows-sysmon.log|Sysmon|Đã kiểm tra: có net user / New-LocalUser (10 dòng khớp)|
|T1547.001|Splunk Attack Data|atomic\_red\_team/windows-sysmon.log|Sysmon|Đã kiểm tra: có CurrentVersion\\Run (16 dòng khớp)|
|T1021.001|EVTX-ATTACK-SAMPLES|Lateral Movement/LM\_sysmon\_3\_12\_13\_1\_SharpRDP.evtx|Sysmon|File chính. 38 sự kiện Sysmon (ID 1, 3, 12, 13). Có 4 sự kiện Sysmon 3 tới cổng 3389 (svchost.exe, Initiated=false, tức đây là log của máy đích nhận kết nối từ 192.168.56.1). Không có mstsc.exe vì là phía nhận. Chỉ 68 KB|
|T1021.001|Splunk Attack Data|mstsc\_rdp\_cmd/mstsc\_sysmon.log|Sysmon + Security|Dự phòng. Chỉ 6 sự kiện: 3 Sysmon 1 có mstsc.exe và cổng 3389 trong dòng lệnh, 3 sự kiện Security 4688. Không có Sysmon 3|

**Tổng kết:** đã có dữ liệu cho 8/8 kỹ thuật. Riêng T1021.001: log chính (EVTX) là phía máy đích, có Sysmon 3 tới cổng 3389 nhưng không có mstsc.exe; log dự phòng (Splunk) là phía máy khởi tạo, có mstsc.exe nhưng không có Sysmon 3.

