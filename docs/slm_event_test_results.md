# Kết quả thử nghiệm 4 SLM với sự kiện Sysmon (Zalo.exe)

- **Ngày chạy:** 24/10/2026
- **Môi trường:** Ollama chạy cục bộ trên CPU, Windows
- **Script:** `run_slm_test_clean.ps1` (prompt đưa qua stdin, UTF-8, có warm-up)
- **Dữ liệu đầu ra gốc:** `output/slm_event_test_clean.txt`, `output/slm_event_test_clean_part2.txt`
- **Nhật ký thời gian:** `output/slm_event_test_runlog.txt`, `output/slm_event_test_runlog_part2.txt`

## 1. Dữ liệu đầu vào

Cùng một prompt tiếng Việt, cùng 3 sự kiện của tiến trình `Zalo.exe` (PID 13424):

| # | Event ID | Nội dung chính |
|---|---|---|
| 1 | 22 | DNS query `tt-sticker-wpa.chat.zalo.me`, `QueryStatus=0` |
| 2 | 22 | DNS query `res-zalo.zadn.vn`, `QueryStatus=0` |
| 3 | 3 | Kết nối TCP, `Initiated=true`, cổng đích 443, IPv6 đích `2001:df0:13:1:0:0:0:1` |

Prompt yêu cầu: giải thích loại sự kiện và các trường quan trọng, đánh giá mức độ đáng ngờ, tách rõ dữ kiện đã cho và suy luận, nêu bằng chứng bổ sung cần thu thập, **không kết luận mã độc** chỉ dựa vào 3 sự kiện.

## 2. Kết quả chấm điểm

Ký hiệu: **Đạt** / **Một phần** / **Sai** / **Không có** (mô hình không đề cập).

| Tiêu chí | qwen3:4b | llama3.2:3b | gemma3:4b | phi4-mini |
|---|---|---|---|---|
| Phân tích đúng yêu cầu 3 sự kiện | Đạt | **Sai** (lạc đề, hướng dẫn sửa lỗi Zalo) | Đạt | Một phần (có cấu trúc, nội dung sai) |
| Event ID 22 = DNS query | Một phần (gọi "Process Creation with Query Name" nhưng mô tả là DNS lookup) | **Sai** | **Sai** (gọi "Network Connection") | **Sai** (gọi "Process Creation") |
| Event ID 3 = kết nối mạng | Đạt | Không có | Đạt | Đạt |
| `QueryStatus=0` = thành công | Đạt | Không có | Một phần (nói "kết nối thành công") | Một phần (hiểu QueryName là tệp tin) |
| Tách dữ kiện và suy luận | Một phần (có bảng tổng hợp) | Không có | **Đạt** (mỗi sự kiện có mục riêng) | Không rõ |
| Đánh giá mức độ đáng ngờ hợp lý | Một phần | Không có | Một phần | Một phần (kết luận đúng, lý do sai) |
| Không kết luận là mã độc | Đạt | Không có | Đạt | Đạt |
| Bằng chứng bổ sung | Đạt (cụ thể) | Không có | Đạt | Một phần (chung chung) |

## 3. Thời gian chạy

| Mô hình | Thời gian (giây) | Quy đổi | Ghi chú |
|---|---:|---|---|
| qwen3:4b-instruct-2507-q4_K_M | 655,80 | 10 phút 55,8 giây | Không đáng tin để so tốc độ (cửa sổ chạy bị tạm dừng do bôi đen chữ) |
| llama3.2:3b | 101,49 | 1 phút 41,49 giây | Nhanh nhưng trả lời lạc đề |
| gemma3:4b | 315,18 | 5 phút 15,18 giây | |
| phi4-mini:latest | 174,86 | 2 phút 54,86 giây | |

Thời gian chạy phụ thuộc tải của máy. Cùng model, lượt chạy trước của qwen3 mất 207,99 giây, lượt này 655,8 giây. Không dùng một lần chạy để kết luận model nào nhanh hơn.

