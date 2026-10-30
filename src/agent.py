"""Agent phát hiện kỹ thuật tấn công trong log Windows (Sysmon). Vòng lặp 5 bước:

  1. Nhận sự kiện mới, gom vào phiên (máy + LogonId + cây tiến trình)               -> gom_phien.py
  2. Đổi sang ký hiệu, so khớp chuỗi với mẫu đã train, lấy vài kỹ thuật ứng viên    -> ky_hieu.py + train.py
  3. Nếu điểm khớp đủ cao: tìm dấu vết bắt buộc của các ứng viên trong DuckDB        -> dau_vet.py
  4. Gửi chuỗi + danh sách ứng viên cho mô hình ngôn ngữ chọn 1 kỹ thuật, kèm bằng chứng -> slm.py
  5. Kiểm chứng: kỹ thuật mô hình chọn phải nằm trong danh sách ứng viên VÀ đủ dấu vết bắt buộc.
     Đạt thì kết luận. Không đạt thì ghi "chưa xác nhận" và chờ thêm sự kiện (không kết luận bừa).

Cách chạy (PowerShell, đứng ở thư mục gốc repo):
  python src\\agent.py D:\\DoAnChuyenNganh\\log\\<file tấn công>.evtx
  python src\\agent.py <file log bình thường>           (phiên điểm thấp chỉ được đếm, không in chi tiết)
  python src\\agent.py <file> --chi-tiet                 (in cả các phiên điểm thấp)
"""
import argparse
import json
import os
import sys

import duckdb

import dau_vet
import train
from doc_log import liet_ke_file, nap_log
from gom_phien import gom_phien
from ky_hieu import loc_su_kien, mo_ta, rut_gon_chuoi

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

GOC_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SO_DONG_GUI_SLM = 40     # mô hình ngôn ngữ nhỏ chạy trên laptop: chỉ gửi tối đa chừng này dòng log


# ---------------------------------------------------------------- nạp mô hình (bước 2)
def nap_mo_hinh(duong):
    """Đọc models/mau_chuoi.json thành dạng mô hình mà các hàm chấm điểm của train.py dùng.
    Tham số chấm điểm (cửa sổ, tỉ lệ gốc, cách chấm) lấy TỪ FILE, để agent chấm giống hệt lúc Thiên đo tỷ lệ đúng."""
    with open(duong, encoding="utf-8") as f:
        j = json.load(f)
    train.CUA_SO = j["cua_so"]
    train.RHO = j["tham_so"]["ty_le"]
    train.CACH_DIEM = j["tham_so"]["cach_diem"]
    return {"bt": j.get("binh_thuong"), "so_chuoi": j["so_chuoi"], "df": j["df"], "tiep_theo": j["tiep_theo"]}


def cua_so_khop_nhat(seq, ma, mh):
    """Đoạn chuỗi (cửa sổ CUA_SO ký hiệu) cho điểm cao nhất với kỹ thuật `ma`: để người xem thấy agent khớp ở đâu."""
    n = train.CUA_SO
    cac = [seq] if len(seq) <= n else [seq[i:i + n] for i in range(len(seq) - n + 1)]
    return max(cac, key=lambda w: train.diem_cua_so(train.cac_doan(w), mh)[ma])


# ---------------------------------------------------------------- mô hình ngôn ngữ (bước 4)
def goi_mo_hinh_ngon_ngu(dong_log, ung_vien, dau_vet_ung_vien):
    """Gọi slm.py của Dũng: chon_ky_thuat(dong_log, ung_vien) -> {"ma_ky_thuat", "bang_chung", "ly_do"}.
    Nếu chưa có slm.py hoặc gọi lỗi (Ollama chưa chạy...) thì dùng BẢN TẠM và ghi rõ là bản tạm."""
    try:
        import slm
        if hasattr(slm, "chon_ky_thuat"):
            return slm.chon_ky_thuat(dong_log, ung_vien), "slm.py"
        loi = "slm.py chưa có hàm chon_ky_thuat"
    except ImportError:
        loi = "chưa có slm.py"
    except Exception as ex:          # lỗi khi gọi Ollama: vẫn chạy tiếp để demo không dừng giữa chừng
        loi = f"slm.py lỗi: {ex}"
    co_du = [m for m in ung_vien if dau_vet_ung_vien[m]["du"]]
    chon = co_du[0] if co_du else ung_vien[0]
    bang_chung = [d for _, ds in dau_vet_ung_vien[chon]["bang_chung"] for d in ds]
    return ({"ma_ky_thuat": chon, "bang_chung": bang_chung[:3],
             "ly_do": "Bản tạm: chọn ứng viên điểm cao nhất có đủ dấu vết (chưa gọi mô hình ngôn ngữ)."},
            f"BẢN TẠM ({loi})")


