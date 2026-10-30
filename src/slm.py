
import json
import urllib.request
import urllib.error


OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_CHINH = "llama3.2:3b"


def _ket_qua_chua_xac_nhan(ly_do):
    return {
        "ma_ky_thuat": "CHUA_XAC_NHAN",
        "bang_chung": [],
        "ly_do": ly_do
    }


def _doc_json(noi_dung):
    """
    Đọc JSON từ nội dung Ollama.
    Hỗ trợ cả trường hợp mô hình thêm chữ ngoài JSON.
    """
    if not isinstance(noi_dung, str) or not noi_dung.strip():
        raise ValueError("Ollama trả về nội dung rỗng.")

    noi_dung = noi_dung.strip()

    # Thử đọc trực tiếp trước
    try:
        return json.loads(noi_dung)
    except json.JSONDecodeError:
        pass

    # Nếu có chữ thừa bên ngoài, tìm đối tượng JSON đầu tiên
    bo_doc = json.JSONDecoder()

    for vi_tri, ky_tu in enumerate(noi_dung):
        if ky_tu == "{":
            try:
                du_lieu, _ = bo_doc.raw_decode(noi_dung[vi_tri:])
                return du_lieu
            except json.JSONDecodeError:
                continue

    raise ValueError("Không tìm thấy JSON hoàn chỉnh trong phản hồi của Ollama.")


def goi_slm(chuoi_su_kien, danh_sach_ung_vien, model=MODEL_CHINH):
    """
    Phân tích chuỗi sự kiện Windows/Sysmon bằng Ollama.

    Kết quả gồm:
    - ma_ky_thuat
    - bang_chung
    - ly_do
    """

    # 1. Chuẩn hóa dữ liệu đầu vào
    if isinstance(chuoi_su_kien, str):
        chuoi_text = chuoi_su_kien
    else:
        chuoi_text = json.dumps(
            chuoi_su_kien,
            ensure_ascii=False,
            default=str
        )

    if not chuoi_text.strip():
        return _ket_qua_chua_xac_nhan("Chuỗi sự kiện đầu vào rỗng.")

    if not danh_sach_ung_vien:
        return _ket_qua_chua_xac_nhan(
            "Không có kỹ thuật ứng viên."
        )

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

    # 3. Tạo yêu cầu ngắn, yêu cầu bằng chứng ngắn để giảm đầu ra
    yeu_cau = f"""
Phân tích log Windows/Sysmon và phân loại MITRE ATT&CK.

DANH SÁCH ỨNG VIÊN:
{json.dumps(danh_sach_ung_vien, ensure_ascii=False, default=str)}

LOG:
{chuoi_text}

QUY TẮC:
- Chỉ chọn mã kỹ thuật có trong danh sách ứng viên.
- Không suy diễn. Chỉ kết luận khi log có bằng chứng trực tiếp.
- Nếu thiếu bằng chứng, chọn CHUA_XAC_NHAN.
- Nếu ứng viên là T1003.001 (LSASS Memory): chỉ thấy tiến trình truy cập
  lsass.exe chưa đủ kết luận đánh cắp thông tin xác thực.
  Với Event ID 10, phải kiểm tra GrantedAccess có bit PROCESS_VM_READ
  (0x0010) hay không. Nếu không có thì không xác nhận T1003.001.
- bang_chung chỉ ghi 1 đến 3 đoạn ngắn trích nguyên văn từ log,
  không chép lại toàn bộ dòng dài.
- Nếu CHUA_XAC_NHAN, bang_chung phải là [].
- ly_do giải thích ngắn gọn bằng tiếng Việt.

CHỈ TRẢ VỀ MỘT JSON HỢP LỆ, đúng cấu trúc:
{{
  "ma_ky_thuat": "mã kỹ thuật hoặc CHUA_XAC_NHAN",
  "bang_chung": ["đoạn log nguyên văn"],
  "ly_do": "giải thích ngắn"
}}
"""

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Bạn là bộ phân tích log bảo mật Windows. "
                    "Trả lời đúng một JSON hợp lệ, không thêm Markdown."
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
            "num_ctx": 4096,
            "num_predict": 256
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
        return _ket_qua_chua_xac_nhan(
            f"Ollama trả về lỗi HTTP {loi.code}: {loi.reason}"
        )

    except (urllib.error.URLError, TimeoutError) as loi:
        return _ket_qua_chua_xac_nhan(
            f"Không gọi được Ollama: {loi}"
        )

    except (json.JSONDecodeError, UnicodeDecodeError) as loi:
        return _ket_qua_chua_xac_nhan(
            f"Phản hồi HTTP từ Ollama không hợp lệ: {loi}"
        )

    # 5. Kiểm tra Ollama đã sinh xong câu trả lời chưa
    thong_tin = phan_hoi.get("message", {})
    noi_dung = thong_tin.get("content", "")
    ly_do_dung = phan_hoi.get("done_reason", "")

    if phan_hoi.get("done") is False or ly_do_dung == "length":
        return _ket_qua_chua_xac_nhan(
            "Phản hồi SLM bị giới hạn độ dài, JSON có thể chưa hoàn chỉnh."
        )

    # 6. Đọc JSON do mô hình trả về
    try:
        du_lieu = _doc_json(noi_dung)
    except (ValueError, TypeError) as loi:
        return _ket_qua_chua_xac_nhan(
            f"Kết quả mô hình không hợp lệ: {loi}"
        )

    if not isinstance(du_lieu, dict):
        return _ket_qua_chua_xac_nhan(
            "JSON SLM trả về không phải một đối tượng."
        )

    ma = du_lieu.get("ma_ky_thuat")
    bang_chung = du_lieu.get("bang_chung")
    ly_do = du_lieu.get("ly_do")

    # 7. Kiểm tra cấu trúc dữ liệu
    if not isinstance(ma, str):
        return _ket_qua_chua_xac_nhan(
            "JSON không có ma_ky_thuat dạng chuỗi."
        )

    if not isinstance(bang_chung, list):
        return _ket_qua_chua_xac_nhan(
            "JSON không có bang_chung dạng danh sách."
        )

    if not isinstance(ly_do, str):
        return _ket_qua_chua_xac_nhan(
            "JSON không có ly_do dạng chuỗi."
        )

    ma = ma.strip()

    # 8. Kiểm tra mã kỹ thuật
    if ma != "CHUA_XAC_NHAN" and ma not in ma_hop_le:
        return _ket_qua_chua_xac_nhan(
            "Mô hình chọn kỹ thuật ngoài danh sách ứng viên."
        )

    # 9. Chỉ giữ bằng chứng thực sự xuất hiện trong log
    bang_chung_hop_le = []

    for dong in bang_chung:
        if not isinstance(dong, str):
            continue

        dong = dong.strip()

        if dong and dong in chuoi_text:
            bang_chung_hop_le.append(dong)

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
        "bang_chung": bang_chung_hop_le,
        "ly_do": ly_do
    }


def chon_ky_thuat(dong_log, ung_vien):
    """Giao diện để agent chọn kỹ thuật từ danh sách ứng viên."""
    return goi_slm(dong_log, ung_vien)


if __name__ == "__main__":
    # Dữ liệu thử giao tiếp, không phải kết quả phát hiện tấn công thật
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

    print("KET QUA SLM:")
    print(json.dumps(ket_qua, ensure_ascii=False, indent=2))
