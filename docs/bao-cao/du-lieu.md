# Dữ liệu



Phần của Thiên — chương báo cáo, viết lại từ `docs/ket-qua-huan-luyen.md` (mục 1, 5, 6d, 9) và `docs/log-binh-thuong.md`.



## 1. Nguồn dữ liệu



### 1.1 Log tấn công có nhãn



Theo đề cương (mục 5.2), log tấn công có nhãn lấy từ ba nguồn công khai:

- **Splunk Attack Data** — dùng để huấn luyện (học mẫu chuỗi ký hiệu cho 8 kỹ thuật).

- **EVTX-ATTACK-SAMPLES** — dùng làm bộ thử cố định (`data/bo-thu.csv`), giữ riêng, không đưa vào huấn luyện.

- **OTRF Security Datasets** — bổ sung thêm log mẫu cho một số kỹ thuật.



### 1.2 Log hoạt động bình thường



Thu từ máy của 3 thành viên (Thiên, Dũng, Khôi), mỗi máy 2-3 tuần sử dụng hằng ngày, cài Sysmon và bật PowerShell Script Block Logging, xuất bằng Event Viewer. Dùng cho hai việc: học lớp "bình thường" và tỉ lệ gốc trong điểm số của bước so khớp chuỗi (xem chương Đánh giá, mục 3), và đo số lần agent báo nhầm trên log không chứa tấn công thật.



## 2. Gán nhãn và sinh ký hiệu



Mỗi sự kiện Sysmon/PowerShell được code (`src/ky_hieu.py`) đổi thành một ký hiệu ngắn, ví dụ `TAO_TIEN_TRINH:certutil.exe`, `MO_BO_NHO:lsass.exe:DOC_BO_NHO`, `SUA_REGISTRY:Run`. Nhãn kỹ thuật gán theo cây tiến trình: gốc là tiến trình có sự kiện khớp dấu hiệu của kỹ thuật (bảng dấu vết bắt buộc ở mục 5 đề cương), chuỗi ký hiệu lấy từ các sự kiện thuộc cây đó. Danh sách file và nhãn lưu trong `data/nhan-file.csv` (cột `Tep, KyThuat, SoSuKien, SoChuoi, DungHuanLuyen, GhiChu`).



## 3. Dữ liệu huấn luyện (`models/mau_chuoi.json`)



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



## 4. Bộ thử cố định (`data/bo-thu.csv`)



Giữ tách biệt hoàn toàn khỏi dữ liệu huấn luyện, dùng một lần để báo cáo số liệu cuối, không dùng để chỉnh code hay chọn ngưỡng. Gồm 21 file chấm điểm từ EVTX-ATTACK-SAMPLES (31 phiên có nhãn, sau khi tách 2 file từng dùng khi phát triển — Dumpert và SharpRDP — còn 29 phiên) và 3 log bình thường chưa dùng chỉnh (Thiên tuần 3, tuần 4, Khôi; tổng 3.290 phiên). Nhãn gán bằng cách đọc lệnh và sự kiện thật trong từng file, không lấy từ kết quả của agent.



## 5. Bộ phát triển (`data/bo-phat-trien*.csv`, tuần 6-7)



Vì không được đụng vào bộ thử khi còn đang chỉnh code, nhóm dựng thêm một bộ dữ liệu tấn công riêng trên máy ảo `DACN-LAB` (Windows 11 Enterprise LTSC, Sysmon 15.22, cấu hình `config/sysmonconfig-dacn.xml`) để thử các thay đổi mà không làm bộ thử "hết mù".



- **Tuần 6:** 21 test hợp lệ từ Atomic Red Team (T1136.001 ×4, T1547.001 ×5, T1053.005 ×5, T1059.001 ×4, T1105 ×3). Phát hiện một lỗi phương pháp: `Invoke-AtomicTest` tự thêm tiến trình con `hostname.exe > whoami.exe` ở đầu mọi phiên, làm điểm bước so khớp chuỗi luôn cao giả tạo; đã lọc bỏ hai sự kiện này khỏi bản sao log để có bản đo trung thực (`data/bo-phat-trien-khong-tien-to.csv`).

- **Tuần 7:** thêm 24 lệnh gõ thủ công (không qua Atomic Red Team) trên 8 kỹ thuật (`data/phien-ngan-log.csv`), nhằm thử huấn luyện lại mô hình với các phiên ngắn, đơn giản hơn. Trong 24 lệnh, 5 lệnh không sinh được ký hiệu nào vì Sysmon không ghi nhận các hành động không tạo tiến trình mới (`New-LocalUser`, tạo user qua ADSI/.NET, `Invoke-WebRequest`, `Start-BitsTransfer` chạy nền) — đây là điểm mù đã biết của Sysmon, ghi lại ở `data/nhan-file-v2.csv`.



Kết quả huấn luyện thử với dữ liệu mở rộng này (mô hình "bản 2", `models/mau_chuoi_v2.json`) và lý do không áp dụng được trình bày ở chương Đánh giá, mục 6.



## 6. Hạn chế của dữ liệu



- Ký hiệu không mang nội dung dòng lệnh, chỉ mang tên hành động + tên tiến trình/tài nguyên — hai lệnh khác nhau cùng loại hành động nhưng khác tham số (ví dụ `net user /add` so với `net use`) có thể không phân biệt được nếu cùng tên tiến trình.

- Hai kỹ thuật T1070.001, T1136.001 có rất ít chuỗi huấn luyện (2-3 chuỗi), số đo liên quan chưa đáng tin.

- Lớp "bình thường" hiện học từ một máy (Thiên); log của Dũng đã dùng để chỉnh dấu vết bắt buộc nên không còn là dữ liệu "mù" khi đo báo nhầm trên máy này.

- Bộ phát triển tuần 6 dựng bằng Atomic Red Team có đặc điểm (tiến trình con tự động, 6/27 test bị Windows Defender chặn) khác với tấn công thật; không dùng bộ này để báo cáo hiệu năng cuối, chỉ dùng để chỉnh.

- Một số nhãn trong bộ thử còn đáng nghi (`createdump_windows-sysmon.log`, `sysmon_soaphound.log`), ghi chú riêng trong `data/bo-thu.csv`.

