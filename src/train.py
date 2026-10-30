"""Học mẫu chuỗi hành vi từ log tấn công có nhãn, đo bằng cách bỏ lần lượt từng file ra thử.

Học gì:
  1) mau_chuoi: với mỗi kỹ thuật, tỉ lệ chuỗi (trong dữ liệu học) chứa đoạn 1/2/3 ký hiệu liền nhau.
     Điểm của một chuỗi cho kỹ thuật k = trung bình, trên các đoạn của chuỗi, của (tỉ lệ ở k) x (phần của k trong tổng các kỹ thuật).
     Chia theo số chuỗi của từng kỹ thuật nên kỹ thuật nhiều dữ liệu không lấn át kỹ thuật ít dữ liệu.
  2) tiep_theo: với mỗi kỹ thuật, sau ký hiệu A thường là ký hiệu B nào (đếm).
Chuỗi dài (phiên) được chấm bằng cửa sổ trượt CUA_SO ký hiệu, lấy điểm cao nhất.

Cách chạy:
  python src/train.py                                  # học + đo trên log tấn công
  python src/train.py --lanh C:\\DACN\\log\\benign_sysmon_thien_tuan1.evtx   # thêm: đo báo động giả trên log bình thường
"""
import os, sys, csv, json, argparse, collections, time, datetime

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

GOC_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CUA_SO = 6
NGUONG = [0.05, 0.1, 0.2, 0.3, 0.4, 0.5]


# ---------------------------------------------------------------- nạp chuỗi có nhãn
def nap_chuoi_co_nhan(duong_nhan, thu_muc_splunk, duong_cache, lam_lai):
    """Trả về list dict {tep, ky_thuat, ky_hieu:[...]} (ký hiệu đã gộp lặp). Lưu cache JSON để lần sau khỏi đọc lại log."""
    if os.path.exists(duong_cache) and not lam_lai:
        with open(duong_cache, encoding="utf-8") as f:
            ds = json.load(f)
        print(f"Dung cache {duong_cache}: {len(ds)} chuoi (them --lam-lai de doc lai log)")
        return ds
    import duckdb, doc_log, gan_nhan, ky_hieu
    ds = []
    with open(duong_nhan, encoding="utf-8", newline="") as f:
        dong = [r for r in csv.DictReader(f) if r["DungHuanLuyen"] == "co"]
    for i, r in enumerate(dong, 1):
        t0 = time.time()
        con = duckdb.connect()
        doc_log.nap_log(con, [os.path.join(thu_muc_splunk, *r["Tep"].split("/"))])
        for c in gan_nhan.lay_chuoi(con, r["KyThuat"]):
            ds.append({"tep": r["Tep"], "ky_thuat": r["KyThuat"],
                       "ky_hieu": [s for s, _ in ky_hieu.rut_gon_chuoi(c)]})
        con.close()
        print(f"  [{i}/{len(dong)}] {r['KyThuat']:10} {r['Tep'].split('/')[-1]:50} ({time.time() - t0:.0f}s)", flush=True)
    os.makedirs(os.path.dirname(os.path.abspath(duong_cache)), exist_ok=True)
    with open(duong_cache, "w", encoding="utf-8") as f:
        json.dump(ds, f, ensure_ascii=False)
    return ds


def khu_trung(chuoi):
    """Bỏ chuỗi giống hệt nhau trong cùng một file: một file lặp lại cùng bài thử nhiều lần
    không phải nhiều mẫu độc lập (và làm phép đo bị thổi phồng)."""
    thay, kq = set(), []
    for c in chuoi:
        khoa = (c["tep"], tuple(c["ky_hieu"]))
        if khoa not in thay:
            thay.add(khoa)
            kq.append(c)
    return kq


# ---------------------------------------------------------------- mô hình
def cac_doan(seq):
    """Tập các đoạn 1, 2, 3 ký hiệu liền nhau của chuỗi."""
    kq = set()
    for n in (1, 2, 3):
        for i in range(len(seq) - n + 1):
            kq.add(" > ".join(seq[i:i + n]))
    return kq


