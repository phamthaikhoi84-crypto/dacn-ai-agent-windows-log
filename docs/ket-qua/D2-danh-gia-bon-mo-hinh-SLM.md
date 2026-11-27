# D2 – Đánh giá và so sánh bốn mô hình SLM trên Ollama

## 1. Mục tiêu

Đánh giá bốn mô hình ngôn ngữ nhỏ (SLM) có thể chạy cục bộ bằng Ollama, so sánh hiệu năng suy luận và chất lượng câu trả lời, sau đó đánh giá khả năng hỗ trợ AI Agent Windows Log trên bộ thử có dữ liệu tấn công và bình thường.

Bốn mô hình được đánh giá:
- Phi-4-mini
- Qwen3 4B
- Llama 3.2 3B
- Gemma3 4B

---

## 2. Thử nghiệm kiến thức chung trên máy Dũng

### 2.1. Môi trường

| Thành phần | Thông số |
|---|---|
| Máy thử nghiệm | Máy Dũng |
| Hệ điều hành | Windows |
| CPU | Intel Core i5-8350U @ 1.70GHz |
| RAM hệ thống | 15,84 GB |
| Ollama | 0.40.0 tại thời điểm thử nghiệm |
| Phương thức suy luận | CPU, không dùng GPU |
| Context | 4096 |
| Ngày thử nghiệm | 16/10/2026 |

### 2.2. Câu hỏi chung

Cả bốn mô hình nhận cùng câu hỏi:

> Explain what PowerShell Script Block Logging is in 3 sentences.

### 2.3. Kết quả

| Mô hình | Dung lượng tải về | Eval rate (tokens/s) | RAM theo `ollama ps` | CPU | Thời gian tổng | Đánh giá câu trả lời |
|---|---:|---:|---:|---:|---:|---|
| Qwen3 4B | 2,5 GB | 7,47 | 3,2 GB | 100% | 15,904 giây | Sai một phần |
| Llama 3.2 3B | 2,0 GB | 10,15 | 2,6 GB | 100% | 12,502 giây | Sai |
| Gemma3 4B | 3,4 GB | 8,08 | 2,9 GB | 100% | 9,180 giây | Khá chính xác |
| Phi-4-mini | 2,0 GB | 7,54 | 3,1 GB | 100% | 8,853 giây | Khá chính xác |

### 2.4. Đánh giá chất lượng câu trả lời

- **Qwen3 4B:** Giải thích được chức năng chính nhưng hướng dẫn bật Script Block Logging chưa chính xác.
- **Llama 3.2 3B:** Nhầm lẫn giữa ghi nội dung Script Block và ghi kết quả đầu ra của script; hướng dẫn bật tính năng không chính xác.
- **Gemma3 4B:** Nắm được chức năng cơ bản nhưng còn nhầm lẫn về nội dung được ghi lại và chưa giải thích rõ cơ chế.
- **Phi-4-mini:** Hiểu mục đích giám sát và kiểm toán bảo mật nhưng chưa mô tả đầy đủ cơ chế ghi nội dung Script Block.

### 2.5. Nhận xét

- Llama 3.2 3B có tốc độ sinh token cao nhất: 10,15 tokens/s.
- Phi-4-mini có thời gian tổng thấp nhất: 8,853 giây.
- Gemma3 4B có câu trả lời tương đối chính xác và thời gian tổng 9,180 giây.
- Qwen3 4B có thời gian tổng cao nhất: 15,904 giây.
- Đây là phép thử kiến thức chung, không đủ để kết luận khả năng phân tích log Windows/Sysmon.

**Lưu ý:** Dung lượng tải về là dung lượng lưu trữ mô hình. RAM từ `ollama ps` là mức bộ nhớ Ollama báo khi mô hình đang được nạp. Eval rate là tốc độ sinh/đánh giá token, không đồng nghĩa với thời gian tổng hoàn thành.

---

## 3. Đánh giá bốn SLM trên bộ thử tuần 6 (K3)

### 3.1. Điều kiện thử nghiệm

