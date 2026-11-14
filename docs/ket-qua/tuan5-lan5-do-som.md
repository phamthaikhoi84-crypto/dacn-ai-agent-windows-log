# Kết quả đánh giá: có SLM và không SLM

- Ngày chạy: 2026-11-15 01:59
- Commit: 0c96ba2
- Mô hình mẫu chuỗi: mau_chuoi.json (sha256 4255be121581), ngưỡng 0.5, 3 ứng viên
- SLM: phi4-mini:latest
- Bộ thử: bo-thu.csv, 21 file đo được, 1 dòng chưa tính

## Bảng chính
Chỉ tính các file CHƯA dùng để chỉnh agent. File đã dùng để chỉnh ghi riêng ở mục Tham khảo.


| Chế độ | Phát hiện đúng (phiên tấn công) | KẾT LUẬN sai mã | Bỏ sót: dừng bước 2 / chưa xác nhận / SLM lỗi | Báo nhầm trên log bình thường | Độ sớm (trung vị, sự kiện) | SLM lỗi (mọi phiên) | Số lần hỏi SLM, tổng giây | Thời gian chạy |
|---|---|---|---|---|---|---|---|---|
| Không SLM | 7/31 (23%) | 0 | 18 / 6 / 0 | 0/0 phiên | 2 (7 phiên) | 0 | - | 1 giây |
| Có SLM | 6/31 (19%) | 0 | 18 / 7 / 0 | 0/0 phiên | 2 (6 phiên) | 0 | 7 lần, 80 giây | 114 giây |

## Báo nhầm theo từng máy (log bình thường, số CHÍNH THỨC)

| File | Ghi chú trong bộ thử | Số phiên | KẾT LUẬN nhầm (Không SLM) | KẾT LUẬN nhầm (Có SLM) | SLM lỗi (Có SLM) | Chưa xác nhận do SLM (Có SLM) |
|---|---|---|---|---|---|---|

## Phát hiện theo kỹ thuật

| Kỹ thuật | Số phiên tấn công | Đúng (Không SLM) | Đúng (Có SLM) |
|---|---|---|---|
| T1003.001 | 6 | 5/6 (83%) | 4/6 (67%) |
| T1021.001 | 5 | 0/5 (0%) | 0/5 (0%) |
| T1053.005 | 4 | 2/4 (50%) | 2/4 (50%) |
| T1059.001 | 1 | 0/1 (0%) | 0/1 (0%) |
| T1105 | 4 | 0/4 (0%) | 0/4 (0%) |
| T1136.001 | 7 | 0/7 (0%) | 0/7 (0%) |
| T1547.001 | 4 | 0/4 (0%) | 0/4 (0%) |

## Tham khảo (không dùng làm kết quả chính thức)

- Không SLM: KẾT LUẬN trên phần còn lại của file tấn công (phiên không được đánh dấu): 0/18 phiên
- Có SLM: KẾT LUẬN trên phần còn lại của file tấn công (phiên không được đánh dấu): 0/18 phiên
- File đã dùng để chỉnh agent (không tính vào bảng chính): evtx-samples/Credential Access/sysmon_10_11_outlfank_dumpert_and_andrewspecial_memdump.evtx
  - Không SLM: phát hiện đúng 1/1 (100%), KẾT LUẬN trên log bình thường 0/0 phiên, SLM lỗi 0
  - Có SLM: phát hiện đúng 1/1 (100%), KẾT LUẬN trên log bình thường 0/0 phiên, SLM lỗi 0

## Không được tính

- dòng 8 (evtx-samples/Credential Access/sysmon_10_1_memdump_comsvcs_minidump.evtx T1003.001): còn ghi 'can kiem tra'

## Cách tính

- Phát hiện đúng: phiên tấn công được KẾT LUẬN đúng mã. Sai mã đếm riêng, không tính là phát hiện đúng.
- Báo nhầm chính thức: phiên của log bình thường bị KẾT LUẬN tấn công.
- Phiên không được đánh dấu trong file tấn công chỉ để tham khảo (có thể lẫn tấn công chưa gán nhãn).
- Độ sớm: số sự kiện từ đầu phiên đến khi agent đủ điều kiện KẾT LUẬN đúng mã; chỉ tính phiên được kết luận đúng.
- Chế độ có SLM: SLM lỗi không được thay bằng chế độ không SLM; phiên đó tính là không kết luận.
- Đọc báo nhầm có SLM cùng cột SLM lỗi: phiên SLM lỗi không bị báo nhầm, nhưng đó là do lỗi kỹ thuật, không phải SLM nhận ra là bình thường. Chỉ cột 'Chưa xác nhận do SLM' là SLM thật sự chặn lại.
