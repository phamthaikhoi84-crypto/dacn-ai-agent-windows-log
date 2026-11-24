# Kết quả đánh giá: có SLM và không SLM

- Ngày chạy: 2026-11-22 14:54
- Commit: 695320d
- Mô hình mẫu chuỗi: mau_chuoi.json (sha256 4255be121581), ngưỡng 0.5, 3 ứng viên
- SLM: phi4-mini:latest
- Luật Startup: tắt
- Cách hỏi SLM: MỚI (SLM_PROMPT_MOI=1)
- Bộ thử: bo-phat-trien-khong-tien-to.csv, 21 file đo được, 6 dòng chưa tính

## Bảng chính
Chỉ tính các file CHƯA dùng để chỉnh agent. File đã dùng để chỉnh ghi riêng ở mục Tham khảo.


| Chế độ | Phát hiện đúng (phiên tấn công) | KẾT LUẬN sai mã | Bỏ sót: dừng bước 2 / chưa xác nhận / SLM lỗi | Báo nhầm trên log bình thường | Độ sớm (trung vị, sự kiện) | SLM lỗi (mọi phiên) | Số lần hỏi SLM, tổng giây | Thời gian chạy |
|---|---|---|---|---|---|---|---|---|
| Có SLM | 2/21 (10%) | 0 | 8 / 11 / 0 | 0/0 phiên | - | 0 | 12 lần, 127 giây | 129 giây |

## Báo nhầm theo từng máy (log bình thường, số CHÍNH THỨC)

| File | Ghi chú trong bộ thử | Số phiên | KẾT LUẬN nhầm (Có SLM) | SLM lỗi (Có SLM) | Chưa xác nhận do SLM (Có SLM) | trong đó SLM chọn BÌNH THƯỜNG |
|---|---|---|---|---|---|---|

## Phát hiện theo kỹ thuật

| Kỹ thuật | Số phiên tấn công | Đúng (Có SLM) |
|---|---|---|
| T1053.005 | 5 | 0/5 (0%) |
| T1059.001 | 4 | 0/4 (0%) |
| T1105 | 3 | 0/3 (0%) |
| T1136.001 | 4 | 1/4 (25%) |
| T1547.001 | 5 | 1/5 (20%) |

## Tham khảo (không dùng làm kết quả chính thức)

- Có SLM: KẾT LUẬN trên phần còn lại của file tấn công (phiên không được đánh dấu): 0/32 phiên

## Không được tính

- dòng 9 (T1547.001-4.evtx T1547.001): còn ghi 'can kiem tra'
- dòng 16 (T1053.005-7.evtx T1053.005): còn ghi 'can kiem tra'
- dòng 18 (T1059.001-10.evtx T1059.001): còn ghi 'can kiem tra'
- dòng 23 (T1105-7.evtx T1105): còn ghi 'can kiem tra'
- dòng 25 (T1105-10.evtx T1105): còn ghi 'can kiem tra'
- dòng 28 (T1105-29.evtx T1105): còn ghi 'can kiem tra'

## Cách tính

- Phát hiện đúng: phiên tấn công được KẾT LUẬN đúng mã. Sai mã đếm riêng, không tính là phát hiện đúng.
- Báo nhầm chính thức: phiên của log bình thường bị KẾT LUẬN tấn công.
- Phiên không được đánh dấu trong file tấn công chỉ để tham khảo (có thể lẫn tấn công chưa gán nhãn).
- Độ sớm: số sự kiện từ đầu phiên đến khi agent đủ điều kiện KẾT LUẬN đúng mã; chỉ tính phiên được kết luận đúng.
- Chế độ có SLM: SLM lỗi không được thay bằng chế độ không SLM; phiên đó tính là không kết luận.
- Đọc báo nhầm có SLM cùng cột SLM lỗi: phiên SLM lỗi không bị báo nhầm, nhưng đó là do lỗi kỹ thuật, không phải SLM nhận ra là bình thường. Chỉ cột 'Chưa xác nhận do SLM' là SLM thật sự chặn lại.