| Thành phần | Thông số |
|---|---|
| Máy thử nghiệm | Máy Khôi |
| Phương thức suy luận | Ollama, CPU |
| Mức sử dụng CPU | 100% trong quá trình suy luận |
| Bộ thử | `data/bo-thu.csv` |
| Dữ liệu | 29 phiên tấn công và 3.290 phiên bình thường |
| Ngưỡng | 0,5 |
| Số ứng viên | 3 |
| Prompt | Prompt cũ, chưa áp dụng D3 |
| Số lần hỏi SLM | 26 lần/mô hình |
| Thời gian | Đêm 20–21/11/2026 |
| Luật Startup | Tắt, trừ lần đo được ghi rõ |

### 3.2. Bảng kết quả

| Mô hình | Phát hiện đúng | Báo nhầm | Chưa xác nhận do SLM trên log bình thường | SLM lỗi | Thời gian TB/lần hỏi | Tổng thời gian |
|---|---:|---:|---:|---:|---:|---:|
| Phi-4-mini | 6/29 (21%) | 8/3.290 (0,24%) | 11 | 0 | 52 giây | 38 phút |
| Qwen3 4B | 7/29 (24%) | 13/3.290 (0,40%) | 6 | 0 | 74 giây | 50 phút |
| Llama 3.2 3B | 6/29 (21%) | 15/3.290 (0,46%) | 4 | 0 | 45 giây | 30 phút |
| Gemma3 4B | 6/29 (21%) | 8/3.290 (0,24%) | 11 | 0 | 58 giây | 34 phút |

### 3.3. Nhận xét từng mô hình

**Phi-4-mini**
- Phát hiện đúng 6/29 phiên tấn công (21%).
- Có 8 phiên báo nhầm trên 3.290 phiên bình thường (0,24%).
- Có 11 phiên chưa xác nhận do kết quả SLM không đủ điều kiện kết luận.
- Thời gian trung bình 52 giây/lần hỏi; tổng thời gian 38 phút.
- Kết quả lặp lại được với lần đo tuần 5, nhưng chưa cải thiện khả năng phát hiện so với chế độ không SLM.

**Qwen3 4B**
- Phát hiện đúng 7/29 phiên (24%), cao nhất trong bốn SLM.
- Có 13 phiên báo nhầm (0,40%) và 6 phiên chưa xác nhận.
- Thời gian trung bình 74 giây/lần hỏi; tổng thời gian 50 phút.
- Có số phiên phát hiện đúng cao nhất trong nhóm SLM nhưng thời gian xử lý dài nhất.

**Llama 3.2 3B**
- Phát hiện đúng 6/29 phiên (21%).
- Có 15 phiên báo nhầm (0,46%), cao nhất trong nhóm.
- Có 4 phiên chưa xác nhận, thấp nhất trong nhóm.
- Thời gian trung bình 45 giây/lần hỏi; tổng thời gian 30 phút.
- Xử lý nhanh hơn các mô hình còn lại trong phép thử này nhưng có số báo nhầm cao nhất.

**Gemma3 4B**
- Phát hiện đúng 6/29 phiên (21%).
- Có 8 phiên báo nhầm (0,24%), cùng mức với Phi-4-mini.
- Có 11 phiên chưa xác nhận.
- Thời gian trung bình 58 giây/lần hỏi; tổng thời gian 34 phút.
- Có mức báo nhầm thấp nhưng chưa cải thiện số phiên phát hiện đúng.

### 3.4. Phân tích theo kỹ thuật

| Kỹ thuật | Không SLM | Phi-4-mini | Qwen3 4B | Llama 3.2 3B | Gemma3 4B |
|---|---:|---:|---:|---:|---:|
| T1003.001 | 5/6 | 4/6 | 5/6 | 5/6 | 5/6 |
| T1053.005 | 2/4 | 2/4 | 2/4 | 1/4 | 1/4 |

- Phi-4-mini bỏ sót phiên `babyshark_mimikatz_powershell` do chọn T1059.001 thay vì T1003.001.
- Llama 3.2 3B và Gemma3 4B bỏ sót phiên `exec_persist_rundll32_mshta_scheduledtask` do chọn T1059.001 thay vì T1053.005.
- Qwen3 4B, Llama 3.2 3B và Gemma3 4B đạt 5/6 ở T1003.001, bằng chế độ không SLM; Phi-4-mini đạt 4/6.

### 3.5. Phân tích lựa chọn trên log Lenovo và Defender

Trong 9 lần hỏi có hai ứng viên T1053.005 và T1070.001:

