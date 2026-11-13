"""Agent phát hiện kỹ thuật tấn công trong log Windows (Sysmon). Vòng lặp 5 bước:

  1. Nhận sự kiện mới, gom vào phiên (máy + LogonId + cây tiến trình)               -> gom_phien.py
  2. Đổi sang ký hiệu, so khớp chuỗi với mẫu đã train, lấy vài kỹ thuật ứng viên    -> ky_hieu.py + train.py
  3. Nếu điểm khớp đủ cao: tìm dấu vết bắt buộc của các ứng viên trong DuckDB        -> dau_vet.py
  4. Gửi chuỗi + danh sách ứng viên cho mô hình ngôn ngữ chọn 1 kỹ thuật, kèm bằng chứng -> slm.py
  5. Kiểm chứng: kỹ thuật mô hình chọn phải nằm trong danh sách ứng viên VÀ đủ dấu vết bắt buộc.
     Đạt thì kết luận. Không đạt thì ghi "chưa xác nhận" và chờ thêm sự kiện (không kết luận bừa).
     Nếu mô hình ngôn ngữ lỗi (Ollama không trả lời, JSON bị cắt...) thì ghi riêng "SLM lỗi", không kết luận.

Cách chạy (PowerShell, đứng ở thư mục gốc repo):
  python src\\agent.py D:\\DoAnChuyenNganh\\log\\<file tấn công>.evtx
  python src\\agent.py <file log bình thường>           (phiên điểm thấp chỉ được đếm, không in chi tiết)
  python src\\agent.py <file> --chi-tiet                 (in cả các phiên điểm thấp)
  python src\\agent.py <file> --khong-slm               (bỏ bước hỏi mô hình ngôn ngữ: chỉ luật + dấu vết;
                                                          tên cũ --ban-tam vẫn dùng được)
  python src\\agent.py <file> --in-dong-slm             (in các dòng log gửi cho mô hình ngôn ngữ)
  python src\\agent.py <file> --phat-lai [N] [--tre 0.5] (phát lại log theo thời gian, mỗi đợt N sự kiện,
                                                          chỉ in khi quyết định của một phiên thay đổi)
"""
import argparse
import contextlib
import io
import json
import os
import sys
import time

import duckdb

import dau_vet
import train
from doc_log import liet_ke_file, nap_log
from gom_phien import gom_phien
from ky_hieu import loai_quyen, loc_su_kien, mo_ta, rut_gon_chuoi

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

GOC_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SO_DONG_GUI_SLM = 40     # mô hình ngôn ngữ nhỏ chạy trên laptop: chỉ gửi tối đa chừng này dòng log
CUA_SO_GIAY_SLM = 60     # lấy các sự kiện cách dấu vết bắt buộc không quá chừng này giây
SO_BAC_TIEN_TRINH = 3    # lấy Event 1 của tiến trình thực hiện dấu vết, tiến trình cha và ông (nếu có trong phiên)

Y_NGHIA_QUYEN = {
    "DAY_DU": "toàn quyền, CÓ quyền đọc bộ nhớ",
    "DOC_BO_NHO": "CÓ quyền đọc bộ nhớ",
    "TRUY_VAN": "chỉ truy vấn thông tin, KHÔNG đọc được bộ nhớ",
    "KHONG_RO": "không rõ quyền",
}


def dong_cho_slm(e):
    """1 dòng log gửi mô hình ngôn ngữ. Event 10 được ghi sẵn ý nghĩa quyền (tính bằng ky_hieu.loai_quyen),
    vì mô hình nhỏ không tự tính phép AND bit chính xác được."""
    d = f"{e['thoi_gian']:%H:%M:%S} {mo_ta(e)}"
    if e["event_id"] == 10:
        d += f" -> {Y_NGHIA_QUYEN[loai_quyen(e['quyen'])]}"
    return d


