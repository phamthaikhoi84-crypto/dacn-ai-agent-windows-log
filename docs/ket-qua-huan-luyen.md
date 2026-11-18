# Kết quả huấn luyện và đo lường

Phần của Thiên (dữ liệu, nhãn, huấn luyện). Số liệu lấy từ các lần tự chạy `src/train.py`, `src/agent.py` và `src/dau_vet.py`, cập nhật ngày 14/11/2026 (có thêm log tuần 4 và kết quả trên bộ thử cố định). Mô hình: `models/mau_chuoi.json` (commit `5c8a3fa`, ký hiệu theo `ky_hieu.py` commit `6defe92`).

## 1. Dữ liệu và nhãn

- `data/nhan-file.csv`: 64 file Splunk Attack Data, 45 file có chuỗi có nhãn dùng được.
- 292 chuỗi có nhãn, còn **128 chuỗi** sau khi bỏ chuỗi trùng nhau trong cùng một file.
- Nhãn gán theo cây tiến trình: gốc là tiến trình có sự kiện khớp dấu hiệu của kỹ thuật, chuỗi gồm các sự kiện thuộc cây đó (Event 1, 3, 11, 12, 13, 14 và Event 10 vào lsass).

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

## 2. Cách học

- Mỗi sự kiện đổi thành một ký hiệu (ví dụ `TAO_TIEN_TRINH:certutil.exe`, `MO_BO_NHO:lsass.exe:DOC_BO_NHO`).
- Mô hình đếm các đoạn 1, 2, 3 ký hiệu liên tiếp trong chuỗi của từng kỹ thuật, cửa sổ trượt 6 ký hiệu.
- Điểm của một đoạn là xác suất kỹ thuật k khi gặp đoạn đó, có tính **tỉ lệ gốc 1e-2** (một cửa sổ tấn công hiếm hơn cửa sổ bình thường) và **lớp bình thường** học từ 60% đầu (603 phiên) log bình thường của máy Thiên. Điểm cửa sổ lấy đoạn cao nhất.
- Bảng "sau ký hiệu A thường là B" học riêng cho từng kỹ thuật, dùng để đoán bước kế tiếp.

## 3. Bảng tỉ lệ đoán đúng (bỏ lần lượt từng file ra thử)

Mỗi lần bỏ một file ra, học từ các file còn lại, rồi thử trên file bị bỏ. Kỹ thuật chỉ có một file thì bỏ lần lượt từng chuỗi. Mỗi kỹ thuật tính trọng số như nhau.

| Kỹ thuật | File | Chuỗi | Đoán đúng kỹ thuật | Không nhận ra | Đoán đúng bước kế (số mẫu) |
|---|---|---|---|---|---|
| T1003.001 | 3 | 15 | 47% | 7% | 13% (45) |
| T1021.001 | 8 | 11 | 55% | 18% | 0% (1) |
| T1053.005 | 7 | 15 | 93% | 0% | 18% (17) |
| T1059.001 | 16 | 54 | 83% | 0% | 39% (569) |
| T1070.001 | 2 | 3 | 67% | 0% | 50% (2), ít dữ liệu |
| T1105 | 5 | 14 | 43% | 7% | 31% (29) |
| T1136.001 | 1 | 3 | 67% | 0% | 86% (7), 1 file, ít dữ liệu |
| T1547.001 | 3 | 13 | 62% | 0% | 42% (97) |
| **Trung bình** | | | **64%** | | |

- "Đoán đúng kỹ thuật": kỹ thuật điểm cao nhất trùng nhãn, chưa áp ngưỡng. Khi áp ngưỡng 0,5 (ngưỡng agent dùng) thì tỉ lệ này là 55%.
- Nhầm lẫn hay gặp (nhãn thật sang dự đoán): T1105 sang T1059.001 (5 chuỗi), T1547.001 sang T1059.001 (5), T1003.001 sang T1059.001 (4), T1059.001 sang T1136.001 (4), T1059.001 sang T1003.001 (3).
- T1070.001 và T1136.001 chỉ có 3 chuỗi nên tỉ lệ của hai kỹ thuật này chưa đáng tin.
- Đoán bước kế còn yếu: T1003.001 13%, T1053.005 18%.

