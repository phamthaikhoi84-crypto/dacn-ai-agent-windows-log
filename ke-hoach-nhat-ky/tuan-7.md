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

Cập nhật tối T6 27/11 (hạn chính). Việc còn dở làm tiếp đến CN 29/11; đến đó vẫn chưa xong thì ghi lý do và chuyển sang tuần 8.

| Việc | Trạng thái | Commit / file |
|---|---|---|
| K1 `dacn.py` + README | Xong | `555856d`, sửa theo T4 ở `630680d` |
| K2 chuỗi tấn công | Xong | `5ddb36e`; thử trực tiếp `25ca167`, `c4c9636` |
| K3 theo dõi 24 giờ + thử Startup | Xong (21,1 giờ) | `docs/bao-cao/danh-gia.md` mục 7 (`5aeab74`) |
| K4 Streamlit bản đầu | Chưa làm | Làm trong hạn bù CN 29/11 |
| K5 máy lạ thứ hai | Đang thu từ 25/11 | `docs/log-binh-thuong.md` mục 8.5 |
| K6 `tuan-7.md`, phiếu, `ai-logs/` | Đang làm | file này |
| T1 log chuỗi tấn công | Xong | `79eca24` |
| T2 dữ liệu train phiên ngắn | Xong, kết quả âm | `docs/ket-qua-huan-luyen.md` mục 9 |
| T3 nháp chương Dữ liệu, Đánh giá | Xong bản nháp | `f185786`, `2fcc679`, `aa8b72b` |
| T4 thử README | Xong | 3 góp ý, đã sửa ở `630680d` |
| D1–D3 Dũng | Chưa thấy kết quả trên repo | xem mục Dũng bên dưới |

### K1. Một lệnh chạy agent (`src/dacn.py`)

- 5 chế độ: `quet`, `phat-lai`, `theo-doi`, `danh-gia`, `chuoi`. `dacn.py` chỉ gọi lại script có sẵn và chuyển nguyên tham số, không chứa logic phát hiện.
- Tham số chung: `--startup` (luật Startup), `--model`, `--prompt-moi`, `--moi-dot`.
- Báo lỗi dễ hiểu khi thiếu file, file bị thành `.evtx.evtx`, đường dẫn có khoảng trắng mà không có ngoặc kép, sai tên chế độ, không đứng ở thư mục gốc repo. Ctrl+C không làm mất tổng kết của `theo-doi`.
- README mục "Cách chạy": cài đặt (có Sysmon), bảng chế độ, thử nhanh bằng file Dumpert, bảng tham số, nơi để kết quả, lỗi hay gặp.
- T4: Thiên làm theo README trên máy Thiên chạy được; 3 chỗ bị kẹt (đường dẫn file Dumpert, ngoặc kép, nhắc `cd` khi mở cửa sổ admin mới) đã sửa.

### K2. Chuỗi tấn công (`src/chuoi_tan_cong.py`)

- `quet` chỉ cho một kết quả mỗi phiên, mà chuỗi T1 nằm trọn trong một phiên, nên `quet` chỉ ra 1 kỹ thuật. `chuoi` phát lại file từng sự kiện qua đúng phần theo dõi trực tiếp; sau mỗi KẾT LUẬN, phần còn lại của phiên được xét như đoạn mới. Không đổi bước 1–5, dấu vết hay mô hình.
- Nối KẾT LUẬN cùng máy cách nhau không quá 60 phút; gán giai đoạn (Xâm nhập, Thực thi, Bám trụ, Đánh cắp đăng nhập, Lan rộng, Xóa dấu vết); ghi chú bước lùi giai đoạn. Cùng kỹ thuật lặp trong 300 giây gộp thành một bước: quy tắc chỉ để hiển thị, đặt ra sau khi thấy log T1.
- Log T1 của Thiên, không SLM: **7 bước, 6 kỹ thuật, 4,2 phút, ĐÚNG thứ tự** so với bảng của Thiên (`--mong-doi`). Ảnh `docs/hinh/tuan7-k2-chuoi-t1-khong-slm.png`.
- `theo_doi.py` in chuỗi khi một máy có từ 2 kỹ thuật. Thử trên máy Khôi (26/11 00:00): `schtasks /create` rồi `reg add` khóa Run ra chuỗi 2 bước. Ảnh `docs/hinh/tuan7-k2-chuoi-truc-tiep.png` (đã che tên máy, người dùng, SID; `--an-ten` giờ che cả SID).
- Lúc thử lộ ra 2 điểm yếu của dấu vết T1547.001: lệnh dọn `reg delete` (Event 12, xóa) cũng bị KẾT LUẬN; khóa `RunNotification` do Windows tự ghi bị khớp nhầm. Chi tiết và hướng sửa ở `docs/bao-cao/danh-gia.md` mục 7.3. Hai lỗi này phát hiện trên máy thật, không phải bộ thử, nên được phép sửa; quyết ở tuần 8 trước khi chốt cấu hình.

