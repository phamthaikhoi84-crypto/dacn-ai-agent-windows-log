import json
import os
import re
import socket
import sys
import time
import urllib.request
import urllib.error


OLLAMA_URL = "http://localhost:11434/api/chat"

# Mỗi lần SLM lỗi (bị cắt, JSON sai cấu trúc, Ollama lỗi HTTP), GHI THÊM prompt và câu trả lời thô vào đây
FILE_LOI = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "output",
    "slm_loi.txt"
)
# Timeout tối đa 600 giây; laptop chạy Ollama 100% CPU, prompt 40 dòng có lần mất trên 240 giây
THOI_GIAN_CHO = 600
SO_LAN_THU = 2
# Cho phép đổi model bằng biến môi trường SLM_MODEL
MODEL_CHINH = os.environ.get("SLM_MODEL", "phi4-mini:latest")

# Chỉ bật prompt mới khi SLM_PROMPT_MOI=1.
SLM_PROMPT_MOI = os.environ.get("SLM_PROMPT_MOI", "0").strip() == "1"
# Tên chính thức của 8 kỹ thuật: đưa vào prompt để mô hình không tự đặt tên sai
TEN_KY_THUAT = {
    "T1003.001": "OS Credential Dumping: LSASS Memory (đánh cắp thông tin đăng nhập từ bộ nhớ LSASS)",
    "T1021.001": "Remote Services: Remote Desktop Protocol",
    "T1053.005": "Scheduled Task/Job: Scheduled Task",
    "T1059.001": "Command and Scripting Interpreter: PowerShell",
    "T1070.001": "Indicator Removal: Clear Windows Event Logs",
    "T1105": "Ingress Tool Transfer",
    "T1136.001": "Create Account: Local Account",
    "T1547.001": "Boot or Logon Autostart Execution: Registry Run Keys / Startup Folder",
}


def _ket_qua_chua_xac_nhan(ly_do):
    return {
        "ma_ky_thuat": "CHUA_XAC_NHAN",
        "bang_chung": [],
        "ly_do": ly_do
    }


def _luu_loi(ly_do, yeu_cau, noi_dung):
    """Ghi thêm prompt và phản hồi lỗi vào output/slm_loi.txt."""
    try:
        os.makedirs(os.path.dirname(FILE_LOI), exist_ok=True)

        with open(FILE_LOI, "a", encoding="utf-8") as f:
            f.write(
                f"\n{'#' * 78}\n"
                f"{time.strftime('%Y-%m-%d %H:%M:%S')} | "
                f"model {MODEL_CHINH} | {ly_do}\n\n"
                f"===== PROMPT =====\n{yeu_cau}\n\n"
                f"===== MÔ HÌNH TRẢ VỀ =====\n{noi_dung}\n"
            )
    except OSError:
        pass


def _loi(ly_do, yeu_cau, noi_dung=""):
    _luu_loi(ly_do, yeu_cau, noi_dung)
    return _ket_qua_loi(ly_do)


def _khuon_json(ma_hop_le, cho_binh_thuong=False):
    """Tạo JSON schema tương ứng với chế độ prompt."""

    cac_ma = list(ma_hop_le)

    if cho_binh_thuong:
        cac_ma.append("BINH_THUONG")

    cac_ma.append("CHUA_XAC_NHAN")

    return {
        "type": "object",
        "properties": {
            "ma_ky_thuat": {
                "type": "string",
                "enum": cac_ma
            },
            "bang_chung": {
                "type": "array",
                "items": {"type": "integer"},
                "maxItems": 3
            },
            "ly_do": {
                "type": "string",
                "maxLength": 300
            },
        },
        "required": ["ma_ky_thuat", "bang_chung", "ly_do"],
    }


def _ket_qua_loi(ly_do):
    kq = _ket_qua_chua_xac_nhan(ly_do)
    kq["loi"] = True
    return kq