## 4. Báo động giả của bước 2 (khớp chuỗi) trên log bình thường

Log bình thường máy Thiên: 402 phiên cuối của tuần 2 (không dùng để học), 20.240 cửa sổ, khoảng 6,4 ngày.

| Ngưỡng | Đoán đúng (có áp ngưỡng) | Cảnh báo giả | Cảnh báo giả mỗi ngày |
|---|---|---|---|
| 0,3 | 55% | 62 | 9,7 |
| **0,5** | **55%** | **39** | **6,1** |

Trước khi thêm lớp bình thường và tỉ lệ gốc (bản 5), cùng log này cho khoảng 56 đến 61 cảnh báo giả mỗi ngày.

## 5. Dấu vết bắt buộc (bước 3, `src/dau_vet.py`)

Chạy trên 45 file Splunk **trước khi Khôi sửa** (commit `e079e87`): đủ dấu vết của kỹ thuật đúng ở **36/45 file (80%)**, trung bình theo kỹ thuật 84%.

| Kỹ thuật | Đủ dấu vết |
|---|---|
| T1053.005, T1070.001, T1136.001, T1547.001 | 7/7, 2/2, 1/1, 3/3 |
| T1059.001 | 14/16 |
| T1105 | 4/5 |
| T1003.001 | 2/3 |
| T1021.001 | 3/8 |

9 file thiếu vì: file RDP chỉ có dấu vết trên đĩa (5 file), lệnh `curl.exe"` có ngoặc kép (1 file), và 3 file mà nhãn đáng nghi (`createdump` dump tiến trình .NET, `soaphound` không dùng PowerShell, `trickbot` chưa rõ). Khôi đã sửa dấu vết T1003.001, T1021.001, T1053.005, T1105.

Số sự kiện khớp dấu vết trong log bình thường máy Thiên (trước khi sửa): T1547.001 333, T1053.005 62, T1059.001 36, T1003.001 4 (đều là `wininit.exe`, `csrss.exe` lúc khởi động), các kỹ thuật còn lại 0.

## 6. Agent đầu-cuối (5 bước, ngưỡng 0,5)

| Log | Số phiên | Qua bước 2 | Bị kết luận tấn công (đều là báo giả) |
|---|---|---|---|
| Máy Dũng, trước khi sửa dấu vết | 2.573 | 91 (3,5%) | 46 (1,79%) |
| Máy Dũng, sau khi sửa | 2.573 | 91 (3,5%) | **10 (0,39%)** |
| Máy Thiên, log mới 2/11 đến 4/11 | 807 | 12 (1,5%) | **0** |
| **Máy Khôi, log 7 ngày, không SLM (cấu hình Sysmon chung, theo Khôi không chạy công cụ tấn công)** | 779 | 44 (5,6%) | **15 (1,9%)** |
| **Máy Khôi, log 7 ngày, có SLM (phi4-mini, sau khi sửa bước 4)** | 779 | 44 (5,6%) | **6 (0,8%)**, khoảng tin cậy 95% xấp xỉ 0,4% đến 1,7%; xem mục 6b về ý nghĩa |
| Máy Thiên, log tuần 4 (5/11 đến 12/11, không trùng thời gian với log học) | 1.704 | 31 (1,8%) | **4 (0,23%)** |
| `demo_nho.evtx` (đoạn nhỏ của Dũng) | 16 | 3 | **0** |

