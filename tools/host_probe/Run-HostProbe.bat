@echo off
setlocal
set "ROOT=%~dp0"
if exist "%ROOT%tools\host_probe\Collect-HostInfo.ps1" (
    pushd "%ROOT%"
) else (
    pushd "%ROOT%..\.."
)

echo GTA VI Windows Research - read-only host probe
echo This reads hardware and Windows capabilities only. It does not launch a game.
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File ".\tools\host_probe\Collect-HostInfo.ps1" -IncludeD3D12Info
if errorlevel 1 (
    echo.
    echo Host inventory failed. No settings were changed.
    pause
    popd
    exit /b 1
)

echo.
powershell -NoProfile -ExecutionPolicy Bypass -File ".\tools\host_probe\Summarize-HostInfo.ps1"
if errorlevel 1 (
    echo.
    echo Summary failed. The JSON report may still be available in reports\host-probe.json.
    pause
    popd
    exit /b 1
)

echo.
echo Report saved to reports\host-probe.json
echo Review the JSON before sharing it; it contains your PC name and hardware details.
pause
popd
