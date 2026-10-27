"""Gom sự kiện thành phiên hành vi: cùng máy + LogonId + cây tiến trình,
các sự kiện cách nhau không quá khoang_cach giây."""
from doc_log import COT
from ky_hieu import ten_ngan


def tim_goc(guid, cha_cua):
    """Leo ngược cây cha-con (chỉ trong phạm vi log có) tới tổ tiên xa nhất."""
    da_qua = set()
    while guid in cha_cua and guid not in da_qua:
        da_qua.add(guid)
        guid = cha_cua[guid]
    return guid


def gom_phien(con, khoang_cach=300):
    """Đọc bảng su_kien, trả về (phien_list, cha_cua, ten_tien_trinh).
    phien_list: [((may, logon_id), [sự kiện, ...]), ...]"""

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
    su_kien = [dict(zip(COT, r)) for r in con.execute(
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
            if (sau["thoi_gian"] - truoc["thoi_gian"]).total_seconds() > khoang_cach:
                phien_list.append((khoa, phien))
                phien = []
            phien.append(sau)
        phien_list.append((khoa, phien))

    return phien_list, cha_cua, ten_tien_trinh