- 10 phiên còn lại trên máy Dũng: 4 T1547.001 (`browser.exe`, `runonce.exe` ghi khóa Run), 4 T1059.001 (PowerShell bộ cài `-ExecutionPolicy Bypass`), 2 T1053.005 (Office `schtasks /Create ... Office Feature Updates`).
- Log tuần 4 máy Thiên: 4 phiên bị kết luận nhầm trên 1.704 (0,23%): Office, `runonce`, Roblox, ProtonVPN, đều là phần mềm hợp lệ. Cùng máy với dữ liệu học nhưng không trùng thời gian.
- 0 trên 807 phiên nghĩa là tỉ lệ báo giả khoảng 0 với cận trên 95% khoảng 0,4%. Nhưng log này cùng máy với dữ liệu học lớp bình thường.
- **Máy Khôi (máy lạ, chưa nằm trong dữ liệu học hay chỉnh dấu vết nào):** 15 phiên bị kết luận nhầm trên 779 phiên (1,9%, khoảng tin cậy 95% xấp xỉ 1,2% đến 3,2%). Khôi đã kiểm tra từng phiên trong 15 phiên; ba nguyên nhân gốc, đều là phần mềm hợp lệ: (1) **Lenovo, 9 phiên**: `schtasks /Create /TN "LvfDriverRemoval"` chạy dưới SYSTEM mỗi lần khởi động máy một lần (T1053.005); (2) **Edge và UniKey, 4 phiên**: ghi khóa Run (T1547.001); (3) **PowerShell ẩn kiểm tra VS Code, 2 phiên**: `-WindowStyle Hidden -ExecutionPolicy Bypass ... Get-AppxPackage -Name 'Microsoft.VisualStudioCode'` (T1059.001). Lần đo đầu trên 2 ngày đầu của log này (6/242, 2,5%) nằm trong 779 phiên này (log 7 ngày xuất lại toàn bộ), nên không cộng dồn.
- Tỉ lệ phiên qua bước 2 tăng theo độ xa so với dữ liệu học: máy Thiên 1,5%, máy Dũng 3,5%, máy Khôi 5,6% (lần đo 2 ngày đầu là 8,3%).

Phép thử mô hình ngôn ngữ trên 6 phiên của máy Khôi (phi4-mini, chạy ngày 6/11): 3 phiên mô hình chọn sai T1070.001 và bước 5 chặn, 2 phiên phản hồi bị cắt, 1 phiên Ollama báo lỗi 500. **Không phiên nào được mô hình nhận ra là bình thường**, nên chưa có bằng chứng bước 4 giúp loại báo giả (bước 5 chặn kết luận sai là việc của bước kiểm chứng, không phải của mô hình). Nguyên nhân Khôi nêu: phiên trên máy thật rất dài (phiên 41 hơn 3 giờ, 5.604 sự kiện), bước 4 chỉ gửi 40 dòng đầu nên mô hình không thấy dòng đáng ngờ; và bước 3 tìm dấu vết trong cả phiên nên phiên dài dễ tìm thấy dấu vết không liên quan đoạn khớp ở bước 2. Hướng sửa: chỉ tìm dấu vết gần đoạn khớp (để tuần sau).

**Cập nhật 14/11 và 15/11:** sau khi Khôi sửa bước 4 (gửi các dòng quanh dấu vết) và `slm.py` (khuôn JSON), có SLM trên máy Khôi còn 6/779 (0,8%), không lỗi SLM. Nhưng như mục 6b ghi, 9 phiên bị chặn là do SLM chọn nhầm kỹ thuật rồi bước kiểm chứng gạt đi, không phải SLM nhận ra phiên bình thường, và cùng cơ chế đó làm mất 1 phát hiện thật. Nên nhận định đúng là SLM `phi4-mini` với cách hỏi hiện tại **chưa giúp**; đoạn nói bước 4 giúp loại báo giả ở bản trước là sai.

Ca tấn công ngoài tập huấn luyện (EVTX-ATTACK-SAMPLES), chạy với `--ban-tam`:

| File | Kết luận |
|---|---|
| `rundll32_cmd_schtask` | T1053.005, 0,865, đúng |
| `babyshark_mimikatz_powershell` phiên 4 | T1003.001, 0,760, đúng (bước 2 xếp T1053.005 0,898, bước 3 loại vì thiếu `schtasks /create`) |
| `DE_timestomp_and_dll_sideloading_and_RunPersist` phiên 1 | T1547.001, 0,910, đúng |
| `CA_sysmon_hashdump_cmd_meterpreter` (chạy 30/10) | T1003.001, 0,760, đúng (chỉ 1 sự kiện lsass) |
| `CA_teamviewer-dumper_sysmon_10` (chạy 30/10), `sideloading_..._run_key` (chạy 30/10) | bỏ sót, log quá ngắn (1 và 7 sự kiện) |

