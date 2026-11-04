\# Tuần 3 (26/10 – 31/10/2026)



Buổi báo cáo 31/10 không diễn ra (thầy bận), báo cáo gộp với tuần 4 vào Chủ nhật 08/11/2026.



\## Mục tiêu (theo góp ý buổi 24/10)



1\. Demo đầy đủ: xem được code agent, vòng lặp agent và phần train.

2\. Trả lời được câu hỏi 99,99% log là bình thường: agent xử lý thế nào, đo báo động nhầm trên log bình thường thật.



\*\*Sản phẩm demo:\*\* chạy agent trên 1 file tấn công không dùng khi train và 1 đoạn log bình thường; agent in từng bước, kết luận đúng kỹ thuật với file tấn công, không báo động với log bình thường.



\## Vòng lặp agent (5 bước)



| Bước | Việc | File |

|---|---|---|

| 1 | Nhận sự kiện, gom vào phiên (máy + LogonId + cây tiến trình + thời gian) | `gom\_phien.py` |

| 2 | Lọc sự kiện, đổi sang chuỗi ký hiệu, so khớp với mẫu đã train, lấy tối đa 3 kỹ thuật ứng viên có điểm ≥ ngưỡng (0,5) | `ky\_hieu.py`, `train.py` |

| 3 | Tìm dấu vết bắt buộc của từng ứng viên bằng truy vấn DuckDB | `dau\_vet.py` |

| 4 | Gửi dòng log + danh sách ứng viên cho mô hình ngôn ngữ (Ollama) chọn 1 kỹ thuật, kèm bằng chứng | `slm.py` |

| 5 | Kiểm chứng: kỹ thuật được chọn phải nằm trong danh sách ứng viên VÀ đủ dấu vết bắt buộc. Đạt thì kết luận; không đạt thì ghi "chưa xác nhận", không kết luận bừa | `agent.py` |



\## Kế hoạch và kết quả



| Người | Việc | Kết quả | File |

|---|---|---|---|

| Khôi | Tách `chuoi\_hanh\_vi.py` thành module | Xong. Kiểm chứng: cả 8 phiên ra kết quả giống hệt tuần 2 | \[src/doc\_log.py](../src/doc\_log.py), \[src/gom\_phien.py](../src/gom\_phien.py), \[src/ky\_hieu.py](../src/ky\_hieu.py) |

| Khôi | Tách ký hiệu registry theo loại khóa | Xong. Phiên SharpRDP ra `SUA\_REGISTRY:RunMRU` | \[src/ky\_hieu.py](../src/ky\_hieu.py) |

| Khôi | Bộ lọc sự kiện dùng chung + phân loại quyền Event 10 | Xong. `MO\_BO\_NHO:lsass.exe:DAY\_DU / DOC\_BO\_NHO / TRUY\_VAN`, khớp với mô hình đã train | \[src/ky\_hieu.py](../src/ky\_hieu.py) |

| Khôi | Dấu vết bắt buộc của 8 kỹ thuật (truy vấn DuckDB) | Xong. File Dumpert: T1003.001 đủ dấu vết; file comsvcs: thiếu | \[src/dau\_vet.py](../src/dau\_vet.py) |

| Khôi | Vòng lặp agent 5 bước | Xong. Chạy từ đầu đến cuối với SLM thật; có `--ban-tam` để đo và dự phòng | \[src/agent.py](../src/agent.py) |

| Thiên | Đọc log XML Splunk ra đúng 14 cột | Xong | \[src/doc\_log.py](../src/doc\_log.py) |

| Thiên | Gắn nhãn 8 kỹ thuật tầng sâu | Xong. 65 file; gắn nhãn theo cây con của tiến trình có lệnh khớp dấu hiệu | \[data/nhan-file.csv](../data/nhan-file.csv), \[src/gan\_nhan.py](../src/gan\_nhan.py) |

| Thiên | Train chuỗi mẫu + bảng "sau A thường là B" | Xong mô hình. Bảng tỷ lệ đúng: (điền) | \[src/train.py](../src/train.py), \[models/mau\_chuoi.json](../models/mau\_chuoi.json) |

| Thiên | Kiểm tra `dau\_vet.py` trên log Splunk + đo báo động nhầm trên log bình thường | Xong. Góp ý 4 điểm đã sửa; báo động nhầm 46 → 10 phiên | |

| Dũng | `slm.py` gọi Ollama, trả JSON | Chạy được với `llama3.2:3b`, ghép vào agent. Còn: phần giải thích sai, chưa chốt model | \[src/slm.py](../src/slm.py), \[src/kiem\_thu\_slm\_lsass.py](../src/kiem\_thu\_slm\_lsass.py) |

| Dũng | Đoạn log bình thường cho demo | Xong. 500 sự kiện, 16 phiên, 0 kết luận tấn công, chạy 2,5 giây | `demo\_nho.evtx` (không đưa lên GitHub) |

| Dũng | Log bình thường "khó", bộ log công khai, câu trả lời 99,99% | (điền) | |



\## Kết quả chạy agent



Lệnh: `python src\\agent.py D:\\DoAnChuyenNganh\\log` (3 file EVTX, 59 sự kiện, 8 phiên)



| Phiên | Bước 2 (khớp chuỗi) | Bước 3 (dấu vết) | Kết quả |

|---|---|---|---|

| 8 – Dumpert | T1003.001, điểm 0,978 | Đủ | \*\*KẾT LUẬN T1003.001\*\*, bằng chứng 3/3 có thật trong log, dự đoán bước tiếp theo `TAO\_FILE:\*.dmp` |

