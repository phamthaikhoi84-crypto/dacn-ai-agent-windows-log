"""Dấu vết bắt buộc của 8 kỹ thuật, viết thành câu truy vấn DuckDB (dùng ở bước 3 và 5 của vòng lặp agent).

Dấu vết bắt buộc là điều kiện CẦN: thiếu thì agent KHÔNG được kết luận kỹ thuật đó.
Không phải điều kiện ĐỦ: quản trị viên tạo scheduled task hợp lệ vẫn có đủ dấu vết của T1053.005.
Phân biệt tấn công với hoạt động bình thường là việc của bước so khớp chuỗi, không phải của file này.

Chỉ dùng các loại sự kiện còn lại sau ky_hieu.loc_su_kien (Event 1, 3, 11, 12, 13, 14 và Event 10 vào lsass).

Cách chạy thử:
  python src\\dau_vet.py <file .evtx hoặc thư mục> [--phien 8] [--ky-thuat T1003.001]
"""
import argparse
import os
import sys

import duckdb

from doc_log import liet_ke_file, nap_log
from gom_phien import gom_phien
from ky_hieu import loai_quyen, ten_ngan

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Mỗi kỹ thuật: danh sách (tên dấu vết, điều kiện SQL trên view `phien`).
# Kỹ thuật "đủ dấu vết" khi MỌI dấu vết trong danh sách đều tìm thấy ít nhất 1 sự kiện.
# Chuỗi SQL của DuckDB không xử lý dấu \ nên đường dẫn Windows viết nguyên dạng (dùng chuỗi r"...").
DAU_VET = {
    "T1003.001": [
        ("Đọc bộ nhớ lsass.exe (Event 10 có quyền PROCESS_VM_READ)",
         r"event_id = 10 AND ends_with(lower(doi_tuong), 'lsass.exe') AND doc_bo_nho"),
    ],
    "T1021.001": [
        ("Dấu hiệu RDP: kết nối cổng 3389, chạy mstsc.exe hoặc sửa khóa Terminal Server",
         r"(event_id = 3 AND ends_with(doi_tuong, ':3389'))"
         r" OR (event_id = 1 AND ends_with(lower(image), 'mstsc.exe'))"
         r" OR (event_id IN (12, 13, 14) AND contains(lower(doi_tuong), '\terminal server'))"),
    ],
    "T1053.005": [
        ("Tạo tác vụ hẹn giờ: schtasks /create, cmdlet ScheduledTask, file trong System32/Tasks hoặc khóa TaskCache",
         r"(event_id = 1 AND regexp_matches(command_line, 'schtasks.*/create|register-scheduledtask|new-scheduledtask', 'i'))"
         r" OR (event_id = 11 AND contains(lower(doi_tuong), '\system32\tasks\'))"
         r" OR (event_id IN (12, 13, 14) AND contains(lower(doi_tuong), '\schedule\taskcache\'))"),
    ],
    "T1059.001": [
        ("PowerShell chạy với tham số ẩn / mã hóa / bỏ qua chính sách / tải và chạy mã",
         r"event_id = 1 AND regexp_matches(lower(image), '(powershell|pwsh)\.exe$')"
         r" AND regexp_matches(command_line, '-e(nc|ncodedcommand)?\s|-nop|-w(indowstyle)?\s+h|bypass|\biex\b"
         r"|invoke-expression|downloadstring|frombase64string|net\.webclient', 'i')"),
    ],
    "T1070.001": [
        ("Xóa nhật ký sự kiện: wevtutil cl, Clear-EventLog",
         r"event_id = 1 AND regexp_matches(command_line, 'wevtutil.{0,6}\s+(cl|clear-log)\s|clear-eventlog|remove-eventlog', 'i')"),
    ],
    "T1105": [
        ("Tải tệp từ xa: certutil -urlcache, bitsadmin /transfer, curl, wget, Invoke-WebRequest, DownloadFile...",
         r"event_id = 1 AND regexp_matches(command_line, 'certutil.*(urlcache|verifyctl)|bitsadmin.*/transfer"
         r"|\bcurl(\.exe)?\s|\bwget(\.exe)?\s|invoke-webrequest|\biwr\b|downloadfile|start-bitstransfer', 'i')"),
    ],
    "T1136.001": [
        ("Tạo tài khoản cục bộ: net user ... /add, New-LocalUser",
         r"event_id = 1 AND regexp_matches(command_line, 'net1?(\.exe)?.{0,2}\s+user\s.*/add|new-localuser', 'i')"),
    ],
    "T1547.001": [
        ("Ghi khóa Run/RunOnce hoặc tạo file trong thư mục Startup",
         r"(event_id IN (12, 13, 14) AND contains(lower(doi_tuong), '\currentversion\run'))"
         r" OR (event_id = 11 AND contains(lower(doi_tuong), '\start menu\programs\startup\'))"),
    ],
}


