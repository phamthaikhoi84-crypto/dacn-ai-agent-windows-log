# So sánh khả năng giám sát: Windows mặc định vs Sysmon

## 1. Mục tiêu

So sánh khả năng ghi nhận hoạt động hệ thống giữa log Windows mặc định và Sysmon. Qua đó, đánh giá vai trò của Sysmon trong việc thu thập dữ liệu phục vụ giám sát, phát hiện và phân tích hành vi đáng ngờ trên Windows.

## 2. Bảng so sánh 8 kỹ thuật

| Kỹ thuật | Windows mặc định | Sysmon bổ sung | Bằng chứng và trạng thái trên máy Dũng |
|---|---|---|---|
| Process creation | Security Event ID 4688 có thể ghi nhận việc tạo tiến trình nếu bật chính sách audit phù hợp. | Event ID 1 ghi nhận thông tin tiến trình, bao gồm đường dẫn và dòng lệnh khi có dữ liệu tương ứng. | DuckDB có 2.403 bản ghi Event ID 1. Chưa đối chiếu với Security Event ID 4688. |
| Process access / LSASS | Log mặc định có thể không cung cấp đầy đủ chi tiết về hoạt động truy cập tiến trình nếu chưa cấu hình audit phù hợp. | Event ID 10 ghi nhận hoạt động truy cập tiến trình theo cấu hình Sysmon. | Chưa có số liệu Event ID 10 trong bảng thống kê DuckDB hiện tại. Cần kiểm tra log gốc để xác nhận. |
| Network connection | Windows Firewall và các nguồn audit có thể ghi nhận một phần hoạt động mạng tùy cấu hình. | Event ID 3 ghi nhận kết nối mạng khi được bật trong cấu hình Sysmon. | DuckDB có 34.647 bản ghi Event ID 3. |
| PowerShell execution | PowerShell có thể ghi Script Block Logging, Module Logging hoặc các sự kiện liên quan nếu được bật. Event ID 4104 thường dùng để ghi nội dung script block. | Event ID 1 cung cấp thông tin tiến trình PowerShell; Sysmon không thay thế log ghi nội dung script của PowerShell. | DuckDB có 2.403 bản ghi Event ID 1. Máy từng ghi nhận PowerShell Event ID 4104; cần kiểm tra thời điểm và nội dung trước khi sử dụng làm bằng chứng. |
| File creation | Windows có thể ghi nhận thao tác tệp khi bật chính sách audit phù hợp và cấu hình SACL tương ứng. | Event ID 11 ghi nhận việc tạo tệp theo cấu hình Sysmon. | Chưa có số liệu Event ID 11 trong bảng thống kê DuckDB hiện tại. |
| Registry modification | Windows có thể ghi nhận thay đổi Registry khi cấu hình audit phù hợp. | Event ID 12–14 ghi nhận hoạt động tạo/xóa khóa, sửa giá trị hoặc đổi tên khóa Registry. | Chưa có số liệu Event ID 12–14 trong bảng thống kê DuckDB hiện tại. |
| DLL/image loading | Log Windows mặc định có thể không cung cấp mức chi tiết tương đương nếu không bật cơ chế giám sát bổ sung. | Event ID 7 ghi nhận hoạt động nạp image, bao gồm DLL, khi được bật. | Chưa có số liệu Event ID 7 trong bảng thống kê DuckDB hiện tại. |
| DNS query | Windows có thể ghi nhận truy vấn DNS qua DNS Client hoặc nguồn log liên quan tùy cấu hình. | Event ID 22 ghi nhận truy vấn DNS theo cấu hình Sysmon. | DuckDB có 2.766 bản ghi Event ID 22. |

**Lưu ý:** Số liệu được lấy từ `output/benign_events.duckdb` tại thời điểm kiểm tra. Chưa thấy một Event ID trong bảng thống kê không đồng nghĩa sự kiện đó chắc chắn không tồn tại trong file EVTX gốc.

## 3. Kết quả thống kê log Sysmon

**File dữ liệu:** `benign_sysmon_dung_tuan1.evtx`  
**Script chuyển đổi:** `src/evtx_to_duckdb.py`  
**Cơ sở dữ liệu:** `output/benign_events.duckdb`

Tại thời điểm kiểm tra, cơ sở dữ liệu có 42.099 bản ghi:

