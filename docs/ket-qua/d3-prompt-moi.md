# D3 - Đánh giá phương pháp Prompt mới

## 1. Mục tiêu

Đánh giá phương pháp Prompt mới của Agent khi phân tích Sysmon,
bổ sung lựa chọn BINH_THUONG để SLM có thể nhận diện hoạt động
bình thường thay vì bắt buộc lựa chọn kỹ thuật MITRE ATT&CK.

Kết quả SLM vẫn phải đi qua bước xác minh ứng viên và bằng chứng
bắt buộc. SLM không được tự quyết định kết luận tấn công.

## 2. Cấu hình thử nghiệm

- Máy thử nghiệm: Máy Dũng.
- Dữ liệu: Log Sysmon bình thường mới.
- Prompt mới: SLM_PROMPT_MOI=1.
- Context: 8192 tokens.
- Database: output/D3_prompt_moi.duckdb.
- File kết quả: output/D3_prompt_moi.txt.
- Mô hình: mô hình được cấu hình trong Ollama tại thời điểm thử nghiệm.
- Phương pháp: chạy Agent trên dữ liệu log và thu thập kết quả.

## 3. Kết quả thu thập được

> **Lưu ý (Khôi, 22/11/2026): số liệu mục 3 không dùng được.** Lần chạy trên log Dũng dùng `agent.py` đã sửa ở nhánh `review-dung-d2-d3`, thêm điều kiện "bằng chứng liên quan" ở bước 5. Điều kiện này so dòng bằng chứng của SLM (định dạng của `chon_dong_cho_slm`) với dòng dấu vết của DuckDB (định dạng của `dau_vet.dong_log`), hai định dạng khác nhau nên gần như không bao giờ khớp, vì vậy chặn mọi kết luận (dòng "bằng chứng liên quan 0/3" ở 3.2). Kiểm tra trên `sysmon_1_11_exec_as_system_via_schedtask.evtx`: bản trên main KẾT LUẬN T1053.005, bản sửa ra CHƯA XÁC NHẬN, cả ở chế độ không SLM. Thay đổi `agent.py` này không gộp vào main; đo lại trên log Dũng ở tuần 7 bằng `agent.py` trên main.

File đầu ra hiện có 72 mục kết quả được trích xuất,
thuộc các ID phiên từ #74 đến #276.
Đây là các kết quả thu thập được trong file, không phải
72 phiên liên tiếp và không đại diện toàn bộ dữ liệu đầu vào.

### 3.1. Kết quả đề xuất kỹ thuật

| Kỹ thuật | Số lần xuất hiện |
|---|---:|
| T1053.005 | 25 |
| T1136.001 | 15 |
| T1003.001 | 13 |
| T1070.001 | 8 |
| T1059.001 | 3 |
| T1105 | 1 |
| Tổng số dòng có mã kỹ thuật | 65 |

Các con số trên là số lần mã kỹ thuật xuất hiện trong phần
kết quả thu thập được. Không được xem là số cuộc tấn công
thực tế hoặc số phát hiện đúng.

### 3.2. Kiểm tra bằng chứng

Trong phần kết quả đã trích xuất:

- 64 dòng có mã kỹ thuật nhưng chưa đủ điều kiện xác nhận.
- 7 dòng kiểm tra không có ứng viên và không có bằng chứng
  (0/0).
- 1 dòng ứng viên T1053.005 có bằng chứng cốt lõi 3/3,
  nhưng bằng chứng liên quan 0/3.

Trường hợp T1053.005 chưa đủ điều kiện kết luận vì thiếu
bằng chứng liên quan theo yêu cầu xác minh.

Không ghi nhận kết luận tấn công được xác nhận trong phần
kết quả đã thu thập.

## 4. Đo lượng token Prompt

File đo token thu thập được 21 lần gọi SLM.

