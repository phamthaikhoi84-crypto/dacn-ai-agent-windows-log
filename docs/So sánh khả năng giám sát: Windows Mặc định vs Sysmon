

| Kỹ thuật | Windows Mặc định thấy gì? | Sysmon bổ sung gì? | Bằng chứng trên máy Dũng |
| :--- | :--- | :--- | :--- |
| **Process creation** | Security Event 4688 (nếu bật audit phù hợp) | Sysmon Event ID 1: Thông tin tiến trình và dòng lệnh (Command Line) khi được ghi nhận | Log thực tế |
| **Process access / LSASS** | Có thể thiếu chi tiết truy cập tiến trình | Sysmon Event ID 10: Chi tiết truy cập tiến trình (nếu cấu hình thu thập phù hợp) | Log thực tế |
| **Network connection** | Có thể có log từ Firewall hoặc audit phù hợp | Sysmon Event ID 3: Chi tiết kết nối mạng (nếu được bật trong Sysmon) | Log thực tế |
| **PowerShell execution** | Có thể có log PowerShell (nếu bật Script Block/Module logging) | Sysmon Event ID 1: Ghi hoạt động tiến trình (không thay thế log nội dung script) | Event ID 1 và log PowerShell |
| **File creation** | Tùy thuộc cấu hình audit và loại file | Sysmon Event ID 11: Tạo file (nếu được cấu hình thu thập) | Log thực tế |
| **Registry modification** | Một số thay đổi được audit (nếu cấu hình phù hợp) | Sysmon Event ID 12–14: Theo dõi thêm/xóa/sửa Registry (nếu được thu thập) | Log thực tế |
| **DLL/image loading** | Có thể hạn chế nếu không bật audit bổ sung | Sysmon Event ID 7: Nạp DLL/Image (nếu được bật) | Log thực tế |
| **DNS query** | Log tùy thuộc cấu hình DNS Client hoặc các nguồn khác | Sysmon Event ID 22: Truy vấn DNS (nếu được bật) | Log thực tế |
