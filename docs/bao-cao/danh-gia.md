# Đánh giá



Phần của Thiên — chương báo cáo, viết lại và mở rộng từ `docs/danh-gia.md` và `docs/ket-qua-huan-luyen.md` (mục 6b-9), cập nhật đến tuần 7. Mô hình chính thức dùng để đo: `models/mau_chuoi.json`, đóng băng từ khi bộ thử cố định được tạo.



## 1. Câu hỏi đánh giá



1. Khi gặp tấn công ngoài tập huấn luyện, agent kết luận đúng kỹ thuật bao nhiêu lần?

2. Khi gặp log bình thường, agent kết luận tấn công nhầm bao nhiêu lần?

3. Agent kết luận sớm đến mức nào?

4. Mô hình ngôn ngữ nhỏ (SLM) có giúp cải thiện hai câu hỏi đầu không?



## 2. Phương pháp đo



**Bộ thử:** `data/bo-thu.csv` (xem chương Dữ liệu, mục 4): 21 file tấn công (29 phiên có nhãn, đã tách 2 file dùng khi phát triển) và 3 log bình thường chưa dùng chỉnh (3.290 phiên).



**Cách tính:**

- **Đúng kỹ thuật:** phiên có nhãn được agent kết luận (điểm ≥ ngưỡng 0,5, đủ dấu vết bắt buộc) đúng mã kỹ thuật. Kết luận sai mã tính riêng.

- **Bỏ sót:** phiên có nhãn không được kết luận đúng — dừng ở bước so khớp chuỗi (điểm dưới ngưỡng), "chưa xác nhận" (thiếu dấu vết hoặc SLM chặn), hoặc SLM lỗi.

- **Báo nhầm:** số phiên log bình thường bị kết luận có tấn công / tổng số phiên.

- **Độ sớm:** số sự kiện từ đầu phiên đến lúc agent đủ điểm và đủ dấu vết để kết luận; số nhỏ là sớm.

- Tỉ lệ kèm khoảng tin cậy Wilson 95%.



## 3. Kết quả chính thức (bộ thử)



Đo ngày 15/11/2026 (commit `0c96ba2`, SLM `phi4-mini` chạy Ollama trên CPU).



| | Không SLM | Có SLM |

|---|---|---|

| Đúng kỹ thuật (29 phiên) | 7 (24%), KTC 95% xấp xỉ 12-42% | 6 (21%), xấp xỉ 10-38% |

| Kết luận sai mã | 0 | 0 |

| Bỏ sót (tổng) | 22 | 23 |

| Báo nhầm (3.290 phiên) | 19 (0,58%), xấp xỉ 0,37-0,90% | 8 (0,24%), xấp xỉ 0,12-0,48% |

| — máy Thiên tuần 3 | 0/807 | 0/807 |

| — máy Thiên tuần 4 | 4/1.704 (0,23%) | 2/1.704 |

| — máy Khôi (máy lạ) | 15/779 (1,9%), xấp xỉ 1,2-3,2% | 6/779 (0,8%) |

| Độ sớm (trung vị) | 2 sự kiện | 2 sự kiện |



Theo kỹ thuật (không SLM): T1003.001 đúng 5/6 phiên, T1053.005 2/4, các kỹ thuật còn lại (T1021.001, T1105, T1136.001, T1547.001, T1059.001, T1070.001) hiện chưa phát hiện đúng phiên nào trên bộ thử — nguyên nhân chủ yếu là file mẫu quá ngắn (1-4 sự kiện), không đủ để vượt ngưỡng so khớp chuỗi.



## 4. SLM có giúp không?



Chưa. Trong 27 lần hỏi SLM, SLM không lần nào trả lời "không phải tấn công". Phần giảm báo nhầm (19 xuống 8) là do SLM chọn nhầm sang một kỹ thuật thiếu dấu vết bắt buộc rồi bị bước kiểm chứng gạt đi — không phải do SLM nhận ra hoạt động bình thường. Cùng cơ chế này làm mất 1 phát hiện thật (`babyshark_mimikatz_powershell`), nên phát hiện đúng giảm từ 7 xuống 6. SLM hiện có xu hướng bám theo từ khóa (ví dụ bám chữ "wevtutil" mà bỏ qua "schtasks" trong cùng phiên) hơn là hiểu đúng ngữ cảnh.



## 5. Bộ phát triển và tinh chỉnh luật (tuần 6)



Để thử cải thiện mà không chạm bộ thử, nhóm dùng bộ phát triển riêng (`data/bo-phat-trien-khong-tien-to.csv`, 21 phiên tấn công từ Atomic Red Team, đã lọc tiền tố nhiễu — xem chương Dữ liệu mục 5).