def hoc(chuoi, bt=None):
    """chuoi: list dict có ky_thuat, ky_hieu. bt: lớp bình thường {"so_cua_so": N, "df": {đoạn: số cửa sổ chứa nó}} hoặc None.
    Trả về mô hình (dict, lưu được thành JSON)."""
    mh = {"bt": bt, "so_chuoi": collections.Counter(), "df": collections.defaultdict(collections.Counter),
          "tiep_theo": collections.defaultdict(lambda: collections.defaultdict(collections.Counter))}
    for c in chuoi:
        k, seq = c["ky_thuat"], c["ky_hieu"]
        mh["so_chuoi"][k] += 1
        for g in cac_doan(seq):
            mh["df"][k][g] += 1
        for a, b in zip(seq, seq[1:]):
            mh["tiep_theo"][k][a][b] += 1
            mh["tiep_theo"]["_chung"][a][b] += 1
    return mh


def _ti_le(mh, g):
    return {k: mh["df"][k].get(g, 0) / mh["so_chuoi"][k] for k in mh["so_chuoi"]}


CACH_DIEM = "max"    # "max": đoạn cao nhất; "hoac": bằng chứng cộng dồn 1-Π(1-s); "trung_binh": trung bình các đoạn
RHO = 1e-3           # tỉ lệ gốc: một cửa sổ tấn công hiếm hơn cửa sổ bình thường bao nhiêu lần (chỉ dùng khi có lớp bình thường)


def diem_cua_so(doan, mh):
    """Điểm của một cửa sổ (tập các đoạn) cho từng kỹ thuật.
    Có lớp bình thường: s = P(kỹ thuật k | đoạn g) = f_k*RHO / (tổng f_j*RHO + f_bt)  (công thức Bayes với tỉ lệ gốc RHO).
    Không có: s = f_k * (f_k / tổng f_j)."""
    kq = {k: 0.0 for k in mh["so_chuoi"]}
    if not doan:
        return kq
    bt = mh.get("bt")
    nho = mh.setdefault("_nho", {})
    for g in doan:
        if g not in nho:
            f = _ti_le(mh, g)
            tong = sum(f.values())
            if bt:
                nho[g] = (f, tong * RHO + (bt["df"].get(g, 0) + 0.5) / (bt["so_cua_so"] + 1), True)
            else:
                nho[g] = (f, tong, False)
        f, mau, co_bt = nho[g]
        if mau <= 0:
            continue
        for k in kq:
            s = f[k] * RHO / mau if co_bt else f[k] * (f[k] / mau)
            if CACH_DIEM == "max":
                kq[k] = max(kq[k], s)
            elif CACH_DIEM == "hoac":
                kq[k] = 1 - (1 - kq[k]) * (1 - s)
            else:
                kq[k] += s
    if CACH_DIEM == "trung_binh":
        return {k: v / len(doan) for k, v in kq.items()}
    return kq


def diem_chuoi(seq, mh):
    """Điểm cao nhất của chuỗi trên các cửa sổ trượt CUA_SO ký hiệu -> {kỹ thuật: điểm}."""
    if not seq:
        return {k: 0.0 for k in mh["so_chuoi"]}
    cua_so = [seq] if len(seq) <= CUA_SO else [seq[i:i + CUA_SO] for i in range(len(seq) - CUA_SO + 1)]
    kq = {k: 0.0 for k in mh["so_chuoi"]}
    for w in cua_so:
        d = diem_cua_so(cac_doan(w), mh)
        for k in kq:
            kq[k] = max(kq[k], d[k])
    return kq


def cac_cua_so(seq, buoc=3):
    """Các cửa sổ CUA_SO ký hiệu của một chuỗi (bước nhảy buoc)."""
    if len(seq) <= CUA_SO:
        return [seq]
    kq = [seq[i:i + CUA_SO] for i in range(0, len(seq) - CUA_SO + 1, buoc)]
    if (len(seq) - CUA_SO) % buoc:
        kq.append(seq[-CUA_SO:])
    return kq


