
import json
import os
import re
import urllib.request
import urllib.error


OLLAMA_URL = "http://localhost:11434/api/chat"

# Cho phép đổi model bằng biến môi trường SLM_MODEL
MODEL_CHINH = os.environ.get("SLM_MODEL", "phi4-mini:latest")


def _ket_qua_chua_xac_nhan(ly_do):
    return {
        "ma_ky_thuat": "CHUA_XAC_NHAN",
        "bang_chung": [],
        "ly_do": ly_do
    }
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

        # 3. Prompt phân tích
    ket_qua_lsass = _kiem_tra_lsass_vm_read(chuoi_text)

    yeu_cau = f"""
Bạn là chuyên gia phân tích log Windows/Sysmon và MITRE ATT&CK.

NHIỆM VỤ:
Phân tích log và chọn kỹ thuật phù hợp nhất trong danh sách ứng viên.
Chỉ kết luận khi có bằng chứng trực tiếp.

DANH SÁCH ỨNG VIÊN:
{json.dumps(danh_sach_ung_vien, ensure_ascii=False, default=str)}

KIỂM TRA LSASS BẰNG PYTHON:
- Có PROCESS_VM_READ: {ket_qua_lsass}
- Giá trị True nghĩa là đã tìm thấy ít nhất một Event ID 10 nhắm LSASS
  có GrantedAccess chứa bit 0x0010.
- Giá trị False nghĩa là không tìm thấy bằng chứng đó.
- Đây là kết quả kiểm tra bằng Python, phải được ưu tiên.
- Không được tự suy diễn ngược lại kết quả này.

LOG WINDOWS/SYSMON:
{chuoi_text}

QUY TẮC:
1. Chỉ chọn mã kỹ thuật có trong danh sách ứng viên.
2. Không tự tạo bằng chứng, RecordID hoặc GrantedAccess.
3. Với T1003.001:
   - Nếu kiểm tra LSASS bằng Python là False,
     bắt buộc chọn CHUA_XAC_NHAN.
   - bang_chung phải là [].
   - ly_do phải nói rõ không tìm thấy PROCESS_VM_READ.
   - Tuyệt đối không nói GrantedAccess có chứa 0x0010.
4. Nếu thiếu bằng chứng bắt buộc của kỹ thuật khác,
   chọn CHUA_XAC_NHAN.
5. Nếu chọn CHUA_XAC_NHAN, bang_chung phải là [].
6. Chỉ trích nguyên văn bằng chứng thực sự có trong log.
7. Giải thích bằng tiếng Việt, ngắn gọn, không mâu thuẫn dữ liệu.

CHỈ TRẢ VỀ JSON HỢP LỆ:
{{
  "ma_ky_thuat": "mã kỹ thuật hoặc CHUA_XAC_NHAN",
  "bang_chung": ["đoạn log nguyên văn"],
  "ly_do": "giải thích ngắn gọn"
}}

Bạn là chuyên gia phân tích Windows/Sysmon và MITRE ATT&CK.

NHIỆM VỤ:
Phân tích log, chọn kỹ thuật phù hợp nhất trong danh sách ứng viên.
Chỉ kết luận khi có bằng chứng trực tiếp trong log.

DANH SÁCH ỨNG VIÊN:
{json.dumps(danh_sach_ung_vien, ensure_ascii=False, default=str)}

LOG WINDOWS/SYSMON:
{chuoi_text}

QUY TẮC PHÂN TÍCH:

1. Chỉ được chọn mã kỹ thuật có trong danh sách ứng viên.
2. Không suy diễn từ tên tiến trình hoặc một sự kiện đơn lẻ.
3. Nếu thiếu bằng chứng bắt buộc, chọn CHUA_XAC_NHAN.

4. QUAN TRỌNG: Phân tích quyền GrantedAccess trong Event ID 10.

GrantedAccess là giá trị bitmask thể hiện các quyền
mà tiến trình yêu cầu đối với tiến trình đích.

Các quyền PROCESS_* thường gặp:

- 0x0001: PROCESS_TERMINATE
- 0x0002: PROCESS_CREATE_THREAD
- 0x0008: PROCESS_VM_OPERATION
- 0x0010: PROCESS_VM_READ
- 0x0020: PROCESS_VM_WRITE
- 0x0040: PROCESS_DUP_HANDLE
- 0x0080: PROCESS_CREATE_PROCESS
- 0x0100: PROCESS_SET_QUOTA
- 0x0200: PROCESS_SET_INFORMATION
- 0x0400: PROCESS_QUERY_INFORMATION
- 0x0800: PROCESS_SUSPEND_RESUME
- 0x1000: PROCESS_QUERY_LIMITED_INFORMATION

Cách kiểm tra PROCESS_VM_READ:

Sử dụng phép AND bit:

    (GrantedAccess & 0x0010) != 0

Nếu kết quả khác 0 thì giá trị quyền có chứa PROCESS_VM_READ.

Ví dụ:

- GrantedAccess = 0x0010:
  Có quyền PROCESS_VM_READ.

- GrantedAccess = 0x0410:
  Có PROCESS_VM_READ và PROCESS_QUERY_INFORMATION.

- GrantedAccess = 0x1ffff:
  CÓ PROCESS_VM_READ vì giá trị này chứa bit 0x0010.
  Tuyệt đối không được giải thích rằng giá trị này
  không có quyền đọc bộ nhớ.

- GrantedAccess = 0x0400:
  Có PROCESS_QUERY_INFORMATION nhưng không có PROCESS_VM_READ.

Lưu ý:
GrantedAccess phải được phân tích như giá trị số dạng hex
hoặc decimal phù hợp, không so sánh chuỗi một cách máy móc.

5. Đối với T1003.001 - LSASS Memory:

- Phải kiểm tra Event ID 10 có tiến trình đích là lsass.exe.
- Kiểm tra GrantedAccess có chứa PROCESS_VM_READ hay không.
- Xem xét tiến trình nguồn, ngữ cảnh và các dấu vết liên quan.
- Chỉ riêng việc truy cập lsass.exe chưa đủ kết luận đánh cắp
  thông tin xác thực.
- Nếu thiếu bằng chứng cần thiết, chọn CHUA_XAC_NHAN.
- Không được phủ nhận quyền đọc bộ nhớ khi bit 0x0010 thực sự tồn tại.

6. BẰNG CHỨNG:

- Chỉ trích 1 đến 3 đoạn ngắn có thật trong LOG.
- Không tự tạo Event ID, GrantedAccess hoặc tên tiến trình.
- Trích nguyên văn để hệ thống có thể kiểm tra lại.
- Nếu CHUA_XAC_NHAN thì bang_chung phải là [].

7. LÝ DO:

- Viết tiếng Việt.
- Chỉ 1 đến 2 câu ngắn.
- Nêu rõ bằng chứng quan trọng nhất.
- Không mâu thuẫn với GrantedAccess và bang_chung.
- Không khẳng định hành vi tấn công nếu chưa đủ bằng chứng.

CHỈ TRẢ VỀ MỘT JSON HỢP LỆ:

{{
  "ma_ky_thuat": "mã kỹ thuật hoặc CHUA_XAC_NHAN",
  "bang_chung": ["đoạn log nguyên văn"],
  "ly_do": "giải thích 1 đến 2 câu"
}}
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
            "num_ctx": 2048,
                "num_predict": 512
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
            f"Ollama lỗi HTTP {loi.code}: {loi.reason}"
        )

    except (urllib.error.URLError, TimeoutError) as loi:
        return _ket_qua_chua_xac_nhan(
            f"Không gọi được Ollama: {loi}"
        )

    except (json.JSONDecodeError, UnicodeDecodeError) as loi:
        return _ket_qua_chua_xac_nhan(
            f"Phản hồi Ollama không hợp lệ: {loi}"
        )

    # 5. Kiểm tra phản hồi
    thong_tin = phan_hoi.get("message", {})
    noi_dung = thong_tin.get("content", "")
    ly_do_dung = phan_hoi.get("done_reason", "")

    if phan_hoi.get("done") is False or ly_do_dung == "length":
        return _ket_qua_chua_xac_nhan(
            "Phản hồi SLM bị giới hạn độ dài."
        )

    # 6. Đọc JSON
    try:
        du_lieu = _doc_json(noi_dung)
    except (ValueError, TypeError) as loi:
        return _ket_qua_chua_xac_nhan(
            f"Kết quả mô hình không hợp lệ: {loi}"
        )

    if not isinstance(du_lieu, dict):
        return _ket_qua_chua_xac_nhan(
            "JSON SLM không phải một đối tượng."
        )

    ma = du_lieu.get("ma_ky_thuat")
    bang_chung = du_lieu.get("bang_chung")
    ly_do = du_lieu.get("ly_do")

    # 7. Kiểm tra cấu trúc
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
    ly_do = ly_do.strip()

    # 8. Kiểm tra mã kỹ thuật
    if ma != "CHUA_XAC_NHAN" and ma not in ma_hop_le:
        return _ket_qua_chua_xac_nhan(
            "Mô hình chọn kỹ thuật ngoài danh sách ứng viên."
        )

    # 9. Kiểm tra bằng chứng nguyên văn
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
        # 10. Kiểm soát độc lập kỹ thuật LSASS Memory
    if ma == "T1003.001":
        if not _kiem_tra_lsass_vm_read(chuoi_text):
            return _ket_qua_chua_xac_nhan(
                "Python kiểm tra log Event ID 10 nhắm vào LSASS "
                "nhưng không tìm thấy GrantedAccess chứa "
                "PROCESS_VM_READ (0x0010). "
                "Chưa đủ bằng chứng xác nhận T1003.001."
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
