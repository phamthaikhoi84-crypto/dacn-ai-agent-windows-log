# Đánh giá agent

Phần của Thiên. Số liệu chi tiết ở `docs/ket-qua-huan-luyen.md`; bộ thử ở `data/bo-thu.csv`. Mô hình đóng băng: `models/mau_chuoi.json` (không huấn luyện lại sau khi bộ thử được tạo).

## 1. Câu hỏi đánh giá

1. Khi gặp tấn công **ngoài tập huấn luyện**, agent kết luận đúng kỹ thuật bao nhiêu lần?
2. Khi gặp log **bình thường**, agent kết luận tấn công nhầm bao nhiêu lần?
3. Agent kết luận **sớm** đến mức nào?

## 2. Bộ thử

`data/bo-thu.csv`, cột `Tep, KyThuat, Phien, Nhan, Nguon, SoPhien, GhiChu`.

- **Tấn công:** 21 file chấm điểm từ EVTX-ATTACK-SAMPLES, không file nào dùng để huấn luyện (huấn luyện dùng Splunk Attack Data), trừ hai file đã dùng khi phát triển/demo là `sysmon_10_11_outlfank_dumpert_and_andrewspecial_memdump` và `LM_sysmon_3_12_13_1_SharpRDP`. Thêm 1 file (`sysmon_10_1_memdump_comsvcs_minidump`, đích là notepad chứ không phải lsass) đánh dấu "can kiem tra" và không tính.
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

Số chính thức do `src/danh_gia.py` ra (15/11/2026, commit `8c43445`, không SLM, 2.961 giây). Đơn vị là phiên theo cột `Phien`. Bảng chính loại file đã dùng để chỉnh agent (Dumpert, log máy Dũng); các file này ghi riêng.

| Việc đo | Kết quả |
|---|---|
| Đúng kỹ thuật, theo phiên | **7/31 (23%, khoảng tin cậy xấp xỉ 11% đến 40%)** |
| Đúng kỹ thuật, theo file | 7/21 (33%) gồm Dumpert; 6/20 không tính Dumpert |
| Bỏ file `sysmon_local_account_creation` (6 phiên, nhãn từng phiên chưa đối chiếu) | 7/25 (28%) |
| Kết luận sai mã | 0 |
| Bỏ sót | 18 phiên dừng ở bước 2, 6 phiên chưa xác nhận (bước 3) |
| Báo giả, máy Thiên tuần 3 | 0/807 |
| Báo giả, máy Thiên tuần 4 | 4/1.704 (0,23%) |
| Báo giả, hai tuần máy Thiên gộp | 4/2.511 (0,16%; khoảng tin cậy xấp xỉ 0,08% đến 0,4%) |
| Báo giả, máy Dũng (đã dùng để chỉnh dấu vết, ghi riêng) | 10/2.573 (0,39%) |
| Báo giả, máy Khôi, không SLM (máy lạ) | 15/779 (1,9%; khoảng tin cậy xấp xỉ 1,2% đến 3,2%) |
| Báo giả, máy Khôi, có SLM phi4-mini (sau khi sửa bước 4) | 6/779 (0,8%; khoảng tin cậy xấp xỉ 0,4% đến 1,7%); SLM chặn 9 phiên, 0 lỗi |
| Độ sớm (trung vị, phiên đúng) | 2 sự kiện (7 phiên) |

Theo kỹ thuật (phiên tấn công): T1003.001 5/6, T1053.005 2/4, T1021.001 0/5, T1059.001 0/1, T1105 0/4, T1136.001 0/7, T1547.001 0/4, T1070.001 không có file.

Số máy Khôi lấy từ lần chạy của Khôi (`docs/ket-qua/tuan5-lan2-bang.md`, commit `a118d22`); `danh_gia.py` ở máy Thiên không có file log của Khôi. Chưa chạy chế độ có SLM trên bộ thử tấn công.

## 5. Hạn chế

- **Cỡ mẫu nhỏ:** 21 file (31 phiên), khoảng tin cậy rộng. T1070.001 không có file nào (không có mẫu Sysmon xóa log), T1059.001 chỉ 1 file, T1136.001 chỉ 2 file; ba kỹ thuật này chưa đủ để kết luận.
- **Nhãn do chúng tôi gán:** bằng cách đọc lệnh, chưa có người ngoài kiểm. Hai file `remote_file_copy` và `smbmap` (T1105) và file `sysmon_local_account_creation...` (T1136.001, 6 phiên chưa đối chiếu từng phiên) có độ chắc trung bình.
- **Đổi nhãn sau khi xem kết quả:** `babyshark_mimikatz_powershell` ban đầu xếp T1059.001, đổi sang T1003.001 sau khi xem kết quả agent. Vì vậy báo cả kết quả khi bỏ file này (28%).
- **File đã dùng khi phát triển/demo:** 04 (Dumpert, được `danh_gia.py` loại khỏi bảng chính, đúng 1/1) và 07 (SharpRDP, vẫn tính, đúng 0/2).
- **File rất ngắn:** nhiều file chỉ 1 đến 4 sự kiện hoặc chỉ sửa registry, chuỗi ký hiệu quá ngắn để khớp. Đây là một phần lớn lý do bỏ sót, và cũng là giới hạn của dữ liệu mẫu chứ không hẳn của mô hình.
- **Hai lỗi của thiết kế:** (1) `dau_vet.py` đòi Event 10 vào lsass nên bỏ sót ca `rdrleakdiag` (tiến trình tự dump); (2) gom phiên theo máy + LogonId + cây tiến trình có thể tách đôi một cuộc tấn công (ca SharpRDP: kết nối 3389 ở phiên khác với lệnh chạy).
- **Hai số đo khác nhau:** 64% (bỏ lần lượt từng file, chỉ so khớp chuỗi, dữ liệu Splunk) và 23% theo phiên (33% theo file; cả các bước, nguồn khác). Chỉ số thứ hai phản ánh agent trên log lạ.
- **Báo giả chỉ có một máy lạ** (máy Khôi); máy Dũng đã dùng để chỉnh dấu vết; máy Thiên cùng máy với dữ liệu học lớp bình thường (log tuần 3 và 4 không trùng thời gian với log học).
- **Chưa đo SLM trên tấn công:** số tấn công ở trên là chế độ không SLM. SLM chỉ mới đo trên log bình thường của máy Khôi (giảm báo giả từ 15 xuống 6 trên 779 phiên); chưa biết SLM có làm mất phát hiện đúng hay không.
- **Một số file chạy bị antivirus chặn:** tên `Invoke-Mimikatz` bị chặn trên máy Thiên; phải chạy qua bản sao đổi tên. Nếu `danh_gia.py` lỗi Access denied ở dòng này thì bỏ dòng đó.
