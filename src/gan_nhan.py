"""Gắn nhãn kỹ thuật cho CHUỖI HÀNH VI: chuỗi = cây con của tiến trình có lệnh khớp dấu hiệu của kỹ thuật.
Không gắn nhãn theo cả file hay cả phiên, vì log Splunk lẫn hạ tầng lab (Ansible, Splunk forwarder, Caldera)
và cả buổi chạy bài thử nằm chung một phiên."""
import re
from collections import defaultdict
from doc_log import COT

I = re.I
DAU_HIEU = {
    "T1003.001": re.compile(r"procdump|comsvcs|mimikatz|sekurlsa|createdump|ntdsutil|lsass\.dmp|lsass_dump|-ma\s+lsass|minidump", I),
    "T1021.001": re.compile(r"mstsc|3389|fdenytsconnections|terminal server|termservice|rdp|remote desktop|tscon|portproxy", I),
    "T1053.005": re.compile(r"schtasks|scheduledtask|taskschd|system32\\tasks", I),
    "T1059.001": re.compile(r"(powershell|pwsh).*(-enc\w*\s|-e\s|-nop\w*|-w(indowstyle)?\s+hidden|-ep\s+bypass|-executionpolicy\s+bypass"
                            r"|iex\b|invoke-expression|downloadstring|frombase64string|net\.webclient)", I),
    "T1070.001": re.compile(r"wevtutil|clear-eventlog|remove-eventlog|clear-winevent", I),
    "T1105": re.compile(r"\bcurl\b|\bwget\b|certutil|bitsadmin|invoke-webrequest|\biwr\b|invoke-restmethod|\birm\b|downloadfile|downloadstring|start-bitstransfer|\btftp\b|\bftp\b|webclient|certreq", I),
    "T1136.001": re.compile(r"net1?(\.exe)?\"?\s+user.*/add|new-localuser|net1?(\.exe)?\"?\s+localgroup.*/add|useradd|adduser", I),
    "T1547.001": re.compile(r"currentversion\\run|\\runonce|\\startup\\|reg(\.exe)?\s+add.*\\run", I),
}
# Hạ tầng lab, không phải bài thử: bỏ qua khi tìm dấu hiệu
LOAI_TRU = re.compile(r"-NonInteractive -ExecutionPolicy Unrestricted|SplunkUniversalForwarder|amazon-ssm|Reboot initiated|Test-Path", I)
CHA_HA_TANG = {"splunkd.exe", "winrshost.exe", "amazon-ssm-agent.exe", "services.exe"}
DO_DAI_TOI_DA = 300     # chuỗi (sau khi lọc) dài hơn coi là gốc nhầm, ví dụ tiến trình chạy bài thử; bỏ


def _ten(p):
    return (p or "").replace("/", "\\").split("\\")[-1].lower()


def la_dau_hieu(k, e):
    """Sự kiện e có phải dấu hiệu của kỹ thuật k không. Chỉ xét theo loại sự kiện:
    ID 1 -> dòng lệnh; ID 3/11/12/13/14 -> đối tượng (địa chỉ mạng, file, registry);
    ID 10 -> chỉ truy cập lsass với quyền 0x1fffff (T1003.001). Không xét tên tiến trình đích của ID 10."""
    eid = e.get("event_id")
    if eid == 1:
        van_ban = e.get("command_line") or ""
    elif eid in (3, 11, 12, 13, 14):
        van_ban = e.get("doi_tuong") or ""
    elif eid == 10:
        return k == "T1003.001" and e.get("quyen") == "0x1fffff" \
            and (e.get("doi_tuong") or "").lower().endswith("lsass.exe")
    else:
        return False
    if LOAI_TRU.search(van_ban) or _ten(e.get("parent_image")) in CHA_HA_TANG:
        return False
    if re.search(r"atomics[\\/]+" + re.escape(k), van_ban, I):
        return True
    return bool(DAU_HIEU[k].search(van_ban))


def giu_su_kien(e):
    """Chỉ giữ loại sự kiện mà cấu hình Sysmon chung của nhóm (sysmonconfig-dacn.xml) cũng ghi.
    Log Splunk ghi thêm nhiều loại khác (ID 10 vào mọi tiến trình, ID 7 mọi DLL, ID 17/18/22/23...)
    mà log thật của nhóm không có, nên bỏ để mô hình không học những thứ đó."""
    eid = e["event_id"]
    if eid == 10:
        return (e["doi_tuong"] or "").lower().endswith("lsass.exe")
    return eid in (1, 3, 11, 12, 13, 14)


def lay_chuoi(con, k):
    """Trả về danh sách chuỗi cho kỹ thuật k: mỗi chuỗi là list các sự kiện (dict, theo thời gian).
    Bỏ qua các chuỗi dài hơn DO_DAI_TOI_DA; số chuỗi bị bỏ nằm ở thuộc tính lay_chuoi.bo_qua."""
    rows = [dict(zip(COT, r)) for r in con.execute(
        "SELECT * FROM su_kien ORDER BY may, thoi_gian, record_id").fetchall()]
    cha, con_cua = {}, defaultdict(list)
    for e in rows:
        if e["event_id"] == 1 and e["guid"] and e["parent_guid"]:
            cha[e["guid"]] = e["parent_guid"]
            con_cua[e["parent_guid"]].append(e["guid"])
    moc = {e["guid"] for e in rows if e["guid"] and la_dau_hieu(k, e)}

    def co_to_tien_la_moc(g):
        da, g = set(), cha.get(g)
        while g and g not in da:
            if g in moc:
                return True
            da.add(g)
            g = cha.get(g)
        return False

    goc = [g for g in moc if not co_to_tien_la_moc(g)]
    theo_guid = defaultdict(list)
    for e in rows:
        theo_guid[e["guid"]].append(e)
    chuoi, bo = [], 0
    for g in goc:
        cay, hang = set(), [g]
        while hang:
            x = hang.pop()
            if x in cay:
                continue
            cay.add(x)
            hang.extend(con_cua.get(x, []))
        ds = sorted((e for x in cay for e in theo_guid.get(x, [])), key=lambda e: (e["thoi_gian"], e["record_id"]))
        ds = [e for e in ds if giu_su_kien(e)]
        if 0 < len(ds) <= DO_DAI_TOI_DA:
            chuoi.append(ds)
        else:
            bo += 1
    chuoi.sort(key=lambda ds: ds[0]["thoi_gian"])
    lay_chuoi.bo_qua = bo
    return chuoi
