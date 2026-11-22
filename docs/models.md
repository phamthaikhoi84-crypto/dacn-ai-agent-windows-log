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

## 7. Đánh giá 4 SLM trên bộ thử tuần 6 (K3)

### 7.1. Điều kiện thử nghiệm

- Máy thử nghiệm: Máy Khôi.
- Phương thức suy luận: Ollama, CPU.
- Mức sử dụng CPU: 100% trong quá trình suy luận.
- Bộ thử: `data/bo-thu.csv`.
- Dữ liệu: 29 phiên tấn công và 3.290 phiên log bình thường.
- Ngưỡng: 0,5.
- Số ứng viên: 3.
- Phương pháp hỏi: Prompt cũ, chưa áp dụng D3.
- Số lần hỏi SLM: 26 lần cho mỗi mô hình.
- Thời gian thử nghiệm: Đêm 20–21/11/2026.
- Luật Startup: Tắt, trừ lần đo được ghi rõ.

### 7.2. Bảng so sánh kết quả

| Mô hình | Phát hiện đúng | Báo nhầm | Chưa xác nhận do SLM | SLM lỗi | Thời gian trung bình mỗi lần hỏi | Tổng thời gian |
|---|---:|---:|---:|---:|---:|---:|
| Phi-4-mini | 6/29 (21%) | 8/3.290 (0,24%) | 11 | 0 | 52 giây | 38 phút |
| Qwen3 4B | 7/29 (24%) | 13/3.290 (0,40%) | 6 | 0 | 74 giây | 50 phút |
| Llama 3.2 3B | 6/29 (21%) | 15/3.290 (0,46%) | 4 | 0 | 45 giây | 30 phút |
| Gemma 3 4B | 6/29 (21%) | 8/3.290 (0,24%) | 11 | 0 | 58 giây | 34 phút |

### 7.3. Nhận xét từng mô hình

#### Phi-4-mini

- Phát hiện đúng 6/29 phiên tấn công, đạt 21%.
- Có 8 phiên báo nhầm trên 3.290 phiên bình thường, tương đương 0,24%.
- Có 11 phiên chưa xác nhận do kết quả SLM không đủ điều kiện kết luận.
- Thời gian trung bình mỗi lần hỏi là 52 giây; tổng thời gian chạy 38 phút.
- Mô hình có kết quả lặp lại được với lần đo tuần 5, nhưng chưa cải thiện khả năng phát hiện so với chế độ không SLM.

#### Qwen3 4B

- Phát hiện đúng 7/29 phiên, đạt 24%, cao nhất trong 4 mô hình.
- Có 13 phiên báo nhầm, tương đương 0,40%.
- Có 6 phiên chưa xác nhận.
- Thời gian trung bình mỗi lần hỏi là 74 giây; tổng thời gian 50 phút.
- Có tỷ lệ phát hiện cao nhất trong nhóm SLM nhưng thời gian xử lý dài nhất.

#### Llama 3.2 3B

- Phát hiện đúng 6/29 phiên, đạt 21%.
- Có 15 phiên báo nhầm, tương đương 0,46%, cao nhất trong nhóm SLM.
- Có 4 phiên chưa xác nhận, thấp nhất trong nhóm.
- Thời gian trung bình mỗi lần hỏi là 45 giây; tổng thời gian 30 phút.
- Có tốc độ xử lý tương đối nhanh nhưng kết quả phân loại ứng viên chưa ổn định.

#### Gemma 3 4B

- Phát hiện đúng 6/29 phiên, đạt 21%.
- Có 8 phiên báo nhầm, tương đương 0,24%.
- Có 11 phiên chưa xác nhận.
- Thời gian trung bình mỗi lần hỏi là 58 giây; tổng thời gian 34 phút.
- Có mức báo nhầm thấp tương đương Phi-4-mini nhưng chưa cải thiện số phiên phát hiện đúng.

### 7.4. Phân tích theo kỹ thuật

| Kỹ thuật | Không SLM | Phi-4-mini | Qwen3 4B | Llama 3.2 3B | Gemma 3 4B |
|---|---:|---:|---:|---:|---:|
| T1003.001 | 5/6 | 4/6 | 5/6 | 5/6 | 5/6 |
| T1053.005 | 2/4 | 2/4 | 2/4 | 1/4 | 1/4 |

- Phi-4-mini bỏ sót phiên `babyshark_mimikatz_powershell` do lựa chọn T1059.001 thay vì T1003.001.
- Llama 3.2 3B và Gemma 3 4B bỏ sót phiên `exec_persist_rundll32_mshta_scheduledtask` do lựa chọn T1059.001 thay vì T1053.005.
- Qwen3 4B đạt kết quả cao nhất ở T1003.001 trong nhóm SLM.

### 7.5. Phân tích báo nhầm trên phiên Lenovo và Defender

Trong 9 lần hỏi có hai ứng viên T1053.005 và T1070.001, các mô hình có xu hướng lựa chọn khác nhau:

| Mô hình | T1053.005 | T1070.001 | Mã khác |
|---|---:|---:|---:|
| Phi-4-mini | 0 | 9 | 0 |
| Qwen3 4B | 3 | 6 | 0 |
| Llama 3.2 3B | 7 | 1 | 1 |
| Gemma 3 4B | 3 | 5 | 1 |

Log cho thấy Lenovo thực sự tạo tác vụ Scheduled Task, đủ dấu vết cho T1053.005. Trong khi đó, Defender gọi `wevtutil` để thay đổi cấu hình kênh nhật ký nhưng không có bằng chứng bắt buộc của T1070.001.

Llama 3.2 3B lựa chọn T1053.005 nhiều nhất nhưng cũng có số báo nhầm cao nhất. Phi-4-mini lựa chọn T1070.001 trong cả 9 lần, khiến bước xác minh bằng chứng chặn kết luận sai.

Kết quả cho thấy số phiên chưa xác nhận không đồng nghĩa với việc SLM đã nhận diện được hoạt động bình thường. Prompt cũ chưa cung cấp lựa chọn phân loại bình thường độc lập.

### 7.6. Hạn chế của phép thử

- Không mô hình nào phát hiện nhiều hơn chế độ không SLM (7/29).
- Không có kết luận sai mã kỹ thuật ở cả bốn mô hình.
- Không có lỗi SLM trong 26 lần hỏi của mỗi mô hình.
- Bộ thử chưa có phiên log bình thường của máy Thiên tuần 3 được phát hiện ở bất kỳ chế độ nào (0/807).
- RAM trong lúc chạy inference trên máy Khôi chưa được ghi nhận.
- Kết quả này chưa đánh giá prompt mới D3.

### 7.7. Kết luận

Qwen3 4B đạt số phiên phát hiện đúng cao nhất trong nhóm SLM với 7/29 phiên, nhưng cũng có số báo nhầm cao hơn Phi-4-mini và Gemma 3 4B.

Phi-4-mini và Gemma 3 4B có tỷ lệ báo nhầm thấp nhất (0,24%), tuy nhiên số phiên chưa xác nhận cao.

Llama 3.2 3B có thời gian trung bình hỏi SLM thấp nhất (45 giây), nhưng số báo nhầm cao nhất.

Không có mô hình nào thể hiện ưu thế toàn diện. Kết quả cho thấy SLM chưa cải thiện rõ ràng khả năng phát hiện so với luật và bước xác minh bằng bằng chứng hiện có. Cần đánh giá thêm phương pháp hỏi mới D3 trước khi lựa chọn cấu hình chính thức.