# ---------------------------------------------------------------- vòng lặp 5 bước cho 1 phiên
def xu_ly_phien(so, may, logon, ds, con, mh, a):
    """Chạy 5 bước trên 1 phiên. Trả về (kết quả, mã kỹ thuật, điểm).
    kết quả: "BINH_THUONG" | "CHUA_XAC_NHAN" | "KET_LUAN"."""
    # Bước 2 tính trước để biết phiên có cần in chi tiết không
    ds_loc = loc_su_kien(ds)
    seq = [k for k, _ in rut_gon_chuoi(ds_loc)]
    diem = train.diem_chuoi(seq, mh) if seq else {}
    ung_vien = sorted((m for m in diem if diem[m] > 0), key=lambda m: -diem[m])[:a.so_ung_vien]
    cao_nhat = diem[ung_vien[0]] if ung_vien else 0.0
    if cao_nhat < a.nguong and not a.chi_tiet:
        return "BINH_THUONG", None, cao_nhat

    print("\n" + "=" * 78)
    print(f"PHIÊN #{so} | máy {may} | {ds[0]['nguoi_dung']} | LogonId {logon}")

    # ---- Bước 1
    so_cay = len({e["goc"] for e in ds})
    print(f"[1] Gom phiên: {len(ds)} sự kiện, {so_cay} cây tiến trình, "
          f"{ds[0]['thoi_gian']} -> {ds[-1]['thoi_gian']}")

    # ---- Bước 2
    print(f"[2] Đổi sang ký hiệu: giữ {len(ds_loc)}/{len(ds)} sự kiện (bỏ loại Sysmon chung không ghi), "
          f"chuỗi {len(seq)} ký hiệu")
    hien = " > ".join(seq[:10]) + (" > ..." if len(seq) > 10 else "")
    print(f"    {hien}")
    if not ung_vien:
        print("    Không đoạn nào khớp mẫu đã train.")
    for m in ung_vien:
        print(f"    ứng viên {m:10} điểm {diem[m]:.3f}")
    if ung_vien:
        print(f"    đoạn khớp nhất với {ung_vien[0]}: {' > '.join(cua_so_khop_nhat(seq, ung_vien[0], mh))}")
    if cao_nhat < a.nguong:
        print(f"    -> điểm cao nhất {cao_nhat:.3f} < ngưỡng {a.nguong}: coi là BÌNH THƯỜNG, dừng ở bước 2.")
        return "BINH_THUONG", None, cao_nhat

    # ---- Bước 3
    print(f"[3] Điểm {cao_nhat:.3f} >= ngưỡng {a.nguong}: tìm dấu vết bắt buộc trong DuckDB")
    dv = {m: dau_vet.kiem_tra(con, m, ds) for m in ung_vien}
    for m in ung_vien:
        if dv[m]["du"]:
            print(f"    {m}: ĐỦ dấu vết")
            for ten, dong in dv[m]["bang_chung"]:
                print(f"       - {ten}")
                for d in dong:
                    print(f"           {d}")
        else:
            print(f"    {m}: THIẾU ({'; '.join(dv[m]['thieu'])})")
    if not any(dv[m]["du"] for m in ung_vien):
        print("[4] Bỏ qua: không ứng viên nào đủ dấu vết, không cần hỏi mô hình ngôn ngữ.")
        print(f"[5] CHƯA XÁC NHẬN: chuỗi giống {ung_vien[0]} nhưng thiếu dấu vết bắt buộc -> chờ thêm sự kiện.")
        return "CHUA_XAC_NHAN", ung_vien[0], cao_nhat

    # ---- Bước 4
    dong_log = [f"{e['thoi_gian']:%H:%M:%S} {mo_ta(e)}" for e in ds_loc]
    if len(dong_log) > SO_DONG_GUI_SLM:
        dong_log = dong_log[:SO_DONG_GUI_SLM]
    kq, nguon = goi_mo_hinh_ngon_ngu(dong_log, ung_vien, dv)
    print(f"[4] Hỏi mô hình ngôn ngữ ({nguon}), gửi {len(dong_log)} dòng log + ứng viên {ung_vien}")
    print("    trả về: " + json.dumps(kq, ensure_ascii=False)[:600])

    # ---- Bước 5
    chon = (kq or {}).get("ma_ky_thuat")
    trong_ds = chon in ung_vien
    du_dv = trong_ds and dv[chon]["du"]
    cho_phep = dong_log + [d for m in ung_vien for _, ds_ in dv[m]["bang_chung"] for d in ds_]
    bc = [b for b in (kq or {}).get("bang_chung", []) if isinstance(b, str) and b.strip()]
    bc_that = [b for b in bc if any(b.strip() in d or d in b for d in cho_phep)]
    print(f"[5] Kiểm chứng {chon}: nằm trong ứng viên: {'có' if trong_ds else 'KHÔNG'} | "
          f"đủ dấu vết: {'có' if du_dv else 'KHÔNG'} | bằng chứng có thật trong log: {len(bc_that)}/{len(bc)}")
    if trong_ds and du_dv:
        buoc_ke = train.doan_buoc_ke(seq[-1], chon, mh) if seq else None
        print(f"    => KẾT LUẬN: {chon} (điểm khớp {diem[chon]:.3f})")
        if buoc_ke:
            print(f"    Bước tiếp theo hay gặp sau '{seq[-1]}': {buoc_ke}")
        return "KET_LUAN", chon, diem[chon]
    print("    => CHƯA XÁC NHẬN: mô hình chọn kỹ thuật không qua kiểm chứng -> không kết luận, chờ thêm sự kiện.")
    return "CHUA_XAC_NHAN", chon, cao_nhat


