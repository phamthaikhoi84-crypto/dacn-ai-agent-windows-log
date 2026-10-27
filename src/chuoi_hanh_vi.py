"""
Demo chuỗi hành vi (tuần 2).

Ý tưởng: log Sysmon chỉ là "đối tượng". Hành vi là CHUỖI hành động có thứ tự,
cùng máy, cùng phiên đăng nhập (LogonId), cùng cây tiến trình, trong một khoảng thời gian.

Các bước script làm:
  1. Đọc 1 hoặc nhiều file .evtx, nạp vào bảng su_kien trong DuckDB.          (doc_log.py)
  2. Từ Event ID 1 (tạo tiến trình) dựng quan hệ cha -> con, tìm "gốc cây".     (gom_phien.py)
  3. Gom sự kiện thành "phiên hành vi": cùng máy + cùng LogonId, các sự kiện cách nhau
     không quá --khoang-cach giây (mặc định 300). Một phiên có thể gồm nhiều cây tiến trình
     (ví dụ tấn công qua WMI làm đứt cây cha-con, nhưng vẫn cùng LogonId).    (gom_phien.py)
  4. In ra từng phiên: cây tiến trình, dòng thời gian, và chuỗi ký hiệu hành động
     (dạng rút gọn để sau này so khớp chuỗi / dự đoán bước tiếp theo).        (ky_hieu.py)

Cách chạy (PowerShell, đứng ở thư mục gốc của repo):
  python src\\chuoi_hanh_vi.py D:\\DoAnChuyenNganh\\log\\file1.evtx D:\\DoAnChuyenNganh\\log\\file2.evtx
  python src\\chuoi_hanh_vi.py D:\\DoAnChuyenNganh\\log           (nạp mọi file .evtx trong thư mục)
  python src\\chuoi_hanh_vi.py D:\\DoAnChuyenNganh\\log --phien 3 (chỉ in chi tiết phiên số 3)

Lưu ý: KHÔNG dùng trường RuleName để nhận diện. RuleName do người viết cấu hình Sysmon
đặt (ví dụ "CredAccess - Memdump"), dùng nó là "nhìn trộm đáp án".
"""
import argparse
import os
import sys

import duckdb

from doc_log import liet_ke_file, nap_log
from ky_hieu import mo_ta, rut_gon_chuoi
from gom_phien import gom_phien

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")  # để in được tiếng Việt khi ghi ra file


def main():
    ap = argparse.ArgumentParser(description="Gom log Sysmon thành chuỗi hành vi")
    ap.add_argument("duong_dan", nargs="+", help="file .evtx hoặc thư mục chứa .evtx")
    ap.add_argument("--db", default="output/chuoi_hanh_vi.duckdb")
    ap.add_argument("--khoang-cach", type=int, default=300,
                    help="2 sự kiện cách nhau quá số giây này thì tách thành 2 phiên (mặc định 300)")
    ap.add_argument("--phien", type=int, nargs="*",
                    help="chỉ in chi tiết các phiên có số thứ tự này, vd: --phien 3  hoặc  --phien 1 3")
    args = ap.parse_args()

    files = liet_ke_file(args.duong_dan)

    os.makedirs(os.path.dirname(args.db) or ".", exist_ok=True)
    con = duckdb.connect(args.db)
    nap_log(con, files)

    # ---------- BƯỚC 1: thống kê nhanh ----------
    print("=" * 78)
    print("BƯỚC 1. Đã nạp vào DuckDB:", args.db)
    for nguon, eid, n in con.execute(
            "SELECT nguon, event_id, COUNT(*) FROM su_kien GROUP BY ALL ORDER BY nguon, event_id").fetchall():
        print(f"   {nguon:<65} Event ID {eid:<5} {n:>3} sự kiện")

    # ---------- Gom phiên (gom_phien.py) ----------
    phien_list, cha_cua, ten_tien_trinh = gom_phien(con, args.khoang_cach)

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
        gon = rut_gon_chuoi(ds)
        print("\n   Chuỗi ký hiệu hành động (dùng cho so khớp chuỗi):")
        print("   " + "\n   -> ".join(k + (f" (x{n})" if n > 1 else "") for k, n in gon))

    print()
    con.close()


if __name__ == "__main__":
    main()