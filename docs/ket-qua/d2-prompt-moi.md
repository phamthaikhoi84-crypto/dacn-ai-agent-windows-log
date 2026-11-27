# D2 - Đánh giá Prompt v2 trên bộ log phát triển

## 1. Mục tiêu

Đánh giá Prompt v2 trong `src/slm.py` trên bộ log phát triển
được chia theo các kỹ thuật MITRE ATT&CK.

Prompt v2 hướng đến việc đánh giá độc lập từng ứng viên,
đối chiếu hành vi trong log và bằng chứng bắt buộc trong DuckDB.
SLM chỉ đưa ra nhận định; Agent tiếp tục kiểm chứng trước khi
đưa ra kết luận kỹ thuật.

Nguyên tắc quan trọng:
- Chỉ kết luận kỹ thuật khi mã kỹ thuật thuộc danh sách ứng viên.
- Phải có bằng chứng bắt buộc trong DuckDB.
- Phải có bằng chứng hành vi thực tế trong log.
- Thiếu bằng chứng thì không được kết luận tấn công.
- Không đồng nhất việc không có ứng viên với việc dữ liệu
  thực tế chắc chắn là hoạt động bình thường.

## 2. Cấu hình thử nghiệm

- Mô hình: `phi4-mini:latest`.
- Context: 8192 tokens (theo thông tin đo trong file đầu ra).
- Ngưỡng điểm ứng viên: 0.5.
- Bộ mẫu chuỗi: `models/mau_chuoi.json`.
- Số kỹ thuật trong bộ mẫu: 8.
- Cửa sổ chuỗi: 6.
- Số dòng tối đa gửi quanh dấu vết: 40.
- Thư mục kết quả: `output/danh_gia_dev_v2/prompt_v2_lan1`.
- Số file EVTX được đánh giá: 21.
- Phương pháp: chạy Agent, lưu đầu ra từng file và đối chiếu
  kết quả SLM với bước xác minh bằng chứng.

## 3. Kết quả tổng hợp

Tổng hợp từ 21 file đầu ra:

| Trạng thái trong đầu ra Agent | Số phiên | Tỷ lệ |
|---|---:|---:|
| Kết luận kỹ thuật đã qua xác minh | 12 | 57,1% |
| Bình thường - dừng ở bước 2 | 8 | 38,1% |
| Chưa xác nhận do thiếu bằng chứng | 1 | 4,8% |
| Tổng | 21 | 100% |

12 phiên kết luận kỹ thuật đều có mã kỹ thuật trùng với nhãn
kỹ thuật trong tên file thử nghiệm. Các phiên này đều có dấu vết
bắt buộc và bằng chứng thực tế được bước kiểm chứng chấp nhận.

## 4. Kết quả theo kỹ thuật

| Kỹ thuật | Số file | Kết luận kỹ thuật | Bình thường | Chưa xác nhận |
|---|---:|---:|---:|---:|
| T1053.005 | 5 | 2 | 3 | 0 |
| T1059.001 | 4 | 2 | 2 | 0 |
| T1105 | 3 | 2 | 1 | 0 |
| T1136.001 | 4 | 2 | 1 | 1 |
| T1547.001 | 5 | 4 | 1 | 0 |
| Tổng | 21 | 12 | 8 | 1 |

## 5. Trường hợp chưa xác nhận

File: `T1136.001-9.txt`.

- Ứng viên T1136.001 có điểm 0.989.
- Chuỗi hành vi có dấu hiệu tương đồng với kỹ thuật T1136.001.
- Kiểm tra DuckDB cho thấy thiếu bằng chứng bắt buộc:
  tạo tài khoản cục bộ bằng `net user ... /add` hoặc
  `New-LocalUser`.
- Agent không gọi SLM để kết luận khi không có ứng viên
  đủ dấu vết.
- Kết quả cuối cùng: CHƯA XÁC NHẬN.

Đây là ví dụ cho thấy điểm ứng viên cao không tự động trở thành
kết luận tấn công. Hàng rào bằng chứng vẫn được áp dụng.

## 6. Đánh giá

### 6.1. Điểm đạt được

1. Có 12/21 file được kết luận đúng mã kỹ thuật theo nhãn
   trong tên file thử nghiệm.
2. Các kết luận này đều đi qua bước kiểm chứng bằng chứng.
3. Không lấy riêng điểm ứng viên của mô hình làm kết luận.
4. Trường hợp T1136.001-9 được giữ ở trạng thái chưa xác nhận
   khi thiếu bằng chứng bắt buộc.
5. Các trường hợp không có ứng viên đủ điều kiện được dừng
   trước bước gọi SLM.

### 6.2. Điểm cần cải thiện

Có 8/21 file được Agent phân loại bình thường ngay ở bước 2.
Do tên file thuộc bộ thử nghiệm theo kỹ thuật tấn công, cần
đối chiếu nội dung EVTX và ground truth để xác định đây có phải
các trường hợp bỏ sót hay không.

Không được xem 8 trường hợp này là 8 mẫu hoạt động bình thường
thực tế chỉ dựa trên nhãn đầu ra của Agent.

Cần tiếp tục xem xét:
- Vì sao chuỗi hành vi không tạo được ứng viên đủ ngưỡng.
- Những sự kiện nào bị loại khi chuyển từ log sang ký hiệu.
- Khả năng mất dấu vết do gom phiên hoặc cây tiến trình.
- Sự khác nhau giữa nhãn kỹ thuật dự kiến và hành vi thực tế
  được ghi nhận trong EVTX.

### 6.3. Giới hạn đánh giá

1. Kết quả được tổng hợp từ 21 file đầu ra, không đại diện
   cho toàn bộ dữ liệu phát triển.
2. Nhãn kỹ thuật trong tên file chưa thay thế được bảng
   ground truth độc lập.
3. Chưa đủ cơ sở tính Accuracy, Precision, Recall và F1.
4. Tỷ lệ 12/21 chỉ mô tả số file có kết luận kỹ thuật đã
   qua xác minh trong lượt thử nghiệm này.
5. Chưa có phép so sánh đối chứng đầy đủ giữa Prompt cũ
   và Prompt v2 trên cùng điều kiện chạy.
6. Kết quả của thử nghiệm này không được gộp với dữ liệu
   log bình thường trong báo cáo D3.

## 7. Kết luận

Prompt v2 đã tạo được 12 kết luận kỹ thuật có bằng chứng
được kiểm chứng trên 21 file thử nghiệm.

Có 8 file được Agent phân loại bình thường ở bước 2 và
1 file chưa xác nhận do thiếu bằng chứng bắt buộc.

Kết quả cho thấy cơ chế xác minh bằng chứng được duy trì,
nhưng khả năng đưa ra ứng viên còn cần cải thiện. Đặc biệt,
cần điều tra 8 trường hợp bị phân loại bình thường để xác định
nguyên nhân bỏ sót trước khi đánh giá hiệu quả tổng thể.

Không sử dụng tỷ lệ 12/21 làm Accuracy, Precision hoặc Recall
khi chưa có ground truth độc lập.

Trạng thái D2: ĐÃ THỬ NGHIỆM, CẦN TIẾP TỤC ĐÁNH GIÁ
CÁC TRƯỜNG HỢP BỎ SÓT.
