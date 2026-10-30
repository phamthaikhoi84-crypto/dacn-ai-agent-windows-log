"""Đọc log vào bảng su_kien (14 cột).
Mọi hàm đọc log (EVTX, XML Splunk...) phải trả về tuple đúng thứ tự cột trong COT."""
import json
import os
from datetime import datetime

from evtx import PyEvtxParser

TAO_BANG = """
CREATE OR REPLACE TABLE su_kien (
    nguon        VARCHAR,    -- tên file .evtx
    record_id    BIGINT,
    thoi_gian    TIMESTAMP,  -- UtcTime của Sysmon (thời điểm xảy ra hành động)
    event_id     INTEGER,
    may          VARCHAR,    -- Computer
    guid         VARCHAR,    -- tiến trình THỰC HIỆN hành động
    parent_guid  VARCHAR,    -- chỉ có ở Event ID 1
    image        VARCHAR,
    parent_image VARCHAR,
    command_line VARCHAR,
    nguoi_dung   VARCHAR,
    logon_id     VARCHAR,
    doi_tuong    VARCHAR,    -- thứ bị tác động: tiến trình đích, file, DLL, khóa registry, địa chỉ mạng...
    quyen        VARCHAR     -- GrantedAccess (Event ID 10)
)
"""

COT = ["nguon", "record_id", "thoi_gian", "event_id", "may", "guid", "parent_guid", "image",
       "parent_image", "command_line", "nguoi_dung", "logon_id", "doi_tuong", "quyen"]


def gia_tri(x):
    """evtx trả về giá trị dạng {'#text': ...} hoặc giá trị thường."""
    return x.get("#text") if isinstance(x, dict) else x


def doc_thoi_gian(event_data, system):
    utc = event_data.get("UtcTime")
    if utc:
        return datetime.strptime(utc[:23], "%Y-%m-%d %H:%M:%S.%f")
    st = system.get("TimeCreated", {}).get("#attributes", {}).get("SystemTime", "")
    return datetime.fromisoformat(st.replace("Z", "")[:26]) if st else None


def doc_evtx(duong_dan):
    ten = os.path.basename(duong_dan)
    for rec in PyEvtxParser(duong_dan).records_json():
        ev = json.loads(rec["data"])["Event"]
        sy = ev.get("System", {})
        d = ev.get("EventData") or {}
        if not isinstance(d, dict):
            d = {}
        eid = int(gia_tri(sy.get("EventID")))

        # Event ID 10 dùng tên trường khác (Source.../Target...)
        guid = d.get("ProcessGuid") or d.get("SourceProcessGUID") or d.get("SourceProcessGuid")
        image = d.get("Image") or d.get("SourceImage")
        doi_tuong = (d.get("TargetImage") or d.get("TargetFilename") or d.get("ImageLoaded")
                     or d.get("TargetObject") or d.get("ScriptBlockText"))
        if eid == 3 and d.get("DestinationIp"):
            doi_tuong = f"{d.get('DestinationIp')}:{d.get('DestinationPort')}"

        yield (ten, rec["event_record_id"], doc_thoi_gian(d, sy), eid, sy.get("Computer"),
               guid, d.get("ParentProcessGuid"), image, d.get("ParentImage"), d.get("CommandLine"),
               d.get("User"), d.get("LogonId"), doi_tuong, d.get("GrantedAccess"))


def liet_ke_file(duong_dan):
    """Nhận danh sách file/thư mục, trả về danh sách file log."""
    files = []
    for p in duong_dan:
        if os.path.isdir(p):
            files += [os.path.join(p, f) for f in sorted(os.listdir(p)) if f.lower().endswith((".evtx", ".log"))]
        else:
            files.append(p)
    return files


def nap_log(con, files):
    """Tạo lại bảng su_kien và nạp các file log vào."""
    con.execute(TAO_BANG)
    for f in files:
        con.executemany("INSERT INTO su_kien VALUES (" + ", ".join(["?"] * len(COT)) + ")",
                        list(doc_log_tu_file(f)))


# ---- Đọc log XML của Splunk (XmlWinEventLog), ra đúng 14 cột của bảng su_kien ----
import xml.etree.ElementTree as ET


def _mo_file_van_ban(duong_dan):
    """Mở file văn bản, tự nhận BOM (UTF-16 hoặc UTF-8)."""
    with open(duong_dan, "rb") as f:
        dau = f.read(3)
    if dau[:2] in (b"\xff\xfe", b"\xfe\xff"):
        ma = "utf-16"
    elif dau[:3] == b"\xef\xbb\xbf":
        ma = "utf-8-sig"
    else:
        ma = "utf-8"
    return open(duong_dan, "r", encoding=ma, errors="replace")


def _bo_ns(tag):
    return tag.split("}", 1)[-1]


