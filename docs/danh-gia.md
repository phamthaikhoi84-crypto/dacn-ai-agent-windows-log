# Đánh giá agent

Phần của Thiên. Số liệu chi tiết ở `docs/ket-qua-huan-luyen.md`; bộ thử ở `data/bo-thu.csv`. Mô hình đóng băng: `models/mau_chuoi.json` (không huấn luyện lại sau khi bộ thử được tạo).

## 1. Câu hỏi đánh giá

1. Khi gặp tấn công **ngoài tập huấn luyện**, agent kết luận đúng kỹ thuật bao nhiêu lần?
2. Khi gặp log **bình thường**, agent kết luận tấn công nhầm bao nhiêu lần?
3. Agent kết luận **sớm** đến mức nào?

## 2. Bộ thử

`data/bo-thu.csv`, cột `Tep, KyThuat, Phien, Nhan, Nguon, SoPhien, GhiChu`.

- **Tấn công:** 21 file chấm điểm từ EVTX-ATTACK-SAMPLES, không file nào dùng để huấn luyện (huấn luyện dùng Splunk Attack Data), trừ hai file đã dùng khi phát triển: `sysmon_10_11_outlfank_dumpert_and_andrewspecial_memdump` (chạy thử và sửa code tuần 4 đến 5) và `LM_sysmon_3_12_13_1_SharpRDP` (dùng để thiết kế ký hiệu `RunMRU` trong `ky_hieu.py`, commit `05161fb` ngày 28/10). Hai file này được tách khỏi bảng chính của `danh_gia.py`, còn 19 file (29 phiên) chấm điểm. Thêm 1 file (`sysmon_10_1_memdump_comsvcs_minidump`, đích là notepad chứ không phải lsass) đã loại.
- **Bình thường:** 4 log (máy Thiên tuần 3 và tuần 4, máy Dũng, máy Khôi). Chỉ log bình thường mới được dùng để đếm báo giả.
- **Nhãn:** gán bằng cách đọc lệnh và sự kiện thật trong từng file, không dùng kết quả của agent hay `dau_vet.py`. Cột `Phien` ghi những phiên chứa **chính hành vi tạo ra kỹ thuật** (ví dụ `schtasks /create`, truy cập lsass, kết nối 3389), không tính phiên chỉ là hậu quả. Phiên còn lại trong file tấn công **không** tính là bình thường và không dùng để đếm báo giả.
- Loại khỏi bộ thử (lý do ghi trong `GhiChu`/mục 5): file không có sự kiện tấn công trong Sysmon, hoặc là kỹ thuật khác (T1218, T1220, T1548.002, T1562, T1055, T1021.006).

## 3. Cách tính

- **Đúng kỹ thuật (phiên tấn công):** phiên trong cột `Phien` được agent kết luận (qua các bước, điểm ≥ 0,5) đúng mã kỹ thuật. Kết luận sai mã đếm riêng, không tính là đúng. Tỉ lệ = phiên đúng / phiên có nhãn, kèm khoảng tin cậy Wilson 95%. Số theo file (ít nhất một phiên có nhãn đúng) báo thêm.
- **Bỏ sót:** phiên có nhãn không được kết luận đúng mã: dừng ở bước 2 (điểm dưới ngưỡng), chưa xác nhận (thiếu dấu vết hoặc SLM chặn) hoặc SLM lỗi.
- **Báo giả (log bình thường):** số phiên bị kết luận là có tấn công / tổng số phiên. Chỉ tính trên log bình thường.
- **Độ sớm:** số sự kiện tính từ sự kiện đầu tiên của phiên đến sự kiện mà agent đưa ra kết luận (đoạn khớp đủ điểm và đủ dấu vết). Ví dụ phiên có 12 sự kiện, kết luận khi đã thấy 5 sự kiện đầu thì độ sớm là 5. Số nhỏ là sớm. Báo cáo trung vị và khoảng của độ sớm trên các phiên đúng, không tính phiên bỏ sót.
- Dòng còn ghi "can kiem tra" bị `danh_gia.py` bỏ qua.

## 4. Kết quả

Số chính thức do `src/danh_gia.py` ra (15/11/2026, commit `0c96ba2`, `phi4-mini` trên CPU; bảng gốc `docs/ket-qua/tuan5-lan4-hai-che-do.md` và `tuan5-lan5-do-som.md`). Đơn vị là phiên theo cột `Phien`. Bảng chính loại file đã dùng để chỉnh agent (Dumpert, SharpRDP, log máy Dũng); các file này ghi riêng. **Lưu ý:** lần đo 15/11 chỉ tách Dumpert (31 phiên). Số dưới đây đã tách thêm SharpRDP (2 phiên, đều bị bỏ sót, tính tay từ lần đo đó) và sẽ được đo lại chính thức ở lần đo 6.

