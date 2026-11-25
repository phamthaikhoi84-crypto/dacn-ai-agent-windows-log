# -*- coding: utf-8 -*-
import csv, re
from collections import Counter

CSV = "output/danh_gia_dev_v2/ket_qua_phien.csv"
TXT = "output/danh_gia_dev_v2/khong-slm/benign_sysmon_dung.evtx.txt"

# 1. Lay danh sach phien bi bao nham (KET_LUAN du nhan that la binh thuong)
bao_nham = {}
with open(CSV, encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        if row["tep"] == "benign_sysmon_dung.evtx" and row["ket_qua"] == "KET_LUAN":
            bao_nham[row["phien"]] = row["ma"]

print(f"Tong so phien bao nham (KET_LUAN) tren benign_sysmon_dung.evtx: {len(bao_nham)}")

# 2. Doc file chi tiet, cat theo tung PHIEN, lay dong "doan khop nhat voi <ma>"
with open(TXT, encoding="utf-8") as f:
    noidung = f.read()

khoi = re.split(r"\nPHIÊN #", noidung)
dem_ma = Counter()
dem_doan = Counter()

for k in khoi[1:]:
    m = re.match(r"(\d+)", k)
    if not m:
        continue
    so_phien = m.group(1)
    if so_phien not in bao_nham:
        continue
    ma = bao_nham[so_phien]
    dem_ma[ma] += 1
    tim = re.search(rf"đoạn khớp nhất với {re.escape(ma)}: (.+)", k)
    if tim:
        dem_doan[tim.group(1).strip()] += 1

print("\n-- So bao nham theo ma ky thuat --")
for ma, c in dem_ma.most_common():
    print(f"{ma}: {c}")

print("\n-- Top 5 doan ky hieu khop hay gap nhat --")
for doan, c in dem_doan.most_common(5):
    print(f"{c} lan: {doan}")