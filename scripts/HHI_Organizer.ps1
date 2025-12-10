# ==============================
# HHI FILE ORGANIZER (PDF/CSV METADATA + GITHUB SYNC)
# ==============================

# ----- CONFIG -----
$SearchRoot = "C:\Users\amy"
$HHIRoot    = "C:\Users\amy\Documents\HHI"
$Dirs       = "00_Raw","01_Codex","02_OPS","03_Datasets","04_Legal","05_Likeness_Protection","06_Media","07_Archive","08_Logs"

# Create directory structure
foreach ($d in $Dirs) {
    $p = Join-Path $HHIRoot $d
    if (!(Test-Path $p)) {
        New-Item -ItemType Directory -Path $p | Out-Null
    }
}

# ----- LOGGING -----
$LogRoot = Join-Path $HHIRoot "08_Logs"
if (!(Test-Path $LogRoot)) {
    New-Item -ItemType Directory -Path $LogRoot | Out-Null
}

$LogFile = Join-Path $LogRoot "HHI_File_Organizer_Log_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"

function Write-Log($msg) {
    Add-Content -Path $LogFile -Value ("$(Get-Date -Format 'u') | $msg")
}

Write-Log "=== HHI FILE ORGANIZER STARTED ==="

# ----- FIND FILES -----
$AllFiles = Get-ChildItem -Path $SearchRoot -Recurse -File -ErrorAction SilentlyContinue
$Seen     = @{}   # hashes for duplicate detection

# ==========================
# MAIN ORGANIZE / METADATA LOOP
# ==========================
foreach ($file in $AllFiles) {

    # Skip the log file itself
    if ($file.FullName -eq $LogFile) { continue }

    # --- DAMAGED (ZERO-BYTE) FILES ---
    if ($file.Length -eq 0) {
        Write-Log "DELETED (DAMAGED): $($file.FullName)"
        Remove-Item $file.FullName -Force
        continue
    }

    # --- DUPLICATES VIA SHA256 HASH ---
    try {
        $h = (Get-FileHash $file.FullName -Algorithm SHA256).Hash
        if ($Seen.ContainsKey($h)) {
            Write-Log "DELETED (DUPLICATE): $($file.FullName)"
            Remove-Item $file.FullName -Force
            continue
        } else {
            $Seen[$h] = $true
        }
    } catch {
        Write-Log "SKIPPED (HASH ERROR): $($file.FullName)"
        continue
    }

    # ----- ROUTING RULES -----
    $n = $file.Name.ToLower()

    if     ($n -match "codex|node|glyph")               { $dest = "01_Codex" }
    elseif ($n -match "ops_|operation_|ledger")         { $dest = "02_OPS" }
    elseif ($n -match "dataset|corpus|hhi_srs|jsonl")   { $dest = "03_Datasets" }
    elseif ($n -match "license|legal|agreement|terms")  { $dest = "04_Legal" }
    elseif ($n -match "face|voice|likeness|biometric")  { $dest = "05_Likeness_Protection" }
    elseif ($file.Extension -match "\.(jpg|jpeg|png|mp4|wav|mp3|mov)$") { $dest = "06_Media" }
    elseif ($n -match "raw|notes|unprocessed")          { $dest = "00_Raw" }
    else                                                { $dest = "07_Archive" }

    $destinationPath = Join-Path $HHIRoot $dest
    $newFilePath     = Join-Path $destinationPath $file.Name

    # ----- MOVE FILE -----
    try {
        Move-Item -Path $file.FullName -Destination $newFilePath -Force
        Write-Log "MOVED: $($file.FullName) --> $newFilePath"
    } catch {
        Write-Log "FAILED TO MOVE: $($file.FullName) | ERROR: $_"
        continue
    }

    # ==============================
    # METADATA EXTRACTION (PDF / CSV)
    # ==============================
    try {
        $metaPath = "$newFilePath.metadata.json"

        $item = Get-Item $newFilePath

        $meta = [ordered]@{
            filename   = $file.Name
            full_path  = $newFilePath
            size_bytes = $item.Length
            created    = $item.CreationTimeUtc
            modified   = $item.LastWriteTimeUtc
            type       = $file.Extension.ToLower()
        }

        # ----- PDF METADATA -----
        if ($file.Extension -match "\.pdf") {
            try {
                $pdfText = Get-Content -Path $newFilePath -Raw -ErrorAction SilentlyContinue

                # best-effort page count based on PDF markers
                $pageCount = ([regex]::Matches($pdfText, "/Type\s*/Page")).Count

                # simple keyword frequency
                $clean = ($pdfText -replace '[^a-zA-Z0-9 ]',' ').ToLower()
                $words = $clean.Split(" ",[System.StringSplitOptions]::RemoveEmptyEntries)
                $freq  = $words | Group-Object | Sort-Object Count -Descending
                $top   = $freq | Select-Object Name,Count -First 20

                $meta.pdf = [ordered]@{
                    page_count   = $pageCount
                    top_keywords = $top
                }
            } catch {
                $meta.pdf = "error_reading_pdf"
            }
        }

        # ----- CSV METADATA -----
        if ($file.Extension -match "\.csv") {
            try {
                $csv = Import-Csv -Path $newFilePath

                if ($csv.Count -gt 0) {
                    $columns = $csv[0].PSObject.Properties.Name
                    $sample  = $csv | Select-Object -First 5
                } else {
                    $columns = @()
                    $sample  = @()
                }

                $meta.csv = [ordered]@{
                    row_count    = $csv.Count
                    column_count = $columns.Count
                    columns      = $columns
                    sample_rows  = $sample
                }
            } catch {
                $meta.csv = "error_parsing_csv"
            }
        }

        # Write metadata JSON
        $meta | ConvertTo-Json -Depth 10 | Out-File -Encoding UTF8 $metaPath
        Write-Log "METADATA CREATED: $metaPath"
    }
    catch {
        Write-Log "FAILED METADATA: $($file.FullName) | ERROR: $_"
    }
}

# ==============================
# GITHUB AUTO-SYNC MODULE
# ==============================
try {
    $repoPath = $HHIRoot
    Set-Location $repoPath

    # Init repo if missing
    if (!(Test-Path ".git")) {
        git init | Out-Null
        # Add origin only if not present
        $hasOrigin = git remote 2>$null | Where-Object { $_ -eq "origin" }
        if (-not $hasOrigin) {
            git remote add origin "https://github.com/hhidatasettechs-oss/HHI.git"
        }
    }

    # Check if there are changes
    $status = git status --porcelain
    if ($status) {
        git add .
        git commit -m "Automated sync: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Out-Null

        # Pull with rebase to avoid simple diverging-history issues
        git pull origin main --rebase 2>$null

        git push origin main
        Write-Log "GITHUB SYNC COMPLETE"
    } else {
        Write-Log "GITHUB SYNC SKIPPED (NO CHANGES)"
    }
}
catch {
    Write-Log "GITHUB SYNC FAILED | ERROR: $_"
}

# ----- END -----
Write-Log "=== HHI FILE ORGANIZER COMPLETED ==="
Write-Log "Log saved to: $LogFile"
Write-Output "Operation Completed. Log saved to $LogFile"
