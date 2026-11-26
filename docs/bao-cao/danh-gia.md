# Đánh giá

## 1. Câu hỏi đánh giá

1. Khi gặp tấn công ngoài tập huấn luyện, agent kết luận đúng kỹ thuật bao nhiêu lần?
2. Khi gặp log bình thường, agent kết luận tấn công nhầm bao nhiêu lần?
3. Agent kết luận sớm đến mức nào?
4. Mô hình ngôn ngữ nhỏ (SLM) có giúp cải thiện hai câu hỏi đầu không?

## 2. Phương pháp đo

Bộ thử: data/bo-thu.csv (xem chương Dữ liệu, mục 4): 21 file tấn công (29 phiên có nhãn, đã tách Dumpert và SharpRDP) và 3 log bình thường (3.290 phiên).

Cách tính:
- Đúng kỹ thuật: phiên có nhãn được agent kết luận (điểm từ 0,5 trở lên, đủ dấu vết bắt buộc) đúng mã kỹ thuật. Kết luận sai mã tính riêng.
- Bỏ sót: phiên có nhãn không được kết luận đúng — dừng ở bước so khớp chuỗi (điểm dưới ngưỡng), chưa xác nhận (thiếu dấu vết hoặc SLM chặn), hoặc SLM lỗi.
- Báo nhầm: số phiên log bình thường bị kết luận có tấn công / tổng số phiên.
- Độ sớm: số sự kiện từ đầu phiên đến lúc agent đủ điểm và đủ dấu vết để kết luận; số nhỏ là sớm.

## 3. Kết quả (đo trên bộ thử trước khi chốt, tuần 6)

Đo đêm 20-21/11/2026, commit 1c7211a, mô hình models/mau_chuoi.json (sha256 4255be121581), ngưỡng 0,5. Bộ thử data/bo-thu.csv: 29 phiên tấn công có nhãn, 3.290 phiên log bình thường (Thiên tuần 3, tuần 4, Khôi 7 ngày; log Dũng chưa tính được ở lần đo này, xem chương Dữ liệu mục 4).

| | Không SLM, luật Startup tắt | Không SLM, luật Startup bật |
|---|---|---|
| Đúng kỹ thuật (29 phiên) | 7 (24%) | 9 (31%) |
| Kết luận sai mã | 0 | 0 |
| Bỏ sót: dừng bước 2 / chưa xác nhận | 17 / 5 | 15 / 5 |
| Báo nhầm (3.290 phiên) | 19 (0,58%) | 19 (0,58%) |
| Thiên tuần 4 / Khôi | 4 / 15 | 4 / 15 |
| Độ sớm trung vị (sự kiện) | 2 (7 phiên) | 2 (9 phiên) |
| Thời gian chạy | 22 phút | 18 phút |

Theo kỹ thuật (luật bật): T1003.001 5/6, T1053.005 2/4, T1547.001 2/4, các kỹ thuật còn lại (T1021.001, T1059.001, T1105, T1136.001) hiện chưa phát hiện đúng phiên nào trên bộ thử — nguyên nhân chủ yếu là file mẫu quá ngắn (1-4 sự kiện), không đủ để vượt ngưỡng so khớp chuỗi.

Lưu ý: đây chưa phải số liệu chính thức cuối cùng của đồ án. Số chính thức sẽ đo một lần duy nhất ở tuần 8 sau khi chốt toàn bộ cấu hình (mô hình, luật, có hay không dùng SLM). Số trên dùng để theo dõi tiến độ trong lúc còn đang chỉnh.

## 4. SLM có giúp không?

So sánh 4 mô hình SLM qua Ollama, cùng điều kiện với mục 3 (commit 1c7211a, bộ thử như trên, cách hỏi SLM cũ, luật Startup tắt trừ 2 dòng đầu), chạy đêm 20-21/11/2026 trên máy Khôi (CPU):