def _kiem_tra_lsass_vm_read(chuoi_text):
    """Giữ lại hàm kiểm tra LSASS của phiên bản cũ."""
    cac_dong = chuoi_text.splitlines()

    for dong in cac_dong:
        # Phải là Event ID 10
        if not re.search(r'EventID\s*[=:]\s*10\b', dong, re.IGNORECASE):
            continue

        # Phải nhắm vào lsass.exe
        if not re.search(r'lsass\.exe', dong, re.IGNORECASE):
            continue

        # Lấy GrantedAccess
        match = re.search(
            r'GrantedAccess\s*[=:]\s*["\']?(0x[0-9a-fA-F]+|\d+)',
            dong,
            re.IGNORECASE
        )

        if not match:
            continue

        try:
            quyen = int(match.group(1), 0)
        except ValueError:
            continue

        # PROCESS_VM_READ = 0x0010
        if (quyen & 0x0010) != 0:
            return True

    return False


def _doc_json(noi_dung):
    """Đọc JSON kể cả khi mô hình có chữ thừa bên ngoài."""

    if not isinstance(noi_dung, str) or not noi_dung.strip():
        raise ValueError("Ollama trả về nội dung rỗng.")

    noi_dung = noi_dung.strip()

    try:
        return json.loads(noi_dung)
    except json.JSONDecodeError:
        pass

    bo_doc = json.JSONDecoder()

    for vi_tri, ky_tu in enumerate(noi_dung):
        if ky_tu == "{":
            try:
                du_lieu, _ = bo_doc.raw_decode(noi_dung[vi_tri:])
                return du_lieu
            except json.JSONDecodeError:
                continue

    raise ValueError("Không tìm thấy JSON hoàn chỉnh.")


def _tao_thong_tin_bang_chung(dau_vet_ung_vien, ma_hop_le):
    """Chuyển trạng thái bằng chứng DuckDB thành văn bản cho prompt mới."""

    if not isinstance(dau_vet_ung_vien, dict):
        return "Không có dữ liệu bằng chứng từ DuckDB."

    cac_muc = []

    for ma in ma_hop_le:
        dv = dau_vet_ung_vien.get(ma)

        if not isinstance(dv, dict):
            cac_muc.append(
                f"- {ma}: KHÔNG CÓ DỮ LIỆU BẰNG CHỨNG."
            )
            continue

        du = dv.get("du") is True
        thieu = dv.get("thieu", [])
        bang_chung = dv.get("bang_chung", [])

        trang_thai = (
            "ĐỦ BẰNG CHỨNG BẮT BUỘC"
            if du else
            "CHƯA ĐỦ BẰNG CHỨNG BẮT BUỘC"
        )

        cac_muc.append(f"- {ma}: {trang_thai}")

        if thieu:
            cac_muc.append(
                "  Bằng chứng còn thiếu: "
                + "; ".join(str(x) for x in thieu)
            )

        for muc in bang_chung:
            if not isinstance(muc, (list, tuple)) or len(muc) < 2:
                continue

            ten, cac_dong = muc[0], muc[1]

            cac_muc.append(f"  Loại bằng chứng: {ten}")

            if isinstance(cac_dong, (list, tuple)):
                for dong in cac_dong[:3]:
                    cac_muc.append(f"    {str(dong)[:500]}")

    return "\n".join(cac_muc)


def _tao_prompt_cu(ds_ung_vien, log_danh_so):
    """Prompt cũ: giữ nguyên nội dung và quy tắc."""

    return f"""Bạn là chuyên gia phân tích log Windows/Sysmon và MITRE ATT&CK.

NHIỆM VỤ: đọc các dòng log dưới đây (mỗi dòng là 1 sự kiện, bắt đầu bằng số dòng L1, L2...; số trong ngoặc vuông là Event ID)
và chọn MỘT kỹ thuật phù hợp nhất trong danh sách ứng viên, hoặc CHUA_XAC_NHAN nếu log không cho thấy kỹ thuật nào.

DANH SÁCH ỨNG VIÊN (mã: tên chính thức):
{ds_ung_vien}

LOG:
{log_danh_so}

QUY TẮC:
1. Chỉ được chọn mã có trong danh sách ứng viên, hoặc CHUA_XAC_NHAN.
2. Với Event ID 10, phần sau dấu "->" đã cho biết tiến trình có đọc được bộ nhớ hay không. Dựa vào đó, KHÔNG tự tính bit.
3. bang_chung: ghi SỐ DÒNG của 1 đến 3 dòng log quan trọng nhất, ví dụ [2, 3]. KHÔNG chép lại nội dung dòng.
4. Nếu chọn CHUA_XAC_NHAN thì bang_chung là [].
5. ly_do: tiếng Việt, 1 câu ngắn, chỉ dựa trên các dòng đã chọn.
6. ma_ky_thuat chỉ ghi MÃ (ví dụ T1003.001), không ghi kèm tên. Nếu nhắc tên kỹ thuật trong ly_do thì dùng đúng tên trong danh sách ứng viên.

CHỈ TRẢ VỀ MỘT JSON:
{{"ma_ky_thuat": "...", "bang_chung": [2], "ly_do": "..."}}
"""