### K3. Theo dõi trực tiếp 21 giờ

- 26/11 00:26 → 21:31 (21,1 giờ, chạy liền), không SLM, luật Startup bật, máy Khôi dùng như mọi ngày.
- 16.581 sự kiện Sysmon, 59 sự kiện PowerShell 4104, **502 phiên**.
- **0 KẾT LUẬN sai.** KẾT LUẬN duy nhất là lần thử ghi file vào thư mục Startup lúc 00:27: ra T1547.001 sau 7,8 giây (tuần 6 lần thử này bị bỏ sót).
- 4 phiên dừng ở CHƯA XÁC NHẬN (2 T1059.001, 2 T1547.001), chưa xét từng phiên.
- Quy tắc ba: cận trên tỉ lệ báo nhầm khoảng 0,6% số phiên, tức khoảng 3 cảnh báo sai mỗi ngày với máy này. So với tuần 6 (75 phút, cận trên khoảng 2,4 lần / giờ) thì chặt hơn nhiều.
- Độ trễ cảnh báo qua các lần thử: không SLM 3,8–15,6 giây, có SLM 23,4 giây (1 lần).
- Ghi vào `docs/bao-cao/danh-gia.md` mục 7 và 8 (`5aeab74`).

### K4. Streamlit bản đầu

- Chưa làm đến tối T6 27/11. Ưu tiên K1–K3 và báo cáo trước. Làm trong hạn bù CN 29/11.

### K5. Máy lạ thứ hai

- Laptop Windows của một người quen, Sysmon chạy từ 25/11/2026 khoảng 22:45, cùng cấu hình `config/sysmonconfig-dacn.xml`, kênh Sysmon 1 GB, bật Script Block Logging. Người đó đã được giải thích Sysmon ghi những gì; tên máy, tài khoản sẽ được che.
- Khoảng 1/12 xuất log; chỉ dùng đo báo nhầm ở lần đo cuối, không dùng để train hay chỉnh.

### Thiên (T1–T4)

- T1: làm lại một lần (bản đầu: comsvcs không dump được do LSA protection, bước xóa log nằm sau lúc xuất, thiếu T1105 và T1136.001, lẫn test cũ). Bản đạt: 62 sự kiện, máy ảo `DACN-LAB`, bước 0 xóa log Sysmon để chuẩn bị và 6 bước T1105 > T1059.001 > T1547.001 > T1136.001 > T1003.001 > T1070.001. Bảng `data/tuan7-t1-bang-thoi-gian.md`. Không dùng để train hay chỉnh agent.
- T2: 24 lệnh phiên ngắn mới cho 8 kỹ thuật (5 lệnh không sinh chuỗi nào vì Sysmon không ghi, vd `New-LocalUser`, `Invoke-WebRequest`), train `models/mau_chuoi_v2.json`. Bản 2 tệ hơn bản 1 cả hai mặt: bộ phát triển 5/21 so với 12/21; báo nhầm log Dũng 54 so với 10, log Thiên tuần 1 13 so với 1. 54/54 báo nhầm đều là T1547.001, do mẫu học từ phiên ngắn chỉ cần kết thúc bằng ghi khóa Run. **Giữ bản 1.**
- T3: nháp `docs/bao-cao/du-lieu.md` và `docs/bao-cao/danh-gia.md`, sửa 2 lượt theo góp ý (lần đo và mẫu số, cách gọi "chính thức", luật Startup thiết kế sau khi đọc bộ thử, RunOnce, Dumpert/SharpRDP). Mục 7–8 do Khôi điền.
- T4: xem K1.