| Event ID | Ý nghĩa | Số bản ghi | Tỷ lệ |
|---:|---|---:|---:|
| 3 | Network connection | 34.647 | 82,30% |
| 22 | DNS query | 2.766 | 6,57% |
| 1 | Process creation | 2.403 | 5,71% |
| 5 | Process terminated | 2.279 | 5,41% |
| 4 | Sysmon service state changed | 2 | 0,005% |
| 16 | Sysmon configuration changed | 2 | 0,005% |
| **Tổng** | | **42.099** | **100%** |

Các tỷ lệ được làm tròn; tổng tỷ lệ hiển thị có thể chênh lệch nhỏ do làm tròn.

Event ID 3 chiếm phần lớn dữ liệu đã nạp, tiếp theo là Event ID 22 và Event ID 1. Điều này cho thấy tập dữ liệu hiện tại có nhiều thông tin về hoạt động mạng, truy vấn DNS và vòng đời tiến trình.

Cần xác nhận quá trình nhập dữ liệu đã hoàn tất và không bỏ sót bản ghi trước khi xem các con số trên là thống kê đầy đủ của toàn bộ file EVTX gốc.

## 4. Chuỗi 3 sự kiện Sysmon của Zalo.exe dùng để thử nghiệm

Dữ liệu được sử dụng trong prompt ngày 24/10/2026 gồm ba sự kiện liên quan đến tiến trình `Zalo.exe`, PID 13424.

| STT | Event ID | Thời điểm | Mô tả sự kiện | Chi tiết chính |
|---|---:|---|---|---|
| 1 | 22 | Chưa có dữ liệu thời điểm chính xác | Truy vấn DNS `tt-sticker-wpa.chat.zalo.me` | PID 13424; ProcessGuid `DF2C5097-098C-6AD2-D305-000000002E01`; `QueryStatus=0` |
| 2 | 22 | Chưa có dữ liệu thời điểm chính xác | Truy vấn DNS `res-zalo.zadn.vn` | Cùng tiến trình; `QueryStatus=0` |
| 3 | 3 | Chưa có dữ liệu thời điểm chính xác | Kết nối mạng TCP | Cùng tiến trình; `Initiated=true`; cổng đích 443; IPv6 đích `2001:df0:13:1:0:0:0:1` |

### Mối liên hệ giữa ba sự kiện

Cả ba sự kiện được đưa vào prompt với tư cách hoạt động của cùng tiến trình `Zalo.exe`, PID 13424. Hai sự kiện đầu ghi nhận truy vấn DNS, trong khi sự kiện thứ ba ghi nhận kết nối mạng TCP.

Chuỗi này có thể được sử dụng để khảo sát hoạt động DNS và kết nối mạng của ứng dụng. Tuy nhiên, chưa có thời điểm chính xác của từng sự kiện để xác định khoảng cách thời gian hoặc chứng minh thứ tự xảy ra từ dữ liệu đang trình bày.

### Nhận định chuẩn dùng để đối chiếu

- Event ID 22 là DNS Query, không phải Process Creation hay Network Connection.
- `QueryName` là tên được truy vấn qua DNS; `QueryStatus=0` thường biểu thị truy vấn thành công.
- Event ID 3 là Network Connection. Cổng 443 thường được sử dụng cho HTTPS nhưng chỉ riêng số cổng không đủ xác nhận giao thức ứng dụng.
- Địa chỉ IPv6 `2001:df0:13:1:0:0:0:1` thuộc không gian Global Unicast `2000::/3`, không phải dải địa chỉ ULA `fc00::/7`.
- Ba sự kiện chưa đủ để kết luận `Zalo.exe` là mã độc. Cần thu thập thêm đường dẫn và chữ ký số của tệp, thông tin DNS/IP, các sự kiện tiến trình liên quan và ngữ cảnh mạng.

## 5. Thử nghiệm 4 model SLM trên Ollama

Thực nghiệm được tiến hành trên Windows bằng Ollama chạy cục bộ trên CPU. Các mô hình sử dụng cùng một prompt tiếng Việt và cùng ba sự kiện Sysmon đã trình bày tại mục 4.

**Ngày chạy:** 24/10/2026  
**Script:** `run_slm_test_clean.ps1`  
**File đầu ra:** `output/slm_event_test_clean.txt`, `output/slm_event_test_clean_part2.txt`  
**Nhật ký thời gian:** `output/slm_event_test_runlog.txt`, `output/slm_event_test_runlog_part2.txt`

Các mô hình được đánh giá:

- `qwen3:4b-instruct-2507-q4_K_M`
- `llama3.2:3b`
- `gemma3:4b`
- `phi4-mini:latest`

### 5.1. Bảng so sánh kết quả

