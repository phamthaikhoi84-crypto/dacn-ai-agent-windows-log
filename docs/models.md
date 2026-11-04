# Thử nghiệm mô hình ngôn ngữ nhỏ trên Ollama

## 1. Môi trường thử nghiệm

- Máy thử nghiệm: Máy Dũng
- Hệ điều hành: Windows
- CPU: Intel(R) Core(TM) i5-8350U CPU @ 1.70GHz
- RAM hệ thống: 15.84 GB (xấp xỉ 16 GB)
- Phiên bản Ollama: 0.40.0
- Phương thức suy luận: CPU, không sử dụng GPU để tăng tốc.
- Ngày thử nghiệm: 16/10/2026
- Context: 4096

## 2. Câu hỏi thử nghiệm chung

Cả bốn mô hình sử dụng cùng một câu hỏi:

> Explain what PowerShell Script Block Logging is in 3 sentences.

## 3. Bảng kết quả thử nghiệm

| Mô hình | Dung lượng tải về | Eval rate (tokens/s) | RAM (ollama ps) | Processor | Thời gian tổng | Đánh giá câu trả lời |
|---|---:|---:|---:|---|---:|---|
| qwen3:4b-instruct-2507-q4_K_M | 2.5 GB | 7.47 | 3.2 GB | 100% CPU | 15.904 giây | Sai một phần |
| llama3.2:3b | 2.0 GB | 10.15 | 2.6 GB | 100% CPU | 12.502 giây | Sai |
| gemma3:4b | 3.4 GB | 8.08 | 2.9 GB | 100% CPU | 9.180 giây | Khá chính xác |
| phi4-mini | 2.0 GB | 7.54 | 3.1 GB | 100% CPU | 8.853 giây | Khá chính xác |

Lưu ý:
- Dung lượng tải về là dung lượng lưu trữ mô hình.
- RAM từ `ollama ps` là mức bộ nhớ sử dụng khi mô hình đang được nạp.
- Eval rate là tốc độ đánh giá/sinh token của mô hình, không đồng nghĩa với tổng thời gian hoàn thành.
- Kết quả thời gian có thể thay đổi theo độ dài đầu ra, tình trạng máy và điều kiện chạy thử.

## 4. Nhận xét kết quả

### 4.1. Hiệu năng

- Cả bốn mô hình đều chạy thành công trên Ollama bằng CPU.
- Llama 3.2 3B có tốc độ sinh token cao nhất, đạt 10.15 tokens/s.
- Phi-4-mini có thời gian tổng thấp nhất trong lần thử nghiệm, đạt 8.853 giây.
- Gemma 3 4B có thời gian tổng 9.180 giây và tốc độ sinh 8.08 tokens/s.
- Qwen3 4B có tốc độ sinh thấp nhất, đạt 7.47 tokens/s, đồng thời có thời gian tổng cao nhất, 15.904 giây.
- Gemma 3 4B có dung lượng tải về lớn nhất, 3.4 GB. Llama 3.2 3B và Phi-4-mini có dung lượng nhỏ nhất, 2.0 GB.

### 4.2. Độ chính xác câu trả lời

| Mô hình | Đánh giá chi tiết |
|---|---|
| Qwen3 4B | Giải thích được chức năng chính nhưng hướng dẫn bật Script Block Logging chưa chính xác. |
| Llama 3.2 3B | Nhầm lẫn giữa ghi nội dung Script Block với ghi kết quả đầu ra của script; hướng dẫn bật tính năng không chính xác. |
| Gemma 3 4B | Nắm được chức năng cơ bản nhưng có nhầm lẫn về nội dung được ghi lại, chưa giải thích rõ cơ chế hoạt động. |
| Phi-4-mini | Hiểu mục đích giám sát và kiểm toán bảo mật nhưng chưa mô tả đầy đủ cơ chế ghi nội dung Script Block. |

### 4.3. Nhận xét chung

Trong lần thử nghiệm này, Llama 3.2 3B có tốc độ sinh token cao nhất, trong khi Phi-4-mini có thời gian tổng thấp nhất.

Gemma 3 4B và Phi-4-mini có câu trả lời tương đối chính xác hơn trong câu hỏi kiến thức chung. Tuy nhiên, chưa thể kết luận khả năng phân tích log bảo mật của hai mô hình chỉ dựa trên kết quả này.

Câu hỏi thử nghiệm chỉ đánh giá kiến thức cơ bản về PowerShell Script Block Logging, chưa đánh giá được khả năng:
- Phân tích các sự kiện Windows/Sysmon.
- Nhận diện hành vi đáng ngờ.
- Đối chiếu bằng chứng với kỹ thuật MITRE ATT&CK.
- Phân tích quyền GrantedAccess trong Event ID 10.
- Trả về JSON đúng cấu trúc theo yêu cầu của AI Agent.

## 5. Kế hoạch đánh giá mô hình trong đồ án

Để lựa chọn mô hình phù hợp cho AI Agent Windows Log, cần thực hiện thêm các thử nghiệm trên dữ liệu log thực tế.

Các tiêu chí đánh giá:

| Tiêu chí | Nội dung kiểm tra |
|---|---|
| Nhận diện kỹ thuật | Chọn đúng mã MITRE ATT&CK trong danh sách ứng viên. |
| Độ chính xác bằng chứng | Trích dẫn đúng nội dung có thật trong log. |
| Giải thích | Giải thích đúng hành vi, không tự suy diễn. |
| Phân tích LSASS | Kiểm tra đúng Event ID 10 và quyền GrantedAccess. |
| Phân biệt bình thường/bất thường | Không cảnh báo sai với log hoạt động bình thường. |
| Định dạng đầu ra | Trả về JSON hợp lệ với đủ ba trường quy định. |
| Hiệu năng | Đo thời gian xử lý, tốc độ sinh token và mức sử dụng RAM. |

Các trường hợp kiểm thử dự kiến:

1. Log PowerShell thực hiện hành vi đáng chú ý.
2. Log truy cập tiến trình LSASS bằng Event ID 10.
3. Log có GrantedAccess chứa PROCESS_VM_READ.
4. Log có GrantedAccess không chứa PROCESS_VM_READ.
5. Log Windows hoạt động bình thường.
6. Log thiếu bằng chứng để xác nhận kỹ thuật.

## 6. Kết luận và định hướng lựa chọn mô hình

Dựa trên thử nghiệm kiến thức chung ngày 16/10/2026:

- Phi-4-mini là ứng viên ưu tiên cho giai đoạn kiểm thử tiếp theo vì có thời gian tổng thấp nhất và câu trả lời khá chính xác.
- Gemma 3 4B là ứng viên dự phòng vì có kết quả trả lời khá chính xác và thời gian tổng gần với Phi-4-mini.
- Llama 3.2 3B có ưu thế về tốc độ sinh token nhưng cần đánh giá thêm độ chính xác.
- Qwen3 4B cần được kiểm tra thêm về khả năng giải thích và thời gian xử lý.

**Chưa chốt mô hình chính thức ở giai đoạn thử nghiệm kiến thức chung.** Quyết định cuối cùng sẽ dựa trên kết quả kiểm thử phân tích log Windows/Sysmon thực tế và khả năng tích hợp ổn định vào AI Agent.

Mô hình được lựa chọn phải đáp ứng đồng thời yêu cầu về độ chính xác, bằng chứng, giải thích, định dạng JSON và hiệu năng trên máy thử nghiệm.
