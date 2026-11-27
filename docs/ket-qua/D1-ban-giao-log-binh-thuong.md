# D1 – Thu thập và bàn giao log Windows bình thường

## 1. Mục tiêu

Thu thập bộ log Sysmon ghi nhận hoạt động Windows bình thường trên máy Dũng và bàn giao cho Khôi để phục vụ quá trình xây dựng, kiểm thử và đánh giá AI Agent Windows Log.

## 2. Dữ liệu sử dụng

- Bộ log: `benign_sysmon_dung.evtx` (tên theo phân công).
- Bản log cục bộ đã được sử dụng trong quá trình xử lý: `benign_sysmon_dung_tuan1.evtx`.
- Dung lượng bản log cục bộ được ghi nhận: 62.984.192 bytes.
- Dữ liệu đã nạp vào DuckDB: 70.232 sự kiện, được gom thành 353 phiên.

### Thống kê Event ID của bản log đã xử lý

| Event ID | Số lượng |
|---:|---:|
| 1 | 3.915 |
| 2 | 29 |
| 3 | 58.155 |
| 4 | 3 |
| 5 | 3.644 |
| 10 | 16 |
| 12 | 1 |
| 13 | 11 |
| 16 | 4 |
| 22 | 4.452 |
| 255 | 2 |
| **Tổng** | **70.232** |

## 3. Bàn giao dữ liệu

File log đã được đưa lên Google Drive và Khôi đã xác nhận nhận được file.

**Kết quả bàn giao:** Đã bàn giao thành công cho Khôi.

## 4. Ý nghĩa đối với đồ án

Bộ log bình thường được dùng làm dữ liệu đối chứng để:
- Kiểm tra khả năng hạn chế cảnh báo sai trên hoạt động Windows thông thường.
- Đánh giá cách Agent xử lý phiên không có đủ bằng chứng cho kỹ thuật tấn công.
- Hỗ trợ so sánh kết quả giữa chế độ không SLM và chế độ có SLM.

## 5. Kết luận

Hạng mục D1 hoàn thành: log Windows bình thường đã được bàn giao và Khôi xác nhận nhận được.

## 6. Ghi chú về tên file

Tên file theo phân công là `benign_sysmon_dung.evtx`, trong khi tên bản log cục bộ được ghi nhận trong quá trình xử lý là `benign_sysmon_dung_tuan1.evtx`. Khi đưa báo cáo vào repository, cần bảo đảm tên file trong báo cáo khớp với tên thực tế của file đã chia sẻ trên Drive nếu hai tên này khác nhau.
