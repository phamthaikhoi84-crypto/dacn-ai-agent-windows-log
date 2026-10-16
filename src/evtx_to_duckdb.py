"""
Đọc 1 file .evtx (Sysmon / PowerShell) và nạp vào DuckDB.

Cách chạy:
    python src/evtx_to_duckdb.py duong_dan\\file.evtx
    python src/evtx_to_duckdb.py duong_dan\\file.evtx --db output/events.duckdb

Mỗi lần chạy sẽ THÊM bản ghi vào bảng `events` (không xóa dữ liệu cũ).
"""

import argparse
import json
import os

import duckdb
from evtx import PyEvtxParser

# Các trường hay dùng của Sysmon / PowerShell được tách ra thành cột riêng.
# Toàn bộ EventData vẫn được giữ nguyên trong cột event_data (JSON).
COT_EVENTDATA = {
    "image": "Image",
    "command_line": "CommandLine",
    "parent_image": "ParentImage",
    "parent_command_line": "ParentCommandLine",
    "user_name": "User",
    "target_filename": "TargetFilename",
    "target_object": "TargetObject",         # Sysmon 12/13: khóa registry
    "details": "Details",                    # Sysmon 13: giá trị registry
    "script_block_text": "ScriptBlockText",  # PowerShell 4104
}

TAO_BANG = """
CREATE TABLE IF NOT EXISTS events (
    source_file         VARCHAR,
    record_id           BIGINT,
    time_created        TIMESTAMP,
    event_id            INTEGER,
    channel             VARCHAR,
    provider            VARCHAR,
    computer            VARCHAR,
    image               VARCHAR,
    command_line        VARCHAR,
    parent_image        VARCHAR,
    parent_command_line VARCHAR,
    user_name           VARCHAR,
    target_filename     VARCHAR,
    target_object       VARCHAR,
    details             VARCHAR,
    script_block_text   VARCHAR,
    event_data          JSON
)
"""


def lay_gia_tri(x):
    """Một số trường bị bọc dạng {"#text": ..., "#attributes": ...} -> lấy phần #text."""
    if isinstance(x, dict):
        return x.get("#text")
    return x


def doc_evtx(duong_dan):
    """Duyệt từng bản ghi trong file .evtx, trả về 1 tuple = 1 dòng của bảng events."""
    parser = PyEvtxParser(duong_dan)
    ten_file = os.path.basename(duong_dan)

    for rec in parser.records_json():
        event = json.loads(rec["data"])["Event"]
        system = event.get("System", {})
        event_data = event.get("EventData") or {}
        if not isinstance(event_data, dict):  # vài event không có EventData dạng key-value
            event_data = {"raw": event_data}

        thoi_gian = system.get("TimeCreated", {}).get("#attributes", {}).get("SystemTime")
        provider = system.get("Provider", {}).get("#attributes", {}).get("Name")

        dong = [
            ten_file,
            rec["event_record_id"],
            thoi_gian.replace("Z", "") if thoi_gian else None,
            lay_gia_tri(system.get("EventID")),
            system.get("Channel"),
            provider,
            system.get("Computer"),
        ]
        dong += [lay_gia_tri(event_data.get(truong)) for truong in COT_EVENTDATA.values()]
        dong.append(json.dumps(event_data, ensure_ascii=False))
        yield tuple(dong)


def main():
    ap = argparse.ArgumentParser(description="Nạp 1 file .evtx vào DuckDB")
    ap.add_argument("evtx", help="đường dẫn file .evtx")
    ap.add_argument("--db", default="output/events.duckdb",
                    help="file DuckDB (mặc định: output/events.duckdb)")
    args = ap.parse_args()

    os.makedirs(os.path.dirname(args.db) or ".", exist_ok=True)
    con = duckdb.connect(args.db)
    con.execute(TAO_BANG)

    cac_dong = list(doc_evtx(args.evtx))
    so_cot = 7 + len(COT_EVENTDATA) + 1
    con.executemany(f"INSERT INTO events VALUES ({', '.join(['?'] * so_cot)})", cac_dong)
    print(f"Đã nạp {len(cac_dong)} bản ghi từ {args.evtx} vào {args.db}")

    # In thống kê nhanh để kiểm tra
    ten_file = os.path.basename(args.evtx)
    con.sql(f"""
        SELECT channel, event_id, COUNT(*) AS so_luong
        FROM events WHERE source_file = '{ten_file}'
        GROUP BY ALL ORDER BY so_luong DESC
    """).show()
    con.sql(f"""
        SELECT time_created, event_id, image, left(command_line, 80) AS command_line
        FROM events WHERE source_file = '{ten_file}'
        ORDER BY time_created LIMIT 10
    """).show()
    con.close()


if __name__ == "__main__":
    main()
