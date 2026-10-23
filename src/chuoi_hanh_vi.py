"""
Demo chuỗi hành vi (tuần 2).

Ý tưởng: log Sysmon chỉ là "đối tượng". Hành vi là CHUỖI hành động có thứ tự,
cùng máy, cùng phiên đăng nhập (LogonId), cùng cây tiến trình, trong một khoảng thời gian.

Các bước script làm:
  1. Đọc 1 hoặc nhiều file .evtx, nạp vào bảng su_kien trong DuckDB.
  2. Từ Event ID 1 (tạo tiến trình) dựng quan hệ cha -> con, tìm "gốc cây" của từng tiến trình.
  3. Gom sự kiện thành "phiên hành vi": cùng máy + cùng LogonId, các sự kiện cách nhau
     không quá --khoang-cach giây (mặc định 300). Một phiên có thể gồm nhiều cây tiến trình
     (ví dụ tấn công qua WMI làm đứt cây cha-con, nhưng vẫn cùng LogonId).
  4. In ra từng phiên: cây tiến trình, dòng thời gian, và chuỗi ký hiệu hành động
     (dạng rút gọn để sau này so khớp chuỗi / dự đoán bước tiếp theo).

Cách chạy (PowerShell, đứng ở thư mục gốc của repo):
  python src\\chuoi_hanh_vi.py D:\\DACN\\log\\file1.evtx D:\\DACN\\log\\file2.evtx
  python src\\chuoi_hanh_vi.py D:\\DACN\\log           (nạp mọi file .evtx trong thư mục)
  python src\\chuoi_hanh_vi.py D:\\DACN\\log --phien 3 (chỉ in chi tiết phiên số 3)

Lưu ý: KHÔNG dùng trường RuleName để nhận diện. RuleName do người viết cấu hình Sysmon
đặt (ví dụ "CredAccess - Memdump"), dùng nó là "nhìn trộm đáp án".
"""
import argparse
import json
import os
import sys
from datetime import datetime

import duckdb
from evtx import PyEvtxParser

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")  # để in được tiếng Việt khi ghi ra file

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


def ten_ngan(path):
    return path.replace("/", "\\").split("\\")[-1] if path else "?"


def ky_hieu(e):
    """Rút gọn 1 sự kiện thành 1 ký hiệu hành động (bỏ chi tiết như PID, đường dẫn cụ thể)."""
    eid, img, dt = e["event_id"], ten_ngan(e["image"]).lower(), e["doi_tuong"] or ""
    if eid == 1:
        return f"TAO_TIEN_TRINH:{img}"
    if eid == 7:
        return f"NAP_DLL:{ten_ngan(dt).lower()}"
    if eid == 10:
        return f"MO_BO_NHO:{ten_ngan(dt).lower()}"
    if eid == 11:
        duoi = os.path.splitext(dt)[1].lower() or "(không đuôi)"
        return f"TAO_FILE:*{duoi}"
    if eid == 3:
        return f"KET_NOI_MANG:{dt.split(':')[-1]}"
    if eid in (12, 13, 14):
        return "SUA_REGISTRY"
    if eid == 4104:
        return "CHAY_SCRIPT_POWERSHELL"
    return f"EVENT_{eid}"


def mo_ta(e):
    """Mô tả 1 sự kiện bằng tiếng Việt cho người đọc."""
    eid, img, dt = e["event_id"], ten_ngan(e["image"]), e["doi_tuong"] or ""
    if eid == 1:
        return f"[1]  {ten_ngan(e['parent_image'])} chạy {img}: {e['command_line']}"
    if eid == 7:
        return f"[7]  {img} nạp DLL {dt}"
    if eid == 10:
        return f"[10] {img} mở bộ nhớ tiến trình {ten_ngan(dt)} (quyền {e['quyen']})"
    if eid == 11:
        return f"[11] {img} tạo file {dt}"
    if eid == 3:
        return f"[3]  {img} kết nối mạng tới {dt}"
    if eid in (12, 13, 14):
        return f"[{eid}] {img} sửa registry {dt}"
    if eid == 4104:
        return f"[4104] PowerShell chạy script: {dt[:80]}"
    return f"[{eid}] {img} {dt}"


