# KẾT QUẢ KIỂM THỬ AGENT TRÊN LOG WINDOWS BÌNH THƯỜNG

## 1. Mục đích kiểm thử

Mục đích của thử nghiệm là đánh giá khả năng xử lý log Windows/Sysmon bình thường của AI Agent và kiểm tra khả năng hạn chế cảnh báo nhầm.

Các nội dung cần đánh giá:

- Khả năng đọc và xử lý log Sysmon.
- Khả năng gom các sự kiện thành phiên hoạt động.
- Khả năng chuyển sự kiện thành chuỗi ký hiệu và so khớp với mẫu đã huấn luyện.
- Khả năng phân biệt hoạt động bình thường với các chuỗi hành vi có dấu hiệu giống kỹ thuật tấn công.
- Khả năng kiểm tra bằng chứng trước khi đưa ra kết luận.

## 2. Quy trình hoạt động của Agent

Agent thực hiện quy trình phân tích gồm 5 bước:

1. **Gom phiên:** Nhận sự kiện Sysmon và gom theo máy tính, LogonId và cây tiến trình.
2. **Chuyển đổi và so khớp:** Chuyển sự kiện thành ký hiệu, sau đó so khớp với các mẫu chuỗi đã huấn luyện để tìm kỹ thuật ATT&CK có khả năng xuất hiện.
3. **Kiểm tra dấu vết:** Nếu điểm khớp đạt ngưỡng (0,5), Agent truy vấn DuckDB để tìm các dấu vết bắt buộc của kỹ thuật tương ứng.
4. **Phân tích bằng SLM:** Sử dụng mô hình ngôn ngữ để phân tích chuỗi log và các kỹ thuật ứng viên.
5. **Kiểm chứng kết quả:** Đối chiếu kết quả phân tích với bằng chứng do Python kiểm tra. Nếu không đủ bằng chứng, Agent giữ trạng thái chưa xác nhận thay vì kết luận tấn công.

Nếu điểm khớp thấp hơn ngưỡng, phiên được xem là bình thường và dừng ở bước 2.

## 3. Dữ liệu kiểm thử

Thử nghiệm sử dụng ba tập dữ liệu log Windows bình thường. Các số liệu đo với `--ban-tam` (bước 4 dùng bản tạm, luôn đồng ý), tức là trường hợp xấu nhất của bước 2, 3 và 5. "Bị đánh dấu" nghĩa là Agent kết luận tấn công (báo nhầm).

| Tập dữ liệu | Nguồn máy | Tổng số phiên | Số phiên bị đánh dấu | Tỷ lệ | Điều kiện của tập dữ liệu |
|---|---|---|---|---|---|
| Log của Thiên | Máy Thiên | 807 | 0 | 0% | Log mới, nhưng cùng máy với dữ liệu dùng để dạy lớp bình thường |
| Log của Dũng | Máy Dũng | 2.573 | 10 | 0,39% | Đã dùng để điều chỉnh dấu vết phát hiện |
| Log của Khôi | Máy Khôi | 779 | 15 | 1,9% (khoảng tin cậy 95%: 1,2% đến 3,2%) | Log từ máy lạ, 7 ngày (31/10–07/11), chưa từng dùng để dạy lớp bình thường hay chỉnh dấu vết |

Ba tập dữ liệu có điều kiện kiểm thử khác nhau nên cần phân tích riêng. Báo cáo không cộng gộp thành một tỷ lệ chung và không xem chúng là ba tập kiểm thử độc lập có cùng mức độ.

## 4. Kết quả trên log của Dũng

- Tổng số phiên: 2.573.
- Số phiên bị đánh dấu: 10 (0,39%).
- Đây là dữ liệu đã được sử dụng trong quá trình điều chỉnh dấu vết phát hiện.

Kết quả cho thấy có 10 phiên hoạt động bình thường bị Agent đưa vào diện cần xem xét.

Tuy nhiên, do dữ liệu này đã tham gia vào quá trình điều chỉnh dấu vết nên kết quả không thể được xem là đánh giá độc lập hoàn toàn trên dữ liệu chưa từng sử dụng.

## 5. Kết quả trên log của Thiên

- Tổng số phiên: 807.
- Số phiên bị đánh dấu: 0.
- Đây là log mới, nhưng vẫn cùng máy tính với dữ liệu được sử dụng để dạy lớp bình thường.

Kết quả cho thấy Agent không đánh dấu phiên nào trong 807 phiên được kiểm tra.

Đây là kết quả tích cực trên tập log mới. Tuy nhiên, vì dữ liệu vẫn đến từ cùng máy tính với dữ liệu dạy lớp bình thường nên chưa chứng minh được khả năng hoạt động ổn định trên các máy tính khác.

## 6. Kết quả trên log của Khôi (máy lạ)