def _chuan_bi(con, ds):
    """Đưa các sự kiện của 1 phiên vào view `phien` để truy vấn.
    Cột doc_bo_nho tính bằng ky_hieu.loai_quyen, để "quyền đọc bộ nhớ" chỉ được định nghĩa ở 1 chỗ."""
    con.execute("CREATE OR REPLACE TEMP TABLE khoa_phien "
                "(nguon VARCHAR, may VARCHAR, record_id BIGINT, doc_bo_nho BOOLEAN)")
    con.executemany("INSERT INTO khoa_phien VALUES (?, ?, ?, ?)",
                    [(e["nguon"], e["may"], e["record_id"], loai_quyen(e["quyen"]) == "doc") for e in ds])
    con.execute("""
        CREATE OR REPLACE TEMP VIEW phien AS
        SELECT s.*, k.doc_bo_nho FROM su_kien s JOIN khoa_phien k
          ON s.nguon = k.nguon AND s.record_id = k.record_id AND s.may IS NOT DISTINCT FROM k.may
    """)


def dong_log(r):
    """Rút gọn 1 dòng kết quả thành 1 dòng log đọc được (làm bằng chứng)."""
    tg, eid, image, cmd, dt, quyen = r
    chi_tiet = cmd if eid == 1 else (f"{dt} (quyền {quyen})" if eid == 10 else dt)
    return f"{str(tg)[11:23]} [{eid}] {ten_ngan(image)}: {chi_tiet}"[:200]


def kiem_tra(con, ma, ds, so_dong=3):
    """Kiểm tra dấu vết bắt buộc của kỹ thuật `ma` trong phiên `ds` (list sự kiện từ gom_phien).
    Trả về {"ma", "du": bool, "thieu": [tên dấu vết], "bang_chung": [(tên dấu vết, [dòng log, ...])]}."""
    _chuan_bi(con, ds)
    kq = {"ma": ma, "du": True, "thieu": [], "bang_chung": []}
    for ten, dieu_kien in DAU_VET[ma]:
        rows = con.execute(
            "SELECT thoi_gian, event_id, image, command_line, doi_tuong, quyen FROM phien "
            f"WHERE ({dieu_kien}) ORDER BY thoi_gian LIMIT {so_dong}").fetchall()
        if rows:
            kq["bang_chung"].append((ten, [dong_log(r) for r in rows]))
        else:
            kq["du"] = False
            kq["thieu"].append(ten)
    return kq


def main():
    ap = argparse.ArgumentParser(description="Kiểm tra dấu vết bắt buộc của 8 kỹ thuật trên từng phiên")
    ap.add_argument("duong_dan", nargs="+", help="file log hoặc thư mục")
    ap.add_argument("--db", default="output/dau_vet.duckdb")
    ap.add_argument("--phien", type=int, nargs="*", help="chỉ kiểm tra các phiên có số thứ tự này")
    ap.add_argument("--ky-thuat", nargs="*", default=list(DAU_VET), help="mặc định: cả 8 kỹ thuật")
    args = ap.parse_args()

    os.makedirs(os.path.dirname(args.db) or ".", exist_ok=True)
    con = duckdb.connect(args.db)
    nap_log(con, liet_ke_file(args.duong_dan))
    phien_list, _, _ = gom_phien(con)

    for so, ((may, logon), ds) in enumerate(phien_list, 1):
        if args.phien and so not in args.phien:
            continue
        print(f"\nPHIÊN #{so} | {may} | {ds[0]['nguoi_dung']} | {len(ds)} sự kiện")
        for ma in args.ky_thuat:
            kq = kiem_tra(con, ma, ds)
            if kq["du"]:
                print(f"   {ma}: đủ dấu vết")
                for ten, cac_dong in kq["bang_chung"]:
                    print(f"      - {ten}")
                    for d in cac_dong:
                        print(f"          {d}")
            else:
                print(f"   {ma}: thiếu dấu vết ({'; '.join(kq['thieu'])})")
    con.close()


if __name__ == "__main__":
    main()