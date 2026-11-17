"""Theo dõi trực tiếp (K1 tuần 6): đọc sự kiện MỚI từ kênh Sysmon (và PowerShell 4104) của máy đang chạy,
nạp vào DuckDB, chạy vòng lặp 5 bước của agent.py trên các phiên vừa có sự kiện mới, in cảnh báo và ghi ra file.
Không cần xuất file .evtx.

Khác `agent.py --phat-lai`: phát lại đọc file .evtx có sẵn; theo dõi trực tiếp đọc kênh nhật ký của Windows.

Cách đọc: cứ --chu-ky giây hỏi Windows các sự kiện có EventRecordID lớn hơn số đã đọc lần trước
(mỗi kênh một bộ đếm riêng). Khi agent đang bận (vd chờ SLM 60 giây) thì sự kiện vẫn nằm trong kênh,
lần sau đọc tiếp từ chỗ cũ, không mất sự kiện.

Phiên đã KẾT LUẬN thì đặt mốc: các sự kiện đến sau đó của cùng phiên được xét như một đoạn mới
(phiên người dùng trên máy thật kéo dài hàng giờ, nếu khóa cả phiên thì lần tấn công thứ hai sẽ không được báo).

Cách chạy (PowerShell mở bằng "Run as administrator", đứng ở thư mục gốc repo):
  pip install pywin32                         (nên cài; không có thì dùng wevtutil.exe, chậm hơn)
  python src\\theo_doi.py --khong-slm          (chỉ luật + dấu vết, báo nhanh)
  python src\\theo_doi.py                      (có SLM, mỗi lần hỏi 10-120 giây trên laptop chạy CPU)
  python src\\theo_doi.py --nap-truoc-phut 30  (nạp thêm 30 phút log gần nhất để có cây tiến trình; mặc định 10)
  python src\\theo_doi.py --an-ten             (thay tên máy, tên người dùng khi in và ghi file: để chụp ảnh báo cáo)
  Dừng: Ctrl + C, agent in tổng kết (số cảnh báo / giờ) và ghi tong_ket.md.

Thử (K1), ở MỘT CỬA SỔ POWERSHELL KHÁC trong lúc theo_doi.py đang chạy:
  schtasks /create /tn DACN_ThuNghiem /tr notepad.exe /sc once /st 23:59 /f
  schtasks /delete /tn DACN_ThuNghiem /f

Kết quả ghi vào output/theo_doi/<ngày-giờ bắt đầu>/: canh_bao.csv, chi_tiet.txt, tong_ket.md.
"""
import argparse
import contextlib
import csv
import io
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone

import duckdb

import agent
import dau_vet
from doc_log import COT, TAO_BANG, _phan_tich_xml, _thoi_gian_xml
from gom_phien import gom_phien
from ky_hieu import loai_quyen

KENH_SYSMON = "Microsoft-Windows-Sysmon/Operational"
KENH_POWERSHELL = "Microsoft-Windows-PowerShell/Operational"
TEN_KQ = {"KET_LUAN": "KẾT LUẬN", "CHUA_XAC_NHAN": "CHƯA XÁC NHẬN", "LOI_SLM": "SLM LỖI", "BINH_THUONG": "BÌNH THƯỜNG"}


