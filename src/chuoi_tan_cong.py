"""Nối các KẾT LUẬN của cùng một máy thành chuỗi tấn công theo giai đoạn (K2 tuần 7).

Hai cách dùng:
  1) Trong theo_doi.py: mỗi lần có KẾT LUẬN thì gọi ChuoiTanCong.them(). Khi chuỗi của máy đó có từ
     2 kỹ thuật khác nhau thì theo_doi.py in chuỗi ra (và ghi vào tong_ket.md lúc dừng).
  2) Chạy riêng trên file .evtx: phát lại từng sự kiện qua ĐÚNG vòng xét của theo_doi.py, rồi in chuỗi.
       python src\\chuoi_tan_cong.py <file.evtx> --khong-slm
       python src\\chuoi_tan_cong.py <file.evtx> --khong-slm --mong-doi T1105,T1059.001,T1547.001
     hoặc qua dacn.py:  python src\\dacn.py chuoi <file.evtx> --khong-slm

Vì sao phải phát lại qua theo_doi.py:
  agent.py (quet / phat-lai) cho mỗi phiên MỘT kết quả, phiên đã KẾT LUẬN thì không xét lại. Chuỗi tấn công
  thật thường nằm trọn trong một phiên (cùng LogonId, các bước cách nhau dưới 300 giây), nên quet chỉ ra
  1 kỹ thuật. theo_doi.py đặt mốc sau mỗi KẾT LUẬN, sự kiện sau mốc được xét như đoạn mới, nhờ vậy mỗi bước
  của chuỗi có cơ hội ra KẾT LUẬN riêng. File này KHÔNG đổi bước 1-5 của agent, không đổi dấu vết hay mô hình.

Quy tắc nối:
  - Chỉ nối KẾT LUẬN cùng máy.
  - Cùng mã kỹ thuật lặp lại trong vòng GOP_GIAY giây: coi là một bước (vd net.exe rồi net1.exe,
    hai lần rundll32 mở lsass). Lưu ý trung thực: quy tắc này đặt sau khi thấy các bước lặp trên log T1
    của Thiên; nó chỉ gộp cách hiển thị, không thêm hay bỏ KẾT LUẬN nào.
  - Hai KẾT LUẬN liên tiếp cách nhau quá --khoang-phut phút (mặc định 60): bắt đầu chuỗi mới.
  - Giai đoạn theo chuỗi 8 kỹ thuật của đề tài: xâm nhập, thực thi, bám trụ, đánh cắp đăng nhập,
    lan rộng, xóa dấu vết. Chuỗi có bước "lùi" giai đoạn (vd xóa dấu vết rồi mới xâm nhập) thì được ghi chú,
    không bị bỏ: có thể là bước chuẩn bị, hai đợt tấn công nối nhau, hoặc một KẾT LUẬN nhầm.
"""
import argparse
import contextlib
import io
import os
import sys
from datetime import timedelta

GOP_GIAY = 300          # bằng khoảng cách ngắt phiên của gom_phien.py

# mã kỹ thuật -> (số thứ tự giai đoạn, tên giai đoạn, tên kỹ thuật)
GIAI_DOAN = {
    "T1105":     (1, "Xâm nhập",           "Ingress Tool Transfer"),
    "T1059.001": (2, "Thực thi",           "PowerShell"),
    "T1053.005": (3, "Bám trụ",            "Scheduled Task"),
    "T1547.001": (3, "Bám trụ",            "Registry Run Keys / Startup Folder"),
    "T1136.001": (3, "Bám trụ",            "Create Account: Local Account"),
    "T1003.001": (4, "Đánh cắp đăng nhập", "LSASS Memory"),
    "T1021.001": (5, "Lan rộng",           "Remote Desktop Protocol"),
    "T1070.001": (6, "Xóa dấu vết",        "Clear Windows Event Logs"),
}


def giai_doan(ma):
    return GIAI_DOAN.get(ma, (0, "Khác", ma))