| Việc đo | Không SLM | Có SLM |
|---|---|---|
| Đúng kỹ thuật, theo phiên (29 phiên) | **7 (24%)**, khoảng tin cậy xấp xỉ 12% đến 42% | **6 (21%)**, xấp xỉ 10% đến 38% |
| Kết luận sai mã | 0 | 0 |
| Bỏ sót (tổng) | 22 | 23 |
| Báo nhầm, 3 log chưa dùng chỉnh (3.290 phiên) | **19 (0,58%)**, xấp xỉ 0,37% đến 0,90% | **8 (0,24%)**, xấp xỉ 0,12% đến 0,48% |
| Báo nhầm, máy Thiên tuần 3 | 0/807 | 0/807 |
| Báo nhầm, máy Thiên tuần 4 | 4/1.704 (0,23%) | 2/1.704 |
| Báo nhầm, máy Khôi (máy lạ) | 15/779 (1,9%), xấp xỉ 1,2% đến 3,2% | 6/779 (0,8%) |
| Báo nhầm, máy Dũng (đã dùng chỉnh dấu vết, ghi riêng) | 10/2.573 (0,39%) | chưa đo |
| Độ sớm (trung vị, phiên đúng) | 2 sự kiện (7 phiên) | 2 sự kiện (6 phiên) |
| SLM lỗi | - | 0 |

Theo kỹ thuật (phiên tấn công, không SLM / có SLM): T1003.001 5/6 và 4/6, T1053.005 2/4 và 2/4, T1021.001 0/3, T1059.001 0/1, T1105 0/4, T1136.001 0/7, T1547.001 0/4 (cả hai chế độ), T1070.001 không có file.

Theo file (không SLM, không tính Dumpert và SharpRDP): 6/19 (32%). Bỏ thêm file `sysmon_local_account_creation` (6 phiên, nhãn từng phiên chưa đối chiếu): 7/23 phiên (30%).

**SLM chưa giúp.** Không lần nào SLM chọn "chưa xác nhận" (không lần nào nói hoạt động bình thường). Báo nhầm giảm từ 19 xuống 8 vì SLM chọn nhầm sang kỹ thuật thiếu dấu vết rồi bước kiểm chứng gạt đi (11 phiên bị chặn: 9 máy Khôi, 2 máy Thiên tuần 4); cùng cơ chế đó làm mất 1 phát hiện thật (`babyshark_mimikatz_powershell`), nên phát hiện đúng giảm từ 7 xuống 6. Chi tiết: `ke-hoach-nhat-ky/tuan-5.md`.

## 5. Hạn chế

- **Cỡ mẫu nhỏ:** 19 file (29 phiên) trong bảng chính, khoảng tin cậy rộng. T1070.001 không có file nào (không có mẫu Sysmon xóa log), T1059.001 chỉ 1 file, T1136.001 chỉ 2 file; ba kỹ thuật này chưa đủ để kết luận.
- **Nhãn do chúng tôi gán:** bằng cách đọc lệnh, chưa có người ngoài kiểm. Hai file `remote_file_copy` và `smbmap` (T1105) và file `sysmon_local_account_creation...` (T1136.001, 6 phiên chưa đối chiếu từng phiên) có độ chắc trung bình.
- **Đổi nhãn sau khi xem kết quả:** `babyshark_mimikatz_powershell` ban đầu xếp T1059.001, đổi sang T1003.001 sau khi xem kết quả agent. Vì vậy báo cả kết quả khi bỏ file này (28%).
- **File đã dùng khi phát triển:** Dumpert (đúng 1/1) và SharpRDP (đúng 0/2) được tách khỏi bảng chính. SharpRDP đã xác nhận có dùng: ký hiệu `SUA_REGISTRY:RunMRU` được thêm ở commit `05161fb` (28/10) và `tuan-3.md` ghi "phiên SharpRDP ra `SUA_REGISTRY:RunMRU`". Hai file khác cùng họ (`LM_sysmon_1_12_13_3_tsclient_SharpRdp`, `sharprdp_sysmon_7_mstscax.dll`) vẫn tính nhưng không hoàn toàn độc lập với file đã dùng chỉnh.
- **File rất ngắn:** nhiều file chỉ 1 đến 4 sự kiện hoặc chỉ sửa registry, chuỗi ký hiệu quá ngắn để khớp. Đây là một phần lớn lý do bỏ sót, và cũng là giới hạn của dữ liệu mẫu chứ không hẳn của mô hình.
- **Hai lỗi của thiết kế:** (1) `dau_vet.py` đòi Event 10 vào lsass nên bỏ sót ca `rdrleakdiag` (tiến trình tự dump); (2) gom phiên theo máy + LogonId + cây tiến trình có thể tách đôi một cuộc tấn công (ca SharpRDP: kết nối 3389 ở phiên khác với lệnh chạy).
- **Hai số đo khác nhau:** 64% (bỏ lần lượt từng file, chỉ so khớp chuỗi, dữ liệu Splunk) và 24% theo phiên (32% theo file; cả các bước, nguồn khác). Chỉ số thứ hai phản ánh agent trên log lạ.
- **Báo giả chỉ có một máy lạ** (máy Khôi; máy Thiên cùng máy với dữ liệu học lớp bình thường); máy Dũng đã dùng để chỉnh dấu vết; máy Thiên cùng máy với dữ liệu học lớp bình thường (log tuần 3 và 4 không trùng thời gian với log học).
- **SLM:** chỉ thử `phi4-mini` với một cách hỏi; kết luận "chưa giúp" áp dụng cho cách hỏi này, chưa phải cho mọi SLM hay cách hỏi (tuần 6: cho SLM biết kết quả bước 3 và cho phép trả lời bình thường). Máy Dũng chưa đo ở chế độ có SLM.
- **Một số file chạy bị antivirus chặn:** tên `Invoke-Mimikatz` bị chặn trên máy Thiên; phải chạy qua bản sao đổi tên. Nếu `danh_gia.py` lỗi Access denied ở dòng này thì bỏ dòng đó.