### 6.1. Kết quả đánh dấu

- 7 ngày (31/10–07/11/2026), 54.198 sự kiện, 779 phiên.
- Máy chưa từng dùng để dạy lớp bình thường hay để chỉnh dấu vết; trong thời gian này không chạy công cụ tấn công nào.
- 735/779 phiên (94%) dừng ngay ở bước 2 vì điểm khớp thấp; chỉ 44 phiên đi tiếp sang bước kiểm tra dấu vết.
- Số phiên bị đánh dấu: 15 (1,9%, khoảng tin cậy 95% từ 1,2% đến 3,2%).

15 phiên này chỉ quy về **3 nguyên nhân gốc**, đều là phần mềm hợp lệ, không nên diễn đạt là "15 báo giả" độc lập (đã kiểm tra từng phiên):

| Nguyên nhân gốc | Kỹ thuật | Số phiên |
|---|---|---|
| Phần mềm Lenovo chạy dưới SYSTEM sau mỗi lần khởi động, tạo tác vụ `LvfDriverRemoval` bằng `schtasks /Create /XML` từ `C:\Windows\TEMP` | T1053.005 | 9 |
| Edge (và UniKey) ghi khóa Run để tự chạy khi đăng nhập | T1547.001 | 4 |
| Một ứng dụng chạy PowerShell ẩn (`-WindowStyle Hidden -ExecutionPolicy Bypass -NoProfile -NonInteractive`) chỉ để kiểm tra VS Code đã cài chưa | T1059.001 | 2 |

Cả 3 nguyên nhân đều là hoạt động hợp lệ tạo **đúng** dấu vết của kỹ thuật tấn công, nên chỉ dựa vào dòng lệnh thì không phân biệt được.

### 6.2. Kết quả thử SLM trên các phiên bị đánh dấu

Để kiểm tra bước 4 của Agent, nhóm thử SLM thật (phi4-mini) trên 6 phiên báo nhầm của 2 ngày đầu trong log máy Khôi:

| Kết quả | Số phiên | Phiên |
|---|---|---|
| Mô hình trả lời, chọn sai T1070.001, bước 5 chặn | 3 | #5, #9, #11 |
| Phản hồi bị cắt (JSON chưa hoàn chỉnh trong 1024 token) | 2 | #1, #4 |
| Ollama lỗi HTTP 500 | 1 | #41 |
| Mô hình nhận ra là hoạt động bình thường | 0 | |

### 6.3. Nhận xét

- SLM không tự nhận ra được phiên bình thường: 0/6 phiên. Ở 3 phiên mô hình còn chọn sai kỹ thuật T1070.001.
- Nhờ bước 5 (kiểm chứng bằng bằng chứng do Python kiểm tra), các kết luận sai của SLM bị chặn lại. Điều này cho thấy bước kiểm chứng là cần thiết, không nên tin kết quả SLM trực tiếp.
- Hai phiên bị cắt JSON và một phiên lỗi HTTP 500 là lỗi kỹ thuật khi chạy mô hình. Nhóm đã tăng `num_predict` lên 1024 và cho `slm.py` đọc JSON trước khi báo lỗi độ dài, nhưng 2 phiên vẫn bị cắt; lỗi HTTP 500 chưa xử lý xong. Nguyên nhân chính nhiều khả năng là phiên trên máy thật rất dài, trong khi bước 4 chỉ gửi 40 dòng đầu nên mô hình không thấy dòng gây nghi ngờ.
- Mẫu chỉ có 6 phiên và chỉ thử một mô hình, nên chưa đủ để kết luận chung về chất lượng của phi4-mini.

## 7. Cơ chế hạn chế cảnh báo nhầm

Agent không chỉ dựa vào điểm so khớp chuỗi để kết luận một phiên là tấn công.

Hệ thống còn thực hiện:

- Kiểm tra dấu vết bắt buộc tương ứng với kỹ thuật ATT&CK.
- Đối chiếu bằng chứng thực tế trong DuckDB.
- Sử dụng SLM để phân tích các kỹ thuật ứng viên.
- Kiểm chứng kết quả SLM với bằng chứng do Python kiểm tra.
- Giữ trạng thái chưa xác nhận nếu thiếu bằng chứng.

Cơ chế này giúp hạn chế việc kết luận tấn công chỉ dựa trên một sự kiện đơn lẻ hoặc một chuỗi có điểm tương đồng cao. Trên máy Khôi, 94% số phiên được loại ngay ở bước 2. Kết quả ở mục 6.2 là minh chứng cho lý do cần giữ bước kiểm chứng.

## 8. Hạn chế của thử nghiệm

### 8.1. Đối với log của Dũng

Kết quả 10/2.573 phiên (0,39%) được tính trên dữ liệu đã sử dụng để điều chỉnh dấu vết phát hiện.