### Dũng (D1–D3)

- Đến tối T6 27/11 chưa có file mới trong `docs/ket-qua/` hay `docs/models.md`. Nhánh `origin/review-dung-d2-d3` chưa xem, chưa gộp.
- (Dũng bổ sung trước CN 29/11. D3 fine-tune nếu không có kết quả thì ghi "đã thử, không kịp, bỏ fine-tune khỏi phạm vi" kèm lý do.)

## Nội dung ghi phiếu tiến độ

Phiếu tuần 7 (23/11 – 29/11/2026), 4 dòng:

- Một lệnh chạy agent (`dacn.py`) và hướng dẫn chạy trong README
- Nối chuỗi tấn công: log kịch bản 6 kỹ thuật ra đúng thứ tự
- Theo dõi trực tiếp 21 giờ trên máy thật: 0 cảnh báo sai / 502 phiên
- Thử dữ liệu train phiên ngắn (không đạt, giữ bản 1); nháp 2 chương báo cáo

## Kết luận tạm

- Đề cương hứa "nối phát hiện thành chuỗi tấn công": đã làm và chạy đúng trên một kịch bản. Mới một kịch bản do nhóm tự tạo nên chưa đo được tỉ lệ nối đúng.
- Theo dõi trực tiếp chạy ổn một ngày liền trên máy thật, không có cảnh báo sai; lần thử Startup bị bỏ sót tuần 6 nay đã phát hiện.
- Thêm dữ liệu train dạng phiên ngắn làm bước 2 tệ hơn. Bước 2 vẫn là điểm yếu chính, nhưng không cải thiện được bằng cách thêm dữ liệu kiểu này.

## Hạn chế cần ghi rõ

- K3 chỉ một máy, một ngày, chế độ không SLM; chưa xét 4 phiên CHƯA XÁC NHẬN.
- Chuỗi tấn công mới thử trên 1 log, kịch bản biết trước, chế độ không SLM. Quy tắc gộp 300 giây đặt ra sau khi xem log T1 (chỉ ảnh hưởng phần hiển thị).
- Dấu vết T1547.001 chưa phân biệt ghi / xóa giá trị registry và khớp nhầm `RunNotification`.
- Luật Startup vẫn là luật thiết kế sau khi đã đọc bộ thử (ghi từ tuần 6).
- Máy lạ thứ hai mới bắt đầu thu.

## Việc tuần 8

- Chốt cấu hình: `mau_chuoi.json` bản 1; cách hỏi SLM; luật Startup bật hay tắt; quyết có sửa 2 điểm yếu T1547.001 không (sửa thì thử lại trên máy thật trước khi chốt).
- Đo cuối trên bộ thử một lần duy nhất, sau khi chốt.
- Lấy log máy lạ thứ hai (khoảng 1/12), đo báo nhầm, rồi gửi lệnh gỡ Sysmon.
- Giao diện (K4) xong; báo cáo nháp đủ các chương.
- Dũng: kết luận fine-tune.

## Dùng AI

- Claude (Anthropic) hỗ trợ Khôi viết `src/dacn.py`, `src/chuoi_tan_cong.py`, phần in chuỗi và che SID trong `theo_doi.py`, mục "Cách chạy" của README; góp ý log T1, bảng T1, hướng dẫn T2 và 2 chương nháp của Thiên; viết mục 7–8 của `danh-gia.md` và phần kết quả tuần này từ file kết quả do nhóm tự chạy. Mọi lần chạy (K2 trên log T1, thử trực tiếp, K3 21 giờ) do Khôi chạy trên máy thật; số liệu lấy từ `tong_ket.md`, `canh_bao.csv`, `chuoi.md`, không do AI tạo. Chi tiết trong `ai-logs/`.