def tim_goc(guid, cha_cua):
    """Leo ngược cây cha-con (chỉ trong phạm vi log có) tới tổ tiên xa nhất."""
    da_qua = set()
    while guid in cha_cua and guid not in da_qua:
        da_qua.add(guid)
        guid = cha_cua[guid]
    return guid


def main():
    ap = argparse.ArgumentParser(description="Gom log Sysmon thành chuỗi hành vi")
    ap.add_argument("duong_dan", nargs="+", help="file .evtx hoặc thư mục chứa .evtx")
    ap.add_argument("--db", default="output/chuoi_hanh_vi.duckdb")
    ap.add_argument("--khoang-cach", type=int, default=300,
                    help="2 sự kiện cách nhau quá số giây này thì tách thành 2 phiên (mặc định 300)")
    ap.add_argument("--phien", type=int, nargs="*",
                    help="chỉ in chi tiết các phiên có số thứ tự này, vd: --phien 3  hoặc  --phien 1 3")
    args = ap.parse_args()

    files = []
    for p in args.duong_dan:
        if os.path.isdir(p):
            files += [os.path.join(p, f) for f in sorted(os.listdir(p)) if f.lower().endswith(".evtx")]
        else:
            files.append(p)

    os.makedirs(os.path.dirname(args.db) or ".", exist_ok=True)
    con = duckdb.connect(args.db)
    con.execute(TAO_BANG)
    for f in files:
        con.executemany("INSERT INTO su_kien VALUES (" + ", ".join(["?"] * 14) + ")", list(doc_evtx(f)))

    # ---------- BƯỚC 1: thống kê nhanh ----------
    print("=" * 78)
    print("BƯỚC 1. Đã nạp vào DuckDB:", args.db)
    for nguon, eid, n in con.execute(
            "SELECT nguon, event_id, COUNT(*) FROM su_kien GROUP BY ALL ORDER BY nguon, event_id").fetchall():
        print(f"   {nguon:<65} Event ID {eid:<5} {n:>3} sự kiện")

    # ---------- Chuẩn bị A: cây tiến trình (từ Event ID 1) ----------
    tien_trinh = con.execute("""
        SELECT guid, parent_guid, image, parent_image, logon_id, nguoi_dung
        FROM su_kien WHERE event_id = 1
    """).fetchall()
    cha_cua = {g: pg for g, pg, *_ in tien_trinh if pg}
    thong_tin = {g: dict(image=i, parent_image=pi, logon_id=l, nguoi_dung=u) for g, _, i, pi, l, u in tien_trinh}
    ten_tien_trinh = {}  # guid -> tên exe (kể cả tiến trình cha không có Event ID 1 trong log)
    for g, pg, i, pi, *_ in tien_trinh:
        ten_tien_trinh[g] = ten_ngan(i)
        ten_tien_trinh.setdefault(pg, ten_ngan(pi))

    # ---------- Chuẩn bị B: gắn LogonId + gốc cây cho mọi sự kiện, rồi gom phiên ----------
    cot = ["nguon", "record_id", "thoi_gian", "event_id", "may", "guid", "parent_guid", "image",
           "parent_image", "command_line", "nguoi_dung", "logon_id", "doi_tuong", "quyen"]
    su_kien = [dict(zip(cot, r)) for r in con.execute(
        "SELECT * FROM su_kien ORDER BY may, thoi_gian, record_id").fetchall()]

    # LogonId của cả cây: nếu mọi tiến trình con trong cây cùng 1 LogonId thì gán LogonId đó cho cây.
    # Nhờ vậy, sự kiện của tiến trình gốc (vd explorer.exe không có Event ID 1 trong log)
    # vẫn được gom chung phiên với các tiến trình con của nó.
    logon_theo_cay = {}
    for g in thong_tin:
        tt = thong_tin[g]
        if tt["logon_id"]:
            logon_theo_cay.setdefault(tim_goc(g, cha_cua), set()).add((tt["logon_id"], tt["nguoi_dung"]))
    logon_cua_cay = {goc: next(iter(ds)) for goc, ds in logon_theo_cay.items() if len(ds) == 1}

    for e in su_kien:
        tt = thong_tin.get(e["guid"], {})
        e["goc"] = tim_goc(e["guid"], cha_cua)
        cay = logon_cua_cay.get(e["goc"], (None, None))
        # Event 7/10/11/12/13 không có LogonId -> lấy từ Event 1 của chính tiến trình, nếu không có thì lấy theo cây
        e["logon_id"] = e["logon_id"] or tt.get("logon_id") or cay[0]
        e["nguoi_dung"] = e["nguoi_dung"] or tt.get("nguoi_dung") or cay[1]
        ten_tien_trinh.setdefault(e["guid"], ten_ngan(e["image"]))

    nhom = {}
    for e in su_kien:
        khoa = (e["may"], e["logon_id"] or f"(không rõ LogonId, cây {e['goc']})")
        nhom.setdefault(khoa, []).append(e)

    phien_list = []
    for khoa, ds in nhom.items():
        phien = [ds[0]]
        for truoc, sau in zip(ds, ds[1:]):
            if (sau["thoi_gian"] - truoc["thoi_gian"]).total_seconds() > args.khoang_cach:
                phien_list.append((khoa, phien))
                phien = []
            phien.append(sau)
        phien_list.append((khoa, phien))

    # ---------- BƯỚC 2: danh sách tóm tắt các phiên ----------
    print("\n" + "=" * 78)
    print(f"BƯỚC 2. Tìm được {len(phien_list)} phiên hành vi (xem chi tiết 1 phiên: thêm --phien <số>)")
    for so, ((may, logon), ds) in enumerate(phien_list, 1):
        nguon = ", ".join(dict.fromkeys(e["nguon"] for e in ds))
        print(f"   #{so:<2} {len(ds):>3} sự kiện | {ds[0]['thoi_gian'].strftime('%Y-%m-%d %H:%M:%S')} | "
              f"{ds[0]['nguoi_dung'] or '(không rõ người dùng)'} | file: {nguon}")

    # ---------- BƯỚC 3: in chi tiết từng phiên ----------
    for so, ((may, logon), ds) in enumerate(phien_list, 1):
        if args.phien and so not in args.phien:
            continue
        cac_goc = list(dict.fromkeys(e["goc"] for e in ds))
        nhan_cay = {g: chr(ord("A") + i) for i, g in enumerate(cac_goc)}
        print("\n" + "=" * 78)
        print(f"PHIÊN HÀNH VI #{so}")
        print(f"   Máy: {may} | Người dùng: {ds[0]['nguoi_dung']} | LogonId: {logon}")
        print(f"   Thời gian: {ds[0]['thoi_gian']}  ->  {ds[-1]['thoi_gian']}"
              f"  ({(ds[-1]['thoi_gian'] - ds[0]['thoi_gian']).total_seconds():.1f} giây)")
        print(f"   Số sự kiện: {len(ds)} | Số cây tiến trình: {len(cac_goc)}"
              + ("  <- chuỗi trải qua nhiều cây, chỉ nối được nhờ LogonId + thời gian" if len(cac_goc) > 1 else ""))

        print("\n   Cây tiến trình:")
        guid_trong_phien = {e["guid"] for e in ds}

        def in_cay(g, muc):
            for con_g, cha_g in cha_cua.items():
                if cha_g == g and con_g in guid_trong_phien:
                    print("   " + "   " * muc + f"└─ {ten_tien_trinh.get(con_g)}")
                    in_cay(con_g, muc + 1)

        for g in cac_goc:
            print(f"   Cây {nhan_cay[g]}: {ten_tien_trinh.get(g, '?')}")
            in_cay(g, 1)

        print("\n   Dòng thời gian:")
        for i, e in enumerate(ds, 1):
            gio = e["thoi_gian"].strftime("%H:%M:%S.%f")[:-3]
            print(f"   {i:>2}. {gio} (cây {nhan_cay[e['goc']]}) {mo_ta(e)}")

        # chuỗi ký hiệu: gộp các bước lặp liên tiếp
        gon = []
        for k in (ky_hieu(e) for e in ds):
            if gon and gon[-1][0] == k:
                gon[-1][1] += 1
            else:
                gon.append([k, 1])
        print("\n   Chuỗi ký hiệu hành động (dùng cho so khớp chuỗi):")
        print("   " + "\n   -> ".join(k + (f" (x{n})" if n > 1 else "") for k, n in gon))

    print()
    con.close()


if __name__ == "__main__":
    main()