| 1 – comsvcs | T1547.001, điểm 0,953 (đoán sai) | Thiếu | \*\*Chưa xác nhận\*\*: bước 3 bắt được lỗi của bước 2 (dump `notepad.exe`, không chạm lsass, không có khóa Run) |

| 3 – SharpRDP | T1059.001, điểm 0,583 | Thiếu | \*\*Chưa xác nhận\*\* |

| 5 phiên còn lại | dưới ngưỡng | – | Bình thường, dừng ở bước 2 |



(Chèn ảnh: `docs/hinh/tuan3-agent-dumpert.png`, `docs/hinh/tuan3-agent-comsvcs.png`, `docs/hinh/tuan3-agent-binh-thuong.png`)



\## Log bình thường (câu hỏi 99,99%)



Đo trên toàn bộ log bình thường của Dũng: 2.573 phiên, 261 MB, chạy với `--ban-tam`.



| | Trước khi sửa | Sau khi sửa |

|---|---|---|

| Kết luận tấn công (báo nhầm) | 46 phiên (1,79%) | \*\*10 phiên (0,39%)\*\* |

| Chưa xác nhận | 45 | 81 |



Các sửa đổi: chỉ xét ứng viên đạt ngưỡng ở bước 3–5; T1053.005 chỉ dùng lệnh tạo tác vụ (bỏ file Tasks vì Defender, Lenovo ghi liên tục); T1003.001 loại `wininit.exe`, `csrss.exe` trong System32 lúc khởi động.



10 phiên còn lại đều là hoạt động hợp lệ tạo đúng dấu vết: 4 T1547.001 (trình duyệt, `runonce.exe` ghi khóa Run), 4 T1059.001 (PowerShell của bộ cài với `-ExecutionPolicy Bypass`), 2 T1053.005 (Office tạo tác vụ cập nhật). Nhóm \*\*không\*\* thêm danh sách ngoại lệ theo tên, vì kẻ tấn công thường giả tên tác vụ Microsoft (T1036).



\## Quyết định thiết kế



1\. \*\*Lọc sự kiện dùng chung\*\* (`ky\_hieu.loc\_su\_kien`): chỉ giữ Event 1, 3, 11, 12, 13, 14 và Event 10 vào lsass. Log Splunk ghi nhiều loại sự kiện mà cấu hình Sysmon phổ biến không ghi; train và agent dùng cùng một bộ lọc để không lệch nhau.

2\. \*\*Quyền Event 10 chia 3 loại\*\* theo bit `PROCESS\_VM\_READ` (0x10): phần mềm bình thường (Defender) mở lsass rất thường xuyên nhưng chỉ để truy vấn; muốn đọc mật khẩu thì bắt buộc phải có quyền đọc bộ nhớ.

3\. \*\*Dấu vết bắt buộc là điều kiện cần, không phải điều kiện đủ:\*\* thiếu thì không kết luận; có đủ chưa chắc là tấn công.

4\. \*\*Không tin lời giải thích của mô hình ngôn ngữ:\*\* bước 5 kiểm chứng bằng DuckDB. Ví dụ thật: `llama3.2:3b` chọn đúng T1003.001 nhưng giải thích sai rằng không có quyền đọc bộ nhớ (dù quyền là 0x1fffff).



\## Chỗ đang vướng / hạn chế



1\. Một vụ tấn công bị chia thành nhiều phiên: SharpRDP có dấu vết RDP (cổng 3389) ở phiên 2 nhưng hành vi ở phiên 3, nên agent chỉ ghi "chưa xác nhận".

2\. `SUA\_REGISTRY:RunMRU` không có trong dữ liệu train.

3\. Dữ liệu train T1003.001 có công cụ Outflank-Dumpert; file demo không nằm trong dữ liệu train nhưng công cụ trùng.

4\. Con số 0,39% đo trên chính log đã dùng để điều chỉnh; cần đo thêm trên log bình thường khác.

5\. Mô hình 3B giải thích sai ý nghĩa giá trị quyền; JSON đôi khi bị cắt.

6\. Bước 4 chỉ gửi 40 dòng log đầu khi phiên dài.

7\. Chưa thêm Security log (4624, 4688, 4720, 1102) như dự kiến tuần 2.



\## Câu hỏi cho thầy



1\. Hoạt động hợp lệ (bộ cài, ứng dụng) tạo đúng dấu vết tấn công: nên xử lý bằng danh sách trắng (theo chữ ký, đường dẫn, tiến trình cha) hay học thêm từ log bình thường?

2\. Một vụ tấn công RDP bị chia thành nhiều phiên: có nên nối các phiên cùng máy trong khoảng thời gian gần nhau không?

3\. Dữ liệu công khai cho T1003.001 trùng công cụ với file demo: cách chia train/thử như vậy có chấp nhận được không?



\## Chuyển sang tuần 4



\- Thiên: bảng tỷ lệ đoán đúng kỹ thuật và bước tiếp theo của `train.py`; đo báo nhầm trên log bình thường khác; chạy SLM thật trên 10 phiên báo nhầm.

\- Dũng: sửa prompt `slm.py`, chốt model trong `models.md`, (các mục chưa xong).

\- Khôi: chế độ phát lại `--phat-lai` cho demo.



\## Nội dung buổi báo cáo 08/11/2026 (điền sau buổi)



\- Câu hỏi / góp ý của thầy:

\- Cách giải quyết:

