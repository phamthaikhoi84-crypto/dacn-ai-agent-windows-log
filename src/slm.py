
import json
import os
import re
import time
import urllib.request
import urllib.error


OLLAMA_URL = "http://localhost:11434/api/chat"

# Khi SLM lỗi (bị cắt, JSON hỏng), lưu prompt và câu trả lời thô vào đây để xem lại
FILE_LOI = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output", "slm_loi_cuoi.txt")

# Cho phép đổi model bằng biến môi trường SLM_MODEL
MODEL_CHINH = os.environ.get("SLM_MODEL", "phi4-mini:latest")

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
    """Ghi đè file output/slm_loi_cuoi.txt: lý do lỗi, prompt đã gửi, câu trả lời thô của mô hình."""
    try:
        os.makedirs(os.path.dirname(FILE_LOI), exist_ok=True)
        with open(FILE_LOI, "w", encoding="utf-8") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} | model {MODEL_CHINH} | {ly_do}\n\n"
                    f"===== PROMPT =====\n{yeu_cau}\n\n===== MÔ HÌNH TRẢ VỀ =====\n{noi_dung}\n")
    except OSError:
        pass


def _ket_qua_loi(ly_do):
    """Lỗi kỹ thuật (Ollama không trả lời, lỗi HTTP, JSON bị cắt hoặc sai cấu trúc).
    Có thêm "loi": True để agent tách riêng loại "SLM lỗi", không gộp vào "chưa xác nhận".
    Khác với trường hợp mô hình trả lời bình thường nhưng chọn CHUA_XAC_NHAN, chọn mã ngoài danh sách
    hoặc bịa bằng chứng: các trường hợp đó là câu trả lời của mô hình, không phải lỗi."""
    kq = _ket_qua_chua_xac_nhan(ly_do)
    kq["loi"] = True
    return kq
def _kiem_tra_lsass_vm_read(chuoi_text):
    """
    Kiểm tra log có Event ID 10 nhắm vào LSASS
    và GrantedAccess chứa PROCESS_VM_READ hay không.
    """

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

        gia_tri = match.group(1)

        try:
            quyen = int(gia_tri, 0)
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


def goi_slm(chuoi_su_kien, danh_sach_ung_vien, model=MODEL_CHINH):
    """
    Phân tích log Windows/Sysmon bằng Ollama.

    Kết quả:
    - ma_ky_thuat
    - bang_chung
    - ly_do
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
    log_danh_so = "\n".join(f"L{i}: {d}" for i, d in enumerate(cac_dong, 1))

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
            ma_hop_le.append(ma.strip())

    if not ma_hop_le:
        return _ket_qua_chua_xac_nhan(
            "Danh sách ứng viên không có mã kỹ thuật hợp lệ."
        )
    ds_ung_vien = "\n".join(f"- {m}: {TEN_KY_THUAT.get(m, 'không rõ tên')}" for m in ma_hop_le)
    # 3. Prompt phân tích

    yeu_cau = f"""Bạn là chuyên gia phân tích log Windows/Sysmon và MITRE ATT&CK.

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
        "format": "json",
        "options": {
            "temperature": 0,
            "num_ctx": 8192,
            "num_predict": 1024
        }
    }

    request = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    # 4. Gọi Ollama
    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            noi_dung_phan_hoi = response.read().decode("utf-8")

        phan_hoi = json.loads(noi_dung_phan_hoi)

    except urllib.error.HTTPError as loi:
        return _ket_qua_loi(
            f"Ollama lỗi HTTP {loi.code}: {loi.reason}"
        )

    except (urllib.error.URLError, TimeoutError) as loi:
        return _ket_qua_loi(
            f"Không gọi được Ollama: {loi}"
        )

    except OSError as loi:              # vd ConnectionResetError khi Ollama bị tắt giữa chừng
        return _ket_qua_loi(
            f"Mất kết nối với Ollama: {loi}"
        )

    except (json.JSONDecodeError, UnicodeDecodeError) as loi:
        return _ket_qua_loi(
            f"Phản hồi Ollama không hợp lệ: {loi}"
        )

    # 5. Kiểm tra phản hồi
    thong_tin = phan_hoi.get("message", {})
    noi_dung = thong_tin.get("content", "")
    ly_do_dung = phan_hoi.get("done_reason", "")

    bi_cat = phan_hoi.get("done") is False or ly_do_dung == "length"

    # 6. Đọc JSON (kể cả khi bị cắt: mô hình có thể đã viết xong JSON rồi mới sinh thêm khoảng trắng thừa)
    try:
        du_lieu = _doc_json(noi_dung)
    except (ValueError, TypeError) as loi:
        _luu_loi("bị cắt" if bi_cat else f"JSON hỏng: {loi}", yeu_cau, noi_dung)
        if bi_cat:
            return _ket_qua_loi("Phản hồi SLM bị giới hạn độ dài.")
        return _ket_qua_loi(
            f"Kết quả mô hình không hợp lệ: {loi}"
        )

    if not isinstance(du_lieu, dict):
        return _ket_qua_loi(
            "JSON SLM không phải một đối tượng."
        )

    ma = du_lieu.get("ma_ky_thuat")
    bang_chung = du_lieu.get("bang_chung")
    ly_do = du_lieu.get("ly_do")

    # 7. Kiểm tra cấu trúc
    if not isinstance(ma, str):
        return _ket_qua_loi(
            "JSON không có ma_ky_thuat dạng chuỗi."
        )

    if not isinstance(bang_chung, list):
        return _ket_qua_loi(
            "JSON không có bang_chung dạng danh sách."
        )

    if not isinstance(ly_do, str):
        return _ket_qua_loi(
            "JSON không có ly_do dạng chuỗi."
        )

    ma = ma.strip()
    ly_do = ly_do.strip()
    tim_ma = re.search(r"T\d{4}(?:\.\d{3})?", ma)
    if ma != "CHUA_XAC_NHAN" and tim_ma:
        ma = tim_ma.group(0)   # mô hình có thể trả "T1003.001 - LSASS Memory": chỉ lấy phần mã

    # 8. Kiểm tra mã kỹ thuật
    if ma != "CHUA_XAC_NHAN" and ma not in ma_hop_le:
        return _ket_qua_chua_xac_nhan(
            f"Mô hình chọn kỹ thuật ngoài danh sách ứng viên: {du_lieu.get('ma_ky_thuat')}"
        )

    # 9. Kiểm tra bằng chứng nguyên văn
    bang_chung_hop_le = []

    for muc in bang_chung:
        so = None
        if isinstance(muc, int) and not isinstance(muc, bool):
            so = muc
        elif isinstance(muc, str):
            tim = re.fullmatch(r"\s*L?(\d+)\s*", muc, re.IGNORECASE)
            if tim:
                so = int(tim.group(1))
            else:                                   # mô hình vẫn chép nguyên dòng: chấp nhận nếu có thật trong log
                dong = re.sub(r"^\s*L\d+:\s*", "", muc).strip()
                if dong and dong in chuoi_text:
                    bang_chung_hop_le.append(dong)
                continue
        if so is not None and 1 <= so <= len(cac_dong) and cac_dong[so - 1] not in bang_chung_hop_le:
            bang_chung_hop_le.append(cac_dong[so - 1])   # số dòng ngoài phạm vi thì bỏ (coi như bịa)

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



def chon_ky_thuat(dong_log, ung_vien):
    """Giao diện tương thích với agent.py."""
    return goi_slm(dong_log, ung_vien)


if __name__ == "__main__":

    chuoi_thu = [
        "EventID=1 Image=powershell.exe CommandLine=powershell.exe -Command Get-Process",
        "EventID=1 Image=cmd.exe CommandLine=cmd.exe /c whoami"
    ]

    ung_vien_thu = [
        {
            "ma_ky_thuat": "T1059.001",
            "ten": "PowerShell"
        },
        {
            "ma_ky_thuat": "T1059.003",
            "ten": "Windows Command Shell"
        }
    ]

    ket_qua = goi_slm(chuoi_thu, ung_vien_thu)

    print("MODEL:", MODEL_CHINH)
    print("KET QUA SLM:")
    print(json.dumps(ket_qua, ensure_ascii=False, indent=2))