| Mô hình | T1053.005 | T1070.001 | Mã khác |
|---|---:|---:|---:|
| Phi-4-mini | 0 | 9 | 0 |
| Qwen3 4B | 3 | 6 | 0 |
| Llama 3.2 3B | 7 | 1 | 1 |
| Gemma3 4B | 3 | 5 | 1 |

Log cho thấy Lenovo thực sự tạo Scheduled Task, có dấu vết cho T1053.005. Defender gọi `wevtutil` để thay đổi cấu hình kênh nhật ký nhưng không có bằng chứng bắt buộc của T1070.001.

Llama 3.2 3B chọn T1053.005 nhiều nhất nhưng cũng có số báo nhầm cao nhất. Phi-4-mini chọn T1070.001 trong cả 9 lần; bước xác minh bằng chứng đã ngăn việc kết luận sai.

Số phiên chưa xác nhận không đồng nghĩa với việc SLM đã nhận diện được hoạt động bình thường. Prompt cũ chưa cung cấp lựa chọn phân loại bình thường độc lập.

### 3.6. Hạn chế

- Không mô hình nào phát hiện nhiều hơn chế độ không SLM (7/29).
- Không có kết luận sai mã kỹ thuật ở cả bốn mô hình.
- Không ghi nhận lỗi SLM trong 26 lần hỏi của mỗi mô hình.
- Máy Thiên tuần 3 có 0/807 báo nhầm ở mọi chế độ; khác biệt về báo nhầm đến từ máy Thiên tuần 4 và máy Khôi.
- RAM trong lúc inference trên máy Khôi chưa được ghi nhận ở phép thử tuần 6.
- Kết quả này sử dụng prompt cũ, chưa đánh giá prompt mới D3.

---

## 4. Ghi nhận dung lượng mô hình trên máy Dũng (28/11/2026)

Các giá trị dưới đây được ghi nhận bằng `ollama ps` khi nạp từng mô hình trên máy Dũng:

| Mô hình | Dung lượng hiển thị khi chạy |
|---|---:|
| Phi-4-mini | 3,1 GB |
| Qwen3 4B | 3,2 GB |
| Gemma3 4B | 2,9 GB |
| Llama 3.2 3B | 2,6 GB |

Điều kiện ghi nhận: CPU, context 4096; runner `llamacpp`; CPU đạt 100% trong quá trình thử.

**Giới hạn đo lường:** Các giá trị từ `ollama ps` là dung lượng bộ nhớ Ollama hiển thị khi mô hình đang chạy. Không được diễn giải chúng thành mức RAM đỉnh của toàn hệ thống hoặc tổng RAM tiêu thụ của Windows và mọi tiến trình. Phép đo này không thay thế phép đo peak RAM bằng công cụ giám sát hệ thống.

---

## 5. Kết luận D2

- Trong phép thử kiến thức chung trên máy Dũng, Phi-4-mini có thời gian tổng thấp nhất; Llama 3.2 3B có tốc độ sinh token cao nhất.
- Trên bộ thử tuần 6, Qwen3 4B có số phiên phát hiện đúng cao nhất trong nhóm SLM (7/29), nhưng thời gian trung bình dài nhất và có 13 báo nhầm.
- Phi-4-mini và Gemma3 4B có số báo nhầm thấp nhất (8 phiên, 0,24%), nhưng đều có 11 phiên chưa xác nhận.
- Llama 3.2 3B có thời gian trung bình thấp nhất trong bộ thử tuần 6 (45 giây), nhưng có 15 báo nhầm.
- Không mô hình nào thể hiện ưu thế toàn diện; không mô hình nào cải thiện số phiên phát hiện đúng so với chế độ không SLM.

**Định hướng:** Tiếp tục dùng Phi-4-mini làm cấu hình ưu tiên cho quá trình phát triển và đánh giá prompt, nhưng chưa kết luận đây là mô hình tối ưu. Quyết định chính thức cần dựa trên độ chính xác bằng chứng, khả năng phân biệt bình thường/bất thường, tuân thủ JSON, độ ổn định và hiệu năng.

## 6. Trạng thái hạng mục

D2 đã có kết quả so sánh bốn mô hình trên bộ thử và báo cáo thử nghiệm Ollama. Tuy nhiên, phép thử tuần 6 chưa có số đo RAM inference trên máy Khôi; số liệu `ollama ps` trên máy Dũng là phép ghi nhận riêng và không thể thay thế phép đo đó.
