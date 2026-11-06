KẾT QUẢ KIỂM THỬ AGENT TRÊN LOG WINDOWS BÌNH THƯỜNG

1. Mục đích kiểm thử

Mục đích của thử nghiệm là đánh giá khả năng xử lý log Windows/Sysmon bình thường của AI Agent và kiểm tra khả năng hạn chế cảnh báo nhầm.

Các nội dung cần đánh giá:

- Khả năng đọc và xử lý log Sysmon.
- Khả năng gom các sự kiện thành phiên hoạt động.
- Khả năng chuyển sự kiện thành chuỗi ký hiệu và so khớp với mẫu đã huấn luyện.
- Khả năng phân biệt hoạt động bình thường với các chuỗi hành vi có dấu hiệu giống kỹ thuật tấn công.
- Khả năng kiểm tra bằng chứng trước khi đưa ra kết luận.

2. Quy trình hoạt động của Agent

Agent thực hiện quy trình phân tích gồm 5 bước:

1. Gom phiên: Nhận sự kiện Sysmon và gom theo máy tính, LogonId và cây tiến trình.
2. Chuyển đổi và so khớp: Chuyển sự kiện thành ký hiệu, sau đó so khớp với các mẫu chuỗi đã huấn luyện để tìm kỹ thuật ATT&CK có khả năng xuất hiện.
3. Kiểm tra dấu vết: Nếu điểm khớp đạt ngưỡng, Agent truy vấn DuckDB để tìm các dấu vết bắt buộc của kỹ thuật tương ứng.
4. Phân tích bằng SLM: Sử dụng mô hình ngôn ngữ để phân tích chuỗi log và các kỹ thuật ứng viên.
5. Kiểm chứng kết quả: Đối chiếu kết quả phân tích với bằng chứng do Python kiểm tra. Nếu không đủ bằng chứng, Agent giữ trạng thái chưa xác nhận thay vì kết luận tấn công.

Nếu điểm khớp thấp hơn ngưỡng, phiên được xem là bình thường và dừng ở bước 2.

3. Dữ liệu kiểm thử

Thử nghiệm sử dụng hai tập dữ liệu log Windows bình thường:

Tập dữ liệu| Tổng số phiên| Số phiên bị đánh dấu
Log của Dũng| 2.573| 10
Log của Thiên| 807| 0
Tổng cộng| 3.380| 10

Hai tập dữ liệu có điều kiện kiểm thử khác nhau nên cần phân tích riêng, không xem chúng là hai tập kiểm thử độc lập có cùng mức độ.

4. Kết quả trên log của Dũng

- Tổng số phiên: 2.573.
- Số phiên bị đánh dấu: 10.
- Đây là dữ liệu đã được sử dụng trong quá trình điều chỉnh dấu vết phát hiện.

Kết quả cho thấy có 10 phiên hoạt động bình thường bị Agent đưa vào diện cần xem xét.

Tuy nhiên, do dữ liệu này đã tham gia vào quá trình điều chỉnh dấu vết nên kết quả không thể được xem là đánh giá độc lập hoàn toàn trên dữ liệu chưa từng sử dụng.

5. Kết quả trên log của Thiên

- Tổng số phiên: 807.
- Số phiên bị đánh dấu: 0.
- Đây là log mới, nhưng vẫn cùng máy tính với dữ liệu được sử dụng để dạy lớp bình thường.

Kết quả cho thấy Agent không đánh dấu phiên nào trong 807 phiên được kiểm tra.

Đây là kết quả tích cực trên tập log mới. Tuy nhiên, vì dữ liệu vẫn đến từ cùng máy tính với dữ liệu dạy lớp bình thường nên chưa chứng minh được khả năng hoạt động ổn định trên các máy tính khác.

6. Cơ chế hạn chế cảnh báo nhầm

Agent không chỉ dựa vào điểm so khớp chuỗi để kết luận một phiên là tấn công.

Hệ thống còn thực hiện:

