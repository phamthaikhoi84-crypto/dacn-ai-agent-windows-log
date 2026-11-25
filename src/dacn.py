"""Một cửa vào cho agent (K1 tuần 7), giống nmap: một lệnh, nhiều chế độ.

File này KHÔNG chứa logic phát hiện. Nó chỉ gọi lại các script đã có, chuyển nguyên tham số:
  quet      -> agent.py <file hoặc thư mục> ...
  phat-lai  -> agent.py <file> ... --phat-lai [N]
  theo-doi  -> theo_doi.py ...
  danh-gia  -> danh_gia.py ...
Ba công tắc môi trường được đổi thành tham số (phải đặt TRƯỚC khi chạy script con,
vì agent.py và slm.py đọc chúng lúc import):
  --startup     -> LUAT_STARTUP=1
  --model TÊN   -> SLM_MODEL=TÊN
  --prompt-moi  -> SLM_PROMPT_MOI=1

Cách chạy (PowerShell, đứng ở thư mục gốc repo):
  python src\\dacn.py --help
  python src\\dacn.py quet D:\\DoAnChuyenNganh\\log\\<file>.evtx --khong-slm
  python src\\dacn.py phat-lai D:\\DoAnChuyenNganh\\log\\<file>.evtx --khong-slm
  python src\\dacn.py theo-doi --khong-slm --startup --an-ten        (PowerShell Run as administrator)
  python src\\dacn.py danh-gia --thu-muc D:\\DoAnChuyenNganh\\log D:\\DoAnChuyenNganh\\log-binh-thuong
  python src\\dacn.py quet --help                                    (tham số riêng của agent.py)
"""
import argparse
import os
import signal
import subprocess
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent
GOC_REPO = SRC.parent

# chế độ -> (script được gọi, mô tả)
CHE_DO = {
    "quet":     ("agent.py",    "Phân tích file .evtx (hoặc cả thư mục) qua 5 bước của agent"),
    "phat-lai": ("agent.py",    "Phát lại file .evtx theo thời gian, xem agent báo sớm tới đâu"),
    "theo-doi": ("theo_doi.py", "Theo dõi trực tiếp log Sysmon của máy này (Run as administrator)"),
    "danh-gia": ("danh_gia.py", "Đo trên bộ thử data/bo-thu.csv, xuất bảng có / không SLM"),
}

# Tham số của agent.py có kèm giá trị: bỏ qua giá trị đó khi tìm đường dẫn file
AGENT_KEM_1_GIA_TRI = {"--mo-hinh", "--nguong", "--so-ung-vien", "--db", "--tre"}
AGENT_KEM_SO = {"--phien", "--phat-lai"}      # theo sau là 0, 1 hoặc nhiều số


def tao_parser():
    p = argparse.ArgumentParser(
        prog="python src\\dacn.py",
        usage="python src\\dacn.py CHẾ_ĐỘ [tham số]",
        description="AI agent phát hiện kỹ thuật MITRE ATT&CK trong log Sysmon (Windows).",
        epilog="Các chế độ:\n"
        + "\n".join(f"  {ten:<9} {mo_ta}" for ten, (_, mo_ta) in CHE_DO.items())
        + "\n\nCác tham số khác (vd --khong-slm, --an-ten, --thu-muc) được chuyển nguyên cho script của chế độ."
        + "\nXem tham số riêng của một chế độ: python src\\dacn.py <chế độ> --help",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False,       # tự xử lý --help để chuyển được cho script con
        allow_abbrev=False,   # không "ăn" nhầm tham số viết tắt của script con
    )
    p.add_argument("che_do", nargs="?", choices=list(CHE_DO), metavar="CHẾ_ĐỘ", help="một trong 4 chế độ bên dưới")
    p.add_argument("-h", "--help", action="store_true", help="in hướng dẫn")
    p.add_argument("--startup", action="store_true", help="bật luật thư mục Startup, T1547.001 (LUAT_STARTUP=1)")
    p.add_argument("--model", metavar="TÊN", help="mô hình Ollama (SLM_MODEL), mặc định phi4-mini:latest")
    p.add_argument("--prompt-moi", action="store_true", help="dùng cách hỏi SLM mới (SLM_PROMPT_MOI=1)")
    p.add_argument("--moi-dot", type=int, default=1, metavar="N",
                   help="(phat-lai) số sự kiện mỗi đợt, mặc định 1")
    return p