| Chỉ số | Kết quả |
|---|---:|
| Số lần gọi được đo | 21 |
| Tổng token Prompt | 105.560 |
| Trung bình mỗi lần gọi | 5.026,67 |
| Thấp nhất | 2.211 |
| Cao nhất | 7.427 |
| Context | 8.192 |
| Mức sử dụng Context cao nhất | 90,66% |

Số liệu đo token chỉ đại diện cho 21 lần gọi được ghi nhận.
Chưa có dữ liệu đầy đủ cho toàn bộ phiên phân tích.

## 5. Đánh giá

Kết quả so sánh trực tiếp trên bộ dữ liệu phát triển do Thiên
thực hiện trong tuần 6:

| Chỉ số | Prompt cũ | Prompt mới |
|---|---:|---:|
| Số phiên phát hiện | 12/21 | 2/21 |

Prompt mới giảm 10 phiên phát hiện so với Prompt cũ.

Kiểm tra 10 phiên bị mất phát hiện cho thấy:
- Cả 10 phiên đều được SLM lựa chọn CHUA_XAC_NHAN.
- Không có phiên nào được SLM lựa chọn BINH_THUONG.

Như vậy, việc bổ sung lựa chọn BINH_THUONG không phải nguyên
nhân trực tiếp của 10 phiên mất phát hiện. Tuy nhiên, Prompt
mới khiến SLM không đưa ra lựa chọn kỹ thuật để Agent tiếp tục
xác minh ở các phiên này.

Kết quả cho thấy Prompt mới chưa đáp ứng tiêu chí
"không làm mất phát hiện" so với Prompt cũ.

Đối với log riêng của Dũng, file kết quả hiện trích xuất được
72 mục, trong đó có 65 dòng chứa mã kỹ thuật. Đây là số liệu
thu thập riêng, không được gộp với kết quả so sánh 12/21 và
2/21 của bộ dữ liệu phát triển.

Hai chỉ số số phiên KET_LUAN và SLM_BINH_THUONG trên log
riêng của Dũng chưa đo được do vấn đề mã hóa và giới hạn
dữ liệu đầu ra. Chuyển việc đo này sang tuần 7.

## 6. Hạn chế

1. Log riêng của Dũng chưa có đầu ra đầy đủ và gặp vấn đề
   mã hóa tiếng Việt, nên chưa xác định được chính xác số
   phiên KET_LUAN và SLM_BINH_THUONG cho từng cách hỏi.
2. Kết quả 12/21 và 2/21 là kết quả so sánh trên bộ dữ liệu
   phát triển của Thiên, không phải kết quả đo trên log riêng
   của Dũng.
3. Token Prompt cao nhất là 7.427/8.192, tương đương khoảng
   91% Context. Những phiên có 3 ứng viên hoặc nội dung dài
   hơn có nguy cơ vượt giới hạn Context.
4. Chưa đo RAM đỉnh trong quá trình suy luận.
5. Chưa đủ dữ liệu để tính đầy đủ Precision, Recall và F1
   cho toàn bộ hệ thống.
6. Số lần xuất hiện mã kỹ thuật trong log Dũng là số liệu
   đề xuất, không phải số cuộc tấn công thực tế hoặc số
   phát hiện đúng.

## 7. Kết luận

Đã triển khai và đo thử phương pháp Prompt mới.

Trên bộ dữ liệu phát triển của Thiên, Prompt cũ phát hiện
12/21 phiên, trong khi Prompt mới chỉ phát hiện 2/21 phiên.
Có 10 phiên mất phát hiện và cả 10 đều do SLM lựa chọn
CHUA_XAC_NHAN; không có phiên nào chọn BINH_THUONG.

Do đó, Prompt mới chưa đạt tiêu chí "không mất phát hiện"
so với Prompt cũ.

Trạng thái D3: ĐÃ THỬ, CHƯA ĐẠT.

Chưa sử dụng Prompt mới làm cấu hình chính thức. Cần tiếp tục
phân tích nguyên nhân, đánh giá và cải thiện phương pháp trong
tuần 7 trước khi xem xét áp dụng.
