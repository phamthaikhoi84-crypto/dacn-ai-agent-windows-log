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

Prompt mới bổ sung lựa chọn BINH_THUONG nhằm giảm việc
SLM phải gán một kỹ thuật MITRE ATT&CK cho hoạt động
không có dấu hiệu tấn công.

Tuy nhiên, file kết quả hiện tại chưa đầy đủ và có vấn đề
mã hóa văn bản. Chưa thể xác định tổng số phiên được xử lý,
tỷ lệ nhận diện log bình thường, tỷ lệ báo nhầm hoặc mức
cải thiện so với Prompt cũ trên cùng một tập dữ liệu.

Việc thiếu bằng chứng bắt buộc khiến Agent giữ trạng thái
CHUA_XAC_NHAN, thay vì kết luận chỉ dựa vào đề xuất của SLM.

## 6. Hạn chế

1. File kết quả không chứa đầy đủ kết quả tất cả phiên.
2. Văn bản đầu ra gặp lỗi mã hóa tiếng Việt.
3. Chưa có phép so sánh Prompt cũ và Prompt mới trên cùng
   dữ liệu, cùng cấu hình và cùng điều kiện.
4. Chưa đo RAM đỉnh trong quá trình suy luận.
5. Chưa thể tính các chỉ số Precision, Recall, F1 hoặc
   tỷ lệ nhận diện bình thường từ phần kết quả hiện có.
6. Số lần xuất hiện kỹ thuật là số liệu đề xuất, không phải
   ground truth.

## 7. Kết luận

Đã triển khai và chạy thử phương pháp Prompt mới trên log
Sysmon bình thường. Cơ chế xác minh bằng chứng tiếp tục
hoạt động và không cho phép xác nhận tấn công khi chưa đủ
bằng chứng.

Kết quả thu thập hiện tại chưa đủ để khẳng định Prompt mới
cải thiện độ chính xác so với Prompt cũ. Cần dữ liệu đầu ra
đầy đủ và phép so sánh cùng điều kiện để đánh giá định lượng.
