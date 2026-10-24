<#
  dem_theo_noi_dung.ps1
  Đếm số file theo NỘI DUNG cho các kỹ thuật ATT&CK trong Splunk Attack Data (bản đã tải về máy).

  Quy tắc:
  - Duyệt mọi file dữ liệu trong datasets/attack_techniques (bỏ .yml, .md, .zip).
  - Đọc tối đa 8 MB đầu mỗi file. File được tính nếu có chuỗi Microsoft-Windows-Sysmon
    (sự kiện Sysmon của Windows) hoặc sự kiện PowerShell 4104.
  - Gộp theo mã ATT&CK v20.0 (bảng tra data/attack-v20-tra-ma.csv), chỉ giữ kỹ thuật có Windows.

  Đầu ra (trong thư mục -ThuMucRa, nằm ngoài repo):
  - dem-noi-dung.csv: kết quả từng file (không chứa log).
  - do-phu-theo-noi-dung.csv: số file theo tên và theo nội dung cho từng kỹ thuật Windows.

  Hạn chế: xem data/do-phu.md mục 9.
#>
param(
  [string]$ThuMucSplunk = "C:\DACN-logs\splunk\datasets\attack_techniques",
  [string]$ThuMucRa     = "C:\DACN-logs",
  [string]$DanhSach     = (Join-Path $PSScriptRoot "..\data\ky-thuat-splunk-sysmon-powershell.csv"),
  [string]$BangTra      = (Join-Path $PSScriptRoot "..\data\attack-v20-tra-ma.csv"),
  [int]$ToiDaMB         = 8
)

foreach ($x in $ThuMucSplunk, $DanhSach, $BangTra) { if (-not (Test-Path $x)) { throw "Khong thay: $x" } }
if (-not (Test-Path $ThuMucRa)) { New-Item -ItemType Directory -Force $ThuMucRa | Out-Null }

# ---- Phan 1: quet noi dung tung file ----
$root = $ThuMucSplunk
$out  = Join-Path $ThuMucRa "dem-noi-dung.csv"
$chunk = 1MB; $cap = $ToiDaMB * 1MB
$mau4104 = @('<EventID>4104</EventID>', 'EventCode=4104', '"EventID":4104', '"EventID": 4104')
$files = @(Get-ChildItem $root -Recurse -File | Where-Object { $_.Extension -notin '.yml','.md','.zip' })
"Tong so file can doc: " + $files.Count
$rows = New-Object System.Collections.Generic.List[object]
$i = 0
foreach ($f in $files) {
  $i++; if ($i % 250 -eq 0) { "$i / $($files.Count)" }
  $coSys = $false; $coPS = $false; $da = 0; $duoi = ''; $tt = 'ok'
  try {
    $fs = [System.IO.File]::OpenRead($f.FullName)
    try {
      $buf = New-Object byte[] $chunk
      $enc = [System.Text.Encoding]::UTF8
      while (-not ($coSys -and $coPS) -and $da -lt $cap) {
        $n = $fs.Read($buf, 0, $chunk)
        if ($n -le 0) { break }
        if ($da -eq 0 -and $n -ge 2 -and $buf[0] -eq 0xFF -and $buf[1] -eq 0xFE) { $enc = [System.Text.Encoding]::Unicode }
        $da += $n
        $s = $duoi + $enc.GetString($buf, 0, $n)
        if (-not $coSys -and $s.Contains('Microsoft-Windows-Sysmon')) { $coSys = $true }
        if (-not $coPS) {
          foreach ($m in $mau4104) { if ($s.Contains($m)) { $coPS = $true; break } }
          if (-not $coPS -and $f.Extension -eq '.json' -and [regex]::IsMatch($s, '(?i)"(EventID|event_id)"\s*:\s*"?4104\b')) { $coPS = $true }
        }
        $duoi = if ($s.Length -gt 100) { $s.Substring($s.Length - 100) } else { $s }
      }
    } finally { $fs.Close() }
  } catch { $tt = 'loi: ' + $_.Exception.Message }
  $p = $f.FullName.Substring($root.Length + 1) -split '\\'
  $rows.Add([pscustomobject]@{ Ma = $p[0].ToUpper(); ThuMuc = $p[1]; Ten = $f.Name; MB = [math]::Round($f.Length/1MB,2); Sysmon = $coSys; PS4104 = $coPS; DaDocMB = [math]::Round($da/1MB,2); TrangThai = $tt })
}
$rows | Export-Csv $out -NoTypeInformation -Encoding UTF8
"Quet xong: {0} file; co Sysmon: {1}; co PS 4104: {2}; loi: {3}" -f $rows.Count, @($rows | Where-Object Sysmon).Count, @($rows | Where-Object PS4104).Count, @($rows | Where-Object { $_.TrangThai -ne 'ok' }).Count

