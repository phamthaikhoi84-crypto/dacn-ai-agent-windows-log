"""Đo agent trên bộ thử cố định data/bo-thu.csv, ở 2 chế độ: CÓ SLM và KHÔNG SLM (chỉ luật + dấu vết).
Trả lời câu hỏi của thầy: mô hình ngôn ngữ nhỏ có giúp gì không.

Bộ thử (data/bo-thu.csv, Thiên giữ), mỗi dòng:
  Tep      tên file log, có thể kèm thư mục con (vd evtx-samples/Persistence/x.evtx); script tìm trong --thu-muc
  KyThuat  mã kỹ thuật (để trống với log bình thường)
  Phien    số thứ tự các phiên chứa kỹ thuật, theo cách agent đánh số khi chạy RIÊNG file đó (vd "3;5"),
           hoặc "tat_ca" với log bình thường
  Nhan     tan_cong | binh_thuong
  SoPhien  số phiên của file khi Thiên gán nhãn. Gom phiên ra số khác -> số thứ tự đã lệch -> BỎ file, không đo sai
  GhiChu   có chữ "can kiem tra" (ở GhiChu hoặc Phien) thì dòng đó chưa được tính;
           có "da dung ... chinh" (vd "da dung de chinh dau vet") thì file đó đã dùng để chỉnh agent:
           vẫn đo nhưng KHÔNG đưa vào bảng chính, chỉ ghi riêng để tham khảo

Cách tính:
  - Phiên tấn công: phát hiện đúng = KẾT LUẬN đúng mã. KẾT LUẬN sai mã đếm riêng.
    Bỏ sót = bình thường (dừng ở bước 2) / chưa xác nhận / SLM lỗi, ghi riêng từng loại.
  - Báo nhầm CHÍNH THỨC: phiên của log bình thường bị KẾT LUẬN tấn công. Tách theo từng máy (từng file).
  - Phiên còn lại trong file tấn công (không được Thiên đánh dấu): KẾT LUẬN ở đó chỉ ghi để THAM KHẢO,
    vì file tấn công có lẫn hoạt động bình thường và có thể có phiên tấn công chưa được đánh dấu.
  - Độ sớm: số sự kiện tính từ đầu phiên tấn công đến lúc agent đủ điều kiện KẾT LUẬN đúng mã
    (cho agent xem dần từng đoạn đầu của phiên). Chỉ tính cho phiên được kết luận đúng.

Cách chạy (PowerShell, ở thư mục gốc repo, mở Ollama trước nếu đo chế độ có SLM):
  python src\\danh_gia.py --thu-muc D:\\DoAnChuyenNganh\\log
  python src\\danh_gia.py --thu-muc D:\\DoAnChuyenNganh\\log --che-do khong-slm      (chạy nhanh, không cần Ollama)
  python src\\danh_gia.py --thu-muc D:\\DoAnChuyenNganh\\log --khong-do-som          (bỏ phần đo độ sớm)
Kết quả:
  output\\danh_gia\\bang.md              bảng để chép vào tuan-5.md / docs/models.md
  output\\danh_gia\\ket_qua_phien.csv    từng phiên, từng chế độ
  output\\danh_gia\\<che-do>\\<file>.txt   chi tiết 5 bước của các phiên có đi qua bước 3
"""
import argparse
import contextlib
import csv
import hashlib
import io
import math
import os
import re
import statistics
import subprocess
import sys
import time
import unicodedata

import duckdb

import agent
import train
from doc_log import nap_log
from gom_phien import gom_phien

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

GOC_REPO = agent.GOC_REPO
CHE_DO = {"co-slm": "Có SLM", "khong-slm": "Không SLM"}
KET_QUA = ("BINH_THUONG", "CHUA_XAC_NHAN", "KET_LUAN", "LOI_SLM")


def bo_dau(s):
    s = unicodedata.normalize("NFD", s or "")
    return "".join(c for c in s if unicodedata.category(c) != "Mn").replace("đ", "d").replace("Đ", "D").lower()