## 4. Các lỗi cụ thể

| Mô hình | Lỗi | Sự thật đối chiếu |
|---|---|---|
| qwen3:4b | Gọi `2001:df0:13:1:0:0:0:1` là "IPv6 private" | Dải `2001::/16` thuộc `2000::/3` (global unicast), không phải dải nội bộ `fc00::/7` |
| qwen3:4b | Nghi `res-zalo.zadn.vn` "không thuộc miền chính thức của Zalo" khi chưa có căn cứ | Cần xác minh bằng WHOIS / DNS, không suy luận từ tên |
| qwen3:4b | Có một chữ Hán lọt vào ProcessGuid | Lỗi sinh văn bản, ProcessGuid gốc `DF2C5097-098C-6AD2-D305-000000002E01` |
| gemma3:4b | Gọi Event ID 22 là "Network Connection" | Event ID 22 là DNS Query |
| gemma3:4b | Khẳng định IPv6 đích là "gán động (DHCP)" | Không có căn cứ trong 3 sự kiện |
| gemma3:4b | Gọi `QueryName` là "URL" | `QueryName` là tên miền được truy vấn DNS |
| phi4-mini | Gọi Event ID 22 là "Process Creation" | Process Create là Event ID 1 |
| phi4-mini | Hiểu `QueryName` là "tệp tin hoặc tệp tin thực thi" | `QueryName` là tên miền |
| llama3.2:3b | Không phân tích sự kiện, đưa hướng dẫn sửa lỗi Zalo chung chung | Không đúng yêu cầu của prompt |

## 5. Chuẩn đối chiếu kỹ thuật

| Mục | Giá trị đúng |
|---|---|
| Sysmon Event ID 22 | DNS Query |
| Sysmon Event ID 3 | Network connection |
| Sysmon Event ID 1 | Process Create |
| `QueryStatus=0` | Truy vấn DNS thành công |
| Cổng 443 | Thường dùng cho HTTPS, nhưng chỉ nhìn cổng không đủ để xác nhận giao thức |
| 3 sự kiện trên | Không đủ để kết luận `Zalo.exe` là mã độc |

## 6. Nhận xét

1. Không mô hình nào trả lời hoàn toàn đúng.
2. Qwen3 và Gemma3 cho kết quả dùng được nhất: kết luận thận trọng, nêu bằng chứng bổ sung. Gemma3 bám đúng yêu cầu "tách dữ kiện và suy luận" nhất.
3. Phi4-mini hiểu sai bản chất Event ID 22 và `QueryName`. Llama3.2 lạc đề.
4. **Kết quả không ổn định giữa các lượt chạy:** Gemma3 lượt trước nhận diện đúng Event ID 22, lượt này sai. Llama3.2 lượt trước nhầm "Registry Query", lượt này lạc đề. Chưa thể kết luận mô hình nào tốt nhất từ một câu hỏi và một lượt chạy.

## 7. Hạn chế

- Chỉ có 1 prompt, 3 sự kiện, 1 lượt chạy cho mỗi mô hình.
- Dùng nhiệt độ mặc định của Ollama nên đầu ra có tính ngẫu nhiên.
- File đầu ra gốc có chữ lặp ở cuối dòng do `ollama run` tự xuống dòng (không phải lỗi mô hình), có thể tránh bằng tham số `--nowordwrap`.
- Việc chấm điểm thực hiện thủ công, chưa có bộ đáp án chuẩn tự động.

## 8. Việc tiếp theo

- [ ] Xây bộ câu hỏi có đáp án chuẩn (nhận diện Event ID, diễn giải trường, mức độ thận trọng, bằng chứng bổ sung).
- [ ] Chạy lặp mỗi mô hình ít nhất 3 lần, cố định nhiệt độ (ví dụ qua API với `temperature: 0`).
- [ ] Thêm `--nowordwrap` vào script để đầu ra sạch.
- [ ] Chọn mô hình đưa vào AI agent phân tích log dựa trên kết quả chấm lặp.
