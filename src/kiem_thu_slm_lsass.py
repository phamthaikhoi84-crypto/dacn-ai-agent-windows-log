
import csv
import json
from pathlib import Path

from slm import goi_slm, MODEL_CHINH


ROOT = Path(__file__).resolve().parent.parent
FILE_CSV = ROOT / "output" / "event10_lsass_phien10.csv"
FILE_KET_QUA = ROOT / "output" / "ket_qua_slm_phien10.json"


def doc_su_kien():
    if not FILE_CSV.exists():
        raise FileNotFoundError(f"Khong tim thay file: {FILE_CSV}")

    with open(FILE_CSV, "r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def tao_chuoi_su_kien(du_lieu):
    cac_dong = []

    for d in du_lieu:
        dong = (
            f"EventID={d.get('event_id', '')} "
            f"RecordID={d.get('record_id', '')} "
            f"Time={d.get('thoi_gian', '')} "
            f"Image={d.get('image', '')} "
            f"ParentImage={d.get('parent_image', '')} "
            f"CommandLine={d.get('command_line', '')} "
            f"Target={d.get('doi_tuong', '')} "
            f"GrantedAccess={d.get('quyen', '')} "
            f"User={d.get('nguoi_dung', '')} "
            f"LogonId={d.get('logon_id', '')}"
        )
        cac_dong.append(dong)

    return "\n".join(cac_dong)


def chuan_hoa_quyen(quyen):
    quyen = str(quyen).strip()

    if not quyen:
        return None

    try:
        return int(quyen, 0)
    except ValueError:
        try:
            return int(quyen, 16)
        except ValueError:
            return None


def la_lsass(target):
    target = str(target).strip().replace("/", "\\")
    return target.rsplit("\\", 1)[-1].lower() == "lsass.exe"


def phan_tich_quyen(du_lieu):
    ket_qua = []

    for d in du_lieu:
        event_id = str(d.get("event_id", "")).strip()
        target = d.get("doi_tuong", "")
        quyen = d.get("quyen", "")

        if event_id != "10" or not la_lsass(target):
            continue

        gia_tri = chuan_hoa_quyen(quyen)

        co_vm_read = (
            gia_tri is not None
            and (gia_tri & 0x0010) != 0
        )

        ket_qua.append({
            "record_id": d.get("record_id", ""),
            "target": target,
            "granted_access": str(quyen),
            "gia_tri_so": gia_tri,
            "co_vm_read": co_vm_read
        })

    return ket_qua


def kiem_soat_ket_qua(ket_qua_slm, ket_qua_quyen):
    ket_qua = dict(ket_qua_slm)

    cac_su_kien_co_vm_read = [
        d for d in ket_qua_quyen if d["co_vm_read"]
    ]

    if not cac_su_kien_co_vm_read:
        ket_qua["ma_ky_thuat"] = "CHUA_XAC_NHAN"
        ket_qua["bang_chung"] = []
        ket_qua["ly_do"] = (
            "Python kiểm tra 16 sự kiện Event ID 10 nhắm vào lsass.exe "
            "nhưng không tìm thấy sự kiện nào có quyền PROCESS_VM_READ "
            "(bit 0x0010). Vì vậy chưa đủ bằng chứng để xác nhận "
            "kỹ thuật T1003.001 - LSASS Memory."
        )
        trang_thai = "KHONG_CO_VM_READ"

    else:
        ket_qua["ma_ky_thuat"] = "CHUA_XAC_NHAN"
        ket_qua["bang_chung"] = []
        ket_qua["ly_do"] = (
            "Đã tìm thấy sự kiện Event ID 10 nhắm vào LSASS có "
            "PROCESS_VM_READ. Tuy nhiên, quyền đọc bộ nhớ chưa đủ "
            "để chứng minh hành vi đánh cắp thông tin xác thực. "
            "Cần đối chiếu thêm chuỗi hành vi."
        )
        trang_thai = "CO_VM_READ_CAN_DIEU_TRA"

    ket_qua["kiem_soat_python"] = {
        "so_su_kien_lsass": len(ket_qua_quyen),
        "so_su_kien_co_vm_read": len(cac_su_kien_co_vm_read),
        "ket_qua": trang_thai
    }

    return ket_qua


def luu_ket_qua(ket_qua):
    FILE_KET_QUA.parent.mkdir(parents=True, exist_ok=True)

    with open(FILE_KET_QUA, "w", encoding="utf-8") as f:
        json.dump(ket_qua, f, ensure_ascii=False, indent=2)


def danh_gia_ket_qua(ket_qua):
    print("\n========== DANH GIA ==========")

    ma = ket_qua.get("ma_ky_thuat", "")
    ly_do = ket_qua.get("ly_do", "")

    if ma == "CHUA_XAC_NHAN":
        print("CHUA XAC NHAN: Chua du bang chung ket luan tan cong.")
    elif ma == "T1003.001":
        print("CAN DIEU TRA: Co dau hieu phu hop T1003.001.")
    else:
        print("Ma ky thuat:", ma)

    print("Ly do:", ly_do)


def main():
    print("DOC DU LIEU EVENT ID 10 NHAM LSASS")

    du_lieu = doc_su_kien()
    print("So su kien:", len(du_lieu))

    if not du_lieu:
        print("Khong co du lieu de kiem thu.")
        return

    ket_qua_quyen = phan_tich_quyen(du_lieu)

    so_vm_read = sum(
        1 for d in ket_qua_quyen if d["co_vm_read"]
    )

    print("\n========== KIEM TRA QUYEN ==========")
    print("So su kien LSASS:", len(ket_qua_quyen))
    print("So su kien co PROCESS_VM_READ:", so_vm_read)

    chuoi_su_kien = tao_chuoi_su_kien(du_lieu)

    ung_vien = [
        {
            "ma_ky_thuat": "T1003.001",
            "ten": "LSASS Memory",
            "mo_ta": "Credential Dumping through reading LSASS process memory"
        }
    ]

    print("\nDANG GOI SLM...")
    print("Model:", MODEL_CHINH)

    ket_qua_slm = goi_slm(
        chuoi_su_kien,
        ung_vien,
        model=MODEL_CHINH
    )

    print("\n========== KET QUA SLM GOC ==========")
    print(json.dumps(ket_qua_slm, ensure_ascii=False, indent=2))

    ket_qua = kiem_soat_ket_qua(
        ket_qua_slm,
        ket_qua_quyen
    )

    print("\n========== KET QUA SAU KIEM SOAT ==========")
    print(json.dumps(ket_qua, ensure_ascii=False, indent=2))

    luu_ket_qua(ket_qua)

    print("\nDa luu ket qua:", FILE_KET_QUA)
    danh_gia_ket_qua(ket_qua)


if __name__ == "__main__":
    main()
