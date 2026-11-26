# Dữ liệu

## 1. Nguồn dữ liệu

### 1.1 Log tấn công có nhãn

Theo đề cương (mục 5.2), log tấn công có nhãn lấy từ ba nguồn công khai:
- Splunk Attack Data — dùng để huấn luyện (học mẫu chuỗi ký hiệu cho 8 kỹ thuật).
- EVTX-ATTACK-SAMPLES — dùng làm bộ thử cố định (data/bo-thu.csv), giữ riêng, không đưa vào huấn luyện.
- OTRF Security Datasets — bổ sung thêm log mẫu cho một số kỹ thuật.

### 1.2 Log hoạt động bình thường

Thu từ máy của 3 thành viên nhóm, cài Sysmon và bật PowerShell Script Block Logging (cấu hình chung config/sysmonconfig-dacn.xml). Cả 3 máy bắt đầu thu cùng thời điểm, xuất log theo đợt (tuần) bằng Event Viewer:

| Máy | Bắt đầu thu | Đợt log dùng trong báo cáo |
|---|---|---|
| Thiên | 17/10/2026 08:58 | tuần 1 (đến 19/10), tuần 2 (đến 27/10), tuần 3 (đến 04/11), tuần 4 (05/11 đến 12/11) |
| Dũng | 17/10/2026 09:37 | đợt dùng để chỉnh dấu vết (đến 30/10, 2.573 phiên) |
| Khôi | 17/10/2026 00:09 | 7 ngày (31/10 đến 07/11, 779 phiên) — máy lạ, không dùng để học hay chỉnh |

Log bình thường dùng cho hai việc: học lớp "bình thường" và tỉ lệ gốc trong điểm số của bước so khớp chuỗi (xem chương Đánh giá, mục 3), và đo số lần agent báo nhầm trên log không chứa tấn công thật.

Máy lạ thứ hai (tuần 7, việc K5 của Khôi): laptop Windows của một người quen ngoài nhóm, Sysmon chạy từ tối 25/11/2026 (khoảng 22:45), cùng cấu hình sysmonconfig-dacn.xml, kênh log 1 GB, có bật Script Block Logging. Thu ít nhất 5 ngày, dự kiến xuất log khoảng 01/12/2026, chỉ dùng để đo báo nhầm ở lần đo cuối tuần 8, không dùng để học hay chỉnh.

## 2. Gán nhãn và sinh ký hiệu

Mỗi sự kiện Sysmon/PowerShell được code (src/ky_hieu.py) đổi thành một ký hiệu ngắn, ví dụ TAO_TIEN_TRINH:certutil.exe, MO_BO_NHO:lsass.exe:DOC_BO_NHO, SUA_REGISTRY:Run. Nhãn kỹ thuật gán theo cây tiến trình: gốc là tiến trình có sự kiện khớp dấu hiệu của kỹ thuật (bảng dấu vết bắt buộc ở mục 5 đề cương), chuỗi ký hiệu lấy từ các sự kiện thuộc cây đó. Danh sách file và nhãn lưu trong data/nhan-file.csv (cột Tep, KyThuat, SoSuKien, SoChuoi, DungHuanLuyen, GhiChu).

## 3. Dữ liệu huấn luyện (models/mau_chuoi.json)

Từ 64 file Splunk Attack Data có nhãn, 45 file cho ra chuỗi dùng được, tổng 292 chuỗi, còn 128 chuỗi sau khi bỏ chuỗi trùng nhau trong cùng một file.

| Kỹ thuật | File | Chuỗi |
|---|---|---|
| T1003.001 | 3 | 15 |
| T1021.001 | 8 | 11 |
| T1053.005 | 7 | 15 |
| T1059.001 | 16 | 54 |
| T1070.001 | 2 | 3 |
| T1105 | 5 | 14 |
| T1136.001 | 1 | 3 |
| T1547.001 | 3 | 13 |

Hai kỹ thuật T1070.001 và T1136.001 chỉ có 2-3 chuỗi huấn luyện, nên số đo liên quan đến hai kỹ thuật này (xem chương Đánh giá) chưa đáng tin.

## 4. Bộ thử cố định (data/bo-thu.csv)

Giữ tách biệt hoàn toàn khỏi dữ liệu huấn luyện, chỉ dùng để theo dõi tiến độ trong lúc còn chỉnh code; số chính thức cuối cùng của đồ án sẽ đo một lần duy nhất ở tuần 8 sau khi chốt cấu hình. Gồm 21 file chấm điểm từ EVTX-ATTACK-SAMPLES, sau khi tách Dumpert (tuần 5) còn 31, tuần 6 tách SharpRDP còn 29.

Dumpert dùng để chạy thử và sửa code tuần 4-5; SharpRDP dùng để thiết kế ký hiệu RunMRU ngày 28/10. Từ tuần 6 trở đi, 29 phiên là mẫu số dùng xuyên suốt các lần đo.

Log bình thường đi kèm: 3.290 phiên (Thiên tuần 3, tuần 4, Khôi 7 ngày). Log Dũng hiện không tính được ở các lần đo từ 20/11 trở đi do lỗi lệch số thứ tự phiên (gom được 353 phiên nhưng bo-thu.csv ghi SoPhien=2.573 từ file cũ) — đang chờ gán nhãn lại.

Nhãn gán bằng cách đọc lệnh và sự kiện thật trong từng file, không lấy từ kết quả của agent.

