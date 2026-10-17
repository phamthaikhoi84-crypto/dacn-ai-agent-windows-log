# Thử nghiệm mô hình ngôn ngữ nhỏ trên Ollama

- Máy thử nghiệm: Máy Dũng
- Hệ điều hành: Windows
- CPU: Intel(R) Core(TM) i5-8350U CPU @ 1.70GHz
- RAM hệ thống: 15.84 GB (xấp xỉ 16 GB)
- Phiên bản Ollama: 0.40.0 (ollama -v)
- Phương thức suy luận: CPU; không sử dụng GPU để tăng tốc suy luận.
- Ngày thử nghiệm: 16/10/2026
- Context: 4096

**- Câu hỏi dùng chung cho cả 4 mô hình:**

- Explain what PowerShell Script Block Logging is in 3 sentences.

| Mô hình | Kích thước tải về | Eval rate (tokens/s) | RAM (ollama ps) | Processor | Thời gian tổng | Câu trả lời đúng/sai |
|---|---:|---:|---:|---|---:|---|
| qwen3:4b-instruct-2507-q4_K_M | 2.5 GB | 7.47 | 3.2 GB | 100% CPU | 15.904 giây | sai một phần |
| llama3.2:3b | 2.0 GB | 10.15 | 2.6 GB | 100% CPU | 12.502 giây | sai|
| gemma3:4b | 3.4 GB | 8.08 | 2.9 GB | 100% CPU | 9.180 giây | khá chính xác |
| phi4-mini | 2.0 GB | 7.54 | 3.1 GB | 100% CPU | 8.853 giây | khá chính xác |


# Nhận xét

- Cả 4 mô hình đều chạy thành công trên Ollama bằng CPU. Trong quá trình suy luận, các mô hình sử dụng CPU để xử lý và không sử dụng GPU để tăng tốc.

- Llama 3.2 3B: Có tốc độ sinh token cao nhất trong bốn mô hình, đạt 10.15 tokens/s.

- Phi-4-mini: Có thời gian tổng thấp nhất trong lần thử nghiệm này, khoảng 8.85 giây.

- Gemma 3 4B: Có thời gian tổng khoảng 9.18 giây và tốc độ sinh token đạt 8.08 tokens/s.

- Qwen3 4B: Có tốc độ sinh token thấp nhất, đạt 7.47 tokens/s, đồng thời có thời gian tổng cao nhất, khoảng 15.90 giây.

- Về dung lượng tải về, Gemma 3 4B có dung lượng lớn nhất với 3.4 GB; Llama 3.2 3B và Phi-4-mini có dung lượng nhỏ nhất với 2.0 GB. Các giá trị RAM từ ollama ps thể hiện mức bộ nhớ sử dụng khi mô hình đang chạy, không phải dung lượng lưu trữ của mô hình trên ổ đĩa.

- Kết luận: Trong lần thử nghiệm này, Llama 3.2 3B có tốc độ sinh token cao nhất. Phi-4-mini có thời gian tổng thấp nhất, nhưng thời gian hoàn thành còn phụ 
thuộc vào số token được sinh ra và các yếu tố xử lý khác. Vì vậy, không thể chỉ dựa vào thời gian tổng để kết luận mô hình nào có tốc độ sinh token cao nhất.

- Đánh giá độ chính xác trong bảng hiện chỉ mang tính sơ bộ, dựa trên câu hỏi kiến thức chung về PowerShell Script Block Logging. Câu hỏi này phù hợp để quan sát tốc độ và mức sử dụng tài nguyên, nhưng chưa đủ để đánh giá khả năng phân tích log của một AI Agent. Việc đánh giá khả năng phân tích log cần được thực hiện ở giai đoạn sau bằng các câu hỏi và dữ liệu log thực tế, theo kế hoạch của đồ án.

## Nhận xét chi tiết câu trả lời

| Mô hình | Đánh giá |
|---|---|
| qwen3:4b-instruct-2507-q4_K_M | Sai một phần: giải thích đúng chức năng chính nhưng hướng dẫn bật tính năng chưa đúng |
| llama3.2:3b | Sai: nhầm lẫn về cơ chế hoạt động và cách bật tính năng |
| gemma3:4b | Khá chính xác: nắm được chức năng cơ bản nhưng phần kỹ thuật còn thiếu |
| phi4-mini | Khá chính xác: hiểu mục đích bảo mật nhưng chưa giải thích rõ cơ chế ghi nội dung script |