## 6b. Bộ thử cố định `data/bo-thu.csv` (số chính thức từ `src/danh_gia.py`, lần đo 4 của Khôi)

Chạy ngày 15/11/2026 (commit `0c96ba2`, mô hình `mau_chuoi.json` sha256 `4255be121581`, ngưỡng 0,5, SLM `phi4-mini` chạy Ollama trên CPU). Bảng gốc: `docs/ket-qua/tuan5-lan4-hai-che-do.md` (hai chế độ) và `tuan5-lan5-do-som.md` (độ sớm). Bộ thử gồm 21 file tấn công chấm điểm từ EVTX-ATTACK-SAMPLES (31 phiên có nhãn; sau khi tách SharpRDP còn 29) và 3 log bình thường chưa dùng chỉnh (máy Thiên tuần 3, tuần 4, máy Khôi; tổng 3.290 phiên). Nhãn lấy bằng cách **đọc lệnh và sự kiện thật** trong từng file, không lấy từ agent hay `dau_vet.py`. Đơn vị đếm là **phiên** (cột `Phien`).

| Chế độ | Phát hiện đúng (29 phiên, đã tách Dumpert và SharpRDP) | Kết luận sai mã | Bỏ sót: dừng bước 2 / chưa xác nhận | Báo nhầm (3.290 phiên bình thường) | Độ sớm (trung vị) | SLM lỗi |
|---|---|---|---|---|---|---|
| Không SLM | **7 (24%)**, khoảng tin cậy 95% xấp xỉ 12% đến 42% | 0 | tổng 22 (lần đo 15/11: 18 / 6 trên 31 phiên) | **19 (0,58%)**, khoảng tin cậy xấp xỉ 0,37% đến 0,90% | 2 sự kiện (7 phiên) | - |
| Có SLM | **6 (21%)**, xấp xỉ 10% đến 38% | 0 | tổng 23 (lần đo 15/11: 18 / 7 trên 31 phiên) | **8 (0,24%)**, xấp xỉ 0,12% đến 0,48% | 2 sự kiện (6 phiên) | 0 |

Báo nhầm theo máy: Thiên tuần 3 0/807 (cả hai chế độ); Thiên tuần 4 4/1.704 không SLM, 2 có SLM; Khôi 15/779 không SLM, 6 có SLM. Log máy Dũng (10/2.573 không SLM) để riêng vì đã dùng chỉnh dấu vết. File Dumpert (đúng 1/1 ở cả hai chế độ) cũng ghi riêng vì đã dùng để chạy thử và sửa code.

| Kỹ thuật | Phiên tấn công | Đúng, không SLM | Đúng, có SLM |
|---|---|---|---|
| T1003.001 | 6 | 5 | 4 |
| T1053.005 | 4 | 2 | 2 |
| T1021.001 | 3 | 0 | 0 |
| T1105 | 4 | 0 | 0 |
| T1136.001 | 7 | 0 | 0 |
| T1547.001 | 4 | 0 | 0 |
| T1059.001 | 1 | 0 | 0 |
| T1070.001 | 0 | không có file | không có file |