def _phan_tich_xml(chuoi):
    """Một chuỗi <Event>...</Event> -> (system, du_lieu), cả hai là dict."""
    goc = ET.fromstring(chuoi)
    sy, d = {}, {}
    for nut in goc:
        ten = _bo_ns(nut.tag)
        if ten == "System":
            for con in nut:
                t = _bo_ns(con.tag)
                if t == "TimeCreated":
                    sy["SystemTime"] = con.get("SystemTime")
                elif t == "Provider":
                    sy["Provider"] = con.get("Name")
                else:
                    sy[t] = (con.text or "").strip()
        elif ten == "EventData":
            for con in nut:
                if _bo_ns(con.tag) == "Data":
                    d[con.get("Name") or "Data"] = con.text or ""
    return sy, d


def _thoi_gian_xml(d, sy):
    utc = d.get("UtcTime")
    if utc:
        return datetime.strptime(utc[:23], "%Y-%m-%d %H:%M:%S.%f")
    st = sy.get("SystemTime") or ""
    return datetime.fromisoformat(st.replace("Z", "")[:26]) if st else None


def _tach_su_kien_xml(duong_dan, thong_ke):
    """Lần lượt trả về từng chuỗi <Event>...</Event> (một dòng hoặc nhiều dòng)."""
    bo_dem = ""
    with _mo_file_van_ban(duong_dan) as f:
        for dong in f:
            if "<Event" not in bo_dem and "<Event" not in dong:
                bo_dem = ""                  # dòng không thuộc sự kiện XML nào, bỏ qua
                continue
            tu = max(0, len(bo_dem) - 8)     # chỉ tìm trong phần mới thêm vào
            bo_dem += dong
            while True:
                kt = bo_dem.find("</Event>", tu)
                if kt < 0:
                    break
                bd = max(bo_dem.rfind("<Event ", 0, kt), bo_dem.rfind("<Event>", 0, kt))
                doan = bo_dem[bd:kt + 8] if bd >= 0 else ""
                bo_dem = bo_dem[kt + 8:]
                tu = 0
                if doan:
                    yield doan
                else:
                    thong_ke["loi"] += 1
            if len(bo_dem) > 5_000_000:      # thẻ mở mà không bao giờ đóng
                bo_dem = ""
                thong_ke["loi"] += 1


def doc_xml_splunk(duong_dan, thong_ke=None):
    """Đọc 1 file log XML Splunk, ra cùng 14 giá trị như doc_evtx (chỉ lấy sự kiện Sysmon).
    thong_ke (dict, tùy chọn) được điền: doc, loi, bo_qua."""
    tk = thong_ke if thong_ke is not None else {}
    tk.update({"doc": 0, "loi": 0, "bo_qua": 0})
    phan = os.path.normpath(duong_dan).split(os.sep)
    ten = "/".join(phan[-3:])                # vd T1003.001/atomic_red_team/windows-sysmon.log
    so_thu_tu = 0
    for doan in _tach_su_kien_xml(duong_dan, tk):
        try:
            sy, d = _phan_tich_xml(doan)
        except ET.ParseError:
            tk["loi"] += 1
            continue
        if "Sysmon" not in (sy.get("Provider") or ""):
            tk["bo_qua"] += 1
            continue
        so_thu_tu += 1
        try:
            eid = int(sy.get("EventID") or 0)
            rid = int(sy.get("EventRecordID") or so_thu_tu)
        except ValueError:
            tk["loi"] += 1
            continue

        # Cùng cách gán cột như doc_evtx
        guid = d.get("ProcessGuid") or d.get("SourceProcessGUID") or d.get("SourceProcessGuid")
        image = d.get("Image") or d.get("SourceImage")
        doi_tuong = (d.get("TargetImage") or d.get("TargetFilename") or d.get("ImageLoaded")
                     or d.get("TargetObject") or d.get("ScriptBlockText"))
        if eid == 3 and d.get("DestinationIp"):
            doi_tuong = f"{d.get('DestinationIp')}:{d.get('DestinationPort')}"
        try:
            tg = _thoi_gian_xml(d, sy)
        except ValueError:
            tk["loi"] += 1
            continue
        tk["doc"] += 1
        yield (ten, rid, tg, eid, sy.get("Computer"),
               guid, d.get("ParentProcessGuid"), image, d.get("ParentImage"), d.get("CommandLine"),
               d.get("User"), d.get("LogonId"), doi_tuong, d.get("GrantedAccess"))


def doc_log_tu_file(duong_dan):
    """Chọn bộ đọc theo đuôi file: .evtx -> doc_evtx, còn lại -> XML Splunk."""
    if duong_dan.lower().endswith(".evtx"):
        return doc_evtx(duong_dan)
    return doc_xml_splunk(duong_dan)
