# Kết quả đánh giá: có SLM và không SLM

- Ngày chạy: 2026-11-15 00:08
- Commit: 0c96ba2
- Mô hình mẫu chuỗi: mau_chuoi.json (sha256 4255be121581), ngưỡng 0.5, 3 ứng viên
- SLM: (không chạy)
- Bộ thử: bo-thu.csv, 5 file đo được, 1 dòng chưa tính

## Bảng chính
Chỉ tính các file CHƯA dùng để chỉnh agent. File đã dùng để chỉnh ghi riêng ở mục Tham khảo.


| Chế độ | Phát hiện đúng (phiên tấn công) | KẾT LUẬN sai mã | Bỏ sót: dừng bước 2 / chưa xác nhận / SLM lỗi | Báo nhầm trên log bình thường | Độ sớm (trung vị, sự kiện) | SLM lỗi (mọi phiên) | Số lần hỏi SLM, tổng giây | Thời gian chạy |
|---|---|---|---|---|---|---|---|---|
| Không SLM | 0/2 (0%) | 0 | 1 / 1 / 0 | 19/3290 (1%) phiên | - | 0 | - | 4146 giây |

## Báo nhầm theo từng máy (log bình thường, số CHÍNH THỨC)

| File | Ghi chú trong bộ thử | Số phiên | KẾT LUẬN nhầm (Không SLM) |
|---|---|---|---|
| benign_sysmon_thien_tuan3.evtx | cung may voi log hoc lop binh thuong nhung khong trung thoi gian (log hoc la 17/10 den 27/10) | 807 | 0 |
| benign_sysmon_thien_tuan4.evtx | cung may nhung khong trung thoi gian voi log hoc; 4 ket luan nham (Office/runonce/Roblox/ProtonVPN) | 1704 | 4 |
| may-khoi-7ngay.evtx | may la; so do truoc khi sua buoc 4; 15 ket luan nham (Lenovo 9 / Edge-UniKey 4 / VS Code 2) | 779 | 15 |

## Phát hiện theo kỹ thuật

| Kỹ thuật | Số phiên tấn công | Đúng (Không SLM) |
|---|---|---|
| T1003.001 | 0 | 0/0 |
| T1021.001 | 2 | 0/2 (0%) |

## Tham khảo (không dùng làm kết quả chính thức)

- Không SLM: KẾT LUẬN trên phần còn lại của file tấn công (phiên không được đánh dấu): 0/4 phiên
- File đã dùng để chỉnh agent (không tính vào bảng chính): evtx-samples/Credential Access/sysmon_10_11_outlfank_dumpert_and_andrewspecial_memdump.evtx
  - Không SLM: phát hiện đúng 1/1 (100%), KẾT LUẬN trên log bình thường 0/0 phiên, SLM lỗi 0

## Không được tính

