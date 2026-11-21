# Kết quả đánh giá: có SLM và không SLM

- Ngày chạy: 2026-11-21 00:44
- Commit: 1c7211a
- Mô hình mẫu chuỗi: mau_chuoi.json (sha256 4255be121581), ngưỡng 0.5, 3 ứng viên
- SLM: (không chạy)
- Luật Startup: BẬT (LUAT_STARTUP=1)
- Bộ thử: bo-thu.csv, 25 file đo được, 1 dòng chưa tính

## Bảng chính
Chỉ tính các file CHƯA dùng để chỉnh agent. File đã dùng để chỉnh ghi riêng ở mục Tham khảo.


| Chế độ | Phát hiện đúng (phiên tấn công) | KẾT LUẬN sai mã | Bỏ sót: dừng bước 2 / chưa xác nhận / SLM lỗi | Báo nhầm trên log bình thường | Độ sớm (trung vị, sự kiện) | SLM lỗi (mọi phiên) | Số lần hỏi SLM, tổng giây | Thời gian chạy |
|---|---|---|---|---|---|---|---|---|
| Không SLM | 9/29 (31%) | 0 | 15 / 5 / 0 | 19/3290 (1%) phiên | 2 (9 phiên) | 0 | - | 1071 giây |

## Báo nhầm theo từng máy (log bình thường, số CHÍNH THỨC)

| File | Ghi chú trong bộ thử | Số phiên | KẾT LUẬN nhầm (Không SLM) |
|---|---|---|---|
| benign_sysmon_thien_tuan3.evtx | cung may voi log hoc lop binh thuong nhung khong trung thoi gian (log hoc la 17/10 den 27/10) | 807 | 0 |
| benign_sysmon_thien_tuan4.evtx | cung may nhung khong trung thoi gian voi log hoc; 4 ket luan nham (Office/runonce/Roblox/ProtonVPN) | 1704 | 4 |
| may-khoi-7ngay.evtx | may la; so do truoc khi sua buoc 4; 15 ket luan nham (Lenovo 9 / Edge-UniKey 4 / VS Code 2) | 779 | 15 |

## Phát hiện theo kỹ thuật

| Kỹ thuật | Số phiên tấn công | Đúng (Không SLM) |
|---|---|---|
| T1003.001 | 6 | 5/6 (83%) |
| T1021.001 | 3 | 0/3 (0%) |
| T1053.005 | 4 | 2/4 (50%) |
| T1059.001 | 1 | 0/1 (0%) |
| T1105 | 4 | 0/4 (0%) |
| T1136.001 | 7 | 0/7 (0%) |
| T1547.001 | 4 | 2/4 (50%) |

## Tham khảo (không dùng làm kết quả chính thức)

- Không SLM: KẾT LUẬN trên phần còn lại của file tấn công (phiên không được đánh dấu): 0/14 phiên
- File đã dùng để chỉnh agent (không tính vào bảng chính): evtx-samples/Credential Access/sysmon_10_11_outlfank_dumpert_and_andrewspecial_memdump.evtx, evtx-samples/Lateral Movement/LM_sysmon_3_12_13_1_SharpRDP.evtx
  - Không SLM: phát hiện đúng 1/3 (33%), KẾT LUẬN trên log bình thường 0/0 phiên, SLM lỗi 0

## Không được tính

- benign_sysmon_dung.evtx: gom được 353 phiên nhưng bộ thử ghi SoPhien = 2573: số thứ tự phiên đã lệch, KHÔNG đo file này (Thiên gán nhãn lại, hoặc kiểm tra gom_phien.py)
- dòng 8 (evtx-samples/Credential Access/sysmon_10_1_memdump_comsvcs_minidump.evtx T1003.001): còn ghi 'can kiem tra'

## Cách tính

- Phát hiện đúng: phiên tấn công được KẾT LUẬN đúng mã. Sai mã đếm riêng, không tính là phát hiện đúng.
- Báo nhầm chính thức: phiên của log bình thường bị KẾT LUẬN tấn công.
- Phiên không được đánh dấu trong file tấn công chỉ để tham khảo (có thể lẫn tấn công chưa gán nhãn).
- Độ sớm: số sự kiện từ đầu phiên đến khi agent đủ điều kiện KẾT LUẬN đúng mã; chỉ tính phiên được kết luận đúng.
- Chế độ có SLM: SLM lỗi không được thay bằng chế độ không SLM; phiên đó tính là không kết luận.
- Đọc báo nhầm có SLM cùng cột SLM lỗi: phiên SLM lỗi không bị báo nhầm, nhưng đó là do lỗi kỹ thuật, không phải SLM nhận ra là bình thường. Chỉ cột 'Chưa xác nhận do SLM' là SLM thật sự chặn lại.