| Chế độ | Đúng/29 | Báo nhầm/3.290 | Thiên t4 / Khôi | Chưa xác nhận do SLM | Số lần hỏi | TB mỗi lần | Thời gian chạy |
|---|---|---|---|---|---|---|---|
| Không SLM, luật tắt | 7 (24%) | 19 (0,58%) | 4 / 15 | - | - | - | 22 phút |
| Không SLM, luật bật | 9 (31%) | 19 (0,58%) | 4 / 15 | - | - | - | 18 phút |
| phi4-mini | 6 (21%) | 8 (0,24%) | 2 / 6 | 11 | 26 | 52 giây | 38 phút |
| qwen3:4b-instruct-2507 | 7 (24%) | 13 (0,40%) | 4 / 9 | 6 | 26 | 74 giây | 50 phút |
| llama3.2:3b | 6 (21%) | 15 (0,46%) | 2 / 13 | 4 | 26 | 45 giây | 30 phút |
| gemma3:4b | 6 (21%) | 8 (0,24%) | 2 / 6 | 11 | 26 | 58 giây | 34 phút |

Không mô hình nào phát hiện đúng nhiều hơn chế độ không SLM (qwen3 bằng, 3 mô hình còn lại kém hơn); 0 kết luận sai mã ở mọi chế độ.

Vì sao báo nhầm giảm khi có SLM: 9 trong số các lần hỏi SLM trên log Khôi là các phiên có 2 ứng viên T1053.005 (Lenovo Vantage tạo tác vụ hẹn giờ thật, đủ dấu vết) và T1070.001 (Defender gọi wevtutil sửa kênh nhật ký, không có wevtutil cl, thiếu dấu vết). Mô hình đọc đúng log nhất (llama3.2, chọn đúng T1053.005 7/9 lần) lại có nhiều báo nhầm nhất, còn mô hình chọn sai nhiều nhất (phi4-mini, chọn T1070.001 cả 9/9 lần, kỹ thuật thiếu dấu vết) lại có ít báo nhầm nhất vì bị bước kiểm chứng chặn. Tức là phần giảm báo nhầm đến từ bước kiểm chứng gạt bỏ lựa chọn sai của SLM, không phải do SLM nhận ra hoạt động bình thường: không mô hình nào trong 4 mô hình (cách hỏi cũ) từng chọn "không phải tấn công" khi có cơ hội.

Thử cách hỏi mới (D3, Thiên đo 22/11/2026, commit 695320d, trên bộ phát triển không tiền tố, phi4-mini): cách hỏi mới cho SLM biết rõ ứng viên nào đủ hay thiếu dấu vết bắt buộc, và thêm hẳn lựa chọn BÌNH_THƯỜNG (bật bằng biến môi trường SLM_PROMPT_MOI=1, prompt dài gấp khoảng 5 lần cách cũ).

| | Cách hỏi cũ | Cách hỏi mới |
|---|---|---|
| Bộ phát triển đúng | 12/21 | 2/21 |
| Số lần hỏi | 12 | 12 |
| Thời gian | 82 giây | 127 giây |

Theo phân tích của Dũng (docs/ket-qua/d3-prompt-moi.md mục 5): cả 10 phiên bị mất đều do SLM chọn CHƯA_XÁC_NHẬN, không phiên nào chọn BÌNH_THƯỜNG. Tức là khi được cho thêm lựa chọn "bình thường" và thấy rõ ứng viên thiếu dấu vết, mô hình trở nên quá thận trọng, né tránh kết luận ngay cả khi đúng, chứ không dùng lựa chọn mới để lọc log bình thường. Kết luận: đã thử, chưa đạt — cách hỏi cũ vẫn dùng tiếp.

## 5. Bộ phát triển và tinh chỉnh luật (tuần 6)

Để thử cải thiện mà không chạm bộ thử, nhóm dùng bộ phát triển riêng (data/bo-phat-trien-khong-tien-to.csv, 21 phiên tấn công từ Atomic Red Team, đã lọc tiền tố nhiễu).

Luật thử: phiên có sự kiện tạo file trong thư mục Startup thì thêm ứng viên T1547.001 ngay cả khi điểm so khớp chuỗi dưới ngưỡng, cho đi tiếp bước tìm dấu vết bắt buộc.

| | Tắt luật | Bật luật |
|---|---|---|
| Bộ phát triển đúng | 12/21 | 13/21 |
| Báo nhầm, log Dũng (2.573 phiên, dữ liệu phát triển) | 10 | 10 (không đổi) |
| Bộ thử data/bo-thu.csv (29 phiên) | 7 (24%) | 9 (31%) |
| Báo nhầm trên bộ thử (3.290 phiên) | 19 (0,58%) | 19 (0,58%), không tăng |

