# Đánh giá thử nghiệm Sysmon Event ID 10 với Gemma 3

- **Ngày thử nghiệm:** 24/10/2026
- **Mô hình:** `gemma3:4b` chạy qua Ollama
- **Dữ liệu đầu vào:** `output/live_demo_events_20261024_123356.duckdb`
- **Kết quả mô hình đã làm sạch:** `output/live_demo_event10_ai_clean.txt`
- **Phạm vi:** Đánh giá một lượt phân tích mẫu Sysmon Event ID 10; không phải kết luận điều tra sự cố.

## 1. Mục tiêu

Kiểm tra khả năng của mô hình ngôn ngữ nhỏ (SLM) trong việc đọc các sự kiện Sysmon Event ID 10, giải thích những trường liên quan đến truy cập tiến trình và đưa ra nhận định bảo mật có căn cứ.

Event ID 10 ghi nhận hoạt động truy cập một tiến trình từ tiến trình khác. Sự kiện này có thể hữu ích khi điều tra hành vi truy cập LSASS, nhưng riêng sự kiện không chứng minh rằng đã xảy ra đánh cắp thông tin xác thực.

## 2. Dữ liệu quan sát

Trong cơ sở dữ liệu của phiên demo có 10 sự kiện Event ID 10. Lượt phân tích dùng một tập con gồm tối đa 5 bản ghi mới nhất.

Một số bản ghi thể hiện:
- `svchost.exe` truy cập `lsass.exe`.
- `GamingServices.exe` truy cập `lsass.exe`.
- `GrantedAccess` có giá trị `0x1000`.
- Các tiến trình trong những bản ghi được xem xét chạy dưới tài khoản `NT AUTHORITY\SYSTEM`.
- Trường `CallTrace` chứa các thành phần liên quan đến chuỗi gọi hàm.

Đây là các dấu hiệu cần đặt trong ngữ cảnh. Tên tiến trình, tài khoản SYSTEM hoặc việc có nhiều sự kiện lặp lại không tự động chứng minh hành vi độc hại.

## 3. Đánh giá câu trả lời của Gemma 3

### Điểm làm được

- Nhận ra mối quan hệ giữa tiến trình nguồn và `lsass.exe`.
- Chú ý đến `GrantedAccess`, tài khoản chạy tiến trình và `CallTrace`.
- Không khẳng định chắc chắn rằng đã xảy ra đánh cắp thông tin xác thực.

### Lỗi kỹ thuật quan trọng

Mô hình diễn giải sai giá trị `GrantedAccess=0x1000`, cho rằng giá trị này bằng 2048.

Giá trị đúng là:

- Hex: `0x1000`
- Decimal: `4096`
- Quyền tương ứng: `PROCESS_QUERY_LIMITED_INFORMATION`

Quyền này cho phép truy vấn một số thông tin giới hạn về tiến trình. Bản thân nó không chứng minh rằng tiến trình nguồn đã đọc bộ nhớ LSASS hoặc lấy được thông tin xác thực.

### Hạn chế trong nhận định

Mô hình đánh giá mức độ đáng ngờ dựa một phần vào việc sự kiện xuất hiện nhiều lần. Tần suất lặp lại cần được xem xét cùng danh tính tiến trình, quyền truy cập, ngữ cảnh máy, chuỗi sự kiện và các dấu hiệu bổ sung. Không nên xếp hành vi là đáng ngờ chỉ vì sự kiện lặp lại.

## 4. Nhận định sau khi đối chiếu

Kết quả cho thấy Gemma 3 có thể nhận diện một số trường quan trọng trong Event ID 10, nhưng chưa diễn giải hoàn toàn chính xác quyền truy cập tiến trình.

Với dữ liệu đang có, kết luận phù hợp là **chưa đủ bằng chứng để xác định hành vi độc hại hoặc đánh cắp thông tin xác thực**. Cần đối chiếu thêm với cấu hình Sysmon, ngữ cảnh tiến trình và các sự kiện liên quan trước khi đưa ra kết luận.

## 5. Giới hạn thử nghiệm

- Đây là một lượt phân tích trên một tập con dữ liệu Event ID 10.
- Kết quả mô hình là văn bản do AI sinh ra, không phải bằng chứng độc lập.
- Chưa có đánh giá định lượng trên tập dữ liệu gán nhãn chuẩn cho trường hợp này.
- Chưa chứng minh toàn bộ pipeline phát hiện và phân tích hoạt động tự động theo thời gian thực chỉ từ lượt thử nghiệm này.

## 6. Hướng cải thiện

1. Bổ sung hướng dẫn giải thích các giá trị `GrantedAccess` phổ biến và yêu cầu mô hình phân biệt dữ kiện với suy luận.
2. Yêu cầu mô hình trích dẫn trường dữ liệu hỗ trợ cho từng nhận định.
3. Đánh giá kết quả bằng tiêu chí rõ ràng: độ chính xác trường dữ liệu, mức độ suy diễn không có căn cứ và chất lượng kết luận.
4. Đối chiếu với kết quả phân tích của người thực hiện và các nguồn dữ liệu bảo mật khác.

## 7. Tệp bằng chứng

- `output/live_demo_event10_ai_clean.txt`: câu trả lời Gemma đã làm sạch.
- `output/live_demo_event10_ai.txt`: đầu ra thô của lượt chạy, có thể chứa thông tin điều khiển terminal.
- `output/live_demo_events_20261024_123356.duckdb`: cơ sở dữ liệu của phiên demo.

**Lưu ý:** Báo cáo này bổ sung một đánh giá riêng cho Event ID 10. Không thay thế hoặc sửa kết quả thử nghiệm Event ID 22 trước đó.