def _tao_prompt_moi(ds_ung_vien, log_danh_so, thong_tin_bang_chung):
    """Prompt v2: đánh giá độc lập từng ứng viên, giữ nguyên hàng rào bằng chứng."""

    return f"""Bạn là chuyên gia phân tích log Windows/Sysmon và MITRE ATT&CK.

NHIỆM VỤ:
Phân tích log của một phiên hoạt động Windows.
Đánh giá các kỹ thuật trong danh sách ứng viên dựa trên:
1. Hành vi thực tế thể hiện trong log.
2. Trạng thái bằng chứng bắt buộc được kiểm tra bởi DuckDB.

Chỉ được chọn MỘT kết quả cuối cùng:
- Mã kỹ thuật có trong danh sách ứng viên.
- BINH_THUONG.
- CHUA_XAC_NHAN.

DANH SÁCH ỨNG VIÊN:
{ds_ung_vien}

TRẠNG THÁI BẰNG CHỨNG TỪ DUCKDB:
{thong_tin_bang_chung}

LOG ĐƯỢC ĐÁNH SỐ:
{log_danh_so}

QUY TẮC PHÂN TÍCH BẮT BUỘC:

1. NGUYÊN TẮC ĐÁNH GIÁ ĐỘC LẬP

- Đánh giá từng kỹ thuật trong danh sách ứng viên một cách độc lập.
- Không để trạng thái thiếu bằng chứng của một ứng viên
  ảnh hưởng đến việc đánh giá các ứng viên còn lại.
- Không sử dụng bằng chứng của kỹ thuật này để xác nhận
  kỹ thuật khác.
- Không mặc định ứng viên có điểm cao nhất là kỹ thuật đúng.
- Không coi tên kỹ thuật, tên tiến trình hoặc điểm số là bằng chứng.

2. KIỂM TRA TỪNG ỨNG VIÊN

Với MỖI ứng viên, lần lượt thực hiện:

BƯỚC A - KIỂM TRA BẰNG CHỨNG DUCKDB:
- Đọc trạng thái bằng chứng bắt buộc của chính ứng viên đó.
- Nếu CHƯA ĐỦ bằng chứng bắt buộc:
  + Không được chọn kỹ thuật đó làm kết quả.
  + Không tự tạo, suy diễn hoặc bổ sung bằng chứng còn thiếu.
  + Tiếp tục đánh giá các ứng viên khác.
- Nếu ĐỦ bằng chứng bắt buộc:
  + Chuyển sang kiểm tra hành vi thực tế trong log.

BƯỚC B - ĐỐI CHIẾU HÀNH VI:
- Kiểm tra log có thực sự thể hiện hành vi của kỹ thuật không.
- Bằng chứng phải liên quan trực tiếp đến hành vi đang đánh giá.
- Xem xét tiến trình, dòng lệnh, Event ID, thông tin sự kiện
  và chuỗi hoạt động có liên quan.
- Nếu bằng chứng đủ nhưng hành vi không phù hợp,
  không được kết luận kỹ thuật đó.
- Không suy luận hành vi tấn công chỉ từ tên tiến trình.

BƯỚC C - ĐÁNH GIÁ KẾT QUẢ CỦA ỨNG VIÊN:
- Chỉ đánh giá ứng viên là phù hợp khi đồng thời:
  + Nằm trong danh sách ứng viên.
  + DuckDB xác nhận đủ bằng chứng bắt buộc.
  + Log thể hiện hành vi tương ứng.
  + Có ít nhất một dòng log trực tiếp hỗ trợ nhận định.

3. CÁC LƯU Ý VỀ LOG WINDOWS/SYSMON

- Event ID 3 thể hiện kết nối mạng.
  Không thể chỉ dựa vào Event ID 3 để kết luận tạo tài khoản,
  xóa log, thực thi PowerShell hoặc đánh cắp thông tin xác thực.

- Event ID 1 thể hiện tạo tiến trình.
  Phải xem xét tiến trình cha, tiến trình con, dòng lệnh
  và ngữ cảnh thực thi.

- Event ID 10 thể hiện truy cập tiến trình.
  Phải xem xét TargetImage, SourceImage, GrantedAccess
  và trạng thái bằng chứng DuckDB.

- Tên tiến trình như svchost.exe, msiexec.exe, net.exe
  không tự chứng minh có hành vi tấn công.

- Tên tiến trình đáng ngờ cũng không đủ để kết luận tấn công
  nếu thiếu hành vi và bằng chứng trực tiếp.

4. LỰA CHỌN KẾT QUẢ CUỐI CÙNG

Sau khi đánh giá độc lập TẤT CẢ ứng viên, chọn một kết quả:

A. KẾT LUẬN KỸ THUẬT:
Chỉ chọn một mã kỹ thuật khi có ứng viên đáp ứng đầy đủ:
- Có trong danh sách ứng viên.
- Đủ bằng chứng bắt buộc từ DuckDB.
- Log thể hiện hành vi tương ứng.
- Có bằng chứng trực tiếp trong log.

Nếu nhiều ứng viên cùng đáp ứng:
- Chọn kỹ thuật được bằng chứng trực tiếp hỗ trợ rõ ràng nhất.
- Không dùng bằng chứng của ứng viên này để hỗ trợ ứng viên khác.
- Không chọn chỉ dựa vào điểm số.

B. BINH_THUONG:
Chọn BINH_THUONG khi:
- Không có ứng viên nào đáp ứng đủ điều kiện kết luận tấn công.
- Các hoạt động trong log có ngữ cảnh bình thường
  hoặc được giải thích hợp lý.
- Không còn hành vi đáng ngờ chưa được giải thích.
- Không có dữ liệu mâu thuẫn đáng kể.

Ví dụ:
- Quản trị viên chạy Sysmon64.exe -c để cập nhật cấu hình.
- Người dùng mở tệp cấu hình Sysmon bằng Notepad.
- Các hoạt động quản trị Windows có ngữ cảnh hợp lý.

Không được chọn BINH_THUONG chỉ vì thiếu bằng chứng DuckDB.

C. CHUA_XAC_NHAN:
Chọn CHUA_XAC_NHAN khi:
- Có hành vi đáng ngờ nhưng chưa đủ bằng chứng bắt buộc.
- Mục đích hoạt động chưa rõ.
- Thiếu dữ liệu quan trọng.
- Các sự kiện mâu thuẫn hoặc không đủ ngữ cảnh
  để phân biệt hoạt động bình thường và tấn công.

Không được chọn CHUA_XAC_NHAN chỉ vì:
- Có ứng viên trong danh sách.
- Điểm số ứng viên cao.
- Một ứng viên không đủ bằng chứng,
  trong khi các hoạt động còn lại đã được giải thích bình thường.

5. THỨ TỰ ƯU TIÊN

- Đủ bằng chứng kỹ thuật và hành vi phù hợp:
  chọn mã kỹ thuật.
- Không có kỹ thuật đủ điều kiện, hoạt động bình thường
  và không còn dấu hiệu đáng ngờ:
  chọn BINH_THUONG.
- Có dấu hiệu đáng ngờ nhưng chưa xác minh được:
  chọn CHUA_XAC_NHAN.

6. QUY TẮC BẰNG CHỨNG ĐẦU RA

Nếu chọn mã kỹ thuật:
- bang_chung phải chứa từ 1 đến 3 số thứ tự dòng log.
- Chỉ chọn dòng log có nội dung trực tiếp hỗ trợ hành vi.
- Không chọn dòng chỉ thể hiện quan hệ thời gian hoặc phiên.
- Không tạo số dòng không tồn tại.
- Không dùng bằng chứng của kỹ thuật khác.

Nếu chọn BINH_THUONG hoặc CHUA_XAC_NHAN:
- bang_chung phải là [].

7. QUY TẮC LÝ DO

- ly_do phải viết bằng tiếng Việt.
- Chỉ viết một câu ngắn.
- Chỉ dựa trên log và trạng thái bằng chứng được cung cấp.
- Không khẳng định hành vi chưa được xác minh.
- Không tự bổ sung thông tin ngoài dữ liệu đầu vào.

8. ĐỊNH DẠNG ĐẦU RA

- ma_ky_thuat chỉ ghi mã kỹ thuật, ví dụ T1003.001.
- Nếu bình thường, ghi BINH_THUONG.
- Nếu chưa xác nhận, ghi CHUA_XAC_NHAN.
- bang_chung là danh sách số nguyên.
- Không thêm Markdown, lời giải thích hoặc nội dung ngoài JSON.

CHỈ TRẢ VỀ MỘT JSON:
{{"ma_ky_thuat": "...", "bang_chung": [2], "ly_do": "..."}}
"""