| Tiêu chí | Qwen3 4B | Llama 3.2 3B | Gemma 3 4B | Phi-4-mini |
|---|---|---|---|---|
| Thời gian phản hồi | 655,80 giây | 101,49 giây | 315,18 giây | 174,86 giây |
| Trả lời đúng bằng tiếng Việt và đúng yêu cầu | Một phần: có phân tích nhưng có lỗi kỹ thuật | Sai: trả lời lạc đề, hướng dẫn sửa lỗi Zalo | Một phần: trình bày rõ nhưng nhận diện sai Event ID 22 | Một phần: có cấu trúc nhưng hiểu sai Event ID 22 |
| Nhận diện đúng loại sự kiện | Một phần: mô tả DNS nhưng gọi tên Event ID 22 chưa chính xác | Sai | Sai với Event ID 22 | Sai với Event ID 22 |
| Đánh giá mức độ đáng ngờ | Một phần: có nhận định nhưng một số suy luận thiếu căn cứ | Không có đánh giá phù hợp | Một phần: thận trọng nhưng có nhận định thiếu căn cứ | Một phần: kết luận tương đối thận trọng nhưng lý do sai |
| Phân biệt dữ kiện và suy luận | Một phần | Không có | Đạt | Không rõ |
| Bằng chứng bổ sung cần thu thập | Đạt | Không có | Đạt | Một phần |
| Tránh kết luận mã độc khi chưa đủ bằng chứng | Đạt | Không có kết luận phù hợp để đánh giá | Đạt | Đạt |
| Đánh giá chung | Có thể tham khảo, cần kiểm tra lỗi kỹ thuật | Không đáp ứng prompt trong lượt chạy này | Trình bày tốt nhưng có lỗi kỹ thuật quan trọng | Cần cải thiện độ chính xác về Sysmon |

*Bảng đánh giá chất lượng được chấm thủ công theo đầu ra đã ghi nhận. Các mức đánh giá không phải điểm số trung bình qua nhiều lượt chạy.*

### 5.2. Các lỗi kỹ thuật cụ thể

| Mô hình | Lỗi quan sát được | Giá trị đối chiếu |
|---|---|---|
| Qwen3 4B | Gọi địa chỉ IPv6 đích là địa chỉ riêng tư | Địa chỉ thuộc không gian Global Unicast `2000::/3` |
| Qwen3 4B | Nghi ngờ `res-zalo.zadn.vn` không thuộc miền chính thức của Zalo mà chưa có căn cứ | Cần xác minh bằng nguồn DNS, thông tin đăng ký tên miền và nguồn đáng tin cậy |
| Qwen3 4B | Có ký tự bất thường trong ProcessGuid | ProcessGuid gốc là `DF2C5097-098C-6AD2-D305-000000002E01` |
| Llama 3.2 3B | Không phân tích các sự kiện, chuyển sang hướng dẫn sửa lỗi Zalo | Không đáp ứng yêu cầu prompt |
| Gemma 3 4B | Gọi Event ID 22 là Network Connection | Event ID 22 là DNS Query |
| Gemma 3 4B | Khẳng định IPv6 đích được cấp phát động bằng DHCP | Dữ liệu không đủ căn cứ xác định phương thức cấp phát |
| Gemma 3 4B | Gọi `QueryName` là URL | `QueryName` là tên được truy vấn DNS |
| Phi-4-mini | Gọi Event ID 22 là Process Creation | Process Create là Event ID 1 |
| Phi-4-mini | Hiểu `QueryName` là tên tệp hoặc tệp thực thi | `QueryName` là tên được truy vấn DNS |

### 5.3. Thời gian thực thi

| Mô hình | Thời gian (giây) | Quy đổi |
|---|---:|---|
| Qwen3 4B | 655,80 | 10 phút 55,80 giây |
| Llama 3.2 3B | 101,49 | 1 phút 41,49 giây |
| Gemma 3 4B | 315,18 | 5 phút 15,18 giây |
| Phi-4-mini | 174,86 | 2 phút 54,86 giây |
| **Tổng** | **1.247,33** | **20 phút 47,33 giây** |

Thời gian Qwen3 4B có thể bị ảnh hưởng bởi việc cửa sổ chạy bị tạm dừng trong lúc bôi đen văn bản. Ở một lượt trước, Qwen3 4B mất khoảng 207,99 giây, trong khi lượt này mất 655,80 giây.

Do đó, chưa thể kết luận mô hình nào nhanh nhất trong điều kiện sử dụng chung. Cần đo lại trong điều kiện được kiểm soát, áp dụng cùng quy trình warm-up và tách thời gian suy luận khỏi các khoảng tạm dừng hoặc thao tác bên ngoài.

