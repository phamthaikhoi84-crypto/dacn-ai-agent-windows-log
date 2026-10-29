"""Đổi 1 sự kiện thành ký hiệu hành động (để so khớp chuỗi) và mô tả tiếng Việt (để người đọc)."""
import os


def ten_ngan(path):
    return path.replace("/", "\\").split("\\")[-1] if path else "?"

# ---- Lọc sự kiện cho so khớp chuỗi (train.py và agent.py PHẢI dùng chung) ----
# Log Splunk ghi nhiều loại sự kiện mà cấu hình Sysmon phổ biến không ghi
# (Event 10 vào mọi tiến trình, 7, 17, 18, 22, 23). Chỉ giữ phần chung để train và log thật so được với nhau.
EVENT_GIU = {1, 3, 11, 12, 13, 14}


def giu_lai(e):
    if e["event_id"] in EVENT_GIU:
        return True
    return e["event_id"] == 10 and ten_ngan(e["doi_tuong"]).lower() == "lsass.exe"


def loc_su_kien(ds):
    """Bỏ các sự kiện không dùng để so khớp chuỗi."""
    return [e for e in ds if giu_lai(e)]


PROCESS_VM_READ = 0x0010


def loai_quyen(quyen):
    """Có quyền đọc bộ nhớ (PROCESS_VM_READ) -> 'doc' (dump được). Không có -> 'truy_van' (thường là bình thường)."""
    try:
        q = int(quyen, 16)
    except (TypeError, ValueError):
        return "khong_ro"
    return "doc" if q & PROCESS_VM_READ else "truy_van"


def loai_khoa_registry(khoa):
    """Xếp khóa registry vào 1 trong 4 loại. Chỉ giữ loại, bỏ SID và phần cụ thể của đường dẫn."""
    k = (khoa or "").lower()
    if "\\explorer\\runmru" in k:
        return "RunMRU"        # lịch sử hộp thoại Run (Win+R), dấu vết của SharpRDP
    if "\\currentversion\\run" in k:
        return "Run"           # Run và RunOnce: tự chạy khi đăng nhập (T1547.001)
    if "controlset" in k and "\\services\\" in k:
        return "Services"      # tạo/sửa dịch vụ
    return "khac"


def ky_hieu(e):
    """Rút gọn 1 sự kiện thành 1 ký hiệu hành động (bỏ chi tiết như PID, đường dẫn cụ thể)."""
    eid, img, dt = e["event_id"], ten_ngan(e["image"]).lower(), e["doi_tuong"] or ""
    if eid == 1:
        return f"TAO_TIEN_TRINH:{img}"
    if eid == 7:
        return f"NAP_DLL:{ten_ngan(dt).lower()}"
    if eid == 10:
        return f"MO_BO_NHO:{ten_ngan(dt).lower()}:{loai_quyen(e['quyen'])}"
    if eid == 11:
        duoi = os.path.splitext(dt)[1].lower() or "(không đuôi)"
        return f"TAO_FILE:*{duoi}"
    if eid == 3:
        return f"KET_NOI_MANG:{dt.split(':')[-1]}"
    if eid in (12, 13, 14):
        return f"SUA_REGISTRY:{loai_khoa_registry(dt)}"
    if eid == 4104:
        return "CHAY_SCRIPT_POWERSHELL"
    return f"EVENT_{eid}"


def mo_ta(e):
    """Mô tả 1 sự kiện bằng tiếng Việt cho người đọc."""
    eid, img, dt = e["event_id"], ten_ngan(e["image"]), e["doi_tuong"] or ""
    if eid == 1:
        return f"[1]  {ten_ngan(e['parent_image'])} chạy {img}: {e['command_line']}"
    if eid == 7:
        return f"[7]  {img} nạp DLL {dt}"
    if eid == 10:
        return f"[10] {img} mở bộ nhớ tiến trình {ten_ngan(dt)} (quyền {e['quyen']})"
    if eid == 11:
        return f"[11] {img} tạo file {dt}"
    if eid == 3:
        return f"[3]  {img} kết nối mạng tới {dt}"
    if eid in (12, 13, 14):
        return f"[{eid}] {img} sửa registry {dt}"
    if eid == 4104:
        return f"[4104] PowerShell chạy script: {dt[:80]}"
    return f"[{eid}] {img} {dt}"


def rut_gon_chuoi(ds):
    """Đổi danh sách sự kiện thành chuỗi ký hiệu, gộp các bước lặp liên tiếp: [[ký hiệu, số lần], ...]"""
    gon = []
    for k in (ky_hieu(e) for e in ds):
        if gon and gon[-1][0] == k:
            gon[-1][1] += 1
        else:
            gon.append([k, 1])
    return gon