def dong_day_du(e, tao):
    """1 dòng log gửi mô hình ngôn ngữ ở bước 4: đường dẫn đầy đủ, kèm tiến trình cha.
    tao: guid -> sự kiện Event 1 (tạo tiến trình) trong phiên, để tra tiến trình cha của Event 3/10/11/13."""
    eid, img, dt = e["event_id"], e["image"] or "?", e["doi_tuong"] or ""
    if eid == 1:
        d = f"[1] {e['parent_image'] or '?'} chạy {img}: {(e['command_line'] or '')[:400]}"
    else:
        if eid == 10:
            d = f"[10] {img} mở bộ nhớ tiến trình {dt} (quyền {e['quyen']}) -> {Y_NGHIA_QUYEN[loai_quyen(e['quyen'])]}"
        elif eid == 11:
            d = f"[11] {img} tạo file {dt}"
        elif eid == 3:
            d = f"[3] {img} kết nối mạng tới {dt}"
        elif eid in (12, 13, 14):
            d = f"[{eid}] {img} sửa registry {dt}"
        else:
            d = f"[{eid}] {img} {dt[:200]}"
        t = tao.get(e["guid"])
        if t and t["parent_image"]:
            d += f" (tiến trình cha: {t['parent_image']})"
    return f"{e['thoi_gian']:%H:%M:%S} {d}"


def chon_dong_cho_slm(ds_loc, dv, ung_vien, toi_da=SO_DONG_GUI_SLM, cua_so=CUA_SO_GIAY_SLM):
    """Chọn các dòng log gửi mô hình ngôn ngữ (bước 4), thay cho cách cũ lấy 40 dòng đầu phiên.
    Phiên trên máy thật có thể dài hàng nghìn sự kiện, dòng gây nghi ngờ thường không nằm ở đầu phiên.
    Thứ tự ưu tiên khi phải cắt bớt:
      1. chính các sự kiện làm bằng chứng ở bước 3 (của các ứng viên đủ dấu vết),
      2. Event 1 tạo ra tiến trình thực hiện bằng chứng, tiến trình cha, tiến trình ông,
      3. các sự kiện khác cách bằng chứng không quá `cua_so` giây, gần hơn thì ưu tiên hơn.
    Sau khi chọn, xếp lại theo thời gian và gộp các dòng giống hệt nhau liền nhau.
    Trả về (danh sách dòng, số sự kiện được chọn)."""
    def khoa(e):
        return (e["nguon"], e["record_id"])

    tao = {e["guid"]: e for e in ds_loc if e["event_id"] == 1 and e["guid"]}
    bc = {k for m in ung_vien if dv[m]["du"] for k in dv[m].get("su_kien", [])}
    moc = [e for e in ds_loc if khoa(e) in bc]
    if not moc:                       # dự phòng, bình thường không xảy ra
        chon = ds_loc[:toi_da]
    else:
        uu_tien = {}
        def them(e, muc):
            k = khoa(e)
            if k not in uu_tien or muc < uu_tien[k]:
                uu_tien[k] = muc
        for e in moc:
            them(e, (0, 0.0))
            g = e["guid"]
            for bac in range(1, SO_BAC_TIEN_TRINH + 1):
                t = tao.get(g)
                if not t:
                    break
                them(t, (1, float(bac)))
                g = t["parent_guid"]
        for e in ds_loc:
            gan = min(abs((e["thoi_gian"] - m["thoi_gian"]).total_seconds()) for m in moc)
            if gan <= cua_so:
                them(e, (2, gan))
        giu = set(sorted(uu_tien, key=uu_tien.get)[:toi_da])
        chon = [e for e in ds_loc if khoa(e) in giu]

    dong = []
    for e in chon:
        d = dong_day_du(e, tao)
        if dong and dong[-1][0][9:] == d[9:]:      # bỏ 9 ký tự giờ "HH:MM:SS " rồi so nội dung
            dong[-1][1] += 1
        else:
            dong.append([d, 1])
    return [d if n == 1 else f"{d} (lặp lại {n} lần)" for d, n in dong], len(chon)


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
def goi_mo_hinh_ngon_ngu(dong_log, ung_vien, dau_vet_ung_vien, khong_slm=False):
    """Bước 4. Trả về (kết quả, nguồn, số giây).
    - Có SLM: gọi slm.chon_ky_thuat(dong_log, ung_vien) -> {"ma_ky_thuat", "bang_chung", "ly_do"[, "loi"]}.
      Nếu gọi lỗi thì trả về kết quả có "loi": True. KHÔNG tự chuyển sang chế độ không SLM,
      để số đo của chế độ có SLM không bị lẫn kết quả của chế độ kia.
    - Không SLM (--khong-slm): chọn ứng viên điểm cao nhất có đủ dấu vết bắt buộc."""
    if khong_slm:
        co_du = [m for m in ung_vien if dau_vet_ung_vien[m]["du"]]
        chon = co_du[0] if co_du else ung_vien[0]
        bang_chung = [d for _, ds in dau_vet_ung_vien[chon]["bang_chung"] for d in ds]
        return ({"ma_ky_thuat": chon, "bang_chung": bang_chung[:3],
                 "ly_do": "Không SLM: chọn ứng viên điểm cao nhất có đủ dấu vết bắt buộc."},
                "KHÔNG SLM, chỉ luật + dấu vết", 0.0)
    bat_dau = time.perf_counter()
    try:
        import slm
        kq = slm.chon_ky_thuat(dong_log, ung_vien)
        nguon = f"slm.py, {getattr(slm, 'MODEL_CHINH', '?')}"
    except Exception as ex:          # thiếu slm.py, lỗi bất ngờ khi gọi: ghi là SLM lỗi, không dừng chương trình
        kq = {"ma_ky_thuat": "CHUA_XAC_NHAN", "bang_chung": [], "ly_do": f"Gọi slm.py lỗi: {ex}", "loi": True}
        nguon = "slm.py"
    if not isinstance(kq, dict):
        kq = {"ma_ky_thuat": "CHUA_XAC_NHAN", "bang_chung": [], "ly_do": "slm.py trả về không phải dict", "loi": True}
    return kq, nguon, time.perf_counter() - bat_dau