- Tính theo file (ít nhất một phiên có nhãn được kết luận đúng) không SLM: 6/19 (32%) khi không tính Dumpert và SharpRDP. Số theo phiên thấp hơn vì file `sysmon_local_account_creation...` (T1136.001) có 6 phiên đều bị bỏ sót và nhãn từng phiên chưa đối chiếu; bỏ file này thì 7/23 phiên (30%).
- File `LM_sysmon_3_12_13_1_SharpRDP` **đã dùng khi phát triển** (ký hiệu `RunMRU` thêm ở commit `05161fb` ngày 28/10, `tuan-3.md` ghi "phiên SharpRDP ra `SUA_REGISTRY:RunMRU`"), nên được tách khỏi bảng chính như Dumpert. Lần đo 15/11 của Khôi chưa tách (31 phiên); số trong bảng trên là số đã tách tính tay (hai phiên SharpRDP đều bị bỏ sót), sẽ đo lại chính thức. Hai file cùng họ (`tsclient_SharpRdp`, `mstscax.dll`) vẫn tính nhưng không hoàn toàn độc lập.
- Bỏ sót chủ yếu ở bước 2 (18 phiên): đoạn khớp không đạt ngưỡng, vì phần lớn file chỉ 1 đến 4 sự kiện hoặc chỉ sửa registry. 6 phiên còn lại dừng ở bước 3 (thiếu dấu vết).
- Độ sớm trung vị là 2 sự kiện, nhưng các phiên đúng đều rất ngắn (1 đến 15 sự kiện) nên con số này chưa nói được độ sớm trên tấn công dài, và chưa phải đo ở chế độ phát lại.
- So với 64% ở phép thử bỏ lần lượt từng file: đó là đoán kỹ thuật chỉ bằng so khớp chuỗi trên dữ liệu Splunk, còn đây là cả các bước trên log từ nguồn khác. Hai con số đo hai việc khác nhau; 24% theo phiên mới là số nên dùng khi nói agent làm được gì trên log lạ.
- File `rdrleakdiag` (T1003.001): agent đoán đúng chuỗi với điểm 0,978 nhưng bước 3 báo thiếu dấu vết, vì tiến trình `rdrleakdiag` tự dump lsass nên log không có Event 10 vào lsass. `dau_vet.py` đòi Event 10 nên bỏ sót thật một ca đúng.
- File SharpRDP (T1021.001): agent đoán nhầm phiên 2 là T1059.001 (0,583) vì sự kiện kết nối 3389 nằm ở phiên 1, bước gom phiên đã tách hai phần của cùng một cuộc tấn công.

### SLM có giúp không?

Theo lần đo của Khôi (`ke-hoach-nhat-ky/tuan-5.md`): **chưa**. Trong 27 lần hỏi SLM ở lần đo chính, SLM không lần nào chọn `CHUA_XAC_NHAN` (nghĩa là không lần nào nói "không phải tấn công").
- 11 báo nhầm bị chặn (9 máy Khôi, 2 máy Thiên tuần 4) đều do SLM **chọn nhầm sang một kỹ thuật thiếu dấu vết bắt buộc**, rồi bước kiểm chứng (bước 5) gạt đi. Đây là giảm do bước kiểm chứng, không phải do SLM nhận ra hoạt động bình thường.
- Cùng cơ chế đó làm **mất 1 phát hiện thật**: `babyshark_mimikatz_powershell` (không SLM đúng T1003.001; có SLM chọn T1059.001, thiếu dấu vết, thành chưa xác nhận). Vì vậy phát hiện đúng giảm 7 xuống 6.
- Các báo nhầm còn lại (6 máy Khôi, 2 máy Thiên) thì SLM đồng ý với kết luận sai, chủ yếu T1547.001.
- Ví dụ phiên 46 máy Khôi: Lenovo tạo 3 tác vụ hẹn giờ bằng `schtasks /Create /XML` cùng lúc Windows Defender gọi `wevtutil.exe`; SLM bỏ qua `schtasks`, bám vào chữ `wevtutil` và chọn T1070.001 dù không có lệnh xóa nhật ký (ảnh `docs/hinh/tuan5-phien46-slm-chon-t1070.png`). SLM đang nhận diện theo từ khóa.
- Thời gian: khoảng 70 giây mỗi lần hỏi với phiên dài trên máy thật (CPU).

## 7. Hạn chế

