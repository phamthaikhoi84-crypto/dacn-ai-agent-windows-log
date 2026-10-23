# Phiên bản MITRE ATT&CK

## Chốt phiên bản

- Dùng **MITRE ATT&CK Enterprise v20.0** (ngày đăng trong kho dữ liệu STIX: 13/10/2026). Tra cứu ngày 23/10/2026.
- Nguồn: kho `mitre-attack/attack-stix-data`, file `enterprise-attack-20.0.json`.
- Lý do: là bản mới nhất khi làm đề tài. Toàn bộ mã đã đổi so với v18.1 đều xuất hiện từ v19.0 (ngày đăng 28/04/2026) và v20.0 không thu hồi thêm kỹ thuật nào, nên bảng đối chiếu bên dưới đúng cho cả v19.x và v20.0.
- Số kỹ thuật và kỹ thuật con còn hiệu lực (tính từ dữ liệu STIX): v18.1 có 691, v19.0 có 697, v20.0 có 706.

## Thay đổi lớn từ v19.0

- Chiến thuật Defense Evasion được tách thành **Stealth** (TA0005) và **Defense Impairment** (TA0112, mới).
- Nhóm kỹ thuật làm suy yếu phòng thủ (T1562.*) và xóa log (T1070.001, T1070.002) được đánh lại mã. T1685 và T1685.005 thuộc Defense Impairment.

## 8 kỹ thuật tầng sâu

| Mã | Tên | Chiến thuật (v20.0) | So với v18.1 |
|---|---|---|---|
| T1105 | Ingress Tool Transfer | Command and Control | Giữ nguyên |
| T1059.001 | PowerShell | Execution | Giữ nguyên |
| T1053.005 | Scheduled Task | Execution, Persistence, Privilege Escalation | Giữ nguyên |
| T1547.001 | Registry Run Keys / Startup Folder | Persistence, Privilege Escalation | Giữ nguyên |
| T1136.001 | Local Account | Persistence | Giữ nguyên |
| T1003.001 | LSASS Memory | Credential Access | Giữ nguyên |
| T1021.001 | Remote Desktop Protocol | Lateral Movement | Giữ nguyên |
| T1070.001 | Clear Windows Event Logs | Defense Impairment (mã mới T1685.005) | **Đổi mã** thành T1685.005 |

## Bảng đối chiếu mã cũ và mã mới (đổi trong v19.0)

| Mã cũ | Tên cũ | Mã mới | Tên mới |
|---|---|---|---|
| T1070.001 | Clear Windows Event Logs | T1685.005 | Clear Windows Event Logs |
| T1070.002 | Clear Linux or Mac System Logs | T1685.006 | Clear Linux or Mac System Logs |
| T1562 | Impair Defenses | T1685 | Disable or Modify Tools |
| T1562.001 | Disable or Modify Tools | T1685 | Disable or Modify Tools |
| T1562.002 | Disable Windows Event Logging | T1685.001 | Disable or Modify Windows Event Log |
| T1562.003 | Impair Command History Logging | T1690 | Prevent Command History Logging |
| T1562.004 | Disable or Modify System Firewall | T1686 | Disable or Modify System Firewall |
| T1562.006 | Indicator Blocking | T1685 | Disable or Modify Tools |
| T1562.007 | Disable or Modify Cloud Firewall | T1686.001 | Cloud Firewall |
| T1562.008 | Disable or Modify Cloud Logs | T1685.002 | Disable or Modify Cloud Log |
| T1562.009 | Safe Mode Boot | T1688 | Safe Mode Boot |
| T1562.010 | Downgrade Attack | T1689 | Downgrade Attack |
| T1562.011 | Spoof Security Alerting | T1685.003 | Modify or Spoof Tool UI |
| T1562.012 | Disable or Modify Linux Audit System | T1685.004 | Disable or Modify Linux Audit System Log |
| T1562.013 | Disable or Modify Network Device Firewall | T1686.002 | Network Device Firewall |
| T1656 | Impersonation | T1684.001 | Impersonation |
| T1672 | Email Spoofing | T1684.002 | Email Spoofing |

## Mã trong danh sách 161 kỹ thuật bị ảnh hưởng

Năm mã trong data/ky-thuat-splunk-sysmon-powershell.csv không còn hiệu lực ở v20.0 (chi tiết số file ở data/do-phu.md):

- T1070.001 thành T1685.005, T1562.001 thành T1685, T1562.002 thành T1685.001, T1562.004 thành T1686: đổi trong v19.0.
- T1574.002 thành T1574.001: đã bị thu hồi từ trước v18.1. T1574.001 đã có sẵn trong danh sách nên hai mã gộp lại, số kỹ thuật giảm từ 161 xuống 160.

## Lưu ý khi dùng

- Nhiều mã cũ gộp về một mã mới (T1562, T1562.001, T1562.006 đều về T1685). Khi đếm số file theo kỹ thuật phải cộng gộp theo mã mới.
- Splunk Attack Data đặt tên thư mục theo mã cũ (ví dụ T1562.001, T1070.001). Cần tra theo quan hệ `revoked-by` trong dữ liệu STIX của MITRE, vì có cả mã bị thu hồi từ trước v19.0.
- Có thư mục viết thường (t1547.014, t1592). Cần chuẩn hóa chữ hoa nếu muốn đếm cả hai.
- Đổi mã không làm đổi nội dung log hay dấu vết Sysmon, chỉ đổi cách gọi tên kỹ thuật.

## Cách kiểm chứng

Bảng đối chiếu lấy từ quan hệ `revoked-by` trong file enterprise-attack-20.0.json của MITRE. Thiên đã đối chiếu lại từng dòng bằng một bảng tra riêng tạo từ cùng dữ liệu STIX.