# ---------------------------------------------------------------- vòng lặp 5 bước cho 1 phiên
def xu_ly_phien(so, may, logon, ds, con, mh, a):
    """Chạy 5 bước trên 1 phiên. Trả về (kết quả, mã kỹ thuật, điểm).
    kết quả: "BINH_THUONG" | "CHUA_XAC_NHAN" | "KET_LUAN" | "LOI_SLM"."""
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
    bo = [m for m in ung_vien if diem[m] < a.nguong]
    ung_vien = [m for m in ung_vien if diem[m] >= a.nguong]   # chỉ ứng viên đạt ngưỡng mới được xét ở bước 3-5
    if bo:
        print(f"    bỏ ứng viên dưới ngưỡng: {', '.join(bo)}")
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
    if a.khong_slm:
        dong_log = []
        kq, nguon, giay = goi_mo_hinh_ngon_ngu(dong_log, ung_vien, dv, True)
        print(f"[4] {nguon}: không hỏi mô hình ngôn ngữ, ứng viên {ung_vien}")
    else:
        dong_log, so_sk = chon_dong_cho_slm(ds_loc, dv, ung_vien)
        kq, nguon, giay = goi_mo_hinh_ngon_ngu(dong_log, ung_vien, dv, False)
        print(f"[4] Hỏi mô hình ngôn ngữ ({nguon}, {giay:.1f} giây): gửi {len(dong_log)} dòng "
              f"({so_sk} sự kiện quanh dấu vết, trong {len(ds_loc)} sự kiện của phiên) + ứng viên {ung_vien}")
        if a.in_dong_slm:
            for d in dong_log:
                print(f"       | {d}")
    print("    trả về: " + json.dumps(kq, ensure_ascii=False)[:600])

    # ---- Bước 5
    if kq.get("loi"):
        print(f"[5] SLM LỖI: {kq.get('ly_do')}")
        print("    => Không kết luận. Ghi riêng là SLM lỗi (không gộp vào chưa xác nhận).")
        return "LOI_SLM", None, cao_nhat
    chon = kq.get("ma_ky_thuat")
    trong_ds = chon in ung_vien
    du_dv = trong_ds and dv[chon]["du"]
    cho_phep = dong_log + [d for m in ung_vien for _, ds_ in dv[m]["bang_chung"] for d in ds_]
    bc = [b for b in kq.get("bang_chung", []) if isinstance(b, str) and b.strip()]
    bc_that = [b for b in bc if any(b.strip() in d or d in b for d in cho_phep)]
    print(f"[5] Kiểm chứng {chon}: nằm trong ứng viên: {'có' if trong_ds else 'KHÔNG'} | "
          f"đủ dấu vết: {'có' if du_dv else 'KHÔNG'} | bằng chứng có thật trong log: {len(bc_that)}/{len(bc)}")
    if trong_ds and du_dv:
        buoc_ke = train.doan_buoc_ke(seq[-1], chon, mh) if seq else None
        print(f"    => KẾT LUẬN: {chon} (điểm khớp {diem[chon]:.3f})")
        if buoc_ke:
            print(f"    Bước tiếp theo hay gặp sau '{seq[-1]}': {buoc_ke}")
        return "KET_LUAN", chon, diem[chon]
    if chon == "CHUA_XAC_NHAN":
        print(f"    => CHƯA XÁC NHẬN: mô hình cho rằng log không thể hiện kỹ thuật nào ({kq.get('ly_do', '')[:200]})")
        return "CHUA_XAC_NHAN", "SLM_BAC", cao_nhat
    else:
        print("    => CHƯA XÁC NHẬN: mô hình chọn kỹ thuật không qua kiểm chứng -> không kết luận, chờ thêm sự kiện.")
    return "CHUA_XAC_NHAN", chon, cao_nhat