# ---------------------------------------------------------------- đọc bộ thử
def doc_bo_thu(duong):
    """Trả về (danh sách file cần đo, các dòng bị bỏ qua).
    Mỗi file: {"tep", "loai": "tan_cong"|"binh_thuong", "so_phien", "ghi_chu", "nhan": {số phiên: {mã, ...}}}"""
    with open(duong, encoding="utf-8-sig", newline="") as f:
        dong = list(csv.DictReader(f))
    can_cot = {"Tep", "KyThuat", "Phien", "Nhan", "SoPhien", "GhiChu"}
    if not dong or not can_cot <= set(dong[0]):
        sys.exit(f"LỖI: {duong} phải có các cột {sorted(can_cot)}")

    tep, bo_qua = {}, []
    for i, d in enumerate(dong, 2):                      # dòng 1 là tiêu đề
        d = {k: (v or "").strip() for k, v in d.items() if k}
        if not d["Tep"]:
            continue
        if "can kiem tra" in bo_dau(d["GhiChu"]) or "can kiem tra" in bo_dau(d["Phien"]):
            bo_qua.append((i, d["Tep"], d["KyThuat"], "còn ghi 'can kiem tra'"))
            continue
        nhan = d["Nhan"].lower()
        if nhan not in ("tan_cong", "binh_thuong"):
            bo_qua.append((i, d["Tep"], d["KyThuat"], f"Nhan '{d['Nhan']}' không hợp lệ"))
            continue
        if not d["SoPhien"].isdigit():
            bo_qua.append((i, d["Tep"], d["KyThuat"], "thiếu SoPhien"))
            continue
        t = tep.setdefault(d["Tep"], {"tep": d["Tep"], "loai": nhan, "so_phien": int(d["SoPhien"]),
                                      "ghi_chu": d["GhiChu"], "nhan": {}, "dong": [], "da_chinh": False})
        t["dong"].append(i)
        if re.search(r"da dung\b.*\bchinh", bo_dau(d["GhiChu"])):
            t["da_chinh"] = True
        if t["loai"] != nhan or t["so_phien"] != int(d["SoPhien"]):
            sys.exit(f"LỖI dòng {i}: file {d['Tep']} có các dòng khác nhau về Nhan hoặc SoPhien")
        if nhan == "tan_cong":
            if not d["KyThuat"]:
                sys.exit(f"LỖI dòng {i}: dòng tấn công thiếu KyThuat")
            so = [int(x) for x in re.findall(r"\d+", d["Phien"])]
            if not so:
                sys.exit(f"LỖI dòng {i}: dòng tấn công thiếu số phiên ở cột Phien")
            for s in so:
                t["nhan"].setdefault(s, set()).add(d["KyThuat"])
    return list(tep.values()), bo_qua


def tim_file(ten, thu_muc):
    """Tìm file của bộ thử trong các thư mục (kể cả thư mục con), không phân biệt hoa thường.
    Tep có kèm thư mục (vd evtx-samples/Persistence/x.evtx): ưu tiên file có đường dẫn kết thúc đúng như vậy;
    không có thì lấy file trùng tên (phần cuối)."""
    duoi = os.path.normcase(os.path.normpath(ten.replace("/", os.sep).replace("\\", os.sep)))
    ten_file = os.path.basename(duoi)
    trung_ten = None
    for g in thu_muc:
        for goc, _, cac_file in os.walk(g):
            for f in cac_file:
                if os.path.normcase(f) != ten_file:
                    continue
                p = os.path.join(goc, f)
                if os.path.normcase(os.path.normpath(p)).endswith(os.sep + duoi) or duoi == ten_file:
                    return p
                trung_ten = trung_ten or p
    return trung_ten


def ten_an_toan(tep):
    """Tên file chi tiết: thay / \\ : ... bằng _ để không tạo thư mục con."""
    return re.sub(r'[\\/:*?"<>|]+', "_", tep)