def main():
    ap = argparse.ArgumentParser(description="Agent phát hiện kỹ thuật tấn công trong log Sysmon")
    ap.add_argument("duong_dan", nargs="+", help="file log hoặc thư mục")
    ap.add_argument("--mo-hinh", default=os.path.join(GOC_REPO, "models", "mau_chuoi.json"))
    ap.add_argument("--nguong", type=float, default=0.3, help="điểm khớp tối thiểu để đi tiếp bước 3 (mặc định 0.3)")
    ap.add_argument("--so-ung-vien", type=int, default=3)
    ap.add_argument("--db", default="output/agent.duckdb")
    ap.add_argument("--phien", type=int, nargs="*", help="chỉ xét các phiên có số thứ tự này")
    ap.add_argument("--chi-tiet", action="store_true", help="in chi tiết cả phiên điểm thấp")
    a = ap.parse_args()

    mh = nap_mo_hinh(a.mo_hinh)
    print(f"Mô hình: {a.mo_hinh} | {len(mh['so_chuoi'])} kỹ thuật | cửa sổ {train.CUA_SO} | "
          f"tỉ lệ gốc {train.RHO} | lớp bình thường: {'có' if mh['bt'] else 'không'}")

    os.makedirs(os.path.dirname(a.db) or ".", exist_ok=True)
    con = duckdb.connect(a.db)
    nap_log(con, liet_ke_file(a.duong_dan))
    tong_su_kien = con.execute("SELECT count(*) FROM su_kien").fetchone()[0]
    phien_list, _, _ = gom_phien(con)
    print(f"Đã nạp {tong_su_kien} sự kiện, gom được {len(phien_list)} phiên")

    ket_qua = []
    for so, ((may, logon), ds) in enumerate(phien_list, 1):
        if a.phien and so not in a.phien:
            continue
        ket_qua.append((so,) + xu_ly_phien(so, may, logon, ds, con, mh, a))
    con.close()

    dem = {k: sum(1 for r in ket_qua if r[1] == k) for k in ("BINH_THUONG", "CHUA_XAC_NHAN", "KET_LUAN")}
    print("\n" + "=" * 78)
    print(f"TỔNG KẾT: {len(ket_qua)} phiên | bình thường (dừng ở bước 2): {dem['BINH_THUONG']} | "
          f"chưa xác nhận: {dem['CHUA_XAC_NHAN']} | kết luận tấn công: {dem['KET_LUAN']}")
    for so, kq, ma, d in ket_qua:
        if kq != "BINH_THUONG":
            print(f"   phiên #{so}: {'KẾT LUẬN' if kq == 'KET_LUAN' else 'chưa xác nhận'} {ma} (điểm {d:.3f})")


if __name__ == "__main__":
    main()