# ---------------------------------------------------------------- chế độ phát lại (--phat-lai)
def ten_ket_qua(kq, ma):
    return {"BINH_THUONG": "BÌNH THƯỜNG",
            "CHUA_XAC_NHAN": f"CHƯA XÁC NHẬN ({ma})",
            "KET_LUAN": f"KẾT LUẬN {ma}",
            "LOI_SLM": "SLM LỖI"}[kq]


def phat_lai(con, mh, a):
    """Nạp sự kiện vào su_kien theo thứ tự thời gian, mỗi đợt a.phat_lai sự kiện, như log đang đến dần.
    Sau mỗi đợt, gom phiên lại và chạy vòng lặp 5 bước cho các phiên vừa có sự kiện mới.
    Chỉ in khi quyết định của một phiên thay đổi. Phiên đã KẾT LUẬN thì giữ nguyên, không xét lại.
    Trả về danh sách (nhãn phiên, kết quả, mã kỹ thuật, điểm) cho phần tổng kết."""
    con.execute("CREATE OR REPLACE TABLE tat_ca AS SELECT *, row_number() OVER "
                "(ORDER BY thoi_gian, nguon, record_id) AS stt FROM su_kien")
    tong = con.execute("SELECT count(*) FROM tat_ca").fetchone()[0]
    print(f"PHÁT LẠI {tong} sự kiện theo thời gian, mỗi đợt {a.phat_lai} sự kiện. "
          f"Chỉ in khi quyết định của một phiên thay đổi.")

    trang_thai = {}   # (máy, LogonId, file, record_id của sự kiện đầu) -> (số sự kiện đã xét, nhãn, kq, mã, điểm)
    so_lan_doi = 0
    for den in range(a.phat_lai, tong + a.phat_lai, a.phat_lai):
        den = min(den, tong)
        con.execute(f"CREATE OR REPLACE TABLE su_kien AS SELECT * EXCLUDE (stt) FROM tat_ca WHERE stt <= {den}")
        gio = con.execute(f"SELECT thoi_gian FROM tat_ca WHERE stt = {den}").fetchone()[0]
        phien_list, _, _ = gom_phien(con)
        for so, ((may, logon), ds) in enumerate(phien_list, 1):
            khoa = (may, logon, ds[0]["nguon"], ds[0]["record_id"])   # không đổi khi phiên dài thêm
            cu = trang_thai.get(khoa)
            if cu and (cu[0] == len(ds) or cu[2] == "KET_LUAN"):
                continue                                             # không có gì mới, hoặc đã kết luận
            bo_dem = io.StringIO()
            with contextlib.redirect_stdout(bo_dem):                 # giữ lại chi tiết 5 bước, chỉ in khi cần
                kq, ma, d = xu_ly_phien(so, may, logon, ds, con, mh, a)
            nhan = f"máy {may} | LogonId {logon}"
            truoc = (cu[2], cu[3]) if cu else ("BINH_THUONG", None)
            trang_thai[khoa] = (len(ds), nhan, kq, ma, d)
            if (kq, ma) != truoc:
                so_lan_doi += 1
                print(f"\n>>> [sự kiện {den}/{tong} | {gio}] {nhan} | {len(ds)} sự kiện: "
                      f"{ten_ket_qua(*truoc)} -> {ten_ket_qua(kq, ma)} (điểm {d:.3f})")
                if kq != "BINH_THUONG":
                    print(bo_dem.getvalue().strip("\n"))
        if a.tre:
            time.sleep(a.tre)
    print(f"\nPhát lại xong: {tong} sự kiện, {len(trang_thai)} phiên, {so_lan_doi} lần quyết định thay đổi.")
    return [(nhan, kq, ma, d) for _, nhan, kq, ma, d in trang_thai.values()]


