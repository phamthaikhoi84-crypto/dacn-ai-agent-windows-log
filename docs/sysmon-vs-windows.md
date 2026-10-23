### So sánh khả năng giám sát_ Windows Mặc định vs Sysmon.md

## 1. Mục tiêu

So sánh khả năng ghi nhận hoạt động hệ thống giữa các log Windows mặc định và Sysmon. Qua đó, đánh giá vai trò của Sysmon trong việc thu thập dữ liệu phục vụ giám sát, phát hiện và phân tích hành vi đáng ngờ trên Windows.

## 2. Bảng so sánh 8 kỹ thuật

| Kỹ thuật | Windows mặc định | Sysmon bổ sung | Bằng chứng và trạng thái trên máy Dũng |
|---|---|---|---|
| Process creation | Security Event ID 4688 có thể ghi nhận việc tạo tiến trình nếu bật chính sách audit phù hợp. | Event ID 1 ghi nhận thông tin tiến trình, bao gồm đường dẫn và dòng lệnh khi có dữ liệu tương ứng. | DuckDB có 2.403 bản ghi Event ID 1. Chưa đối chiếu với Security Event ID 4688. |
| Process access / LSASS | Các log mặc định có thể không cung cấp đầy đủ chi tiết về tiến trình truy cập tiến trình khác nếu chưa cấu hình audit phù hợp. | Event ID 10 ghi nhận hoạt động truy cập tiến trình theo cấu hình thu thập. | Chưa có số liệu Event ID 10 trong bảng thống kê DuckDB hiện tại. Cần kiểm tra log gốc để xác nhận. |
| Network connection | Windows Firewall và các nguồn audit có thể ghi nhận một phần hoạt động mạng tùy cấu hình. | Event ID 3 ghi nhận kết nối mạng khi được bật trong cấu hình Sysmon. | DuckDB có 34.647 bản ghi Event ID 3. |
| PowerShell execution | PowerShell có thể ghi log Script Block, Module hoặc các sự kiện liên quan nếu được bật. Event ID 4104 thường dùng để ghi nội dung script block. | Event ID 1 cung cấp thông tin tiến trình PowerShell; Sysmon không thay thế log ghi nội dung script của PowerShell. | DuckDB có 2.403 bản ghi Event ID 1. Trước đó, máy đã ghi nhận PowerShell Event ID 4104; cần kiểm tra lại thời điểm và nội dung nếu sử dụng làm bằng chứng trong báo cáo. |
| File creation | Windows có thể ghi nhận thao tác tệp khi bật chính sách audit phù hợp và cấu hình SACL tương ứng. | Event ID 11 ghi nhận việc tạo tệp theo cấu hình Sysmon. | Chưa có số liệu Event ID 11 trong bảng thống kê DuckDB hiện tại. |
| Registry modification | Windows có thể ghi nhận thay đổi Registry khi cấu hình audit phù hợp. | Event ID 12–14 ghi nhận các hoạt động tạo/xóa khóa, sửa giá trị hoặc đổi tên khóa Registry. | Chưa có số liệu Event ID 12–14 trong bảng thống kê DuckDB hiện tại. |
| DLL/image loading | Log Windows mặc định có thể không cung cấp cùng mức chi tiết nếu không bật cơ chế giám sát bổ sung. | Event ID 7 ghi nhận hoạt động nạp image, bao gồm DLL, khi được bật. | Chưa có số liệu Event ID 7 trong bảng thống kê DuckDB hiện tại. |
| DNS query | Windows có thể ghi nhận truy vấn DNS qua các log DNS Client hoặc nguồn liên quan tùy cấu hình. | Event ID 22 ghi nhận truy vấn DNS theo cấu hình Sysmon. | DuckDB có 2.766 bản ghi Event ID 22. |

**Lưu ý về bằng chứng:** Các số liệu trên được lấy từ cơ sở dữ liệu `output/benign_events.duckdb` tại thời điểm kiểm tra. Việc chưa thấy một Event ID trong kết quả thống kê hiện tại không đồng nghĩa sự kiện đó chắc chắn không tồn tại trên máy hoặc trong file log gốc.

## 3. Kết quả thống kê log Sysmon

File dữ liệu được sử dụng là `benign_sysmon_dung_tuan1.evtx`. Script `src/evtx_to_duckdb.py` được sử dụng để chuyển dữ liệu sang DuckDB.

Tại thời điểm kiểm tra, cơ sở dữ liệu có 42.099 bản ghi:

| Event ID | Ý nghĩa | Số bản ghi |
|---:|---|---:|
| 3 | Network connection | 34.647 |
| 22 | DNS query | 2.766 |
| 1 | Process creation | 2.403 |
| 5 | Process terminated | 2.279 |
| 4 | Sysmon service state changed | 2 |
| 16 | Sysmon configuration changed | 2 |
| **Tổng** | | **42.099** |

Các bản ghi Event ID 3 chiếm số lượng lớn nhất trong dữ liệu đã nạp, tiếp theo là Event ID 22 và Event ID 1. Điều này cho thấy tập dữ liệu hiện tại có nhiều thông tin về hoạt động mạng, truy vấn DNS và vòng đời tiến trình.

Cần xác nhận quá trình nhập dữ liệu đã hoàn tất trước khi sử dụng các con số trên làm thống kê đầy đủ của toàn bộ file EVTX gốc.

## 4. Vì sao cần Sysmon?

Sysmon bổ sung dữ liệu giám sát có cấu trúc cho Windows, giúp người phân tích có thêm thông tin về tiến trình, dòng lệnh, kết nối mạng, truy vấn DNS, truy cập tiến trình và các hoạt động hệ thống khác khi cấu hình tương ứng được bật.

Khi không có Sysmon, Windows vẫn có thể ghi lại nhiều hoạt động thông qua Security, System, PowerShell và các nguồn log khác. Tuy nhiên, mức độ chi tiết phụ thuộc vào chính sách audit và cấu hình từng nguồn; một số hoạt động có thể khó quan sát hoặc khó liên kết với nhau hơn.

Sysmon không tự động phát hiện mọi cuộc tấn công. Hiệu quả giám sát phụ thuộc vào cấu hình, dữ liệu thu thập, việc lưu giữ log và quá trình phân tích.

## 5. Kết luận

Kết quả thống kê DuckDB cho thấy dữ liệu Sysmon trên máy Dũng có thể được truy vấn và phân nhóm theo Event ID để phục vụ phân tích. Sysmon bổ sung một nguồn telemetry hữu ích bên cạnh log Windows mặc định, nhưng cần đối chiếu với cấu hình và log thực tế trước khi kết luận một loại sự kiện đã hoặc chưa được ghi nhận.