### 5.4. Nhận xét

**Mô hình có kết quả đáng tham khảo nhất:** Qwen3 4B và Gemma 3 4B. Qwen3 4B có đề xuất bằng chứng bổ sung; Gemma 3 4B trình bày rõ ràng và phân biệt dữ kiện với suy luận tốt hơn trong lượt này. Tuy nhiên, cả hai đều có lỗi kỹ thuật cần được kiểm tra trước khi sử dụng kết quả.

**Mô hình còn hạn chế:** Phi-4-mini nhận diện sai bản chất Event ID 22 và `QueryName`. Llama 3.2 3B trả lời lạc đề trong lượt chạy được đánh giá.

**Hạn chế của thử nghiệm:** Chỉ sử dụng một prompt và ba sự kiện; số lượt chạy được đánh giá còn ít; nhiệt độ và điều kiện đo chưa được chuẩn hóa đầy đủ; kết quả được chấm thủ công. Các lượt trước còn cho thấy câu trả lời của cùng mô hình có thể thay đổi.

### 5.5. Hướng phát triển tiếp theo

1. Xây dựng bộ câu hỏi gồm nhiều loại sự kiện Sysmon và có đáp án chuẩn.
2. Bổ sung chuỗi hoạt động bình thường và chuỗi đáng ngờ để kiểm tra khả năng phân biệt.
3. Chạy lặp mỗi mô hình ít nhất ba lần, cố định các tham số như `temperature=0` qua Ollama API.
4. Chuẩn hóa cách đo thời gian, quy trình warm-up và cách lưu đầu ra.
5. Xây dựng bộ tiêu chí chấm điểm có thể lặp lại và kiểm tra thủ công các trường hợp khó.
6. Lựa chọn mô hình cho AI agent dựa trên độ chính xác, mức độ thận trọng, độ ổn định và thời gian phản hồi, thay vì chỉ dựa trên một lượt chạy.

## 6. Vì sao cần Sysmon?

Sysmon bổ sung dữ liệu giám sát có cấu trúc cho Windows, giúp người phân tích có thêm thông tin về tiến trình, dòng lệnh, kết nối mạng, truy vấn DNS, truy cập tiến trình và các hoạt động hệ thống khác khi cấu hình tương ứng được bật.

Windows mặc định vẫn có thể ghi lại nhiều hoạt động qua Security, System, PowerShell và các nguồn log khác. Tuy nhiên, mức độ chi tiết phụ thuộc vào chính sách audit và cấu hình từng nguồn. Sysmon cung cấp thêm telemetry để người phân tích có thể đối chiếu, liên kết các sự kiện và điều tra hành vi đáng ngờ.

Sysmon không tự động phát hiện mọi cuộc tấn công. Hiệu quả giám sát phụ thuộc vào cấu hình, dữ liệu thu thập, việc lưu giữ log và quy trình phân tích.

## 7. Kết luận

Kết quả thống kê DuckDB cho thấy dữ liệu Sysmon trên máy Dũng có thể được truy vấn và phân nhóm theo Event ID. Trong 42.099 bản ghi đã thống kê, Event ID 3 chiếm số lượng lớn nhất với 34.647 bản ghi, tiếp theo là Event ID 22 với 2.766 bản ghi và Event ID 1 với 2.403 bản ghi.

Thử nghiệm bốn mô hình SLM trên ba sự kiện liên quan đến `Zalo.exe` cho thấy không có mô hình nào đáp ứng hoàn toàn tất cả các tiêu chí trong lượt chạy được đánh giá. Qwen3 4B và Gemma 3 4B có ưu điểm về một số khía cạnh của đầu ra, nhưng vẫn mắc lỗi kỹ thuật. Phi-4-mini nhầm lẫn khái niệm Event ID 22, trong khi Llama 3.2 3B không đáp ứng yêu cầu của prompt.

Kết quả bước đầu cho thấy việc sử dụng SLM để hỗ trợ phân tích log cần đi kèm cơ chế đối chiếu dữ liệu, kiểm tra loại sự kiện và xác minh các nhận định. Chưa đủ cơ sở để xác định mô hình tốt nhất một cách tổng quát vì số lượng prompt và lượt chạy còn hạn chế.

Trong giai đoạn tiếp theo, cần mở rộng bộ dữ liệu, chuẩn hóa cấu hình suy luận, chạy lặp nhiều lần và xây dựng bộ chấm điểm có đáp án chuẩn. Đây là cơ sở để lựa chọn mô hình phù hợp cho AI agent phân tích log Windows trong phạm vi đồ án.
