# Tuần 7 (23/11 – 29/11/2026)

## Mục tiêu tuần

Sau tuần 6 đã có đủ 4 thứ thầy cần cuối kỳ (theo dõi trực tiếp, bảng có / không SLM, báo nhầm trên máy chưa dùng huấn luyện, bảng 4 SLM). Còn 4 tuần, nên tuần 7 kéo sớm các phần của tuần 9–10 và làm nốt phần đề cương đã hứa mà chưa có:

1. **Nối chuỗi tấn công:** đề cương hứa "nối phát hiện thành chuỗi tấn công" và đo "khả năng nối đúng chuỗi", hiện chưa làm. Cần một kịch bản chuỗi thật và code nối chuỗi.
2. **Một lệnh chạy được agent** (`src/dacn.py`) và mục "Cách chạy" trong README, để thầy và người chấm tự chạy.
3. **Giao diện bản đầu** (kéo từ tuần 9 lên): xem cảnh báo và chi tiết 5 bước.
4. **Bước 2 vẫn là điểm yếu lớn nhất:** thử dữ liệu train bổ sung dạng phiên ngắn, đo trên bộ phát triển.
5. **Quyết định fine-tune** (đề cương tuần 7–8) bằng một lần thử có giới hạn thời gian.
6. **Bắt đầu viết báo cáo cuối kỳ** (đề cương để tuần 10).

Quy tắc giữ nguyên: mọi chỉnh sửa bước 2 và cách hỏi SLM làm trên bộ phát triển. Tuần 7 **không đo bộ thử**; lần đo cuối trên bộ thử làm một lần ở tuần 8, sau khi chốt cấu hình.

**Hạn:** hạn chính là **tối thứ 6 27/11** cho mọi việc. Chưa xong thì hạn bù **chủ nhật 29/11**. Đến chủ nhật vẫn chưa xong thì chuyển sang tuần 8 và hoàn thành chung với lần đo cuối; ghi rõ trong `tuan-7.md` phần đã làm và lý do chưa xong.

## Lộ trình còn lại

| Tuần | Mục tiêu |
|---|---|
| 7 (23/11 – 29/11) | Chuỗi tấn công, `dacn.py`, giao diện bản đầu, dữ liệu train bước 2, quyết định fine-tune, bắt đầu báo cáo |
| 8 (30/11 – 6/12) | Chốt cấu hình; lần đo cuối trên bộ thử và máy lạ thứ hai; giao diện xong; báo cáo bản nháp đủ các chương |
| 9 (7/12 – 13/12) | Slide, video demo, chạy thử buổi bảo vệ, sửa báo cáo theo góp ý |
| 10 (14/12 – 20/12) | Dự phòng, nộp |

So với đề cương: giao diện kéo từ tuần 9 lên tuần 7–8, báo cáo kéo từ tuần 10 lên tuần 7–9, để tuần 10 làm dự phòng.

## Phân công

### Khôi (agent, chuỗi tấn công, giao diện)

| Việc | Xong khi |
|---|---|
| K1. `src/dacn.py`: một cửa vào cho các chế độ `quet`, `phat-lai`, `theo-doi`, `danh-gia`; mục "Cách chạy" trong README | Thiên làm theo README trên máy Thiên, chạy được cả 4 chế độ mà không cần hỏi |
| K2. `src/chuoi_tan_cong.py`: nối các KẾT LUẬN cùng máy trong một khoảng thời gian thành chuỗi theo giai đoạn (xâm nhập, thực thi, bám trụ, đánh cắp đăng nhập, lan rộng, xóa dấu vết); `theo_doi.py` in chuỗi khi có từ 2 kỹ thuật | Chạy trên log kịch bản chuỗi của Thiên (T1) ra đúng thứ tự các bước Thiên đã ghi |
| K3. Theo dõi trực tiếp 24 giờ (không SLM, luật Startup bật); thử lại ghi file vào thư mục Startup trên máy thật với luật bật | Bật tối T5 26/11, tắt tối T6 27/11. Có `tong_ket.md` 24 giờ (số cảnh báo / ngày); lần thử Startup ra KẾT LUẬN T1547.001 hoặc ghi rõ vì sao không |
| K4. Trang Streamlit bản đầu: đọc kết quả của `theo_doi.py` (`canh_bao.csv`, `chi_tiet.txt`) và `danh_gia.py` (`bang.md`); xem danh sách cảnh báo, bấm vào xem chi tiết 5 bước | `streamlit run` chạy được trên máy Khôi, có ảnh chụp (đã che tên máy) |
| K5. Máy lạ thứ hai: gửi hướng dẫn cài Sysmon (cùng cấu hình) cho người quen dùng laptop Windows, bắt đầu thu | Sysmon chạy, ghi ngày bắt đầu vào `docs/log-binh-thuong.md`; thu ít nhất 5 ngày để kịp lần đo cuối tuần 8 |
| K6. `tuan-7.md`, phiếu, `ai-logs/` (bổ sung dòng tuần 3–5 còn thiếu) | Đã push, phiếu nộp LMS |

### Thiên (dữ liệu, bước 2, báo cáo)

