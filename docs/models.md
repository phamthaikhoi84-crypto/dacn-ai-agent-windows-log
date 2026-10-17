# Thử nghiệm mô hình ngôn ngữ nhỏ trên Ollama

- Máy chạy: Windows; cả bốn mô hình đều chạy bằng CPU, các mô hình đều sử dụng Ram trong quá trình suy luận , không sử dụng GPU để tăng tốc suy luận
- Phiên bản Ollama: 0.40.0(`ollama -v`)
- Ngày chạy: 16/10/2026
- Câu hỏi dùng chung cho cả 4 mô hình:

Explain what PowerShell Script Block Logging is in 3 sentences.

| Mô hình | Kích thước tải về | Eval rate (tokens/s) | RAM (ollama ps) | Processor | Thời gian tổng | Câu trả lời đúng/sai |
|---|---:|---:|---:|---|---:|---|
| qwen3:4b-instruct-2507-q4_K_M | 2.5 GB | 7.47 | 3.2 GB | 100% CPU | 15.904 giây | sai một phần: giải thích đúng chức năng chính nhưng hướng dẫn bật tính năng chưa đúng. |
| llama3.2:3b | 2.0 GB | 10.15 | 2.6 GB | 100% CPU | 12.502 giây | sai: có nhầm lẫn về cơ chế hoạt động và cách bật tính năng.|
| gemma3:4b | 3.4 GB | 8.08 | 2.9 GB | 100% CPU | 9.180 giây | Khá chính xác: nắm được chức năng cơ bản nhưng phần kỹ thuật còn thiếu hoặc chưa rõ. |
| phi4-mini | 2.0 GB | 7.54 | 3.1 GB | 100% CPU | 8.853 giây | Khá chính xác: hiểu mục đích bảo mật nhưng chưa giải thích rõ cơ chế ghi nội dung script. |


## Nhận xét
Cả 4 mô hình đều chạy thành công trên Ollama bằng CPU, với mức sử dụng CPU 100% và context 4096.
- Llama 3.2 3B: có tốc độ sinh token cao nhất, đạt 10.15 tokens/s.
- Phi-4-mini: có thời gian tổng thấp nhất, khoảng 8.85 giây.
- Gemma 3 4B: hoàn thành trong khoảng 9.18 giây.
- Qwen3 4B: có tốc độ sinh token thấp nhất, 7.47 tokens/s, và thời gian tổng cao nhất, khoảng 15.90 giây.
  
Về dung lượng tải về, Gemma 3 4B lớn nhất với 3.4 GB, còn Llama 3.2 3B nhỏ nhất với 2.0 GB. Các giá trị SIZE từ ollama ps cao hơn hoặc khác dung lượng tải về vì đây là số liệu bộ nhớ mô hình khi đang chạy, không phải dung lượng lưu trữ trên ổ đĩa.

Kết luận: Trong lần thử nghiệm này, Llama 3.2 3B có tốc độ sinh token cao nhất, còn Phi-4-mini hoàn thành nhanh nhất. 

Tuy nhiên, tốc độ nhanh không đồng nghĩa với câu trả lời chính xác hơn. Đánh giá độ chính xác hiện là sơ bộ; để kết luận chắc chắn cần đối chiếu nội dung đầu ra nguyên văn của từng mô hình.
...  