def hoc_lop_binh_thuong(chuoi_tan_cong, phien_binh_thuong):
    """Đếm, trên các cửa sổ của phiên bình thường, bao nhiêu cửa sổ chứa từng đoạn.
    Chỉ đếm đoạn từng xuất hiện trong chuỗi tấn công (đoạn khác không ảnh hưởng điểm, và nhờ vậy
    mô hình lưu lên GitHub không mang tên tiến trình riêng của máy dùng để thu log)."""
    tap = set()
    for c in chuoi_tan_cong:
        tap |= cac_doan(c["ky_hieu"])
    df, n = collections.Counter(), 0
    for seq in phien_binh_thuong:
        for w in cac_cua_so(seq):
            n += 1
            for g in cac_doan(w):
                if g in tap:
                    df[g] += 1
    return {"so_cua_so": max(n, 1), "df": df}


def doan_ky_thuat(seq, mh):
    """(kỹ thuật điểm cao nhất, điểm); (None, 0) nếu không đoạn nào khớp."""
    d = diem_chuoi(seq, mh)
    k = max(d, key=lambda x: d[x])
    return (k, d[k]) if d[k] > 0 else (None, 0.0)


def doan_buoc_ke(a, k, mh):
    """Ký hiệu hay đứng sau a trong chuỗi của kỹ thuật k (nếu chưa thấy thì dùng bảng chung)."""
    for bang in (mh["tiep_theo"].get(k, {}), mh["tiep_theo"]["_chung"]):
        if a in bang and bang[a]:
            return max(bang[a], key=lambda x: bang[a][x])
    return None


# ---------------------------------------------------------------- đo: bỏ lần lượt từng file
def nhom_thu(chuoi):
    """Nhóm để bỏ ra thử: theo file; riêng kỹ thuật chỉ có 1 file thì mỗi chuỗi là một nhóm."""
    so_file = collections.defaultdict(set)
    for c in chuoi:
        so_file[c["ky_thuat"]].add(c["tep"])
    nhom = []
    for i, c in enumerate(chuoi):
        nhom.append(f"{c['tep']}#{i}" if len(so_file[c["ky_thuat"]]) < 2 else c["tep"])
    return nhom, {k: len(v) for k, v in so_file.items()}


def do_bo_tung_nhom(chuoi, bt=None):
    nhom, so_file = nhom_thu(chuoi)
    ketqua = []        # mỗi chuỗi thử: dict
    for g in sorted(set(nhom)):
        hoc_ds = [c for c, n in zip(chuoi, nhom) if n != g]
        thu_ds = [c for c, n in zip(chuoi, nhom) if n == g]
        mh = hoc(hoc_ds, bt)
        for c in thu_ds:
            seq, that = c["ky_hieu"], c["ky_thuat"]
            if that not in mh["so_chuoi"]:
                continue                              # kỹ thuật không còn chuỗi nào để học
            k, d = doan_ky_thuat(seq, mh)
            dung_bk = dung_bk_that = tong_vt = 0
            for i in range(len(seq) - 1):
                khat, _ = doan_ky_thuat(seq[:i + 1], mh)
                tong_vt += 1
                dung_bk += doan_buoc_ke(seq[i], khat, mh) == seq[i + 1] if khat else 0
                dung_bk_that += doan_buoc_ke(seq[i], that, mh) == seq[i + 1]
            ketqua.append({"that": that, "doan": k, "diem": d, "vt": tong_vt,
                           "dung_bk": int(dung_bk), "dung_bk_that": int(dung_bk_that)})
    return ketqua, so_file


