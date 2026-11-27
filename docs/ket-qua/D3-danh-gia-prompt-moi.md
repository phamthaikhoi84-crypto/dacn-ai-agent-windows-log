# D3 – Đánh giá prompt mới cho SLM trong AI Agent Windows Log

## 1. Mục tiêu

Đánh giá thay đổi prompt SLM nhằm:
- Cho phép mô hình cân nhắc từng kỹ thuật ứng viên độc lập.
- Đánh giá dựa trên bằng chứng được trích xuất từ log.
- Phân biệt kết luận kỹ thuật, hoạt động bình thường và trường hợp chưa đủ bằng chứng.
- Hạn chế việc SLM tự suy diễn hoặc chọn kỹ thuật không phù hợp.
- Giữ nguyên nguyên tắc xác minh: thiếu bằng chứng bắt buộc thì không kết luận tấn công.

## 2. Nguyên tắc đánh giá

Agent thực hiện quy trình theo các bước:
1. Gom sự kiện thành phiên theo máy, LogonId và quan hệ tiến trình.
2. Đối chiếu mẫu/ứng viên kỹ thuật.
3. Kiểm tra bằng chứng bắt buộc trong DuckDB.
4. Gửi ngữ cảnh và bằng chứng cho SLM.
5. Kiểm tra lại kết quả SLM với ứng viên và bằng chứng.

Quy tắc an toàn: kết quả SLM không thuộc danh sách ứng viên hoặc không có đủ bằng chứng bắt buộc thì không được kết luận kỹ thuật. Trạng thái chưa đủ điều kiện phải được giữ là chưa xác nhận, không tự chuyển thành kết luận tấn công.

## 3. So sánh prompt cũ và prompt mới trên bộ phát triển

| Chỉ tiêu | Prompt cũ | Prompt mới |
|---|---:|---:|
| Số phiên trong phép so sánh | 21 | 21 |
| Kết quả phát hiện đúng theo báo cáo thử nghiệm | 12/21 | 2/21 |
| Số kết quả bị giảm so với prompt cũ | – | 10 |

Trong lần thử nghiệm này, prompt mới làm giảm số kết quả phát hiện từ 12 xuống 2 trên bộ 21 phiên. Mười trường hợp bị giảm đều được SLM đưa về trạng thái `CHUA_XAC_NHAN`; không có trường hợp nào được SLM chọn `BINH_THUONG`.

Kết quả cho thấy prompt mới chưa đạt mục tiêu phân biệt rõ hoạt động bình thường với hoạt động chưa đủ bằng chứng. Không thể diễn giải việc giảm kết luận tấn công thành khả năng nhận diện bình thường tốt hơn.

## 4. Kết quả chạy trên log D3

Báo cáo chạy trên log D3 ghi nhận:
- 72 kết quả được trích xuất; đây là số kết quả/đầu mục được ghi nhận, không mặc nhiên là 72 phiên liên tục độc lập.
- 65 dòng có mã kỹ thuật.
- Nhiều trường hợp không vượt qua kiểm tra bằng chứng bắt buộc.
- Có một trường hợp T1053.005 đạt 3/3 bằng chứng lõi, nhưng bằng chứng liên quan đạt 0/3.
- Không có kết luận tấn công được xác nhận trong lượt chạy này.

Các con số trên mô tả đầu ra của lượt chạy cụ thể; không được sử dụng làm tỷ lệ phát hiện nếu chưa xác định cùng một mẫu số và ground truth cho từng phiên.

## 5. Đo lượng token

| Chỉ tiêu | Kết quả |
|---|---:|
| Số dòng đo token | 21 |
| Tổng prompt token | 105.560 |
| Trung bình | 5.026,67 |
| Nhỏ nhất | 2.211 |
| Lớn nhất | 7.427 |
| Context | 8.192 |
| Mức sử dụng context lớn nhất | 90,66% |

Đây là 21 dòng đo token. Không khẳng định đây là 21 lượt gọi API thực tế nếu log đo không chứng minh được điều đó.

## 6. So sánh bổ sung trên log tuần 7

Nguồn log: `sysmon_binh_thuong_D3_20261119_072713.evtx`.

- 436.729 sự kiện.
- 5.414 phiên sau khi gom nhóm.
- Đầu ra prompt cũ có 150 tiêu đề phiên; prompt mới có 72 tiêu đề phiên.
- Dòng đo token: prompt cũ 34; prompt mới 21.
- Dòng/đầu mục xác minh: prompt cũ 149; prompt mới 72.
- Prompt cũ có 15 dấu vết ứng viên trong log: T1547.001 có 11 và T1059.001 có 4.
- Prompt mới không có dấu vết ứng viên tương ứng trong phần so sánh này.
- Các dấu vết ứng viên của prompt cũ đều không vượt qua kiểm tra bằng chứng bắt buộc.

**Giới hạn:** Số tiêu đề phiên, dòng đo token và dòng xác minh giữa hai đầu ra không bằng nhau. Vì vậy không được dùng phép chia trực tiếp các số này để kết luận tỷ lệ phát hiện hoặc tỷ lệ báo nhầm. Kết quả chỉ là so sánh dấu vết đầu ra trên cùng nguồn EVTX.

## 7. Quyết định về LoRA

Không triển khai huấn luyện LoRA trong phạm vi thử nghiệm D3 do giới hạn thời gian và phạm vi đồ án. Đây là quyết định giới hạn phạm vi thực hiện, không phải kết luận rằng LoRA không hiệu quả.

## 8. Kết luận

Prompt mới đã được triển khai và đánh giá, nhưng **chưa đạt tiêu chí chấp nhận**.

Các vấn đề chính:
- Số kết quả phát hiện trên bộ phát triển giảm từ 12/21 xuống 2/21.
- Mười trường hợp giảm kết quả chuyển thành `CHUA_XAC_NHAN`, không phải `BINH_THUONG`.
- Lượt chạy log D3 chưa chứng minh được khả năng nhận diện hoạt động bình thường một cách đáng tin cậy.
- Phép so sánh bổ sung tuần 7 có số lượng đầu ra khác nhau nên chưa đủ điều kiện tính tỷ lệ so sánh trực tiếp.

## 9. Hướng xử lý tiếp theo

1. Rà soát lý do prompt mới làm các trường hợp trước đây được xác nhận chuyển thành `CHUA_XAC_NHAN`.
2. Tách rõ ba trạng thái: có đủ bằng chứng cho kỹ thuật, có căn cứ xác định hoạt động bình thường, và chưa đủ dữ liệu để kết luận.
3. Đánh giá trên cùng một tập phiên có ground truth và cùng mẫu số giữa prompt cũ/mới.
4. Đo riêng số lần gọi SLM, token đầu vào/đầu ra, thời gian và RAM để bảo đảm các chỉ số có thể đối chiếu.
5. Chỉ công nhận D3 đạt khi prompt mới cải thiện phân biệt bình thường/bất thường mà không làm mất các phát hiện đúng trên bộ phát triển.

## 10. Trạng thái hạng mục

**Đã triển khai và đã đánh giá – chưa đạt tiêu chí chấp nhận.**

Không ghi D3 là “đạt” hoặc “hoàn thành đạt yêu cầu”. Có thể ghi nhận phần công việc thử nghiệm và báo cáo đã hoàn tất, đồng thời giữ kết luận kỹ thuật là chưa đạt.
