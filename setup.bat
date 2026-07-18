@echo off
:: CP Dashboard Setup Wrapper
:: Launches the automated PowerShell setup script.

echo ===================================================
echo CP Contest Calendar Dashboard - Setup
echo ===================================================
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup.ps1"

if %errorlevel% neq 0 (
    echo.
    echo [-] Setup encountered an error. Please review the details above.
) else (
    echo.
    echo [+] Success! The skin is now active on your desktop.
)
echo.
pause
