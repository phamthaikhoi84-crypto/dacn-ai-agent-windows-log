
import csv
import json
from pathlib import Path

from slm import goi_slm, MODEL_CHINH


ROOT = Path(__file__).resolve().parent.parent
FILE_CSV = ROOT / "output" / "event10_lsass_phien10.csv"
FILE_KET_QUA = ROOT / "output" / "ket_qua_slm_phien10.json"


def doc_su_kien():
    if not FILE_CSV.exists():
        raise FileNotFoundError(
            f"Khong tim thay file: {FILE_CSV}"
        )

    with open(
        FILE_CSV,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as f:
        reader = csv.DictReader(f)
        du_lieu = list(reader)

    return du_lieu


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


def luu_ket_qua(ket_qua):
    FILE_KET_QUA.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        FILE_KET_QUA,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            ket_qua,
            f,
            ensure_ascii=False,
            indent=2
        )


def danh_gia_ket_qua(ket_qua):
    print("\n========== DANH GIA ==========")

    ma = ket_qua.get("ma_ky_thuat", "")
    ly_do = ket_qua.get("ly_do", "")

    ly_do_thuong = ly_do.lower()

    # Trường hợp 1: Không kết nối được Ollama
    if (
        "không gọi được ollama" in ly_do_thuong
        or "timeout" in ly_do_thuong
        or "timed out" in ly_do_thuong
        or "lỗi http" in ly_do_thuong
        or "phản hồi http" in ly_do_thuong
    ):
        print(
            "KIEM THU THAT BAI: "
            "Khong ket noi duoc hoac Ollama tra ve loi."
        )
        print("Ly do:", ly_do)
        return

    # Trường hợp 2: JSON bị cắt hoặc không hợp lệ
    if (
        "không hợp lệ" in ly_do_thuong
        or "không tìm thấy json" in ly_do_thuong
        or "json" in ly_do_thuong and (
            "hoàn chỉnh" in ly_do_thuong
            or "rỗng" in ly_do_thuong
        )
        or "giới hạn độ dài" in ly_do_thuong
    ):
        print(
            "KIEM THU THAT BAI: "
            "SLM tra ve du lieu khong hop le hoac bi cat."
        )
        print("Ly do:", ly_do)
        return

    # Trường hợp 3: SLM trả về mã kỹ thuật chưa xác nhận
    if ma == "CHUA_XAC_NHAN":
        if (
            "không có kỹ thuật ứng viên" in ly_do_thuong
            or "danh sách ứng viên" in ly_do_thuong
            or "không xác minh được" in ly_do_thuong
            or "không có ma_ky_thuat" in ly_do_thuong
            or "không có bang_chung" in ly_do_thuong
            or "không có ly_do" in ly_do_thuong
            or "không phải một đối tượng" in ly_do_thuong
            or "ngoài danh sách" in ly_do_thuong
        ):
            print(
                "KIEM THU THAT BAI: "
                "Du lieu dau vao hoac dau ra khong dat yeu cau."
            )
            print("Ly do:", ly_do)
            return

        print(
            "PHU HOP: SLM khong xac nhan ky thuat "
            "khi chua co du bang chung."
        )
        print("Ly do:", ly_do)
        return

    # Trường hợp 4: SLM xác nhận LSASS Memory
    if ma == "T1003.001":
        print(
            "CAN KIEM TRA: SLM da chon T1003.001 - LSASS Memory."
        )
        print(
            "Can doi chieu bang chung va GrantedAccess "
            "truoc khi ket luan phat hien tan cong."
        )
        print("Bang chung:", ket_qua.get("bang_chung", []))
        print("Ly do:", ly_do)
        return

    # Trường hợp 5: Mã kỹ thuật không mong đợi
    print(
        "KIEM THU THAT BAI: "
        "SLM tra ve ma ky thuat khong mong doi."
    )
    print("Ma ky thuat:", ma)
    print("Ly do:", ly_do)


def main():
    print("DOC DU LIEU EVENT ID 10 NHAM LSASS")

    du_lieu = doc_su_kien()

    print("So su kien:", len(du_lieu))

    if not du_lieu:
        print("Khong co du lieu de kiem thu.")
        return

    chuoi_su_kien = tao_chuoi_su_kien(du_lieu)

    ung_vien = [
        {
            "ma_ky_thuat": "T1003.001",
            "ten": "LSASS Memory",
            "mo_ta": (
                "Credential Dumping through reading LSASS process memory"
            )
        }
    ]

    print("\nDANG GOI SLM...")
    print("Model:", MODEL_CHINH)
    print("Ky thuat ung vien: T1003.001 - LSASS Memory")

    ket_qua = goi_slm(
        chuoi_su_kien,
        ung_vien,
        model=MODEL_CHINH
    )

    print("\n========== KET QUA SLM ==========")

    print(
        json.dumps(
            ket_qua,
            ensure_ascii=False,
            indent=2
        )
    )

    luu_ket_qua(ket_qua)

    print("\nDa luu ket qua:", FILE_KET_QUA)

    danh_gia_ket_qua(ket_qua)


if __name__ == "__main__":
    main()
