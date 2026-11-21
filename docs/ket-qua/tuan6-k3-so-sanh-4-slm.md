# Tuần 6 – K3: so sánh 4 SLM và lần đo 6 không SLM trên bộ thử

Điều kiện chung: commit `1c7211a`, `mau_chuoi.json` sha256 `4255be121581`, ngưỡng 0,5, 3 ứng viên, `data/bo-thu.csv` (29 phiên tấn công chưa dùng chỉnh agent, 3.290 phiên log bình thường của máy Thiên tuần 3, tuần 4 và máy Khôi 7 ngày), cách hỏi SLM cũ (chưa có cách hỏi mới D3), luật Startup tắt trừ dòng ghi rõ. Chạy trên máy Khôi (Ollama, 100% CPU), đêm 20–21/11/2026. Chi tiết từng lần: các file `tuan6-lan6-*.md`, `tuan6-k3-slm-*.md` cùng thư mục.

Log máy Dũng không được tính: file nhận ngày 20/11 gom được 353 phiên, còn `bo-thu.csv` ghi 2.573 phiên (file khác với bản Thiên đã đo), nên `danh_gia.py` bỏ qua. Log này vốn chỉ để tham khảo, không ảnh hưởng bảng chính.

## Bảng chính

| Chế độ | Phát hiện đúng / 29 | Báo nhầm / 3.290 | Thiên t4 / Khôi | "Chưa xác nhận do SLM" | SLM lỗi | Số lần hỏi | TB mỗi lần hỏi | Thời gian chạy |
|---|---|---|---|---|---|---|---|---|
| Không SLM, luật Startup tắt | 7 (24%) | 19 (0,58%) | 4 / 15 | – | – | – | – | 22 phút |
| Không SLM, luật Startup bật | 9 (31%) | 19 (0,58%) | 4 / 15 | – | – | – | – | 18 phút |
| phi4-mini | 6 (21%) | 8 (0,24%) | 2 / 6 | 11 | 0 | 26 | 52 giây | 38 phút |
| qwen3:4b-instruct-2507 | 7 (24%) | 13 (0,40%) | 4 / 9 | 6 | 0 | 26 | 74 giây | 50 phút |
| llama3.2:3b | 6 (21%) | 15 (0,46%) | 2 / 13 | 4 | 0 | 26 | 45 giây | 30 phút |
| gemma3:4b | 6 (21%) | 8 (0,24%) | 2 / 6 | 11 | 0 | 26 | 58 giây | 34 phút |

- Máy Thiên tuần 3: 0/807 ở mọi chế độ.
- Không mô hình nào phát hiện nhiều hơn chế độ không SLM (7/29). 0 KẾT LUẬN sai mã ở mọi chế độ.
- phi4-mini chạy lại cho đúng số của lần đo 4 tuần 5 (6/29, 8 báo nhầm): kết quả lặp lại được.
- Luật Startup (T3 của Thiên) đúng như dự kiến ghi trước: +2 phiên T1547.001 (`LM_tsclient_startup_folder` phiên 2, `lateral_movement_startup_3_11` phiên 1), không thêm báo nhầm. Luật được thiết kế sau khi đã đọc bộ thử.

## Phát hiện theo kỹ thuật (chỉ ghi kỹ thuật có khác biệt)

| Kỹ thuật | Không SLM | phi4-mini | qwen3 | llama3.2 | gemma3 |
|---|---|---|---|---|---|
| T1003.001 (6) | 5 | 4 | 5 | 5 | 5 |
| T1053.005 (4) | 2 | 2 | 2 | 1 | 1 |

- phi4-mini mất `babyshark_mimikatz_powershell` (chọn T1059.001 thay vì T1003.001), giống tuần 5.
- llama3.2 và gemma3 mất `exec_persist_rundll32_mshta_scheduledtask` (chọn T1059.001 thay vì T1053.005).

## Vì sao báo nhầm giảm: 9 lần hỏi trên máy Khôi có 2 ứng viên T1053.005 / T1070.001

Đây là các phiên Lenovo Vantage / Defender (cùng kiểu phiên #46 tuần 5): Lenovo chạy `schtasks /Create` thật (đủ dấu vết T1053.005), Defender gọi `wevtutil` sửa kênh nhật ký (không có `wevtutil cl`, thiếu dấu vết T1070.001).

| Mô hình | Chọn T1053.005 | Chọn T1070.001 | Chọn khác |
|---|---|---|---|
| phi4-mini | 0 | 9 | 0 |
| qwen3 | 3 | 6 | 0 |
| llama3.2 | 7 | 1 | 1 (T1059.001) |
| gemma3 | 3 | 5 | 1 (T1059.001) |

- Đọc đúng log thì đáp án là T1053.005 (Lenovo thật sự tạo tác vụ hẹn giờ). Mô hình đọc đúng nhất (llama3.2) lại có nhiều báo nhầm nhất; mô hình chọn sai (phi4-mini chọn T1070.001 cả 9 lần) bị bước 5 chặn nên ít báo nhầm.
- Vậy cột "Chưa xác nhận do SLM" không phải SLM nhận ra hoạt động bình thường: chưa mô hình nào có lựa chọn "bình thường" (cách hỏi cũ chỉ cho chọn trong ứng viên hoặc CHUA_XAC_NHAN, và không mô hình nào chọn CHUA_XAC_NHAN).
- Đây là lý do cần cách hỏi mới (D3: cho SLM biết ứng viên nào đủ / thiếu dấu vết và thêm lựa chọn BINH_THUONG).

## Còn thiếu cho bảng 4 SLM (D2)

- RAM khi chạy (`ollama ps`), nhận xét từng mô hình: Dũng bổ sung vào `docs/models.md`.
- Log máy Dũng: chờ xác nhận đúng file 2.573 phiên.