Hai phiên tăng thêm trên bộ thử khi bật luật: LM_tsclient_startup_folder phiên 2 và lateral_movement_startup_3_11 phiên 1 (cả hai đều T1547.001).

Lưu ý quan trọng: luật được thiết kế sau khi đã đọc và phân tích bộ thử, nên kết quả tăng 2 phiên trên bộ thử không phải kiểm tra độc lập — đây là điểm cần nêu rõ khi bảo vệ đồ án, tránh hiểu nhầm là luật được kiểm định mù trên dữ liệu chưa từng thấy. Luật được Khôi chốt dùng vì tăng phát hiện đúng mà không tăng báo nhầm trên mọi dữ liệu đã kiểm tra (kể cả bộ thử), nhưng mức độ khái quát thật của luật trên log/tấn công hoàn toàn mới vẫn chưa được kiểm chứng độc lập. Hạn chế khác: danh sách bỏ qua chỉ rút từ một máy, một kẻ tấn công có quyền ghi đúng tên tiến trình/thư mục vẫn có thể lách qua.

## 6. Thử nghiệm huấn luyện lại với dữ liệu mở rộng (tuần 7)

Mục tiêu: xem việc bổ sung 24 phiên ngắn thủ công mới (chương Dữ liệu, mục 5) vào tập huấn luyện có cải thiện mô hình không. Huấn luyện ra models/mau_chuoi_v2.json (bản 2), giữ models/mau_chuoi.json (bản 1) làm đối chứng.

| | Bản 1 | Bản 2 |
|---|---|---|
| Bộ phát triển đúng | 12/21 (57%) | 5/21 (24%) |
| Báo nhầm, log Dũng | 10/2.573 | 54/2.573 |
| Báo nhầm, log Thiên tuần 1 | 1/526 | 13/526 |

Bản 2 tệ hơn bản 1 ở cả hai tiêu chí đặt trước (bộ phát triển tốt hơn và báo nhầm không tăng), nên không áp dụng bản 2, giữ nguyên bản 1 làm mô hình chính thức.

Phân tích nguyên nhân (54 báo nhầm của bản 2 trên log Dũng): lọc các phiên bị kết luận tấn công trên log bình thường, đối chiếu đoạn ký hiệu khớp (script src/phan_tich_bao_nham.py). Toàn bộ 54/54 phiên (100%) đều bị kết luận nhầm là T1547.001; cả 5 đoạn ký hiệu khớp phổ biến nhất đều kết thúc bằng SUA_REGISTRY:Run, một số còn lẫn MO_BO_NHO:lsass.exe:TRUY_VAN (truy vấn LSASS bình thường của hệ thống, không phải dump thật). Mẫu T1547.001 học từ các phiên ngắn mới trở nên quá ngắn/chung chung, chỉ cần chuỗi kết thúc bằng ghi registry khóa Run là đã khớp mẫu.

## 7. Theo dõi trực tiếp

(chưa điền đầy đủ — Khôi điền thêm: độ trễ cảnh báo, số cảnh báo mỗi giờ khi chạy theo-doi trên log trực tiếp của Khôi, kèm ảnh docs/hinh/tuan7-k2-chuoi-truc-tiep.png.)

Ví dụ cảnh báo sai khi theo dõi trực tiếp (Khôi, 00:00-00:07 ngày 26/11/2026, theo-doi --khong-slm --an-ten):

Thứ tự lệnh và cảnh báo:
1. schtasks /create /tn DACN_ThuNghiem ... -> CẢNH BÁO 1, KẾT LUẬN T1053.005 (đúng).
2. reg add HKCU...CurrentVersion\Run /v DACN_ThuNghiem /d notepad.exe /f -> CẢNH BÁO 2, KẾT LUẬN T1547.001 (đúng), bằng chứng Event 13 reg.exe ghi khóa ...\Run\DACN_ThuNghiem.
3. Dọn dẹp: schtasks /delete ... và reg delete HKCU...\Run /v DACN_ThuNghiem /f -> CẢNH BÁO 3, KẾT LUẬN T1547.001 (điểm 0,968). Cảnh báo này sai.