def goi_slm(
    chuoi_su_kien,
    danh_sach_ung_vien,
    model=MODEL_CHINH,
    dau_vet_ung_vien=None
):
    """
    Phân tích log Windows/Sysmon bằng Ollama.

    Chế độ cũ: chỉ chọn kỹ thuật hoặc CHUA_XAC_NHAN.
    Chế độ mới: có thêm BINH_THUONG và trạng thái bằng chứng DuckDB.
    """

    # 1. Chuẩn hóa đầu vào
    if isinstance(chuoi_su_kien, str):
        cac_dong = chuoi_su_kien.splitlines()
    else:
        cac_dong = [str(d) for d in chuoi_su_kien]

    cac_dong = [d for d in cac_dong if d.strip()]
    chuoi_text = "\n".join(cac_dong)

    # Đánh số dòng (L1, L2, ...): mô hình chỉ cần trả số dòng làm bằng chứng, không phải chép lại cả dòng.
    # Chép lại dòng dài (đường dẫn đầy đủ, tiếng Việt) làm mô hình nhỏ viết quá giới hạn token và JSON bị cắt.
    log_danh_so = "\n".join(
        f"L{i}: {d}"
        for i, d in enumerate(cac_dong, 1)
    )

    if not chuoi_text.strip():
        return _ket_qua_chua_xac_nhan("Chuỗi sự kiện đầu vào rỗng.")

    if not danh_sach_ung_vien:
        return _ket_qua_chua_xac_nhan("Không có kỹ thuật ứng viên.")

    # 2. Lấy danh sách mã kỹ thuật hợp lệ
    ma_hop_le = []

    for ung_vien in danh_sach_ung_vien:
        if isinstance(ung_vien, str):
            ma = ung_vien
        elif isinstance(ung_vien, dict):
            ma = ung_vien.get("ma_ky_thuat", "")
        else:
            continue

        if isinstance(ma, str) and ma.strip():
            ma = ma.strip()
            if ma not in ma_hop_le:
                ma_hop_le.append(ma)

    if not ma_hop_le:
        return _ket_qua_chua_xac_nhan(
            "Danh sách ứng viên không có mã kỹ thuật hợp lệ."
        )

    ds_ung_vien = "\n".join(
        f"- {m}: {TEN_KY_THUAT.get(m, 'không rõ tên')}"
        for m in ma_hop_le
    )

    # 3. Chọn prompt và schema tương ứng
    if SLM_PROMPT_MOI:
        thong_tin_bang_chung = _tao_thong_tin_bang_chung(
            dau_vet_ung_vien,
            ma_hop_le
        )

        yeu_cau = _tao_prompt_moi(
            ds_ung_vien,
            log_danh_so,
            thong_tin_bang_chung
        )
    else:
        yeu_cau = _tao_prompt_cu(
            ds_ung_vien,
            log_danh_so
        )

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Bạn là bộ phân tích log bảo mật Windows. "
                    "Phân tích bằng chứng chính xác. "
                    "Chỉ trả về một JSON hợp lệ, không thêm Markdown."
                )
            },
            {
                "role": "user",
                "content": yeu_cau
            }
        ],
        "stream": False,
        "format": _khuon_json(
            ma_hop_le,
            cho_binh_thuong=SLM_PROMPT_MOI
        ),
        "options": {
            "temperature": 0,
            "num_ctx": 8192,
            "num_predict": 1024
        }
    }

    request = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(
            payload,
            ensure_ascii=False
        ).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    # 4. Gọi Ollama
    phan_hoi = None

    # Lỗi HTTP 500 hoặc mất kết nối thì thử lại một lần.
    for lan in range(1, SO_LAN_THU + 1):
        try:
            with urllib.request.urlopen(
                request,
                timeout=THOI_GIAN_CHO
            ) as response:
                noi_dung_phan_hoi = response.read().decode("utf-8")

            phan_hoi = json.loads(noi_dung_phan_hoi)
            break

        except urllib.error.HTTPError as loi:
            try:
                than = loi.read().decode("utf-8", "replace")[:500]
            except Exception:
                than = ""

            if loi.code >= 500 and lan < SO_LAN_THU:
                _luu_loi(
                    f"Ollama lỗi HTTP {loi.code} lần {lan}, thử lại",
                    yeu_cau,
                    than
                )
                time.sleep(5)
                continue

            return _loi(
                f"Ollama lỗi HTTP {loi.code}: {loi.reason} {than}".strip(),
                yeu_cau,
                than
            )

        except (TimeoutError, socket.timeout) as loi:
            return _loi(
                f"Ollama không trả lời sau {THOI_GIAN_CHO} giây: {loi}",
                yeu_cau
            )

        except (urllib.error.URLError, OSError) as loi:
            if lan < SO_LAN_THU:
                time.sleep(5)
                continue

            return _loi(
                f"Không gọi được Ollama: {loi}",
                yeu_cau
            )

        except (json.JSONDecodeError, UnicodeDecodeError) as loi:
            return _loi(
                f"Phản hồi Ollama không hợp lệ: {loi}",
                yeu_cau
            )

    # 5. Kiểm tra phản hồi
    if not isinstance(phan_hoi, dict):
        return _loi("Phản hồi Ollama không hợp lệ.", yeu_cau)

    # Ghi số token prompt Ollama thực sự xử lý ra stderr.
    so_token_prompt = phan_hoi.get('prompt_eval_count')
    if isinstance(so_token_prompt, int) and not isinstance(so_token_prompt, bool):
        ti_le_context = so_token_prompt / 8192 * 100
        print(
            f"[SLM-DO-LUONG] prompt_eval_count={so_token_prompt}; num_ctx=8192; su_dung={ti_le_context:.1f}%",
            file=sys.stderr,
            flush=True
        )
    else:
        print(
            "[SLM-DO-LUONG] Ollama khong tra prompt_eval_count; num_ctx=8192",
            file=sys.stderr,
            flush=True
        )

    thong_tin = phan_hoi.get("message", {})
    noi_dung = thong_tin.get("content", "")
    ly_do_dung = phan_hoi.get("done_reason", "")

    bi_cat = (
        phan_hoi.get("done") is False
        or ly_do_dung == "length"
    )

    # 6. Đọc JSON (kể cả khi bị cắt: mô hình có thể đã viết xong JSON rồi mới sinh thêm khoảng trắng thừa)
    try:
        du_lieu = _doc_json(noi_dung)
    except (ValueError, TypeError) as loi:
        if bi_cat:
            return _loi(
                "Phản hồi SLM bị giới hạn độ dài.",
                yeu_cau,
                noi_dung
            )

        return _loi(
            f"Kết quả mô hình không hợp lệ: {loi}",
            yeu_cau,
            noi_dung
        )

    if not isinstance(du_lieu, dict):
        return _loi(
            "JSON SLM không phải một đối tượng.",
            yeu_cau,
            noi_dung
        )

    ma = du_lieu.get("ma_ky_thuat")
    bang_chung = du_lieu.get("bang_chung")
    ly_do = du_lieu.get("ly_do")

    # 7. Kiểm tra cấu trúc
    if not isinstance(ma, str):
        return _loi(
            "JSON không có ma_ky_thuat dạng chuỗi.",
            yeu_cau,
            noi_dung
        )

    if not isinstance(bang_chung, list):
        return _loi(
            "JSON không có bang_chung dạng danh sách.",
            yeu_cau,
            noi_dung
        )

    if not isinstance(ly_do, str):
        return _loi(
            "JSON không có ly_do dạng chuỗi.",
            yeu_cau,
            noi_dung
        )

    ma = ma.strip()
    ly_do = ly_do.strip()

    tim_ma = re.search(r"T\d{4}(?:\.\d{3})?", ma)

    if ma not in ("CHUA_XAC_NHAN", "BINH_THUONG") and tim_ma:
        ma = tim_ma.group(0)

    # 8. Kiểm tra BINH_THUONG
    if ma == "BINH_THUONG":
        if not SLM_PROMPT_MOI:
            return _ket_qua_chua_xac_nhan(
                "Prompt cũ không cho phép kết quả BINH_THUONG."
            )

        if bang_chung:
            return _ket_qua_chua_xac_nhan(
                "Kết quả BINH_THUONG không được chứa bằng chứng."
            )

        return {
            "ma_ky_thuat": "BINH_THUONG",
            "bang_chung": [],
            "ly_do": ly_do
        }

    # Mã kỹ thuật phải thuộc danh sách ứng viên.
    # 9. Kiểm tra mã kỹ thuật
    if ma != "CHUA_XAC_NHAN" and ma not in ma_hop_le:
        return _ket_qua_chua_xac_nhan(
            "Mô hình chọn kỹ thuật ngoài danh sách ứng viên: "
            + str(du_lieu.get("ma_ky_thuat"))
        )

    # Chỉ chấp nhận bằng chứng có thật trong log.
    # 10. Kiểm tra bằng chứng nguyên văn
    bang_chung_hop_le = []

    for muc in bang_chung:
        so = None

        if isinstance(muc, int) and not isinstance(muc, bool):
            so = muc

        elif isinstance(muc, str):
            tim = re.fullmatch(
                r"\s*L?(\d+)\s*",
                muc,
                re.IGNORECASE
            )

            if tim:
                so = int(tim.group(1))
            else:
                dong = re.sub(
                    r"^\s*L\d+:\s*",
                    "",
                    muc
                ).strip()

                if dong and dong in chuoi_text:
                    bang_chung_hop_le.append(dong)

                continue

        if (
            so is not None
            and 1 <= so <= len(cac_dong)
            and cac_dong[so - 1] not in bang_chung_hop_le
        ):
            bang_chung_hop_le.append(cac_dong[so - 1])

    if ma == "CHUA_XAC_NHAN":
        return {
            "ma_ky_thuat": "CHUA_XAC_NHAN",
            "bang_chung": [],
            "ly_do": ly_do
        }

    if not bang_chung_hop_le:
        return _ket_qua_chua_xac_nhan(
            "Không xác minh được bằng chứng nguyên văn trong log."
        )

    return {
        "ma_ky_thuat": ma,
        "bang_chung": bang_chung_hop_le[:3],
        "ly_do": ly_do
    }


def chon_ky_thuat(
    dong_log,
    ung_vien,
    dau_vet_ung_vien=None
):
    """Giao diện tương thích với agent.py và bộ đánh giá D2/D3."""

    return goi_slm(
        dong_log,
        ung_vien,
        dau_vet_ung_vien=dau_vet_ung_vien
    )