class ChuoiTanCong:
    """Giữ các chuỗi theo từng máy. Mỗi chuỗi là list bước: {ma, dau, cuoi, so_lan, diem}."""

    def __init__(self, khoang_phut=60, gop_giay=GOP_GIAY):
        self.khoang = timedelta(minutes=khoang_phut)
        self.gop = timedelta(seconds=gop_giay)
        self.theo_may = {}

    def them(self, may, luc, ma, diem=None):
        """Thêm 1 KẾT LUẬN (luc = giờ UTC của bằng chứng). Trả về chuỗi hiện tại của máy đó."""
        ds = self.theo_may.setdefault(may, [])
        if not ds or luc - ds[-1][-1]["cuoi"] > self.khoang:
            ds.append([])
        chuoi = ds[-1]
        if chuoi and chuoi[-1]["ma"] == ma and luc - chuoi[-1]["cuoi"] <= self.gop:
            chuoi[-1]["cuoi"] = max(chuoi[-1]["cuoi"], luc)
            chuoi[-1]["so_lan"] += 1
        else:
            chuoi.append({"ma": ma, "dau": luc, "cuoi": luc, "so_lan": 1, "diem": diem})
        return chuoi

    def cac_chuoi(self, toi_thieu=2):
        """[(máy, chuỗi)] có từ toi_thieu kỹ thuật khác nhau."""
        return [(may, c) for may, ds in self.theo_may.items() for c in ds if so_ky_thuat(c) >= toi_thieu]


def so_ky_thuat(chuoi):
    return len({b["ma"] for b in chuoi})


def luc_bang_chung(doan, khoa_bang_chung):
    """Giờ của bằng chứng SỚM nhất trong đoạn (để xếp thứ tự bước). Không có bằng chứng thì None."""
    tg = [e["thoi_gian"] for e in doan if (e["nguon"], e["record_id"]) in khoa_bang_chung]
    return min(tg) if tg else None


def mo_ta_chuoi(chuoi, may, lech_gio=timedelta(0)):
    """Các dòng chữ mô tả một chuỗi. lech_gio: đổi giờ UTC sang giờ máy (vd +7 giờ)."""
    dau, cuoi = chuoi[0]["dau"], chuoi[-1]["cuoi"]
    dong = [f">>> CHUỖI TẤN CÔNG trên máy {may}: {len(chuoi)} bước, {so_ky_thuat(chuoi)} kỹ thuật, "
            f"{dau + lech_gio:%H:%M:%S} -> {cuoi + lech_gio:%H:%M:%S} "
            f"({(cuoi - dau).total_seconds() / 60:.1f} phút)"]
    for i, b in enumerate(chuoi, 1):
        so, ten_gd, ten_kt = giai_doan(b["ma"])
        lap = f" (x{b['so_lan']})" if b["so_lan"] > 1 else ""
        dong.append(f"    {i}. {b['dau'] + lech_gio:%H:%M:%S}  [{so} {ten_gd}]".ljust(42)
                    + f"{b['ma']:<10} {ten_kt}{lap}")
    lui = [(i, a, b) for i, (a, b) in enumerate(zip(chuoi, chuoi[1:]), 1)
           if giai_doan(b["ma"])[0] < giai_doan(a["ma"])[0]]
    if lui:
        dong.append("    Giai đoạn lùi: " + "; ".join(
            f"bước {i} -> {i + 1} ({giai_doan(a['ma'])[1]} -> {giai_doan(b['ma'])[1]})" for i, a, b in lui)
            + ". Có thể là bước chuẩn bị, hai đợt nối nhau hoặc một KẾT LUẬN nhầm: cần xem lại.")
    else:
        dong.append("    Giai đoạn đi đúng chiều (không có bước lùi).")
    return dong