def in_bang_do(ketqua, so_file, chuoi):
    print("\n===== Ket qua do (bo lan luot tung file ra thu) =====")
    print(f"{'Ky thuat':10} {'file':>4} {'chuoi':>5} {'dung KT':>8} {'khong nhan ra':>13} {'buoc ke (du doan)':>18} {'buoc ke (biet KT)':>18}  ghi chu")
    tong_c = collections.Counter(c["ky_thuat"] for c in chuoi)
    for k in sorted(tong_c):
        rs = [r for r in ketqua if r["that"] == k]
        if not rs:
            continue
        n = len(rs)
        dung = sum(r["doan"] == k for r in rs)
        khong = sum(r["doan"] is None for r in rs)
        vt = sum(r["vt"] for r in rs)
        bk = f"{100 * sum(r['dung_bk'] for r in rs) / vt:.0f}% ({vt})" if vt else "-"
        bk2 = f"{100 * sum(r['dung_bk_that'] for r in rs) / vt:.0f}% ({vt})" if vt else "-"
        ghi = []
        if so_file[k] < 2:
            ghi.append("1 file: bo tung chuoi")
        if n < 10:
            ghi.append("it du lieu")
        print(f"{k:10} {so_file[k]:>4} {n:>5} {100 * dung / n:>7.0f}% {100 * khong / n:>12.0f}% {bk:>18} {bk2:>18}  {'; '.join(ghi)}")
    ky_thuat = [k for k in sorted(tong_c) if any(r["that"] == k for r in ketqua)]
    tl = [sum(r["doan"] == k for r in ketqua if r["that"] == k) / sum(r["that"] == k for r in ketqua) for k in ky_thuat]
    print(f"\nTrung binh theo ky thuat (moi ky thuat tinh nhu nhau): dung ky thuat {100 * sum(tl) / len(tl):.0f}%")
    sai = collections.Counter((r["that"], r["doan"]) for r in ketqua if r["doan"] != r["that"])
    if sai:
        print("\nNham lan hay gap nhat (that -> du doan):")
        for (a, b), so in sai.most_common(6):
            print(f"   {a} -> {b}: {so} chuoi")


# ---------------------------------------------------------------- log bình thường
def nap_phien_binh_thuong(duong_dan, duong_db=None):
    """Đọc từng file (EVTX hoặc XML Splunk), chỉ giữ loại sự kiện cùng loại với log tấn công, gom phiên.
    duong_db: file DuckDB lưu các sự kiện đã lọc để lần sau khỏi đọc lại (chứa dữ liệu cá nhân: KHÔNG đưa lên GitHub)."""
    import duckdb, doc_log, gan_nhan, gom_phien, ky_hieu
    tong = giu = 0
    if duong_db and os.path.exists(duong_db):
        con = duckdb.connect(duong_db)
        giu = con.execute("SELECT count(*) FROM su_kien").fetchone()[0]
        print(f"Dung cache log binh thuong {duong_db}: {giu} su kien (xoa file de doc lai)")
        tong = giu
    else:
        tam = duong_db + ".tmp" if duong_db else None
        if tam and os.path.exists(tam):
            os.remove(tam)
        con = duckdb.connect(tam) if tam else duckdb.connect()
        con.execute(doc_log.TAO_BANG)
        ph = ",".join(["?"] * len(doc_log.COT))
        for f in duong_dan:
            t0 = time.time()
            lo = []
            for row in doc_log.doc_log_tu_file(f):
                tong += 1
                if gan_nhan.giu_su_kien(dict(zip(doc_log.COT, row))):
                    lo.append(row)
                    giu += 1
                    if len(lo) >= 50000:
                        con.executemany(f"INSERT INTO su_kien VALUES ({ph})", lo)
                        lo = []
            if lo:
                con.executemany(f"INSERT INTO su_kien VALUES ({ph})", lo)
            print(f"  doc {os.path.basename(f)}: {tong} su kien, giu {giu} ({time.time() - t0:.0f}s)", flush=True)
        if tam:
            con.execute("CHECKPOINT")
            con.close()
            os.replace(tam, duong_db)
            con = duckdb.connect(duong_db)
    quyen = con.execute("SELECT quyen, count(*) FROM su_kien WHERE event_id = 10 GROUP BY quyen ORDER BY 2 DESC LIMIT 8").fetchall()
    day_du = con.execute("SELECT thoi_gian, regexp_extract(image, '[^\\\\\\\\/]*$') FROM su_kien WHERE event_id = 10 AND quyen = '0x1fffff' "
                         "ORDER BY thoi_gian LIMIT 10").fetchall()
    nguon = con.execute("SELECT regexp_extract(image, '[^\\\\/]*$'), quyen, count(*) FROM su_kien WHERE event_id = 10 "
                        "GROUP BY 1, 2 ORDER BY 3 DESC LIMIT 8").fetchall()
    phien_list, _, _ = gom_phien.gom_phien(con)
    con.close()
    phien = [(p[0]["thoi_gian"], [s for s, _ in ky_hieu.rut_gon_chuoi(p)]) for _, p in phien_list if len(p) >= 1]
    phien.sort(key=lambda x: x[0])
    return phien, tong, giu, quyen, nguon, day_du