# ---- Phan 2: gop ve ma ATT&CK v20.0, chi giu ky thuat Windows ----
$scan = Import-Csv $out -Encoding UTF8
$tra  = Import-Csv $BangTra -Encoding UTF8
$h = @{}; $tra | ForEach-Object { $h[$_.ma] = $_ }
$ds = Import-Csv $DanhSach -Encoding UTF8 | ForEach-Object {
  [pscustomobject]@{ Ma = $_.ma_ky_thuat.Trim().ToUpper(); TheoTen = [int]$_.so_file_sysmon + [int]$_.so_file_powershell }
}
$dat = @($scan | Where-Object { $_.Sysmon -eq 'True' -or $_.PS4104 -eq 'True' })
$demMa = @{}; $dat | Group-Object Ma | ForEach-Object { $demMa[$_.Name] = $_.Count }
$tk = $ds | ForEach-Object {
  $r = $h[$_.Ma]
  [pscustomobject]@{
    Ma = $_.Ma
    MaV20 = if ($r -and $r.ma_v20) { $r.ma_v20 } else { $_.Ma }
    Windows = if ($r) { $r.co_windows } else { 'khong ro' }
    TheoTen = $_.TheoTen
    TheoNoiDung = [int]$demMa[$_.Ma]
  }
}
$g = $tk | Group-Object MaV20 | ForEach-Object {
  [pscustomobject]@{ Ma = $_.Name; Windows = ($_.Group | Select-Object -First 1).Windows
    TheoTen = ($_.Group | Measure-Object TheoTen -Sum).Sum; TheoNoiDung = ($_.Group | Measure-Object TheoNoiDung -Sum).Sum }
}
$w = @($g | Where-Object Windows -eq 'co')
function Tang2($x, $prop) { "{0} ky thuat | >=3: {1} | 2: {2} | 1: {3} | 0: {4}" -f @($x).Count, @($x | Where-Object { $_.$prop -ge 3 }).Count, @($x | Where-Object { $_.$prop -eq 2 }).Count, @($x | Where-Object { $_.$prop -eq 1 }).Count, @($x | Where-Object { $_.$prop -eq 0 }).Count }
"Windows, theo ten (cach cu):   " + (Tang2 $w 'TheoTen')
"Windows, theo noi dung (moi):  " + (Tang2 $w 'TheoNoiDung')
"Ky thuat Windows co file theo ten nhung 0 file theo noi dung: " + (($w | Where-Object { $_.TheoNoiDung -eq 0 } | Sort-Object Ma | ForEach-Object { $_.Ma }) -join ', ')
$gset = @{}; $g | ForEach-Object { $gset[$_.Ma] = $true }
$ng = $dat | Group-Object Ma | ForEach-Object {
  $r = $h[$_.Name]
  [pscustomobject]@{ Ma = $_.Name; MaV20 = if ($r -and $r.ma_v20) { $r.ma_v20 } else { $_.Name }; Windows = if ($r) { $r.co_windows } else { 'khong ro' }; SoFile = $_.Count }
} | Where-Object { $_.Windows -eq 'co' -and -not $gset.ContainsKey($_.MaV20) } | Group-Object MaV20
"Ky thuat Windows NGOAI danh sach nhung co file Sysmon hoac 4104 theo noi dung: {0}" -f @($ng).Count
$csvKt = Join-Path $ThuMucRa "do-phu-theo-noi-dung.csv"
$w | Sort-Object Ma | Export-Csv $csvKt -NoTypeInformation -Encoding UTF8
"Da ghi: $out va $csvKt"