Luật thử: phiên có sự kiện tạo file trong thư mục Startup thì thêm ứng viên T1547.001 ngay cả khi điểm so khớp chuỗi dưới ngưỡng, cho đi tiếp bước tìm dấu vết bắt buộc.



| | Tắt luật | Bật luật |

|---|---|---|

| Bộ phát triển đúng | 12/21 | 13/21 |

| Báo nhầm, log Dũng (2.573 phiên) | 10 | 10 (không đổi, nhờ danh sách bỏ qua tiến trình ONENOTE.EXE hợp lệ) |



Luật được Khôi chốt dùng, vì tăng phát hiện đúng 1 phiên mà không tăng báo nhầm trên dữ liệu đã kiểm tra. Hạn chế: danh sách bỏ qua chỉ rút từ một máy, một kẻ tấn công có quyền ghi đúng tên tiến trình/thư mục vẫn có thể lách qua.



## 6. Thử nghiệm huấn luyện lại với dữ liệu mở rộng (tuần 7)



Mục tiêu: xem việc bổ sung 24 phiên ngắn thủ công mới (chương Dữ liệu, mục 5) vào tập huấn luyện có cải thiện mô hình không. Huấn luyện ra `models/mau_chuoi_v2.json` ("bản 2"), giữ `models/mau_chuoi.json` ("bản 1") làm đối chứng.



| | Bản 1 | Bản 2 |

|---|---|---|

| Bộ phát triển đúng | 12/21 (57%) | 5/21 (24%) |

| Báo nhầm, log Dũng | 10/2.573 | 54/2.573 |

| Báo nhầm, log Thiên tuần 1 | 1/526 | 13/526 |



Bản 2 tệ hơn bản 1 ở cả hai tiêu chí đặt trước (bộ phát triển tốt hơn và báo nhầm không tăng), nên không áp dụng bản 2, giữ nguyên bản 1 làm mô hình chính thức.



Phân tích nguyên nhân (54 báo nhầm của bản 2 trên log Dũng): lọc các phiên bị kết luận tấn công trên log bình thường, đối chiếu đoạn ký hiệu khớp (script `src/phan_tich_bao_nham.py`). Toàn bộ 54/54 phiên (100%) đều bị kết luận nhầm là T1547.001; cả 5 đoạn ký hiệu khớp phổ biến nhất đều kết thúc bằng `SUA_REGISTRY:Run` (ghi khóa Run), một số còn lẫn `MO_BO_NHO:lsass.exe:TRUY_VAN` (truy vấn LSASS bình thường của hệ thống, không phải dump thật). Mẫu T1547.001 học từ các phiên ngắn mới trở nên quá ngắn/chung chung, chỉ cần chuỗi kết thúc bằng ghi registry khóa Run — hành vi rất phổ biến ở phần mềm tự khởi động cùng Windows (ví dụ vgc.exe, taskhostw.exe) — là đã khớp mẫu.



## 7. Hạn chế



- Bộ thử chỉ có 29 phiên có nhãn, một số kỹ thuật chỉ 1-2 file nên số đo theo kỹ thuật chưa đáng tin (T1070.001 không có file nào, T1059.001 chỉ 1 file, T1136.001 chỉ 2 file).

- Chỉ có một log từ máy hoàn toàn lạ (máy Khôi, 779 phiên) để đo báo nhầm; chưa đủ để nói tỉ lệ trên máy bất kỳ.

- Ghi khóa Registry Run (T1547.001) là điểm yếu dai dẳng nhất của agent. Đây là hành vi rất phổ biến ở phần mềm hợp lệ tự khởi động cùng Windows (Office, Edge, UniKey, trình cập nhật driver...), nên dấu vết bắt buộc hiện tại (Sysmon ghi giá trị vào khóa Run) gần như không lọc được gì — tuyến phòng thủ chính cho kỹ thuật này vẫn là bước so khớp chuỗi, không phải bước tìm dấu vết. Thử nghiệm bản 2 (mục 6) càng cho thấy rõ: khi mẫu chuỗi học quá ngắn/chung chung, toàn bộ 54 báo nhầm quan sát được đều rơi vào đúng lỗ hổng này. Cần một dấu vết bắt buộc chặt hơn cho T1547.001 (ví dụ loại trừ theo đường dẫn tiến trình hợp lệ, hoặc đòi thêm bằng chứng khác đi kèm) mới có thể giảm báo nhầm mà không giảm phát hiện thật.

- SLM phi4-mini với cách hỏi hiện tại chưa giúp cải thiện cả hai chỉ số chính; phần giảm báo nhầm quan sát được là do cơ chế kiểm chứng, không phải do SLM.

- Các con số trên bộ phát triển (tuần 6-7) dùng để chỉnh/so sánh, không thay thế số liệu trên bộ thử cố định khi báo cáo hiệu năng cuối.