def dau_vet_binh_thuong(duong_db):
    """Bước 3 của agent: trong log bình thường có bao nhiêu sự kiện khớp dấu vết (quy tắc gan_nhan.DAU_HIEU) của từng kỹ thuật."""
    import re, duckdb, doc_log, gan_nhan
    con = duckdb.connect(duong_db, read_only=True)
    cur = con.execute("SELECT * FROM su_kien WHERE event_id IN (1, 3, 10, 11, 12, 13, 14)")
    dem, tien_trinh, vd = collections.Counter(), collections.defaultdict(set), collections.defaultdict(collections.Counter)
    tong = 0
    while True:
        rows = cur.fetchmany(50000)
        if not rows:
            break
        for r in rows:
            e = dict(zip(doc_log.COT, r))
            tong += 1
            for k in gan_nhan.DAU_HIEU:
                if gan_nhan.la_dau_hieu(k, e):
                    dem[k] += 1
                    tien_trinh[k].add(e["guid"])
                    van = re.sub(r"(?i)[a-z]:\\users\\[^\\]+", r"C:\\Users\\<user>", (e["command_line"] or e["doi_tuong"] or ""))
                    if len(vd[k]) < 300:
                        vd[k][f"ID{e['event_id']} {gan_nhan._ten(e['image'])}: {van[:80]}"] += 1
    con.close()
    print(f"\n===== Dau vet (buoc 3) tren log binh thuong: {tong} su kien xet =====")
    print(f"{'Ky thuat':10} {'su kien khop':>13} {'tien trinh':>11}  vi du")
    for k in sorted(gan_nhan.DAU_HIEU):
        vi_du = " | ".join(x for x, _ in vd[k].most_common(2))
        print(f"{k:10} {dem[k]:>13} {len(tien_trinh[k]):>11}  {vi_du[:150]}")


def quet(chuoi, bt, thu_bt, ngay):
    """Thử nhiều tỉ lệ gốc và cách chấm điểm, in gọn một dòng cho mỗi cấu hình và ngưỡng."""
    global RHO, CACH_DIEM
    print(f"\n===== QUET THAM SO ({len(thu_bt)} phien thu, ~{ngay:.1f} ngay) =====")
    print(f"{'ty_le':>7} {'cach':>5} {'nguong':>7} {'tan cong dung (TB KT)':>22} {'cua so bao dong':>18} {'canh bao/ngay':>14}")
    cu = (RHO, CACH_DIEM)
    for rho in (1e-1, 1e-2, 1e-3, 1e-4):
        for cach in ("max", "hoac"):
            RHO, CACH_DIEM = rho, cach
            kq, _ = do_bo_tung_nhom(chuoi, bt)
            cs = do_cua_so(thu_bt, hoc(chuoi, bt))
            kts = sorted({r["that"] for r in kq})
            for t_ in (0.1, 0.2, 0.3, 0.5, 0.7, 0.9):
                tc = sum(sum(r["doan"] == r["that"] and r["diem"] >= t_ for r in kq if r["that"] == k)
                         / sum(r["that"] == k for r in kq) for k in kts) / len(kts)
                bd = [x[0] >= t_ for x in cs]
                cb = sum(1 for i_, b in enumerate(bd) if b and not (i_ > 0 and bd[i_ - 1] and cs[i_ - 1][3] == cs[i_][3]))
                print(f"{rho:>7.0e} {cach:>5} {t_:>7} {100 * tc:>21.0f}% {sum(bd):>9} ({100 * sum(bd) / len(cs):>5.2f}%) {cb / ngay:>14.1f}")
    RHO, CACH_DIEM = cu