- Kiểm tra dấu vết bắt buộc tương ứng với kỹ thuật ATT&CK.
- Đối chiếu bằng chứng thực tế trong DuckDB.
- Sử dụng SLM để phân tích các kỹ thuật ứng viên.
- Kiểm chứng kết quả SLM với bằng chứng do Python kiểm tra.
- Giữ trạng thái chưa xác nhận nếu thiếu bằng chứng.

Cơ chế này giúp hạn chế việc kết luận tấn công chỉ dựa trên một sự kiện đơn lẻ hoặc một chuỗi có điểm tương đồng cao.

7. Hạn chế của thử nghiệm

7.1. Đối với log của Dũng

Kết quả 10/2.573 phiên được tính trên dữ liệu đã sử dụng để điều chỉnh dấu vết phát hiện.

Vì vậy, đây không phải tập kiểm thử độc lập hoàn toàn. Kết quả có thể chịu ảnh hưởng từ quá trình phát triển và điều chỉnh hệ thống.

7.2. Đối với log của Thiên

Kết quả 0/807 phiên được ghi nhận trên log mới của Thiên.

Tuy nhiên, log này vẫn đến từ cùng máy tính với dữ liệu được sử dụng để dạy lớp bình thường. Vì vậy, kết quả mới đánh giá được trên dữ liệu mới của cùng môi trường máy tính, chưa chứng minh khả năng tổng quát hóa trên máy tính khác.

7.3. Chưa có log bình thường mới từ máy lạ

Hiện tại chưa có tập log bình thường đáp ứng đồng thời hai điều kiện:

- Là dữ liệu mới, chưa tham gia huấn luyện hoặc điều chỉnh dấu vết.
- Được thu thập từ một máy tính khác với máy đã sử dụng để dạy lớp bình thường.

Đây là hạn chế quan trọng cần được khắc phục trong các thử nghiệm tiếp theo.

7.4. Phạm vi kết luận

Các kết quả chỉ phản ánh khả năng xử lý của Agent trên những tập log đã kiểm tra.

Không thể từ các kết quả này khẳng định Agent không bao giờ cảnh báo nhầm hoặc có thể phát hiện chính xác mọi kỹ thuật tấn công trong mọi môi trường Windows.

8. Kết luận và hướng phát triển

Qua hai tập dữ liệu kiểm thử:

- Log Dũng: 10/2.573 phiên bị đánh dấu.
- Log Thiên: 0/807 phiên bị đánh dấu.

Kết quả trên log Thiên cho thấy Agent không đánh dấu phiên nào trong 807 phiên mới được kiểm tra. Đây là tín hiệu tích cực, nhưng cần đặt trong đúng bối cảnh vì log vẫn đến từ cùng máy tính với dữ liệu dùng để dạy lớp bình thường.

Kết quả trên log Dũng cũng cần được nhìn nhận thận trọng vì tập dữ liệu này đã được sử dụng trong quá trình điều chỉnh dấu vết.

Hướng phát triển tiếp theo:

1. Thu thập log bình thường mới từ một máy tính khác.
2. Không sử dụng tập log kiểm thử mới để điều chỉnh dấu vết trước khi đánh giá.
3. Giữ cố định mô hình và tham số trong quá trình kiểm thử.
4. Kiểm tra thủ công các phiên bị đánh dấu để xác định nguyên nhân.
5. Mở rộng số lượng máy tính và môi trường Windows được kiểm thử.
6. Ghi nhận riêng số phiên bình thường, số phiên bị đánh dấu và số phiên chưa xác nhận.

Kết luận chung: Kết quả hiện tại cho thấy Agent đã xử lý được hai tập log bình thường với tổng cộng 3.380 phiên, trong đó có 10 phiên bị đánh dấu. Tuy nhiên, cần bổ sung thử nghiệm trên log bình thường mới từ máy tính lạ để đánh giá khách quan hơn khả năng tổng quát hóa và hạn chế cảnh báo nhầm của hệ thống.