def main():
    ap = argparse.ArgumentParser(description="Agent phát hiện kỹ thuật tấn công trong log Sysmon")
    ap.add_argument("duong_dan", nargs="+", help="file log hoặc thư mục")
    ap.add_argument("--mo-hinh", default=os.path.join(GOC_REPO, "models", "mau_chuoi.json"))
    ap.add_argument("--nguong", type=float, default=0.5, help="điểm khớp tối thiểu để đi tiếp bước 3 (mặc định 0.5, chốt từ bảng báo động giả)")
    ap.add_argument("--so-ung-vien", type=int, default=3)
    ap.add_argument("--db", default="output/agent.duckdb")
    ap.add_argument("--phien", type=int, nargs="*", help="chỉ xét các phiên có số thứ tự này")
    ap.add_argument("--chi-tiet", action="store_true", help="in chi tiết cả phiên điểm thấp")
    ap.add_argument("--khong-slm", "--ban-tam", dest="khong_slm", action="store_true",
                    help="bỏ bước hỏi mô hình ngôn ngữ, chỉ dùng luật + dấu vết (tên cũ: --ban-tam)")
    ap.add_argument("--in-dong-slm", action="store_true", help="in các dòng log gửi cho mô hình ngôn ngữ ở bước 4")
    ap.add_argument("--phat-lai", type=int, nargs="?", const=1, default=0, metavar="N",
                    help="phát lại log theo thời gian, mỗi đợt N sự kiện (mặc định 1); chỉ in khi quyết định thay đổi")
    ap.add_argument("--tre", type=float, default=0.0, help="số giây nghỉ giữa 2 đợt khi phát lại (để demo dễ theo dõi)")
    a = ap.parse_args()

    mh = nap_mo_hinh(a.mo_hinh)
    if a.khong_slm:
        print("Chế độ: KHÔNG SLM (bước 4 chỉ dùng luật + dấu vết)")
    else:
        print(f"Chế độ: CÓ SLM (model {os.environ.get('SLM_MODEL', 'phi4-mini:latest')}), "
              f"gửi tối đa {SO_DONG_GUI_SLM} dòng quanh dấu vết, cửa sổ {CUA_SO_GIAY_SLM} giây")
    print(f"Mô hình: {a.mo_hinh} | {len(mh['so_chuoi'])} kỹ thuật | cửa sổ {train.CUA_SO} | "
          f"tỉ lệ gốc {train.RHO} | lớp bình thường: {'có' if mh['bt'] else 'không'}")

    os.makedirs(os.path.dirname(a.db) or ".", exist_ok=True)
    con = duckdb.connect(a.db)
    nap_log(con, liet_ke_file(a.duong_dan))
    tong_su_kien = con.execute("SELECT count(*) FROM su_kien").fetchone()[0]

    if a.phat_lai:
        ket_qua = phat_lai(con, mh, a)
    else:
        phien_list, _, _ = gom_phien(con)
        print(f"Đã nạp {tong_su_kien} sự kiện, gom được {len(phien_list)} phiên")
        ket_qua = []
        for so, ((may, logon), ds) in enumerate(phien_list, 1):
            if a.phien and so not in a.phien:
                continue
            ket_qua.append((f"phiên #{so}",) + xu_ly_phien(so, may, logon, ds, con, mh, a))
    con.close()

    dem = {k: sum(1 for r in ket_qua if r[1] == k) for k in ("BINH_THUONG", "CHUA_XAC_NHAN", "KET_LUAN", "LOI_SLM")}
    print("\n" + "=" * 78)
    print(f"TỔNG KẾT: {len(ket_qua)} phiên | bình thường (dừng ở bước 2): {dem['BINH_THUONG']} | "
          f"chưa xác nhận: {dem['CHUA_XAC_NHAN']} | kết luận tấn công: {dem['KET_LUAN']} | SLM lỗi: {dem['LOI_SLM']}")
    ten = {"KET_LUAN": "KẾT LUẬN", "CHUA_XAC_NHAN": "chưa xác nhận", "LOI_SLM": "SLM lỗi"}
    for nhan, kq, ma, d in ket_qua:
        if kq != "BINH_THUONG":
            print(f"   {nhan}: {ten[kq]} {ma or ''} (điểm {d:.3f})")


if __name__ == "__main__":
    main()