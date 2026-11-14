# Kết quả đánh giá: có SLM và không SLM

- Ngày chạy: 2026-11-14 18:16
- Commit: a118d22
- Mô hình mẫu chuỗi: mau_chuoi.json (sha256 4255be121581), ngưỡng 0.5, 3 ứng viên
- SLM: phi4-mini:latest
- Bộ thử: bo-thu.csv, 1 file đo được, 0 dòng chưa tính

## Bảng chính

| Chế độ | Phát hiện đúng (phiên tấn công) | KẾT LUẬN sai mã | Bỏ sót: dừng bước 2 / chưa xác nhận / SLM lỗi | Báo nhầm trên log bình thường | Độ sớm (trung vị, sự kiện) | SLM lỗi (mọi phiên) | Số lần hỏi SLM, tổng giây | Thời gian chạy |
|---|---|---|---|---|---|---|---|---|
| Không SLM | 0/0 | 0 | 0 / 0 / 0 | 15/779 (2%) phiên | - | 0 | - | 180 giây |
| Có SLM | 0/0 | 0 | 0 / 0 / 0 | 6/779 (1%) phiên | - | 0 | 15 lần, 1194 giây | 1384 giây |

## Báo nhầm theo từng máy (log bình thường, số CHÍNH THỨC)

| File | Ghi chú trong bộ thử | Số phiên | KẾT LUẬN nhầm (Không SLM) | KẾT LUẬN nhầm (Có SLM) | SLM lỗi (Có SLM) | Chưa xác nhận do SLM (Có SLM) |
|---|---|---|---|---|---|---|
| may-khoi-7ngay.evtx | may la; so do truoc khi sua buoc 4; 15 ket luan nham (Lenovo 9 / Edge-UniKey 4 / VS Code 2) | 779 | 15 | 6 | 0 | 9 |

## Phát hiện theo kỹ thuật

| Kỹ thuật | Số phiên tấn công | Đúng (Không SLM) | Đúng (Có SLM) |
|---|---|---|---|

## Tham khảo (không dùng làm kết quả chính thức)

- Không SLM: KẾT LUẬN trên phần còn lại của file tấn công (phiên không được đánh dấu): 0/0 phiên
- Có SLM: KẾT LUẬN trên phần còn lại của file tấn công (phiên không được đánh dấu): 0/0 phiên

## Không được tính

- benign_sysmon_thien_tuan3.evtx: không tìm thấy file trong ['D:\\DoAnChuyenNganh\\log', 'D:\\DoAnChuyenNganh\\log-binh-thuong']
- benign_sysmon_thien_tuan4.evtx: không tìm thấy file trong ['D:\\DoAnChuyenNganh\\log', 'D:\\DoAnChuyenNganh\\log-binh-thuong']
- benign_sysmon_dung.evtx: không tìm thấy file trong ['D:\\DoAnChuyenNganh\\log', 'D:\\DoAnChuyenNganh\\log-binh-thuong']

## Cách tính

- Phát hiện đúng: phiên tấn công được KẾT LUẬN đúng mã. Sai mã đếm riêng, không tính là phát hiện đúng.
- Báo nhầm chính thức: phiên của log bình thường bị KẾT LUẬN tấn công.
- Phiên không được đánh dấu trong file tấn công chỉ để tham khảo (có thể lẫn tấn công chưa gán nhãn).
- Độ sớm: số sự kiện từ đầu phiên đến khi agent đủ điều kiện KẾT LUẬN đúng mã; chỉ tính phiên được kết luận đúng.
- Chế độ có SLM: SLM lỗi không được thay bằng chế độ không SLM; phiên đó tính là không kết luận.
- Đọc báo nhầm có SLM cùng cột SLM lỗi: phiên SLM lỗi không bị báo nhầm, nhưng đó là do lỗi kỹ thuật, không phải SLM nhận ra là bình thường. Chỉ cột 'Chưa xác nhận do SLM' là SLM thật sự chặn lại.