# ---------------------------------------------------------------- đếm lần gọi SLM
class DemSLM:
    """Bọc agent.goi_mo_hinh_ngon_ngu: đếm số lần gọi, tổng thời gian, và nhớ câu trả lời.
    Ollama chạy temperature 0, cùng dòng log + cùng ứng viên thì cùng câu trả lời, nên không hỏi lại
    (đo độ sớm phải chạy agent nhiều lần trên các đoạn đầu của cùng một phiên)."""

    def __init__(self):
        self.goc = agent.goi_mo_hinh_ngon_ngu
        self.nho, self.so_lan, self.giay = {}, 0, 0.0
        agent.goi_mo_hinh_ngon_ngu = self

    def __call__(self, dong_log, ung_vien, dv, khong_slm=False):
        if khong_slm:
            return self.goc(dong_log, ung_vien, dv, True)
        khoa = (tuple(dong_log), tuple(ung_vien))
        if khoa in self.nho:
            kq, nguon, _ = self.nho[khoa]
            return kq, nguon + ", câu trả lời đã có", 0.0
        print(f"     hỏi SLM lần {self.so_lan + 1}: {len(dong_log)} dòng, ứng viên {ung_vien} ...",
              end=" ", file=sys.stderr, flush=True)
        kq, nguon, giay = self.goc(dong_log, ung_vien, dv, False)
        self.so_lan += 1
        self.giay += giay
        print(f"{giay:.0f} giây -> {'LỖI: ' + kq.get('ly_do', '') if kq.get('loi') else kq.get('ma_ky_thuat')}",
              file=sys.stderr, flush=True)
        if not kq.get("loi"):                 # lỗi thì lần sau hỏi lại
            self.nho[khoa] = (kq, nguon, giay)
        return kq, nguon, giay


def chay_phien(so, khoa, ds, con, mh, a):
    """Chạy vòng lặp 5 bước, giữ lại phần in ra. Trả về (kết quả, mã, điểm, chữ in ra)."""
    (may, logon) = khoa
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        kq, ma, d = agent.xu_ly_phien(so, may, logon, ds, con, mh, a)
    return kq, ma, d, buf.getvalue()


def do_som(so, khoa, ds, con, mh, a, dung, dem, toi_da_slm):
    """Số sự kiện ít nhất (tính từ đầu phiên) để agent KẾT LUẬN đúng một mã trong `dung`.
    Xét lần lượt các đoạn đầu ds[:k]. Phiên dài quá 300 sự kiện thì nhảy cách đều để giữ khoảng 300 lần xét.
    Chế độ có SLM: dừng khi đã hỏi mô hình quá `toi_da_slm` lần cho phiên này, trả về None (chưa đo được)."""
    buoc = max(1, math.ceil(len(ds) / 300))
    truoc = dem.so_lan if dem else 0
    for k in list(range(buoc, len(ds), buoc)) + [len(ds)]:
        kq, ma, _, _ = chay_phien(so, khoa, ds[:k], con, mh, a)
        if kq == "KET_LUAN" and ma in dung:
            giay = (ds[k - 1]["thoi_gian"] - ds[0]["thoi_gian"]).total_seconds()
            return k, giay, buoc
        if dem and dem.so_lan - truoc >= toi_da_slm:
            return None, None, buoc
    return None, None, buoc