- benign_sysmon_dung.evtx: không tìm thấy file trong ['D:\\DoAnChuyenNganh\\log', 'D:\\DoAnChuyenNganh\\log-binh-thuong']
- evtx-samples/Credential Access/sysmon_10_lsass_mimikatz_sekurlsa_logonpasswords.evtx: không tìm thấy file trong ['D:\\DoAnChuyenNganh\\log', 'D:\\DoAnChuyenNganh\\log-binh-thuong']
- evtx-samples/Credential Access/sysmon_10_11_lsass_memdump.evtx: không tìm thấy file trong ['D:\\DoAnChuyenNganh\\log', 'D:\\DoAnChuyenNganh\\log-binh-thuong']
- evtx-samples/Credential Access/sysmon_rdrleakdiag_lsass_dump.evtx: không tìm thấy file trong ['D:\\DoAnChuyenNganh\\log', 'D:\\DoAnChuyenNganh\\log-binh-thuong']
- evtx-samples/Credential Access/sysmon_3_10_Invoke-Mimikatz_hosted_Github.evtx: không tìm thấy file trong ['D:\\DoAnChuyenNganh\\log', 'D:\\DoAnChuyenNganh\\log-binh-thuong']
- evtx-samples/Credential Access/babyshark_mimikatz_powershell.evtx: không tìm thấy file trong ['D:\\DoAnChuyenNganh\\log', 'D:\\DoAnChuyenNganh\\log-binh-thuong']
- evtx-samples/Lateral Movement/LM_sysmon_1_12_13_3_tsclient_SharpRdp.evtx: không tìm thấy file trong ['D:\\DoAnChuyenNganh\\log', 'D:\\DoAnChuyenNganh\\log-binh-thuong']
- evtx-samples/Lateral Movement/sharprdp_sysmon_7_mstscax.dll.evtx: không tìm thấy file trong ['D:\\DoAnChuyenNganh\\log', 'D:\\DoAnChuyenNganh\\log-binh-thuong']
- evtx-samples/Privilege Escalation/sysmon_1_11_exec_as_system_via_schedtask.evtx: không tìm thấy file trong ['D:\\DoAnChuyenNganh\\log', 'D:\\DoAnChuyenNganh\\log-binh-thuong']
- evtx-samples/Execution/exec_persist_rundll32_mshta_scheduledtask_sysmon_1_3_11.evtx: không tìm thấy file trong ['D:\\DoAnChuyenNganh\\log', 'D:\\DoAnChuyenNganh\\log-binh-thuong']
- evtx-samples/Lateral Movement/powercat_revShell_sysmon_1_3.evtx: không tìm thấy file trong ['D:\\DoAnChuyenNganh\\log', 'D:\\DoAnChuyenNganh\\log-binh-thuong']
- evtx-samples/Execution/sysmon_11_1_lolbas_downldr_desktopimgdownldr.evtx: không tìm thấy file trong ['D:\\DoAnChuyenNganh\\log', 'D:\\DoAnChuyenNganh\\log-binh-thuong']
- evtx-samples/Lateral Movement/remote_file_copy_system_proc_file_write_sysmon_11.evtx: không tìm thấy file trong ['D:\\DoAnChuyenNganh\\log', 'D:\\DoAnChuyenNganh\\log-binh-thuong']
- evtx-samples/Lateral Movement/smbmap_upload_exec_sysmon.evtx: không tìm thấy file trong ['D:\\DoAnChuyenNganh\\log', 'D:\\DoAnChuyenNganh\\log-binh-thuong']
- evtx-samples/Persistence/persistence_hidden_local_account_sysmon.evtx: không tìm thấy file trong ['D:\\DoAnChuyenNganh\\log', 'D:\\DoAnChuyenNganh\\log-binh-thuong']
- evtx-samples/Persistence/sysmon_local_account_creation_and_added_admingroup_12_13.evtx: không tìm thấy file trong ['D:\\DoAnChuyenNganh\\log', 'D:\\DoAnChuyenNganh\\log-binh-thuong']
- evtx-samples/Persistence/evasion_persis_hidden_run_keyvalue_sysmon_13.evtx: không tìm thấy file trong ['D:\\DoAnChuyenNganh\\log', 'D:\\DoAnChuyenNganh\\log-binh-thuong']
- evtx-samples/Persistence/persistence_startup_UserShellStartup_Folder_Changed_sysmon_13.evtx: không tìm thấy file trong ['D:\\DoAnChuyenNganh\\log', 'D:\\DoAnChuyenNganh\\log-binh-thuong']
- evtx-samples/Lateral Movement/LM_tsclient_startup_folder.evtx: không tìm thấy file trong ['D:\\DoAnChuyenNganh\\log', 'D:\\DoAnChuyenNganh\\log-binh-thuong']
- evtx-samples/Lateral Movement/lateral_movement_startup_3_11.evtx: không tìm thấy file trong ['D:\\DoAnChuyenNganh\\log', 'D:\\DoAnChuyenNganh\\log-binh-thuong']
- dòng 8 (evtx-samples/Credential Access/sysmon_10_1_memdump_comsvcs_minidump.evtx T1003.001): còn ghi 'can kiem tra'

## Cách tính

- Phát hiện đúng: phiên tấn công được KẾT LUẬN đúng mã. Sai mã đếm riêng, không tính là phát hiện đúng.
- Báo nhầm chính thức: phiên của log bình thường bị KẾT LUẬN tấn công.
- Phiên không được đánh dấu trong file tấn công chỉ để tham khảo (có thể lẫn tấn công chưa gán nhãn).
- Độ sớm: số sự kiện từ đầu phiên đến khi agent đủ điều kiện KẾT LUẬN đúng mã; chỉ tính phiên được kết luận đúng.
- Chế độ có SLM: SLM lỗi không được thay bằng chế độ không SLM; phiên đó tính là không kết luận.
- Đọc báo nhầm có SLM cùng cột SLM lỗi: phiên SLM lỗi không bị báo nhầm, nhưng đó là do lỗi kỹ thuật, không phải SLM nhận ra là bình thường. Chỉ cột 'Chưa xác nhận do SLM' là SLM thật sự chặn lại.
