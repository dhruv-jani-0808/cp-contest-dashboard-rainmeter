# CP Dashboard Automated Setup Script
# Auto-detects Rainmeter paths, deploys files, configures variables, fetches contests, loads skin, and sets up Scheduled Tasks.

$ErrorActionPreference = "Stop"

# 1. Locate Rainmeter.ini to find the active Skins folder
$iniPath = "$env:APPDATA\Rainmeter\Rainmeter.ini"
if (!(Test-Path $iniPath)) {
    Write-Host "[-] Rainmeter.ini not found. Please verify Rainmeter is installed." -ForegroundColor Red
    exit 1
}

$skinPathLine = Get-Content $iniPath | Select-String -Pattern "SkinPath="
if (!$skinPathLine) {
    Write-Host "[-] Could not find SkinPath setting inside Rainmeter.ini." -ForegroundColor Red
    exit 1
}

# Extract and clean skin path
$skinPath = $skinPathLine.Line.Split("=", 2)[1].Trim()
$destination = Join-Path $skinPath "CPDashboard"

Write-Host "[+] Found active Rainmeter skins folder at: $skinPath" -ForegroundColor Green
Write-Host "[+] Deploying skin files to: $destination..." -ForegroundColor Cyan

# 2. Create the destination directory and copy files
New-Item -ItemType Directory -Force -Path $destination | Out-Null

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Copy-Item -Path (Join-Path $scriptDir "rainmeter\*") -Destination $destination -Recurse -Force

# 3. Resolve paths for variables.inc config
$fetcherPath = Join-Path $scriptDir "fetch\fetch_contests.py"
$pythonPath = "python"
try {
    $resolvedPython = (Get-Command python -ErrorAction SilentlyContinue).Source
    if ($resolvedPython) {
        $pythonPath = $resolvedPython
    }
} catch {}

Write-Host "[+] Auto-configuring paths in variables.inc..." -ForegroundColor Cyan
Write-Host "    - Python executable: $pythonPath"
Write-Host "    - Fetcher script: $fetcherPath"

# Read, modify, and overwrite variables.inc
$variablesPath = Join-Path $destination "variables.inc"
$variablesContent = Get-Content $variablesPath
$newContent = @()
foreach ($line in $variablesContent) {
    if ($line -like "PythonPath=*") {
        $newContent += "PythonPath=$pythonPath"
    } elseif ($line -like "FetcherPath=*") {
        $newContent += "FetcherPath=$fetcherPath"
    } else {
        $newContent += $line
    }
}
$newContent | Out-File -FilePath $variablesPath -Encoding utf8 -Force

# 4. Fetch initial contest list once
Write-Host "[+] Executing contest fetcher to generate initial contest database..." -ForegroundColor Cyan
python "$fetcherPath"

# Copy the updated contest.json file to the skins folder
Copy-Item -Path (Join-Path $scriptDir "rainmeter\contest.json") -Destination (Join-Path $destination "contest.json") -Force

# 5. Tell Rainmeter to refresh and load the skin
$rainmeterPath = "C:\Program Files\Rainmeter\Rainmeter.exe"
if (Test-Path $rainmeterPath) {
    Write-Host "[+] Refreshing Rainmeter and activating CPDashboard skin..." -ForegroundColor Green
    # Refresh all configs
    Start-Process $rainmeterPath -ArgumentList "!RefreshApp"
    Start-Sleep -Seconds 1
    # Activate our specific skin config
    Start-Process $rainmeterPath -ArgumentList "!ActivateConfig CPDashboard CPDashboard.ini"
} else {
    Write-Host "[!] Rainmeter executable not found at standard path. Please refresh/load CPDashboard manually in Rainmeter Manager." -ForegroundColor Yellow
}

# 6. Register Windows Scheduled Tasks for 8:00 PM WhatsApp and 10:00 PM Phone Call reminders
Write-Host "[+] Registering Windows Scheduled Tasks for 8:00 PM WhatsApp & 10:00 PM Call reminders..." -ForegroundColor Cyan
try {
    $reminderScript = Join-Path $scriptDir "fetch\check_reminders.py"
    
    $action8PM = New-ScheduledTaskAction -Execute $pythonPath -Argument "`"$reminderScript`" --type whatsapp"
    $trigger8PM = New-ScheduledTaskTrigger -Daily -At 8:00PM
    Register-ScheduledTask -TaskName "CPDashboard_8PM_WhatsApp" -Action $action8PM -Trigger $trigger8PM -User $env:USERNAME -Force | Out-Null
    Write-Host "    - Registered task: CPDashboard_8PM_WhatsApp (Daily at 8:00 PM)" -ForegroundColor Green
    
    $action10PM = New-ScheduledTaskAction -Execute $pythonPath -Argument "`"$reminderScript`" --type call"
    $trigger10PM = New-ScheduledTaskTrigger -Daily -At 10:00PM
    Register-ScheduledTask -TaskName "CPDashboard_10PM_Call" -Action $action10PM -Trigger $trigger10PM -User $env:USERNAME -Force | Out-Null
    Write-Host "    - Registered task: CPDashboard_10PM_Call (Daily at 10:00 PM)" -ForegroundColor Green
} catch {
    Write-Host "[!] Could not register Windows Scheduled Tasks automatically: $_" -ForegroundColor Yellow
}

Write-Host "`n[+] CPDashboard Setup Completed Successfully!" -ForegroundColor Green