# ---------------------------------------------------------------- đo 1 file ở 1 chế độ
def do_file(t, duong, che_do, mh, a, dem, thu_muc_ra):
    a.khong_slm = che_do == "khong-slm"
    duong_db = os.path.join(thu_muc_ra, "danh_gia.duckdb")
    if os.path.exists(duong_db):
        os.remove(duong_db)
    con = duckdb.connect(duong_db)
    nap_log(con, [duong])
    phien_list, _, _ = gom_phien(con)
    if len(phien_list) != t["so_phien"]:
        con.close()
        return None, (f"gom được {len(phien_list)} phiên nhưng bộ thử ghi SoPhien = {t['so_phien']}: "
                      f"số thứ tự phiên đã lệch, KHÔNG đo file này (Thiên gán nhãn lại, hoặc kiểm tra gom_phien.py)")
    thieu = [s for s in t["nhan"] if s > len(phien_list)]
    if thieu:
        con.close()
        return None, f"bộ thử có phiên {thieu} nhưng file chỉ có {len(phien_list)} phiên"

    os.makedirs(os.path.join(thu_muc_ra, che_do), exist_ok=True)
    hang = []
    with open(os.path.join(thu_muc_ra, che_do, ten_an_toan(t["tep"]) + ".txt"), "w", encoding="utf-8") as chi_tiet:
        for so, (khoa, ds) in enumerate(phien_list, 1):
            if t["loai"] == "binh_thuong":
                loai, dung = "binh_thuong", set()
            elif so in t["nhan"]:
                loai, dung = "tan_cong", t["nhan"][so]
            else:
                loai, dung = "con_lai", set()
            lan_truoc = dem.so_lan if dem else 0
            giay_truoc = dem.giay if dem else 0.0
            kq, ma, d, chu = chay_phien(so, khoa, ds, con, mh, a)
            if chu.strip():
                chi_tiet.write(f"##### nhãn thật: {loai} {','.join(sorted(dung))}\n{chu}\n")
                chi_tiet.flush()
            h = {"tep": t["tep"], "da_chinh": int(t["da_chinh"]), "phien": so, "may": khoa[0], "logon_id": khoa[1], "so_su_kien": len(ds),
                 "loai": loai, "nhan_that": ";".join(sorted(dung)), "che_do": che_do, "ket_qua": kq,
                 "ma": ma or "", "diem": round(d, 3), "dung": "", "do_som_su_kien": "", "do_som_giay": "",
                 "buoc_do_som": "", "so_lan_hoi_slm": (dem.so_lan - lan_truoc) if dem else 0,
                 "giay_slm": round((dem.giay - giay_truoc) if dem else 0.0, 1)}
            if loai == "tan_cong":
                h["dung"] = int(kq == "KET_LUAN" and ma in dung)
                if h["dung"] and not a.khong_do_som:
                    k, giay, buoc = do_som(so, khoa, ds, con, mh, a, dung, dem, a.toi_da_slm_do_som)
                    h["do_som_su_kien"] = k if k else "chua_do_duoc"
                    h["do_som_giay"] = round(giay, 1) if k else ""
                    h["buoc_do_som"] = buoc
            hang.append(h)
    con.close()
    return hang, None


# ---------------------------------------------------------------- bảng kết quả
def ti_le(a, b):
    return f"{a}/{b} ({100 * a / b:.0f}%)" if b else "0/0"


def tong_hop(hang):
    tc = [h for h in hang if h["loai"] == "tan_cong"]
    bt = [h for h in hang if h["loai"] == "binh_thuong"]
    cl = [h for h in hang if h["loai"] == "con_lai"]
    som = [h["do_som_su_kien"] for h in tc if isinstance(h["do_som_su_kien"], int)]
    return {
        "tc": len(tc),
        "dung": sum(h["dung"] == 1 for h in tc),
        "sai_ma": sum(h["ket_qua"] == "KET_LUAN" and h["dung"] == 0 for h in tc),
        "sot_bt": sum(h["ket_qua"] == "BINH_THUONG" for h in tc),
        "sot_cxn": sum(h["ket_qua"] == "CHUA_XAC_NHAN" for h in tc),
        "sot_loi": sum(h["ket_qua"] == "LOI_SLM" for h in tc),
        "bt": len(bt), "nham": sum(h["ket_qua"] == "KET_LUAN" for h in bt),
        "cl": len(cl), "nham_cl": sum(h["ket_qua"] == "KET_LUAN" for h in cl),
        "loi": sum(h["ket_qua"] == "LOI_SLM" for h in hang),
        "som": statistics.median(som) if som else None, "so_som": len(som),
        "lan_slm": sum(h["so_lan_hoi_slm"] for h in hang), "giay_slm": sum(h["giay_slm"] for h in hang),
    }