- Ký hiệu không có nội dung dòng lệnh (không phân biệt `net user /add` với `net use`), nên bước 2 chỉ là bộ lọc thô và dấu vết bắt buộc mới quyết định kết luận.
- Công cụ chưa gặp khi huấn luyện (ví dụ `createdump.exe`) không khớp được vì ký hiệu chứa tên tiến trình.
- T1070.001 và T1136.001 chỉ có 3 chuỗi. Trên bộ thử, T1070.001 không có file nào, T1059.001 chỉ 1 file, T1136.001 chỉ 2 file, nên số đo ba kỹ thuật này chưa đáng tin.
- Lớp bình thường học từ một máy (máy Thiên). Log của Dũng đã được dùng để chỉnh dấu vết, nên 0,39% là số trên dữ liệu đã dùng để chỉnh. Log mới của máy Thiên (0 trên 807 phiên) cùng máy với dữ liệu học. **Chỉ có một log từ máy lạ (máy Khôi, 779 phiên trong 7 ngày): 15 phiên bị kết luận nhầm (1,9%).** Số này mới có một máy, nên chưa nói được tỉ lệ trên máy bất kỳ.
- Hoạt động hợp lệ tạo đúng dấu vết tấn công (Office, Lenovo, PowerShell bộ cài, ứng dụng ghi khóa Run) vẫn còn báo giả. Đây là điểm yếu chính của hai kỹ thuật T1053.005 và T1547.001: phần mềm hợp lệ làm đúng việc mà kẻ tấn công làm.
- Phiên rất dài (hàng nghìn sự kiện) làm bước 3 dễ thấy dấu vết ở chỗ không liên quan đoạn khớp ở bước 2, và bước 4 chỉ gửi 40 dòng đầu cho mô hình ngôn ngữ.
- Bộ thử: file `babyshark_mimikatz_powershell` ban đầu xếp T1059.001, được **đổi sang T1003.001 sau khi xem kết quả agent** (lệnh trong file là Mimikatz); file 04 và 07 từng dùng để phát triển/demo; hai file `remote_file_copy` và `smbmap` có độ chắc nhãn trung bình.
- Hai nhãn đáng nghi: `createdump_windows-sysmon.log` (T1003.001) và `sysmon_soaphound.log` (T1059.001).

## 8. Trả lời câu hỏi "log bình thường chiếm 99,99%"

Log bình thường nhiều hơn log tấn công rất nhiều, nên bộ lọc chỉ đoán "giống tấn công" sẽ báo giả nhiều. Agent xử lý bằng ba lớp:

1. **Lớp bình thường và tỉ lệ gốc trong điểm** (bước 2): đưa cảnh báo giả trên log của Thiên từ khoảng 56 xuống khoảng 6 mỗi ngày (ngưỡng 0,5).
2. **Dấu vết bắt buộc** (bước 3): kỹ thuật chỉ được xét tiếp khi tìm thấy dấu vết thật trong log (ví dụ `schtasks /create`, mở lsass có quyền đọc). Thiếu dấu vết thì "chưa xác nhận".
3. **Kiểm chứng** (bước 5): kỹ thuật chọn phải nằm trong ứng viên, đủ dấu vết, điểm đạt ngưỡng, và dòng log trích làm bằng chứng phải có thật.

Kết quả: máy Thiên (log mới) 0 phiên nhầm trên 807 và 4 trên 1.704 ở tuần 4; máy Dũng 10 phiên nhầm trên 2.573 (0,39%); máy Khôi, máy lạ, 15 phiên nhầm trên 779 (1,9%, khoảng tin cậy 95% xấp xỉ 1,2% đến 3,2%, ba nguyên nhân gốc). Tức là tỉ lệ báo giả cuối cùng khoảng 0 đến vài phần trăm số phiên tùy máy, thấp hơn nhiều so với chỉ so khớp chuỗi (1,5% đến 5,6% phiên qua bước 2), nhưng chưa về 0 trên máy lạ. Phần còn lại chủ yếu là phần mềm hợp lệ tạo tác vụ hẹn giờ hay khóa Run.

Mặt còn lại: trên tấn công ngoài tập huấn luyện (bộ thử cố định, mục 6b) agent chỉ kết luận đúng kỹ thuật ở 7/29 phiên (24%) khi không dùng SLM, và 6/29 (21%) khi dùng SLM (đã tách file Dumpert và SharpRDP dùng để phát triển). Báo nhầm trên 3.290 phiên bình thường chưa dùng chỉnh: 19 (0,58%) không SLM, 8 (0,24%) có SLM. SLM `phi4-mini` chưa giúp: phần giảm báo giả là do bước kiểm chứng, và SLM làm mất 1 phát hiện thật. Báo giả thấp nhờ agent thận trọng, nhưng cái giá là bỏ sót nhiều ca ngắn hoặc chỉ sửa registry.
