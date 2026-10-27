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
            files += [os.path.join(p, f) for f in sorted(os.listdir(p)) if f.lower().endswith(".evtx")]
        else:
            files.append(p)
    return files


def nap_log(con, files):
    """Tạo lại bảng su_kien và nạp các file log vào."""
    con.execute(TAO_BANG)
    for f in files:
        con.executemany("INSERT INTO su_kien VALUES (" + ", ".join(["?"] * len(COT)) + ")",
                        list(doc_evtx(f)))