| Việc | Xong khi |
|---|---|
| T1. Kịch bản chuỗi tấn công trong máy ảo: chạy nối tiếp trong một phiên 5–6 kỹ thuật (vd tải file T1105, PowerShell T1059.001, tạo tác vụ T1053.005 hoặc khóa Run T1547.001, tạo tài khoản T1136.001, đọc bộ nhớ lsass T1003.001, xóa log T1070.001), ghi giờ từng bước; xuất `.evtx` | File `.evtx` + bảng các bước và giờ chạy trong `data/`; không dùng để train, không dùng chỉnh agent |
| T2. Dữ liệu train bổ sung cho bước 2: thu mẫu phiên ngắn (lệnh đơn lẻ) cho 8 kỹ thuật trong máy ảo, khác các lệnh đã có trong bộ phát triển đơn lẻ; train `mau_chuoi.json` bản 2; đo bản 1 và bản 2 trên bộ phát triển và log bình thường (Dũng, Thiên tuần 1) | Bảng trước / sau trong `docs/ket-qua-huan-luyen.md`; chỉ đề nghị chốt bản 2 nếu bộ phát triển tốt hơn và báo nhầm không tăng |
| T3. Báo cáo cuối kỳ: chương dữ liệu và chương đánh giá, bản nháp đủ mục (dùng mục 6b–6e, bảng tuần 5–6) | File nháp trong repo (`docs/bao-cao/`), Khôi đọc góp ý |
| T4. Thử README của Khôi (K1) trên máy Thiên | Ghi lại bước nào bị kẹt |

### Dũng (SLM)

| Việc | Xong khi |
|---|---|
| D1. Việc còn nợ tuần 6: đo lại trên log riêng bằng `agent.py` trên main, cách hỏi cũ và mới, mỗi cách 2 số (KẾT LUẬN, SLM_BINH_THUONG); đo RAM 4 mô hình (`ollama ps`); xác nhận file log 353 hay 2.573 phiên | Số đã ghi vào `docs/ket-qua/d3-prompt-moi.md` và `docs/models.md` |
| D2. Phân tích vì sao cách hỏi mới chọn CHUA_XAC_NHAN ở 10 phiên bộ phát triển (`--in-dong-slm`); thử cách hỏi mới bản 2 (nới quy tắc khi ứng viên đã đủ dấu vết) trên bộ phát triển và log riêng | Bảng cũ / mới / mới bản 2 trên bộ phát triển; tiêu chí giữ nguyên: không mất phát hiện, chọn BINH_THUONG ở phiên Lenovo/Defender |
| D3. Fine-tune, thử có giới hạn: chuẩn bị dữ liệu từ log train (không dùng bộ thử, bộ phát triển), LoRA 1 mô hình trên Colab | Đến tối T6 27/11: hoặc có mô hình chạy được qua Ollama và số trên bộ phát triển, hoặc ghi "đã thử, không kịp, bỏ fine-tune khỏi phạm vi" kèm lý do |

Dũng chỉ sửa `slm.py` và tài liệu của mình; cần đổi `agent.py`, `dau_vet.py`, `danh_gia.py` thì nhắn Khôi trước.

## Mốc trong tuần

| Ngày | Khôi | Thiên | Dũng |
|---|---|---|---|
| Tối T4 25/11 | K1 `dacn.py` + README | T1 log kịch bản chuỗi | D1 số trên log riêng, RAM, xác nhận file log |
| Tối T5 26/11 | Bật theo dõi 24 giờ (K3); gửi hướng dẫn Sysmon (K5) | T4 thử README; T2 thu xong dữ liệu train | D2 phân tích 10 phiên CHUA_XAC_NHAN |
| **Tối T6 27/11 (hạn chính)** | K2 chạy trên log của Thiên; K4 Streamlit bản đầu; tắt theo dõi 24 giờ, thử Startup | T2 bảng bản 1 / bản 2; T3 nháp 2 chương | D2 cách hỏi bản 2; D3 có kết quả fine-tune hoặc ghi dừng |
| T7 28/11 | Báo cáo nếu thầy hẹn | | |
| **CN 29/11 (hạn bù)** | Việc còn dở; `tuan-7.md`, phiếu, `ai-logs/` | Việc còn dở | Việc còn dở |

Việc nào đến chủ nhật vẫn chưa xong thì chuyển sang tuần 8.

## Vượt tiến độ (làm khi phần chính đã xong)

| Người | Việc | Vì sao đáng làm |
|---|---|---|
| Khôi | Giao diện xem chuỗi tấn công dạng dòng thời gian | Demo cuối kỳ dễ hiểu hơn bảng chữ |
| Khôi | Quay video demo ngắn (theo dõi trực tiếp + chuỗi tấn công) | Đề cương để tuần 10; quay sớm để có thời gian sửa |
| Thiên | Kịch bản chuỗi thứ hai khác thứ tự / khác công cụ | Đo "nối đúng chuỗi" trên hơn 1 kịch bản |
| Dũng | Thử `qwen3:8b` với cách hỏi cũ trên bộ phát triển | Xem mô hình lớn hơn có bớt chọn theo từ khóa không |

## Khi nào coi là đạt

- Agent nối được chuỗi tấn công trên log kịch bản của Thiên, đúng thứ tự các bước.
- Chạy agent bằng một lệnh theo README, người khác làm theo được.
- Có giao diện bản đầu xem được cảnh báo và chi tiết.
- Có quyết định rõ về fine-tune (làm tiếp hay bỏ, kèm lý do).
- Đủ điều kiện cho lần đo cuối tuần 8: `mau_chuoi.json` bản nào, cách hỏi nào, luật Startup bật hay tắt đều có số trên bộ phát triển để chốt.

## Kết quả

(Điền cuối tuần.)