Cảnh báo 3 có 2 bằng chứng, không cái nào thật sự là hành vi tấn công:
- Event 12 reg.exe ghi ...\Run\DACN_ThuNghiem: đây chính là lệnh xóa khóa (dọn dẹp), nhưng dấu vết bắt buộc hiện tại chỉ kiểm tra Event 12/13/14 có nhắc tới đường dẫn khóa Run, không phân biệt ghi hay xóa giá trị (bảng su_kien (doc_log.py) chưa có cột EventType).
- Event 13 của sihost.exe ghi khóa HKU...CurrentVersion\RunNotification\StartupTNoti...: đây là khóa Windows tự ghi để hiển thị thông báo khi có mục khởi động mới, không liên quan đến T1547.001, nhưng bị khớp vì điều kiện dấu vết hiện tại chỉ kiểm tra chuỗi đường dẫn có chứa currentversion\run.

Ảnh docs/hinh/tuan7-k2-chuoi-truc-tiep.png (K2, Khôi) chỉ ghi lại cảnh báo 1 và 2; chi tiết cảnh báo 3 lấy từ log máy Khôi, không push lên repo.

Hướng sửa đề xuất: thêm cột EventType (ghi giá trị hay xóa giá trị) vào dấu vết bắt buộc của T1547.001 để loại các thao tác xóa; sửa điều kiện khớp đường dẫn registry thành khớp chính xác đoạn \run\ hoặc \runonce\ có dấu gạch chéo ở cuối (RunOnce cũng là khóa tự khởi động thật của T1547.001), để không khớp nhầm các khóa con khác như RunNotification có tên bắt đầu giống Run nhưng không phải khóa tự khởi động thật.

## 8. Chuỗi tấn công

(chưa điền — Khôi điền: kết quả ghép chuỗi T1 bằng src/chuoi_tan_cong.py của Khôi, xác nhận đúng thứ tự 7 bước (bước 0 và 6 kỹ thuật), kèm ảnh docs/hinh/tuan7-k2-chuoi-t1-khong-slm.png.)

## 9. Hạn chế

- Bộ thử chỉ có 29 phiên có nhãn, một số kỹ thuật chỉ 1-2 file nên số đo theo kỹ thuật chưa đáng tin (T1070.001 không có file nào, T1059.001 chỉ 1 file, T1136.001 chỉ 2 file).
- Log Dũng hiện không tính được trong các lần đo chính thức từ 20/11 trở đi (lệch số thứ tự phiên), đang chờ gán nhãn lại; chỉ có một log từ máy hoàn toàn lạ (Khôi, 779 phiên) để đo báo nhầm.
- Luật Startup (mục 5) tăng phát hiện đúng trên bộ thử nhưng được thiết kế sau khi đã xem bộ thử, nên con số tăng thêm không phải kiểm tra độc lập; cần dữ liệu tấn công hoàn toàn mới để kiểm định luật này đáng tin đến đâu.
- Cách hỏi SLM mới (D3, mục 4) nhằm giảm báo nhầm bằng lựa chọn BÌNH_THƯỜNG chưa đạt — mô hình trở nên quá thận trọng, bỏ sót nhiều hơn nhận đúng.
- Ghi khóa Registry Run (T1547.001) là điểm yếu dai dẳng nhất của agent. Đây là hành vi rất phổ biến ở phần mềm hợp lệ tự khởi động cùng Windows (Office, Edge, UniKey, trình cập nhật driver...) và cả ở chính thao tác xóa khóa hay các khóa con liên quan (RunNotification) như mục 7 đã nêu, nên dấu vết bắt buộc hiện tại gần như không lọc được gì — tuyến phòng thủ chính cho kỹ thuật này vẫn là bước so khớp chuỗi, không phải bước tìm dấu vết. Thử nghiệm bản 2 (mục 6) càng cho thấy rõ: khi mẫu chuỗi học quá ngắn/chung chung, toàn bộ 54 báo nhầm quan sát được đều rơi vào đúng lỗ hổng này.
- SLM phi4-mini (và 3 mô hình khác đã thử) với cách hỏi hiện tại chưa giúp cải thiện cả hai chỉ số chính; phần giảm báo nhầm quan sát được là do cơ chế kiểm chứng, không phải do SLM.
- Các con số trên bộ phát triển (tuần 6-7) dùng để chỉnh/so sánh, không thay thế số liệu trên bộ thử cố định khi báo cáo hiệu năng cuối.