def bao(thong_diep):
    """Thông báo của dacn in ra stderr, để không lẫn vào file khi dùng > ."""
    print(f"[dacn] {thong_diep}", file=sys.stderr, flush=True)


def duong_dan_trong(tham_so):
    """Lấy các đường dẫn file / thư mục trong tham số của agent.py (bỏ giá trị của các tham số khác)."""
    ra, i = [], 0
    while i < len(tham_so):
        x = tham_so[i]
        if x in AGENT_KEM_1_GIA_TRI:
            i += 2
            continue
        if x in AGENT_KEM_SO:
            i += 1
            while i < len(tham_so) and tham_so[i].isdigit():
                i += 1
            continue
        if not x.startswith("-"):
            ra.append(x)
        i += 1
    return ra


def kiem_tra_file(che_do, tham_so):
    """quet / phat-lai cần ít nhất một đường dẫn có thật. Báo lỗi dễ hiểu thay vì traceback."""
    ds = duong_dan_trong(tham_so)
    if not ds:
        bao(f"chế độ {che_do} cần đường dẫn file .evtx, vd: "
            f"python src\\dacn.py {che_do} D:\\DoAnChuyenNganh\\log\\<file>.evtx")
        return False
    thieu = [d for d in ds if not Path(d).exists()]
    if thieu and len(ds) > 1:
        # PowerShell tách đường dẫn có khoảng trắng (vd "Credential Access") thành nhiều tham số
        for i in range(len(ds)):
            for j in range(len(ds), i + 1, -1):
                ghep = " ".join(ds[i:j])
                if Path(ghep).exists():
                    bao(f'đường dẫn có khoảng trắng phải đặt trong ngoặc kép, vd: "{ghep}"')
                    return False
    for d in thieu:
        bao(f"không thấy: {d}")
        if Path(d + ".evtx").exists():
            bao(f"  có file {Path(d).name}.evtx: Windows đang ẩn đuôi, đổi tên file cho đúng.")
    return not thieu


def main():
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    p = tao_parser()
    ts, tham_so = p.parse_known_args()

    if ts.che_do is None:
        p.print_help()
        return 0 if (ts.help or not tham_so) else 2

    script, _ = CHE_DO[ts.che_do]
    if ts.help:
        tham_so.append("--help")
    else:
        if Path.cwd().resolve() != GOC_REPO:
            bao(f"nên đứng ở thư mục gốc repo ({GOC_REPO}): kết quả output\\ sẽ ghi vào thư mục hiện tại")
        if ts.che_do in ("quet", "phat-lai") and not kiem_tra_file(ts.che_do, tham_so):
            return 2
        if ts.che_do == "phat-lai" and "--phat-lai" not in tham_so:
            tham_so += ["--phat-lai", str(ts.moi_dot)]

    env = os.environ.copy()
    cong_tac = []
    if ts.startup:
        env["LUAT_STARTUP"] = "1"
        cong_tac.append("LUAT_STARTUP=1")
    if ts.model:
        env["SLM_MODEL"] = ts.model
        cong_tac.append(f"SLM_MODEL={ts.model}")
    if ts.prompt_moi:
        env["SLM_PROMPT_MOI"] = "1"
        cong_tac.append("SLM_PROMPT_MOI=1")

    if not ts.help:
        bao("chạy: python " + " ".join([f"src\\{script}"] + tham_so)
            + (f"   ({', '.join(cong_tac)})" if cong_tac else ""))

    # Ctrl+C tới cả dacn.py lẫn script con. dacn.py bỏ qua Ctrl+C và chờ: theo_doi.py tự bắt Ctrl+C
    # rồi in tổng kết, ghi tong_ket.md; agent.py / danh_gia.py thì tự dừng. Không giết script con giữa chừng.
    signal.signal(signal.SIGINT, lambda so, khung: None)
    return subprocess.call([sys.executable, str(SRC / script)] + tham_so, env=env)


if __name__ == "__main__":
    sys.exit(main())
