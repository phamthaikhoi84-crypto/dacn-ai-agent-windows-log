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

- **Đúng kỹ thuật (file tấn công):** agent kết luận (qua đủ 5 bước, điểm ≥ 0,5) đúng kỹ thuật nhãn ở ít nhất một phiên trong cột `Phien`. Tỉ lệ = số file đúng / số file chấm điểm, kèm khoảng tin cậy Wilson 95%.
- **Bỏ sót:** không phiên nào trong `Phien` bị kết luận đúng kỹ thuật (gồm cả "chưa xác nhận" và kết luận sai kỹ thuật).
- **Báo giả (log bình thường):** số phiên bị kết luận là có tấn công / tổng số phiên. Chỉ tính trên log bình thường.
- **Độ sớm:** số sự kiện tính từ sự kiện đầu tiên của phiên đến sự kiện mà agent đưa ra kết luận (đoạn khớp đủ điểm và đủ dấu vết). Ví dụ phiên có 12 sự kiện, kết luận khi đã thấy 5 sự kiện đầu thì độ sớm là 5. Số nhỏ là sớm. Báo cáo trung vị và khoảng của độ sớm trên các phiên đúng, không tính phiên bỏ sót.
- Dòng còn ghi "can kiem tra" bị `danh_gia.py` bỏ qua.

## 4. Kết quả

| Việc đo | Kết quả |
|---|---|
| Đúng kỹ thuật trên 21 file | 7/21 (33%, khoảng tin cậy xấp xỉ 17% đến 55%) |
| Bỏ file demo (04, 07) | 6/19 (32%) |
| Bỏ thêm file 15 (nhãn đổi) | 5/18 (28%) |
| Báo giả, máy Thiên tuần 3 | 0/807 |
| Báo giả, máy Thiên tuần 4 | 4/1.704 (0,23%) |
| Báo giả, máy Dũng (đã dùng để chỉnh dấu vết) | 10/2.573 (0,39%) |
| Báo giả, máy Khôi (máy lạ, đo trước khi sửa bước 4) | 15/779 (1,9%; khoảng tin cậy xấp xỉ 1,2% đến 3,2%) |
| Độ sớm | [ĐIỀN: sau khi `danh_gia.py` chạy xong] |

Theo kỹ thuật: T1003.001 5/6, T1053.005 2/2, T1021.001 0/3, T1059.001 0/1, T1105 0/3, T1136.001 0/2, T1547.001 0/4, T1070.001 không có file.

## 5. Hạn chế

- **Cỡ mẫu nhỏ:** 21 file, khoảng tin cậy rộng. T1070.001 không có file nào (không có mẫu Sysmon xóa log), T1059.001 chỉ 1 file, T1136.001 chỉ 2 file; ba kỹ thuật này chưa đủ để kết luận.
- **Nhãn do chúng tôi gán:** bằng cách đọc lệnh, chưa có người ngoài kiểm. Hai file `remote_file_copy` và `smbmap` (T1105) và file `sysmon_local_account_creation...` (T1136.001, 6 phiên chưa đối chiếu từng phiên) có độ chắc trung bình.
- **Đổi nhãn sau khi xem kết quả:** `babyshark_mimikatz_powershell` ban đầu xếp T1059.001, đổi sang T1003.001 sau khi xem kết quả agent. Vì vậy báo cả kết quả khi bỏ file này (28%).
- **File đã dùng khi phát triển/demo:** 04 và 07; kết quả bỏ hai file này ở mục 4.
- **File rất ngắn:** nhiều file chỉ 1 đến 4 sự kiện hoặc chỉ sửa registry, chuỗi ký hiệu quá ngắn để khớp. Đây là một phần lớn lý do bỏ sót, và cũng là giới hạn của dữ liệu mẫu chứ không hẳn của mô hình.
- **Hai lỗi của thiết kế:** (1) `dau_vet.py` đòi Event 10 vào lsass nên bỏ sót ca `rdrleakdiag` (tiến trình tự dump); (2) gom phiên theo máy + LogonId + cây tiến trình có thể tách đôi một cuộc tấn công (ca SharpRDP: kết nối 3389 ở phiên khác với lệnh chạy).
- **Hai số đo khác nhau:** 64% (bỏ lần lượt từng file, chỉ so khớp chuỗi, dữ liệu Splunk) và 33% (cả 5 bước, nguồn khác). Chỉ số thứ hai phản ánh agent trên log lạ.
- **Báo giả chỉ có một máy lạ** (máy Khôi), đo trước khi sửa bước 4; máy Dũng đã dùng để chỉnh dấu vết; máy Thiên cùng máy với dữ liệu học lớp bình thường (log tuần 3 và 4 không trùng thời gian với log học).
- **Chưa có mô hình ngôn ngữ trong các số đo tấn công:** chạy bản `--ban-tam`; phép thử phi4-mini trên máy Khôi chưa cho thấy bước 4 giúp loại báo giả.
- **Một số file chạy bị antivirus chặn:** tên `Invoke-Mimikatz` bị chặn trên máy Thiên; phải chạy qua bản sao đổi tên. Nếu `danh_gia.py` lỗi Access denied ở dòng này thì bỏ dòng đó.