def bay_gio_utc():
    """Giờ UTC dạng naive, cùng kiểu với cột thoi_gian (UtcTime của Sysmon)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


LECH_GIO = datetime.now().astimezone().utcoffset()     # vd +7 giờ ở Việt Nam


def gio_may(t_utc):
    return f"{t_utc + LECH_GIO:%H:%M:%S}"


# ---------------------------------------------------------------- đọc kênh nhật ký của Windows
class LoiDocKenh(Exception):
    pass


def _giai_ma(b):
    if not b:
        return ""
    if b[:2] in (b"\xff\xfe", b"\xfe\xff") or b"\x00<" in b[:200]:
        return b.decode("utf-16", errors="replace")
    try:
        return b.decode("utf-8")
    except UnicodeDecodeError:
        return b.decode("mbcs" if os.name == "nt" else "latin-1", errors="replace")


class KenhLog:
    """Một kênh nhật ký (Sysmon hoặc PowerShell). Nhớ EventRecordID lớn nhất đã đọc."""

    def __init__(self, kenh, nguon, chi_event=None, cach="tu-dong"):
        self.kenh, self.nguon = kenh, nguon
        self.loc_eid = f"(EventID={chi_event})" if chi_event else ""
        self.cuoi = 0
        self.da_doc = 0
        self.cach = cach
        if cach == "tu-dong":
            try:
                import win32evtlog  # noqa: F401
                self.cach = "pywin32"
            except ImportError:
                self.cach = "wevtutil"

    def _xp(self, dieu_kien=""):
        phan = [p for p in (self.loc_eid, dieu_kien) if p]
        return f"*[System[{' and '.join(phan)}]]" if phan else "*"

    def _hoi(self, xpath, nguoc=False, toi_da=None):
        """Trả về danh sách chuỗi XML <Event>...</Event> theo thứ tự RecordID (nguoc=True: mới nhất trước)."""
        if self.cach == "pywin32":
            import pywintypes
            import win32evtlog
            co = win32evtlog.EvtQueryChannelPath | (
                win32evtlog.EvtQueryReverseDirection if nguoc else win32evtlog.EvtQueryForwardDirection)
            try:
                h = win32evtlog.EvtQuery(self.kenh, co, xpath)
                ra = []
                while toi_da is None or len(ra) < toi_da:
                    try:
                        cac = win32evtlog.EvtNext(h, 256)
                    except pywintypes.error as ex:
                        if ex.winerror == 259:          # ERROR_NO_MORE_ITEMS
                            break
                        raise
                    if not cac:
                        break
                    ra += [win32evtlog.EvtRender(e, win32evtlog.EvtRenderEventXml) for e in cac]
                return ra[:toi_da] if toi_da else ra
            except pywintypes.error as ex:
                raise LoiDocKenh(f"{self.kenh}: lỗi {ex.winerror} {ex.strerror}") from None
        lenh = ["wevtutil", "qe", self.kenh, f"/q:{xpath}", "/f:xml"]
        if nguoc:
            lenh.append("/rd:true")
        if toi_da:
            lenh.append(f"/c:{toi_da}")
        r = subprocess.run(lenh, capture_output=True, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        if r.returncode != 0:
            raise LoiDocKenh(f"{self.kenh}: {(_giai_ma(r.stderr) or _giai_ma(r.stdout)).strip()[:300]}")
        return re.findall(r"<Event[ >].*?</Event>", _giai_ma(r.stdout), re.S)

    def bat_dau(self, phut_truoc):
        """Đặt bộ đếm tại sự kiện mới nhất hiện có. phut_truoc > 0: trả về thêm các sự kiện trong chừng ấy phút gần nhất
        (để gom phiên có cây tiến trình đầy đủ hơn)."""
        moi_nhat = self._hoi(self._xp(), nguoc=True, toi_da=1)
        if moi_nhat:
            self.cuoi = int(_phan_tich_xml(moi_nhat[0])[0].get("EventRecordID") or 0)
        if phut_truoc <= 0 or not self.cuoi:
            return []
        ms = int(phut_truoc * 60_000)
        xml = self._hoi(self._xp(f"TimeCreated[timediff(@SystemTime) <= {ms}] and (EventRecordID <= {self.cuoi})"))
        return xml

    def doc_moi(self, toi_da=20_000):
        xml = self._hoi(self._xp(f"(EventRecordID > {self.cuoi})"), toi_da=toi_da)
        return xml


def chuyen_dong(xml, nguon, pid_minh):
    """1 chuỗi XML -> (record_id, tuple 14 cột hoặc None nếu bỏ, lý do bỏ). Gán cột giống doc_log.doc_evtx."""
    sy, d = _phan_tich_xml(xml)
    rid = int(sy.get("EventRecordID") or 0)
    eid = int(sy.get("EventID") or 0)
    # Sự kiện của chính agent (python.exe này, wevtutil.exe do nó gọi): bỏ, để agent không tự theo dõi mình
    if pid_minh in (d.get("ProcessId"), d.get("ParentProcessId"), d.get("SourceProcessId")):
        return rid, None, "cua_agent"
    guid = d.get("ProcessGuid") or d.get("SourceProcessGUID") or d.get("SourceProcessGuid")
    image = d.get("Image") or d.get("SourceImage")
    doi_tuong = (d.get("TargetImage") or d.get("TargetFilename") or d.get("ImageLoaded")
                 or d.get("TargetObject") or d.get("ScriptBlockText"))
    if eid == 3 and d.get("DestinationIp"):
        doi_tuong = f"{d.get('DestinationIp')}:{d.get('DestinationPort')}"
    try:
        tg = _thoi_gian_xml(d, sy)
    except ValueError:
        return rid, None, "loi"
    return rid, (nguon, rid, tg, eid, sy.get("Computer"), guid, d.get("ParentProcessGuid"), image,
                 d.get("ParentImage"), d.get("CommandLine"), d.get("User"), d.get("LogonId"), doi_tuong,
                 d.get("GrantedAccess")), ""


# ---------------------------------------------------------------- bọc agent: nhớ câu trả lời SLM, ghi lại dấu vết
class NhoSLM:
    """Bọc agent.goi_mo_hinh_ngon_ngu. Phiên dài thêm vài sự kiện ở xa dấu vết thì dòng gửi SLM không đổi:
    dùng lại câu trả lời cũ, không hỏi lại (mỗi lần hỏi trên laptop mất 10-120 giây)."""

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
        print(f"   ... hỏi SLM: {len(dong_log)} dòng, ứng viên {ung_vien}", end=" ", file=sys.stderr, flush=True)
        kq, nguon, giay = self.goc(dong_log, ung_vien, dv, False)
        self.so_lan += 1
        self.giay += giay
        print(f"{giay:.0f} giây -> {'LỖI' if kq.get('loi') else kq.get('ma_ky_thuat')}", file=sys.stderr, flush=True)
        if not kq.get("loi"):
            self.nho[khoa] = (kq, nguon, giay)
        return kq, nguon, giay


def chen_nhieu(con, bang, so_cot, hang, lo=400):
    """INSERT nhiều dòng trong một câu lệnh. executemany của DuckDB chèn từng dòng nên rất chậm
    (đo trên log máy Khôi: 4.000 dòng mất ~5 giây, cách này dưới 0,5 giây)."""
    mot = "(" + ", ".join(["?"] * so_cot) + ")"
    for i in range(0, len(hang), lo):
        phan = hang[i:i + lo]
        con.execute(f"INSERT INTO {bang} VALUES " + ", ".join([mot] * len(phan)),
                    [x for h in phan for x in h])


_phien_da_chuan_bi = [None]


def _chuan_bi_nhanh(con, ds):
    """Giống hệt dau_vet._chuan_bi (cùng bảng khoa_phien, cùng view phien), chỉ khác cách chèn:
    chèn nhiều dòng một lần, và không chèn lại khi bước 3 kiểm tra nhiều ứng viên trên cùng một phiên."""
    dau = (id(ds), len(ds), ds[0]["record_id"] if ds else None, ds[-1]["record_id"] if ds else None)
    if _phien_da_chuan_bi[0] == dau:
        return
    con.execute("CREATE OR REPLACE TEMP TABLE khoa_phien "
                "(nguon VARCHAR, may VARCHAR, record_id BIGINT, doc_bo_nho BOOLEAN)")
    chen_nhieu(con, "khoa_phien", 4, [(e["nguon"], e["may"], e["record_id"],
                                      loai_quyen(e["quyen"]) in ("DAY_DU", "DOC_BO_NHO")) for e in ds])
    con.execute("""
        CREATE OR REPLACE TEMP VIEW phien AS
        SELECT s.*, k.doc_bo_nho FROM su_kien s JOIN khoa_phien k
          ON s.nguon = k.nguon AND s.record_id = k.record_id AND s.may IS NOT DISTINCT FROM k.may
    """)
    _phien_da_chuan_bi[0] = dau


dau_vet._chuan_bi = _chuan_bi_nhanh


DAU_VET_LAN_CUOI = {}            # mã kỹ thuật -> kết quả dau_vet.kiem_tra của lần xét phiên gần nhất
_kiem_tra_goc = dau_vet.kiem_tra


def _kiem_tra_ghi_lai(con, ma, ds, so_dong=3):
    kq = _kiem_tra_goc(con, ma, ds, so_dong)
    DAU_VET_LAN_CUOI[ma] = kq
    return kq


dau_vet.kiem_tra = _kiem_tra_ghi_lai      # agent.py gọi dau_vet.kiem_tra qua tên module nên dùng bản này


# ---------------------------------------------------------------- theo dõi
class TheoDoi:
    def __init__(self, a):
        self.a = a
        self.mh = agent.nap_mo_hinh(a.mo_hinh)
        self.con = duckdb.connect(a.db)
        self.con.execute(TAO_BANG)
        self.pid = str(os.getpid())
        self.doc_luc = {}                 # (nguon, record_id) -> giờ UTC agent đọc được sự kiện
        self.trang_thai = {}              # khóa phiên -> dict trạng thái
        self.so_phien = 0
        self.bo = {"cua_agent": 0, "loi": 0}
        self.canh_bao = []                # các lần KET_LUAN
        self.nghi_ngo = set()             # id phiên từng CHƯA XÁC NHẬN
        self.loi_slm = 0
        self.bat_dau = bay_gio_utc()
        self.thu_muc = os.path.join(a.ra, datetime.now().strftime("%Y%m%d-%H%M%S"))
        os.makedirs(self.thu_muc, exist_ok=True)
        self.f_chi_tiet = open(os.path.join(self.thu_muc, "chi_tiet.txt"), "a", encoding="utf-8")
        self.f_csv = open(os.path.join(self.thu_muc, "canh_bao.csv"), "a", encoding="utf-8-sig", newline="")
        self.csv = csv.writer(self.f_csv)
        self.csv.writerow(["lan", "loai", "bao_luc", "may", "nguoi_dung", "logon_id", "ma_ky_thuat", "diem",
                           "so_su_kien_doan", "bang_chung_luc", "tre_doc_giay", "tre_bao_giay", "tu_log_truoc_khi_bat"])
        self.nho_slm = None if a.khong_slm else NhoSLM()
        # Thay tên máy / người dùng khi in (để chụp ảnh báo cáo)
        self.thay = []
        if a.an_ten:
            for ten, gia in ((os.environ.get("COMPUTERNAME"), "MAY-KHOI"), (os.environ.get("USERNAME"), "nguoi-dung")):
                if ten:
                    self.thay.append((re.compile(re.escape(ten), re.I), gia))

    def an(self, s):
        for mau, gia in self.thay:
            s = mau.sub(gia, s)
        return s

    def in_ra(self, s="", file_cung=True):
        s = self.an(s)
        print(s, flush=True)
        if file_cung:
            self.f_chi_tiet.write(s + "\n")
            self.f_chi_tiet.flush()

    # ---- nạp
    def nap(self, kenh, ds_xml):
        luc = bay_gio_utc()
        dong = []
        for x in ds_xml:
            try:
                rid, t, ly_do = chuyen_dong(x, kenh.nguon, self.pid)
            except Exception:
                self.bo["loi"] += 1
                continue
            kenh.cuoi = max(kenh.cuoi, rid)
            if t is None:
                self.bo[ly_do] = self.bo.get(ly_do, 0) + 1
                continue
            dong.append(t)
            self.doc_luc[(t[0], t[1])] = luc
        if dong:
            chen_nhieu(self.con, "su_kien", len(COT), dong)
            kenh.da_doc += len(dong)
        return len(dong)

    # ---- xét phiên
    def _tim_phien_cu(self, may, logon, ds):
        """Phiên đã theo dõi nhưng sự kiện đầu đổi (có sự kiện đến muộn xếp lên trước): nhận lại trạng thái cũ."""
        khoa_ds = {(e["nguon"], e["record_id"]): i for i, e in enumerate(ds)}
        for k, tt in list(self.trang_thai.items()):
            if k[0] == may and k[1] == logon and (k[2], k[3]) in khoa_ds:
                lech = khoa_ds[(k[2], k[3])]
                tt["tu"] += lech
                tt["da_xet"] += lech
                del self.trang_thai[k]
                return tt
        return None

    def xet(self, truoc_khi_bat=False):
        phien_list, _, _ = gom_phien(self.con)
        for (may, logon), ds in phien_list:
            khoa = (may, logon, ds[0]["nguon"], ds[0]["record_id"])
            tt = self.trang_thai.get(khoa) or self._tim_phien_cu(may, logon, ds)
            if tt is None:
                self.so_phien += 1
                tt = {"id": self.so_phien, "tu": 0, "da_xet": 0, "kq": "BINH_THUONG", "ma": None, "doan": 1}
            self.trang_thai[khoa] = tt
            if len(ds) == tt["da_xet"]:
                continue
            tt["da_xet"] = len(ds)
            doan = ds[tt["tu"]:]
            if not doan:
                continue
            DAU_VET_LAN_CUOI.clear()
            _phien_da_chuan_bi[0] = None
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                kq, ma, diem = agent.xu_ly_phien(tt["id"], may, logon, doan, self.con, self.mh, self.a)
            truoc = (tt["kq"], tt["ma"])
            tt["kq"], tt["ma"] = kq, ma
            if (kq, ma) == truoc:
                continue
            self.bao(tt, may, logon, doan, kq, ma, diem, truoc, buf.getvalue(), truoc_khi_bat)
            if kq == "KET_LUAN":          # đặt mốc: sự kiện sau đó xét như đoạn mới của phiên
                tt["tu"], tt["kq"], tt["ma"] = len(ds), "BINH_THUONG", None
                tt["doan"] += 1

    def bao(self, tt, may, logon, doan, kq, ma, diem, truoc, chi_tiet, truoc_khi_bat):
        luc = bay_gio_utc()
        nguoi = next((e["nguoi_dung"] for e in doan if e["nguoi_dung"]), "?")
        ten_phien = f"phiên #{tt['id']}" + (f" (đoạn {tt['doan']})" if tt["doan"] > 1 else "")
        dong_dau = (f"máy {may} | {nguoi} | LogonId {logon} | {ten_phien} | {len(doan)} sự kiện: "
                    f"{TEN_KQ[truoc[0]]}{' ' + truoc[1] if truoc[1] else ''} -> {TEN_KQ[kq]} {ma or ''}")
        bc_luc, tre_doc, tre_bao = None, None, None
        if kq == "KET_LUAN":
            khoa_bc = set(DAU_VET_LAN_CUOI.get(ma, {}).get("su_kien", []))
            tg_bc = [e for e in doan if (e["nguon"], e["record_id"]) in khoa_bc]
            if tg_bc:
                moi = max(tg_bc, key=lambda e: e["thoi_gian"])
                bc_luc = moi["thoi_gian"]
                doc = self.doc_luc.get((moi["nguon"], moi["record_id"]), luc)
                tre_doc = (doc - bc_luc).total_seconds()
                tre_bao = (luc - bc_luc).total_seconds()
            self.canh_bao.append((luc, ma, truoc_khi_bat))
            so = len(self.canh_bao)
            self.in_ra("\n" + "!" * 78)
            self.in_ra(f"!!! CẢNH BÁO #{so} lúc {gio_may(luc)}"
                       f"{' (từ log có trước khi bật theo dõi)' if truoc_khi_bat else ''} | {dong_dau} (điểm {diem:.3f})")
            if bc_luc:
                self.in_ra(f"!!! Bằng chứng mới nhất xảy ra lúc {gio_may(bc_luc)}: agent đọc được sau {tre_doc:.1f} giây, "
                           f"báo sau {tre_bao:.1f} giây")
            self.in_ra(chi_tiet.strip("\n"))
        else:
            if kq == "CHUA_XAC_NHAN":
                self.nghi_ngo.add(tt["id"])
            elif kq == "LOI_SLM":
                self.loi_slm += 1
            so = ""
            # Chưa xác nhận / SLM lỗi / trở về bình thường: in 1 dòng, chi tiết chỉ ghi vào file
            self.in_ra(f"\n[{gio_may(luc)}] {dong_dau} (điểm {diem:.3f})", file_cung=True)
            if kq != "BINH_THUONG":
                self.f_chi_tiet.write(self.an(chi_tiet) + "\n")
                self.f_chi_tiet.flush()
        if kq != "BINH_THUONG":
            hang = [so, kq, f"{luc + LECH_GIO:%Y-%m-%d %H:%M:%S}", may, nguoi, logon, ma or "", f"{diem:.3f}", len(doan),
                    f"{bc_luc + LECH_GIO:%Y-%m-%d %H:%M:%S.%f}"[:-3] if bc_luc else "",
                    f"{tre_doc:.1f}" if tre_doc is not None else "", f"{tre_bao:.1f}" if tre_bao is not None else "",
                    "co" if truoc_khi_bat else ""]
            self.csv.writerow([self.an(str(x)) for x in hang])
            self.f_csv.flush()

    # ---- tổng kết
    def tong_ket(self, kenh):
        ket = bay_gio_utc()
        gio = max((ket - self.bat_dau).total_seconds() / 3600, 1e-9)
        moi = [c for c in self.canh_bao if not c[2]]
        theo_ma = {}
        for _, ma, _ in moi:
            theo_ma[ma] = theo_ma.get(ma, 0) + 1
        dong = [
            "# Tổng kết theo dõi trực tiếp",
            "",
            f"- Thời gian: {self.bat_dau + LECH_GIO:%Y-%m-%d %H:%M:%S} -> {ket + LECH_GIO:%H:%M:%S} "
            f"({gio * 60:.1f} phút), chu kỳ đọc {self.a.chu_ky} giây, nạp trước {self.a.nap_truoc_phut} phút",
            f"- Chế độ: {'KHÔNG SLM' if self.a.khong_slm else 'CÓ SLM (' + os.environ.get('SLM_MODEL', 'phi4-mini:latest') + ')'}"
            f", ngưỡng {self.a.nguong}, {self.a.so_ung_vien} ứng viên, cách đọc kênh: {kenh[0].cach}",
            "- Sự kiện đã nạp: " + ", ".join(f"{k.nguon} {k.da_doc:,}" for k in kenh)
            + f" (bỏ {self.bo.get('cua_agent', 0):,} sự kiện của chính agent, {self.bo.get('loi', 0)} lỗi đọc)",
            f"- Phiên đã theo dõi: {self.so_phien:,}",
            f"- Cảnh báo (KẾT LUẬN) trong lúc theo dõi: {len(moi)} = {len(moi) / gio:.2f} cảnh báo / giờ"
            + (f" ({', '.join(f'{m}: {n}' for m, n in sorted(theo_ma.items()))})" if theo_ma else ""),
            f"- Cảnh báo từ log có trước khi bật: {len(self.canh_bao) - len(moi)}",
            f"- Phiên từng ở trạng thái CHƯA XÁC NHẬN: {len(self.nghi_ngo)}",
            f"- SLM lỗi: {self.loi_slm}",
        ]
        if self.nho_slm:
            dong.append(f"- Hỏi SLM: {self.nho_slm.so_lan} lần, tổng {self.nho_slm.giay:.0f} giây")
        dong.append("- Chi tiết: `canh_bao.csv`, `chi_tiet.txt` cùng thư mục")
        chu = self.an("\n".join(dong))
        print("\n" + "=" * 78 + "\n" + chu, flush=True)
        with open(os.path.join(self.thu_muc, "tong_ket.md"), "w", encoding="utf-8") as f:
            f.write(chu + "\n")
        print(f"\nĐã ghi vào {self.thu_muc}")


def main():
    goc = agent.GOC_REPO
    ap = argparse.ArgumentParser(description="Theo dõi trực tiếp log Sysmon trên máy đang chạy")
    ap.add_argument("--chu-ky", type=float, default=3.0, help="số giây giữa 2 lần đọc sự kiện mới (mặc định 3)")
    ap.add_argument("--nap-truoc-phut", type=float, default=10.0,
                    help="lúc bật, nạp thêm chừng này phút log gần nhất để có cây tiến trình (0 = chỉ sự kiện mới)")
    ap.add_argument("--khong-slm", "--ban-tam", dest="khong_slm", action="store_true",
                    help="bỏ bước hỏi mô hình ngôn ngữ, chỉ dùng luật + dấu vết")
    ap.add_argument("--khong-powershell", action="store_true", help="không đọc kênh PowerShell 4104")
    ap.add_argument("--cach-doc", choices=["tu-dong", "pywin32", "wevtutil"], default="tu-dong")
    ap.add_argument("--mo-hinh", default=os.path.join(goc, "models", "mau_chuoi.json"))
    ap.add_argument("--nguong", type=float, default=0.5)
    ap.add_argument("--so-ung-vien", type=int, default=3)
    ap.add_argument("--in-dong-slm", action="store_true", help="ghi các dòng log gửi SLM vào chi tiết")
    ap.add_argument("--db", default=":memory:", help="file DuckDB (mặc định trong RAM)")
    ap.add_argument("--ra", default=os.path.join("output", "theo_doi"))
    ap.add_argument("--an-ten", action="store_true", help="thay tên máy, tên người dùng khi in và ghi file")
    ap.add_argument("--trang-thai", type=float, default=60.0, help="số giây giữa 2 dòng trạng thái (mặc định 60)")
    a = ap.parse_args()
    a.chi_tiet = False

    td = TheoDoi(a)
    kenh = [KenhLog(KENH_SYSMON, "Sysmon (truc tiep)", cach=a.cach_doc)]
    if not a.khong_powershell:
        kenh.append(KenhLog(KENH_POWERSHELL, "PowerShell 4104 (truc tiep)", chi_event=4104, cach=a.cach_doc))

    td.in_ra(f"THEO DÕI TRỰC TIẾP | {'KHÔNG SLM' if a.khong_slm else 'CÓ SLM (' + os.environ.get('SLM_MODEL', 'phi4-mini:latest') + ')'}"
             f" | mỗi {a.chu_ky:g} giây | đọc kênh bằng {kenh[0].cach} | ghi vào {td.thu_muc}")
    for k in list(kenh):
        try:
            n = td.nap(k, k.bat_dau(a.nap_truoc_phut))
            td.in_ra(f"  {k.kenh}: bắt đầu sau RecordID {k.cuoi}, nạp trước {n:,} sự kiện ({a.nap_truoc_phut:g} phút gần nhất)")
        except LoiDocKenh as ex:
            if k.kenh == KENH_SYSMON:
                print(f"\nKhông đọc được kênh Sysmon: {ex}\n"
                      "Kiểm tra: (1) PowerShell mở bằng Run as administrator; (2) Sysmon đang chạy "
                      "(Get-Service Sysmon*).", file=sys.stderr)
                sys.exit(1)
            td.in_ra(f"  Bỏ qua {k.kenh}: {ex}")
            kenh.remove(k)
    if any(k.kenh == KENH_POWERSHELL for k in kenh):
        td.in_ra("  Ghi chú: sự kiện 4104 được nạp vào DuckDB nhưng bước 2-3 hiện chỉ dùng Event 1, 3, 10 (lsass), 11-14.")

    try:
        td.xet(truoc_khi_bat=True)
        td.in_ra(f"Đang theo dõi ({td.so_phien} phiên từ log gần nhất). Dừng bằng Ctrl + C.\n")
        lan_trang_thai = time.monotonic()
        while True:
            dau = time.monotonic()
            moi = 0
            for k in kenh:
                try:
                    moi += td.nap(k, k.doc_moi())
                except LoiDocKenh as ex:
                    print(f"[{gio_may(bay_gio_utc())}] lỗi đọc {k.kenh}: {ex}", file=sys.stderr)
            if moi:
                td.xet()
            if time.monotonic() - lan_trang_thai >= a.trang_thai:
                lan_trang_thai = time.monotonic()
                print(td.an(f"[{gio_may(bay_gio_utc())}] đã nạp " + ", ".join(f"{k.nguon.split()[0]} {k.da_doc:,}" for k in kenh)
                            + f" | {td.so_phien} phiên | cảnh báo {len(td.canh_bao)} | chưa xác nhận {len(td.nghi_ngo)}"),
                      file=sys.stderr, flush=True)
            time.sleep(max(0.0, a.chu_ky - (time.monotonic() - dau)))
    except KeyboardInterrupt:
        print("\nĐã dừng (Ctrl + C).", file=sys.stderr)
    finally:
        td.tong_ket(kenh)
        td.f_chi_tiet.close()
        td.f_csv.close()
        td.con.close()


if __name__ == "__main__":
    main()