## 5. Bộ phát triển (data/bo-phat-trien*.csv, tuần 6-7)

Vì không được đụng vào bộ thử khi còn đang chỉnh code, nhóm dựng thêm dữ liệu tấn công riêng trên máy ảo DACN-LAB (Windows 11 Enterprise LTSC, Sysmon 15.22, cấu hình config/sysmonconfig-dacn.xml) để thử các thay đổi mà không làm bộ thử "hết mù".

- Tuần 6 (T2, bộ phát triển chính): 21 test hợp lệ từ Atomic Red Team (T1136.001 x4, T1547.001 x5, T1053.005 x5, T1059.001 x4, T1105 x3). Phát hiện một lỗi phương pháp: Invoke-AtomicTest tự thêm tiến trình con hostname.exe > whoami.exe ở đầu mọi phiên, làm điểm bước so khớp chuỗi luôn cao giả tạo; đã lọc bỏ hai sự kiện này khỏi bản sao log để có bản đo trung thực (data/bo-phat-trien-khong-tien-to.csv).
- Tuần 6 (T3, phía phát hiện): thêm 14 lệnh gõ thủ công, không qua Atomic Red Team, trên máy ảo (data/bo-phat-trien-don-le.csv, chi tiết lệnh ở data/bo-phat-trien-don-le-log.csv): nhóm Startup (A1-A3), khóa Run (B1-B4), tác vụ hẹn giờ (C1-C3), tạo tài khoản (D1-D3), kết nối RDP loopback (E1). Dùng để so sánh lệnh gọi trực tiếp công cụ hệ thống (reg.exe, schtasks.exe, net.exe) với lệnh bọc qua cmdlet PowerShell (kết quả ở chương Đánh giá).
- Tuần 7 (T2): thêm 24 lệnh gõ thủ công khác trên 8 kỹ thuật (data/phien-ngan-log.csv), nhằm thử huấn luyện lại mô hình với các phiên ngắn, đơn giản hơn.

Kiểm chứng lại ngày 26/11: 5 trong 24 lệnh của tuần 7 ban đầu ghi "0 chuỗi huấn luyện" với lý do "Sysmon không ghi nhận" — lý do này sai, đã kiểm tra lại trực tiếp. Cả 5 trường hợp (tạo user qua ADSI/.NET AccountManagement, Invoke-WebRequest, Start-BitsTransfer, Test-NetConnection tới cổng 3389) đều vẫn sinh một vài sự kiện Sysmon (ví dụ Invoke-WebRequest sinh đúng 1 sự kiện Event 3 kết nối mạng, đã kiểm tra lại và xác nhận). Khi quét lại 5 file này bằng agent, tất cả đều dừng ở bước so khớp chuỗi (điểm quá thấp, không khớp mẫu) chứ không phải "0 sự kiện". Nguyên nhân thật: các cách gọi thay thế này (cmdlet PowerShell, gọi API .NET/ADSI trực tiếp, dịch vụ BITS chạy nền) không để lại tên tiến trình/câu lệnh đặc trưng mà train.py và mẫu chuỗi đang dựa vào để gán nhãn và so khớp (không có net user ... /add, không có mstsc.exe, không có tên công cụ tải file quen thuộc) — cùng loại hạn chế đã nêu ở mục 7 dưới đây (ký hiệu phụ thuộc tên tiến trình), không phải điểm mù hoàn toàn của Sysmon.

## 6. Log chuỗi tấn công T1 dùng để thử ghép chuỗi (K2, việc của Khôi)

Log chuỗi tấn công T1 (tuan7-t1-chuoi-tan-cong.evtx) được Khôi dùng thêm để thử src/chuoi_tan_cong.py — code nối các KẾT LUẬN cùng máy thành chuỗi tấn công theo giai đoạn (xâm nhập, thực thi, bám trụ, đánh cắp đăng nhập, lan rộng, xóa dấu vết). Log này chỉ dùng để thử tính năng ghép chuỗi, không dùng để huấn luyện hay chỉnh agent. Kết quả ghép chuỗi trình bày ở chương Đánh giá, mục "Chuỗi tấn công".

## 7. Hạn chế của dữ liệu

- Ký hiệu không mang nội dung dòng lệnh, chỉ mang tên hành động + tên tiến trình/tài nguyên — hai lệnh khác nhau cùng loại hành động nhưng khác tham số (ví dụ net user /add so với net use) có thể không phân biệt được nếu cùng tên tiến trình.
- Hai kỹ thuật T1070.001, T1136.001 có rất ít chuỗi huấn luyện (2-3 chuỗi), số đo liên quan chưa đáng tin.
- Lớp "bình thường" hiện học từ một máy (Thiên); log của Dũng đã dùng để chỉnh dấu vết bắt buộc nên không còn là dữ liệu "mù" khi đo báo nhầm trên máy này.
- Bộ phát triển tuần 6 dựng bằng Atomic Red Team có đặc điểm (tiến trình con tự động, 6/27 test bị Windows Defender chặn) khác với tấn công thật; không dùng bộ này để báo cáo hiệu năng cuối, chỉ dùng để chỉnh.
- Một số nhãn trong bộ thử còn đáng nghi (createdump_windows-sysmon.log, sysmon_soaphound.log), ghi chú riêng trong data/bo-thu.csv.