Vì vậy, đây không phải tập kiểm thử độc lập hoàn toàn. Kết quả có thể chịu ảnh hưởng từ quá trình phát triển và điều chỉnh hệ thống. Chỉ trích dẫn riêng số 0,39% sẽ làm kết quả trông tốt hơn thực tế.

### 8.2. Đối với log của Thiên

Kết quả 0/807 phiên được ghi nhận trên log mới của Thiên.

Tuy nhiên, log này vẫn đến từ cùng máy tính với dữ liệu được sử dụng để dạy lớp bình thường. Vì vậy, kết quả mới đánh giá được trên dữ liệu mới của cùng môi trường máy tính, chưa chứng minh khả năng tổng quát hóa trên máy tính khác.

### 8.3. Đối với log của Khôi

Kết quả 15/779 phiên (1,9%) được ghi nhận trên máy lạ, nên đây là số gần nhất với khả năng hoạt động trên máy tính chưa từng thấy.

Tuy nhiên, số này còn những giới hạn sau:

- Mới có một máy lạ, trong 7 ngày.
- 9 trong 15 phiên bị đánh dấu có cùng một nguyên nhân (Lenovo `LvfDriverRemoval`), nên kết quả phụ thuộc nhiều vào phần mềm riêng của máy này.
- Nếu nhóm điều chỉnh dấu vết dựa trên chính các phiên này thì log của Khôi sẽ không còn là dữ liệu độc lập, cần thu thập log máy lạ khác để đo lại.

### 8.4. Phạm vi kết luận

Các kết quả chỉ phản ánh khả năng xử lý của Agent trên những tập log đã kiểm tra.

Không thể từ các kết quả này khẳng định Agent không bao giờ cảnh báo nhầm hoặc có thể phát hiện chính xác mọi kỹ thuật tấn công trong mọi môi trường Windows.

## 9. Kết luận và hướng phát triển

Qua ba tập dữ liệu kiểm thử:

| Tập dữ liệu | Kết quả | Ý nghĩa |
|---|---|---|
| Log Thiên | 0/807 | Cùng máy với dữ liệu học |
| Log Dũng | 10/2.573 (0,39%) | Đã dùng để chỉnh dấu vết |
| Log Khôi | 15/779 (1,9%) | Máy lạ, số đáng tin nhất về khả năng tổng quát hóa |

Kết quả trên log Thiên là tín hiệu tích cực, nhưng cần đặt trong đúng bối cảnh vì log vẫn đến từ cùng máy tính với dữ liệu dùng để dạy lớp bình thường.

Kết quả trên log Dũng cần được nhìn nhận thận trọng vì tập dữ liệu này đã được sử dụng trong quá trình điều chỉnh dấu vết.

Kết quả trên log Khôi cho thấy khi gặp máy lạ, tỷ lệ phiên bị đánh dấu cao hơn (1,9%), nhưng chỉ quy về 3 nguyên nhân gốc, trong đó một nguyên nhân chiếm 9/15 phiên. Điều này cho thấy hướng cải thiện rõ ràng là xử lý các nguyên nhân gốc này và huấn luyện lớp bình thường trên nhiều máy hơn.

Hướng phát triển tiếp theo:

1. Huấn luyện lớp bình thường từ log của nhiều máy, rồi đo theo kiểu "bỏ một máy ra, học trên các máy còn lại, thử trên máy bỏ ra". Cách này đo được số trên máy lạ chính xác hơn.
2. Cải thiện cách đưa dữ liệu cho SLM: chỉ tìm dấu vết gần đoạn khớp, gửi các dòng quanh dấu vết thay vì 40 dòng đầu cho mô hình.
3. Không sử dụng tập log kiểm thử mới để điều chỉnh dấu vết trước khi đánh giá.
4. Giữ cố định mô hình và tham số trong quá trình kiểm thử.
5. Kiểm tra thủ công các phiên bị đánh dấu để xác định nguyên nhân gốc.
6. Ghi nhận riêng số phiên bình thường, số phiên bị đánh dấu, số phiên chưa xác nhận và số lần SLM lỗi.

**Kết luận chung:** Kết quả hiện tại cho thấy Agent đã xử lý được ba tập log bình thường với các tỷ lệ đánh dấu lần lượt là 0/807 (máy Thiên), 10/2.573 = 0,39% (máy Dũng) và 15/779 = 1,9% (máy Khôi, máy lạ). Ba số này có điều kiện khác nhau nên được báo cáo riêng, không cộng gộp. Số 1,9% trên máy lạ là con số khách quan nhất về hạn chế cảnh báo nhầm, và cần bổ sung thử nghiệm trên nhiều máy lạ hơn để đánh giá khả năng tổng quát hóa của hệ thống.