def do_cua_so(seqs, mh):
    """Chấm từng cửa sổ của các phiên. Trả về list (điểm, kỹ thuật, cửa sổ, số phiên, vị trí), theo thứ tự phiên rồi vị trí."""
    kq = []
    for pi, seq in enumerate(seqs):
        for vi, w in enumerate(cac_cua_so(seq)):
            d = diem_cua_so(cac_doan(w), mh)
            k = max(d, key=lambda x: d[x])
            kq.append((d[k], k, w, pi, vi))
    return kq


def do_binh_thuong(phien, mh):
    diem = []
    for seq in phien:
        k, d = doan_ky_thuat(seq, mh)
        diem.append((d, k, seq))
    return diem


# ---------------------------------------------------------------- lưu mô hình
def luu_mo_hinh(mh, duong_ra, thong_ke):
    out = {"phien_ban": 2, "ngay": datetime.date.today().isoformat(), "cua_so": CUA_SO, "thong_ke": thong_ke,
           "tham_so": {"cach_diem": CACH_DIEM, "ty_le": RHO},
           "binh_thuong": ({"so_cua_so": mh["bt"]["so_cua_so"], "df": dict(mh["bt"]["df"])} if mh.get("bt") else None),
           "so_chuoi": dict(mh["so_chuoi"]),
           "df": {k: dict(v) for k, v in mh["df"].items()},
           "tiep_theo": {k: {a: dict(b) for a, b in v.items()} for k, v in mh["tiep_theo"].items()}}
    os.makedirs(os.path.dirname(os.path.abspath(duong_ra)), exist_ok=True)
    with open(duong_ra, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nhan", default=os.path.join(GOC_REPO, "data", "nhan-file.csv"))
    ap.add_argument("--splunk", default=r"C:\DACN-logs\splunk\datasets\attack_techniques")
    ap.add_argument("--cache", default=r"C:\DACN-logs\chuoi-co-nhan.json")
    ap.add_argument("--lam-lai", action="store_true", help="doc lai log Splunk thay vi dung cache")
    ap.add_argument("--giu-trung", action="store_true", help="giu chuoi trung hat nhau trong cung file")
    ap.add_argument("--ra", default=os.path.join(GOC_REPO, "models", "mau_chuoi.json"))
    ap.add_argument("--lanh-cache", default=r"C:\DACN-logs\binh-thuong-loc.duckdb", help="file cache cac su kien binh thuong da loc (khong dua len GitHub)")
    ap.add_argument("--cach-diem", choices=["max", "hoac", "trung_binh"], default="max")
    ap.add_argument("--ty-le", type=float, default=1e-3, help="ti le goc tan cong/binh thuong cua mot cua so (mac dinh 1e-3)")
    ap.add_argument("--quet", action="store_true", help="thu nhieu ty le goc va cach cham diem, roi dung")
    ap.add_argument("--lanh", nargs="*", default=[], help="file log binh thuong (.evtx) de do bao dong gia")
    a = ap.parse_args()
    global CACH_DIEM, RHO
    CACH_DIEM, RHO = a.cach_diem, a.ty_le

    chuoi = nap_chuoi_co_nhan(a.nhan, a.splunk, a.cache, a.lam_lai)
    if not a.giu_trung:
        truoc = len(chuoi)
        chuoi = khu_trung(chuoi)
        print(f"Bo chuoi trung hat nhau trong cung file: {truoc} -> {len(chuoi)} chuoi (them --giu-trung de giu lai)")
    print(f"\nTong: {len(chuoi)} chuoi co nhan, {len({c['tep'] for c in chuoi})} file, "
          f"{len({c['ky_thuat'] for c in chuoi})} ky thuat")

    phien = []
    if a.lanh:
        print("\n===== Doc log binh thuong =====")
        phien, tong, giu, quyen, nguon, day_du = nap_phien_binh_thuong(a.lanh, a.lanh_cache)
        print(f"{len(phien)} phien (tu {giu}/{tong} su kien giu lai)")
        print(f"Quyen truy cap vao lsass trong log binh thuong (Event ID 10): {quyen}")
        print(f"Tien trinh hay mo lsass (ten, quyen, so lan): {nguon}")
        print(f"Cac lan mo lsass voi quyen 0x1fffff (gio, tien trinh): {[(str(t)[:19], n) for t, n in day_du]}")

    seq_binh_thuong = [s for _, s in phien]
    cat = int(len(phien) * 0.6)
    hoc_bt, thu_bt = seq_binh_thuong[:cat], seq_binh_thuong[cat:]
    bt = hoc_lop_binh_thuong(chuoi, hoc_bt) if hoc_bt else None
    if phien:
        print(f"\nLop binh thuong: hoc tu {len(hoc_bt)} phien dau (theo thoi gian), thu bao dong gia tren {len(thu_bt)} phien sau.")

    if a.quet and bt:
        ngay = max((phien[-1][0] - phien[cat][0]).total_seconds() / 86400, 0.01)
        quet(chuoi, bt, thu_bt, ngay)
        return

    ketqua0, so_file = do_bo_tung_nhom(chuoi)
    print("\n##### MO HINH CHI CO LOP TAN CONG #####")
    in_bang_do(ketqua0, so_file, chuoi)
    ketqua1 = None
    if bt:
        ketqua1, _ = do_bo_tung_nhom(chuoi, bt)
        print("\n##### MO HINH CO THEM LOP BINH THUONG #####")
        in_bang_do(ketqua1, so_file, chuoi)

    mh0 = hoc(chuoi)
    mh1 = hoc(chuoi, bt)
    mh_luu = mh1 if bt else mh0
    thong_ke = {k: {"so_chuoi": mh_luu["so_chuoi"][k], "so_file": so_file[k]} for k in mh_luu["so_chuoi"]}
    luu_mo_hinh(mh_luu, a.ra, thong_ke)
    print(f"\nDa luu mo hinh ({'co' if bt else 'khong co'} lop binh thuong) -> {a.ra}")

    if a.lanh and os.path.exists(a.lanh_cache):
        dau_vet_binh_thuong(a.lanh_cache)

    if thu_bt:
        ngay = max((phien[-1][0] - phien[cat][0]).total_seconds() / 86400, 0.01)
        for ten, mh, kq in (("CHI CO LOP TAN CONG", mh0, ketqua0), ("CO THEM LOP BINH THUONG", mh1, ketqua1)):
            if kq is None:
                continue
            cs = do_cua_so(thu_bt, mh)
            print(f"\n===== Bao dong gia: {len(cs)} cua so tu {len(thu_bt)} phien binh thuong chua tung hoc "
                  f"(~{ngay:.1f} ngay), mo hinh {ten} =====")
            print(f"{'Nguong':>7} {'tan cong nhan dung (TB KT)':>27} {'cua so bao dong':>20} {'canh bao (nhom lien tiep)':>26} {'canh bao/ngay':>14}")
            for t_ in NGUONG:
                kts = sorted({r["that"] for r in kq})
                tc = sum(sum(r["doan"] == r["that"] and r["diem"] >= t_ for r in kq if r["that"] == k)
                         / sum(r["that"] == k for r in kq) for k in kts) / len(kts)
                bd = [x[0] >= t_ for x in cs]
                canh_bao = sum(1 for i_, b in enumerate(bd) if b and not (i_ > 0 and bd[i_ - 1] and cs[i_ - 1][3] == cs[i_][3]))
                print(f"{t_:>7} {100 * tc:>26.0f}% {sum(bd):>10} ({100 * sum(bd) / len(cs):.2f}%) {canh_bao:>16} {canh_bao / ngay:>14.1f}")
            t_ = 0.3
            theo_kt = collections.Counter(x[1] for x in cs if x[0] >= t_)
            print(f"Cua so bao dong o nguong {t_}, theo ky thuat: {dict(theo_kt)}")
            thay, top = set(), []
            for x in sorted(cs, key=lambda x: -x[0]):
                khoa = tuple(x[2])
                if x[0] >= t_ and khoa not in thay:
                    thay.add(khoa)
                    top.append(x)
                if len(top) >= 6:
                    break
            for d, k, w, _, _ in top:
                print(f"   diem {d:.2f} -> {k}: " + " > ".join(s.replace("TAO_TIEN_TRINH:", "P:") for s in w))


if __name__ == "__main__":
    main()