def viet_bang(hang, cac_che_do, thong_tin, bo_qua, loi_file, thoi_gian):
    o = ["# Kết quả đánh giá: có SLM và không SLM", ""]
    o += [f"- {k}: {v}" for k, v in thong_tin.items()]
    o.append("")

    o += ["## Bảng chính", "",
          "| Chế độ | Phát hiện đúng (phiên tấn công) | KẾT LUẬN sai mã | Bỏ sót: dừng bước 2 / chưa xác nhận / SLM lỗi "
          "| Báo nhầm trên log bình thường | Độ sớm (trung vị, sự kiện) | SLM lỗi (mọi phiên) | Số lần hỏi SLM, tổng giây | Thời gian chạy |",
          "|---|---|---|---|---|---|---|---|---|"]
    o.insert(len(o) - 3, "Chỉ tính các file CHƯA dùng để chỉnh agent. File đã dùng để chỉnh ghi riêng ở mục Tham khảo.")
    o.insert(len(o) - 3, "")
    for cd in cac_che_do:
        t = tong_hop([h for h in hang if h["che_do"] == cd and not h["da_chinh"]])
        som = f"{t['som']:g} ({t['so_som']} phiên)" if t["som"] is not None else "-"
        slm = f"{t['lan_slm']} lần, {t['giay_slm']:.0f} giây" if cd == "co-slm" else "-"
        o.append(f"| {CHE_DO[cd]} | {ti_le(t['dung'], t['tc'])} | {t['sai_ma']} | {t['sot_bt']} / {t['sot_cxn']} / {t['sot_loi']} "
                 f"| {ti_le(t['nham'], t['bt'])} phiên | {som} | {t['loi']} | {slm} | {thoi_gian.get(cd, 0):.0f} giây |")
    o.append("")

    o += ["## Báo nhầm theo từng máy (log bình thường, số CHÍNH THỨC)", "",
          "| File | Ghi chú trong bộ thử | Số phiên | " + " | ".join(f"KẾT LUẬN nhầm ({CHE_DO[cd]})" for cd in cac_che_do)
          + (" | SLM lỗi (Có SLM) | Chưa xác nhận do SLM (Có SLM) |" if "co-slm" in cac_che_do else " |"),
          "|---|---|---|" + "---|" * (len(cac_che_do) + (2 if "co-slm" in cac_che_do else 0))]
    for tep in dict.fromkeys(h["tep"] for h in hang if h["loai"] == "binh_thuong"):
        ds = [h for h in hang if h["tep"] == tep]
        n = len([h for h in ds if h["che_do"] == cac_che_do[0]])
        cot = [str(sum(h["ket_qua"] == "KET_LUAN" for h in ds if h["che_do"] == cd)) for cd in cac_che_do]
        if "co-slm" in cac_che_do:
            co = [h for h in ds if h["che_do"] == "co-slm"]
            cot.append(str(sum(h["ket_qua"] == "LOI_SLM" for h in co)))
            cot.append(str(sum(h["ket_qua"] == "CHUA_XAC_NHAN" and h["so_lan_hoi_slm"] > 0 for h in co)))
        o.append(f"| {tep} | {thong_tin_ghi_chu.get(tep, '')} | {n} | " + " | ".join(cot) + " |")
    o.append("")

    o += ["## Phát hiện theo kỹ thuật", "",
          "| Kỹ thuật | Số phiên tấn công | " + " | ".join(f"Đúng ({CHE_DO[cd]})" for cd in cac_che_do) + " |",
          "|---|---|" + "---|" * len(cac_che_do)]
    ma_ky = sorted({m for h in hang if h["loai"] == "tan_cong" for m in h["nhan_that"].split(";")})
    for m in ma_ky:
        cot, n = [], 0
        for cd in cac_che_do:
            ds = [h for h in hang if h["che_do"] == cd and h["loai"] == "tan_cong" and not h["da_chinh"]
                  and m in h["nhan_that"].split(";")]
            n = len(ds)
            cot.append(ti_le(sum(h["dung"] == 1 for h in ds), len(ds)))
        o.append(f"| {m} | {n} | " + " | ".join(cot) + " |")
    o.append("")

    o += ["## Tham khảo (không dùng làm kết quả chính thức)", ""]
    for cd in cac_che_do:
        t = tong_hop([h for h in hang if h["che_do"] == cd and not h["da_chinh"]])
        o.append(f"- {CHE_DO[cd]}: KẾT LUẬN trên phần còn lại của file tấn công (phiên không được đánh dấu): "
                 f"{t['nham_cl']}/{t['cl']} phiên")
    da = sorted({h["tep"] for h in hang if h["da_chinh"]})
    if da:
        o.append(f"- File đã dùng để chỉnh agent (không tính vào bảng chính): {', '.join(da)}")
        for cd in cac_che_do:
            t = tong_hop([h for h in hang if h["che_do"] == cd and h["da_chinh"]])
            o.append(f"  - {CHE_DO[cd]}: phát hiện đúng {ti_le(t['dung'], t['tc'])}, "
                     f"KẾT LUẬN trên log bình thường {t['nham']}/{t['bt']} phiên, SLM lỗi {t['loi']}")
    o.append("")

    if loi_file or bo_qua:
        o += ["## Không được tính", ""]
        o += [f"- {tep}: {ly_do}" for tep, ly_do in loi_file]
        o += [f"- dòng {i} ({tep} {ky}): {ly_do}" for i, tep, ky, ly_do in bo_qua]
        o.append("")

    o += ["## Cách tính", "",
          "- Phát hiện đúng: phiên tấn công được KẾT LUẬN đúng mã. Sai mã đếm riêng, không tính là phát hiện đúng.",
          "- Báo nhầm chính thức: phiên của log bình thường bị KẾT LUẬN tấn công.",
          "- Phiên không được đánh dấu trong file tấn công chỉ để tham khảo (có thể lẫn tấn công chưa gán nhãn).",
          "- Độ sớm: số sự kiện từ đầu phiên đến khi agent đủ điều kiện KẾT LUẬN đúng mã; chỉ tính phiên được kết luận đúng.",
          "- Chế độ có SLM: SLM lỗi không được thay bằng chế độ không SLM; phiên đó tính là không kết luận.",
          "- Đọc báo nhầm có SLM cùng cột SLM lỗi: phiên SLM lỗi không bị báo nhầm, nhưng đó là do lỗi kỹ thuật,"
          " không phải SLM nhận ra là bình thường. Chỉ cột 'Chưa xác nhận do SLM' là SLM thật sự chặn lại."]
    return "\n".join(o) + "\n"


