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

T1021.001 và T1070.001 dưới 3 file theo quy tắc đếm ở mục 1. Kết quả kiểm tra theo nội dung ở mục 7.

## 6. Hạn chế

- Số "file" chưa phải số file log: quy tắc đếm cả file mô tả .yml, và một file có cả hai từ trong đường dẫn bị đếm hai lần.
- Đếm theo tên thư mục nên mọi file trong thư mục có chữ powershell đều thành "PowerShell", kể cả log Sysmon. Ví dụ T1059.001 có 73 "file PowerShell".
- Tên file và mô tả không đảm bảo nội dung: file mstsc_sysmon.log của T1021.001 có cả sự kiện Sysmon 1 và Security 4688.
- Hai thư mục viết thường (t1547.014, t1592) không được tính vì quy tắc chỉ nhận thư mục bắt đầu bằng chữ T hoa.
- Cột "áp dụng cho Windows" dựa vào nền tảng ghi trong ATT&CK, chưa kiểm tra nội dung log.
- EVTX-ATTACK-SAMPLES chỉ đưa vào cho T1021.001 và T1070.001 (mục 7). OTRF chưa đưa vào bản này.

## 7. Bổ sung cho T1021.001 và T1070.001 (kiểm tra theo nội dung)

Theo quy tắc đếm ở mục 1, T1021.001 có 1 file và T1070.001 có 2 file. Thiên đếm lại theo nội dung các file Splunk đã tải về máy (ngày 16/10/2026): đếm số sự kiện theo nhà cung cấp log (Sysmon, Security, PowerShell) trong từng file.

### T1021.001: Splunk

| Thư mục | File | Sự kiện Sysmon | Sự kiện Security |
|---|---|---|---|
| bmc_creation | bmc_creation.log | 1 | 0 |
| execution_from_rdp_share | execution_from_rdp_share.log | 7 | 0 |
| mstsc_admini | mstsc_admin.log | 10 | 0 |
| mstsc_rdp_cmd | mstsc_sysmon.log | 3 | 3 |
| rdp_creation | deafault_rdp_created.log | 1 | 0 |
| rdp_session_established | 4624_10_logon.log | 0 | 16 |
| remote_desktop_connection | zeek_conn.log | 0 | 0 |
| susp_default_rdp_creation | default_rdp.log | 2 | 0 |
| susp_default_rdp_creation | default_rdp_dropped.log | 7 | 0 |
| terminal_server_reg_created | terminal_sever_client_Reg_created.log | 7 | 0 |
| unhide_file | unhide_file.log | 12 | 0 |

Nhận xét: 9 trong 11 file có sự kiện Sysmon, nhưng mỗi file chỉ có từ 1 đến 12 sự kiện. 4624_10_logon.log là log Security. zeek_conn.log không có sự kiện nào theo cách đếm này (tên file cho thấy là log mạng Zeek). Mstsc_sysmon.log có cả 3 sự kiện Sysmon và 3 sự kiện Security.

### T1021.001: EVTX-ATTACK-SAMPLES

| File | Sự kiện Sysmon | Ghi chú |
|---|---|---|
| Lateral Movement/LM_sysmon_3_12_13_1_SharpRDP.evtx | 38 | Đã mở kiểm tra: ID 1, 3, 12, 13; có 4 sự kiện Sysmon 3 tới cổng 3389 (svchost.exe, Initiated=false, log của máy đích) |
| Lateral Movement/LM_sysmon_1_12_13_3_tsclient_SharpRdp.evtx | 9 | Theo evtx_data.csv của repo, chưa mở kiểm tra |
| Lateral Movement/sharprdp_sysmon_7_mstscax.dll.evtx | 4 | Theo evtx_data.csv của repo, chưa mở kiểm tra |
| Lateral Movement/LM_tsclient_startup_folder.evtx | 4 | Theo evtx_data.csv của repo, chưa mở kiểm tra |

### T1070.001: Splunk

| Thư mục | File | Sự kiện | Ghi chú |
|---|---|---|---|
| atomic_red_team | windows-sysmon.log | 6226 Sysmon | Được tính theo quy tắc ở mục 1 |
| atomic_red_team | windows-powershell.log | 10000 PowerShell | Được tính theo quy tắc ở mục 1 |
| windows_pwh_log_cleared | wevtutil_clear_log.log | 16 Sysmon, 3 Security | Không được tính theo quy tắc vì tên file và tên thư mục không chứa "sysmon" hay "powershell" |

Các file còn lại trong thư mục T1070.001 (windows-security.log, windows-system.log, ssa_wevtutil, windows_event_log_cleared...) không có sự kiện Sysmon hoặc PowerShell theo cách đếm này. Cách đếm chỉ nhận định dạng XML cho Security nên chưa kết luận về sự kiện Security 1102.

### T1070.001: EVTX-ATTACK-SAMPLES

DE_1102_security_log_cleared.evtx (Security 1102) và DE_104_system_log_cleared.evtx (System 104) theo evtx_data.csv của repo. Cả hai không phải log Sysmon hay PowerShell, chưa mở kiểm tra từng sự kiện.

### Kết luận

- Theo quy tắc đếm tên file: T1021.001 có 1 file, T1070.001 có 2 file, đều dưới 3.
- Theo nội dung: Splunk có 9 file chứa sự kiện Sysmon cho T1021.001 (mỗi file 1 đến 12 sự kiện) và 3 file chứa sự kiện Sysmon hoặc PowerShell cho T1070.001. Thêm nguồn EVTX thì T1021.001 có thêm 1 file đã kiểm tra, T1070.001 chưa có thêm file Sysmon hoặc PowerShell.
- Ví dụ cho hạn chế của "dòng khớp": file windows-sysmon.log của T1070.001 có 6226 sự kiện Sysmon nhưng chỉ 6 dòng chứa wevtutil hoặc Clear-EventLog (khoảng 0,1%).
- Cách đếm dùng để báo cáo với thầy cần Khôi quyết định.