# ---------------------------------------------------------------- chạy riêng trên file .evtx
def phat_lai_file(a):
    import duckdb
    import doc_log
    import theo_doi                      # nhập ở đây để tránh vòng lặp import (theo_doi.py nhập file này)
    from doc_log import COT

    tam = duckdb.connect()
    doc_log.nap_log(tam, doc_log.liet_ke_file(a.duong_dan))
    hang = tam.execute("SELECT * FROM su_kien ORDER BY thoi_gian, nguon, record_id").fetchall()
    tam.close()

    # Các tham số theo_doi.py cần mà chế độ phát lại không dùng
    a.chu_ky, a.nap_truoc_phut, a.khong_powershell, a.cach_doc = 0, 0, False, "tu-dong"
    a.db, a.trang_thai, a.chi_tiet = ":memory:", 60, False
    td = theo_doi.TheoDoi(a)
    print(f"PHÁT LẠI {len(hang)} sự kiện qua vòng xét của theo_doi.py, mỗi đợt {a.moi_dot} sự kiện "
          f"| {'KHÔNG SLM' if a.khong_slm else 'CÓ SLM (' + os.environ.get('SLM_MODEL', 'phi4-mini:latest') + ')'} "
          f"| chi tiết ghi vào {td.thu_muc}", flush=True)

    bao_goc = td.bao

    def bao_gon(tt, may, logon, doan, kq, ma, diem, truoc, chi_tiet, truoc_khi_bat):
        # Gọi đúng hàm bao của theo_doi.py (ghi chi_tiet.txt, canh_bao.csv, nối chuỗi) nhưng không in dài
        with contextlib.redirect_stdout(io.StringIO()):
            bao_goc(tt, may, logon, doan, kq, ma, diem, truoc, chi_tiet, truoc_khi_bat)
        if kq == "KET_LUAN":
            b = td.chuoi.theo_may[may][-1][-1]
            print(td.an(f"  KẾT LUẬN {ma:<10} lúc {b['cuoi'] + theo_doi.LECH_GIO:%H:%M:%S} | máy {may} | "
                        f"phiên #{tt['id']} đoạn {tt['doan']} | điểm {diem:.3f}"), flush=True)

    td.bao = bao_gon
    for i in range(0, len(hang), a.moi_dot):
        theo_doi.chen_nhieu(td.con, "su_kien", len(COT), hang[i:i + a.moi_dot])
        td.xet()

    ds = td.chuoi.cac_chuoi()
    ket = ["", "=" * 78]
    if not ds:
        ket.append("Không có chuỗi nào (chưa máy nào có từ 2 kỹ thuật KẾT LUẬN).")
    for may, c in ds:
        ket += mo_ta_chuoi(c, may, theo_doi.LECH_GIO) + [""]
    if a.mong_doi:
        mong = [m.strip() for m in a.mong_doi.split(",") if m.strip()]
        thuc = [b["ma"] for _, c in ds for b in c] if len(ds) == 1 else None
        if thuc is None:
            ket.append(f"SO VỚI MONG ĐỢI: không so được vì có {len(ds)} chuỗi (cần đúng 1).")
        elif thuc == mong:
            ket.append(f"SO VỚI MONG ĐỢI: ĐÚNG thứ tự ({len(mong)} bước).")
        else:
            ket.append("SO VỚI MONG ĐỢI: KHÁC.\n    mong đợi: " + " > ".join(mong)
                       + "\n    thực tế:  " + " > ".join(thuc))
    chu = td.an("\n".join(ket))
    print(chu)
    with open(os.path.join(td.thu_muc, "chuoi.md"), "w", encoding="utf-8") as f:
        f.write(f"# Chuỗi tấn công: {', '.join(os.path.basename(p) for p in a.duong_dan)}\n\n```\n{chu.strip()}\n```\n")
    td.f_chi_tiet.close()
    td.f_csv.close()
    td.con.close()
    print(f"\nĐã ghi: {os.path.join(td.thu_muc, 'chuoi.md')}")


def main():
    goc = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ap = argparse.ArgumentParser(description="Phát lại file log qua vòng xét của theo_doi.py, nối KẾT LUẬN thành chuỗi")
    ap.add_argument("duong_dan", nargs="+", help="file .evtx hoặc thư mục")
    ap.add_argument("--khong-slm", "--ban-tam", dest="khong_slm", action="store_true",
                    help="bỏ bước hỏi mô hình ngôn ngữ, chỉ dùng luật + dấu vết")
    ap.add_argument("--mo-hinh", default=os.path.join(goc, "models", "mau_chuoi.json"))
    ap.add_argument("--nguong", type=float, default=0.5)
    ap.add_argument("--so-ung-vien", type=int, default=3)
    ap.add_argument("--in-dong-slm", action="store_true", help="ghi các dòng log gửi SLM vào chi tiết")
    ap.add_argument("--moi-dot", type=int, default=1, help="số sự kiện mỗi đợt phát lại (mặc định 1)")
    ap.add_argument("--khoang-phut", type=float, default=60,
                    help="hai KẾT LUẬN cùng máy cách nhau quá chừng này phút thì tách chuỗi mới (mặc định 60)")
    ap.add_argument("--mong-doi", help="thứ tự mã kỹ thuật mong đợi, cách nhau dấu phẩy, để tự so")
    ap.add_argument("--ra", default=os.path.join("output", "chuoi"))
    ap.add_argument("--an-ten", action="store_true", help="thay tên máy, tên người dùng khi in và ghi file")
    phat_lai_file(ap.parse_args())


if __name__ == "__main__":
    main()