thong_tin_ghi_chu = {}


def git_commit():
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=GOC_REPO, capture_output=True,
                              text=True, timeout=10).stdout.strip() or "?"
    except Exception:
        return "?"


def main():
    ap = argparse.ArgumentParser(description="Đo agent trên bộ thử cố định, có SLM và không SLM")
    ap.add_argument("--bo-thu", default=os.path.join(GOC_REPO, "data", "bo-thu.csv"))
    ap.add_argument("--thu-muc", nargs="+", default=[r"D:\DoAnChuyenNganh\log"],
                    help="các thư mục chứa file log của bộ thử (tìm cả thư mục con)")
    ap.add_argument("--che-do", nargs="+", choices=list(CHE_DO), default=["khong-slm", "co-slm"])
    ap.add_argument("--mo-hinh", default=os.path.join(GOC_REPO, "models", "mau_chuoi.json"))
    ap.add_argument("--nguong", type=float, default=0.5)
    ap.add_argument("--so-ung-vien", type=int, default=3)
    ap.add_argument("--khong-do-som", action="store_true", help="bỏ phần đo độ sớm (chạy nhanh hơn)")
    ap.add_argument("--toi-da-slm-do-som", type=int, default=10,
                    help="khi đo độ sớm ở chế độ có SLM, hỏi mô hình tối đa chừng này lần mỗi phiên (mặc định 10)")
    ap.add_argument("--ra", default=os.path.join(GOC_REPO, "output", "danh_gia"))
    a = ap.parse_args()
    a.chi_tiet, a.in_dong_slm = False, False

    cac_tep, bo_qua = doc_bo_thu(a.bo_thu)
    for t in cac_tep:
        thong_tin_ghi_chu[t["tep"]] = t["ghi_chu"]
    mh = agent.nap_mo_hinh(a.mo_hinh)
    with open(a.mo_hinh, "rb") as f:
        bam = hashlib.sha256(f.read()).hexdigest()[:12]
    os.makedirs(a.ra, exist_ok=True)

    print(f"Bộ thử: {a.bo_thu} | {len(cac_tep)} file | bỏ qua {len(bo_qua)} dòng")
    for i, tep, ky, ly_do in bo_qua:
        print(f"   bỏ qua dòng {i} ({tep} {ky}): {ly_do}")
    loi_file, duong_file = [], {}
    for t in cac_tep:
        p = tim_file(t["tep"], a.thu_muc)
        if p:
            duong_file[t["tep"]] = p
        else:
            loi_file.append((t["tep"], f"không tìm thấy file trong {a.thu_muc}"))
            print(f"   KHÔNG TÌM THẤY: {t['tep']}")

    dem = DemSLM()
    hang, thoi_gian = [], {}
    for cd in a.che_do:
        print(f"\n===== {CHE_DO[cd]} =====")
        bat_dau = time.perf_counter()
        for t in cac_tep:
            if t["tep"] not in duong_file:
                continue
            print(f"  {t['tep']} ({t['loai']}) ...", flush=True)
            h, loi = do_file(t, duong_file[t["tep"]], cd, mh, a, dem if cd == "co-slm" else None, a.ra)
            if loi:
                print(f"     BỎ: {loi}")
                if (t["tep"], loi) not in loi_file:
                    loi_file.append((t["tep"], loi))
                continue
            tt = tong_hop(h)
            print(f"     {len(h)} phiên | tấn công đúng {tt['dung']}/{tt['tc']} | KẾT LUẬN trên log bình thường "
                  f"{tt['nham']}/{tt['bt']} | SLM lỗi {tt['loi']}")
            hang += h
        thoi_gian[cd] = time.perf_counter() - bat_dau

    thong_tin = {
        "Ngày chạy": time.strftime("%Y-%m-%d %H:%M"),
        "Commit": git_commit(),
        "Mô hình mẫu chuỗi": f"{os.path.basename(a.mo_hinh)} (sha256 {bam}), ngưỡng {a.nguong}, {a.so_ung_vien} ứng viên",
        "SLM": os.environ.get("SLM_MODEL", "phi4-mini:latest") if "co-slm" in a.che_do else "(không chạy)",
        "Bộ thử": f"{os.path.basename(a.bo_thu)}, {len(duong_file)} file đo được, {len(bo_qua)} dòng chưa tính",
    }
    with open(os.path.join(a.ra, "ket_qua_phien.csv"), "w", encoding="utf-8-sig", newline="") as f:
        if hang:
            w = csv.DictWriter(f, fieldnames=list(hang[0]))
            w.writeheader()
            w.writerows(hang)
    bang = viet_bang(hang, a.che_do, thong_tin, bo_qua, loi_file, thoi_gian)
    with open(os.path.join(a.ra, "bang.md"), "w", encoding="utf-8") as f:
        f.write(bang)
    print("\n" + bang)
    print(f"Đã ghi: {os.path.join(a.ra, 'bang.md')} và ket_qua_phien.csv")


if __name__ == "__main__":
    main()
