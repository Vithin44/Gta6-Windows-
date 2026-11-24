GTA VI Windows Research — Windows host probe

Built from: %GITHUB_SHA%
Workflow run: %GITHUB_SERVER_URL%/%GITHUB_REPOSITORY%/actions/runs/%GITHUB_RUN_ID%

1. Extract the entire artifact ZIP to a folder on your Windows PC.
2. Double-click `Run-HostProbe.bat` in the extracted folder. It runs the read-only inventory and prints a readable summary.

Manual PowerShell alternative (run from the folder containing this README.txt):

   powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\host_probe\Collect-HostInfo.ps1 -IncludeD3D12Info
   powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\host_probe\Summarize-HostInfo.ps1

The JSON report is saved to .\reports\host-probe.json.

Optional: if vulkaninfo is already installed and on PATH, add -IncludeVulkanInfo to the collection command. This probe does not install Vulkan tools.

Safety:
- Does not scan for GTA VI files, launch a game, install drivers/SDKs, change settings, or modify the page file.
- Reads CPU feature flags and queries Windows DXGI/D3D12 capabilities; it does not submit rendering or compute work.
- The JSON includes your machine name and hardware/software details. Review it before sharing.
- No Rockstar game files, keys, extracted assets or proprietary binaries are included.

Executable SHA-256: %HOST_CAPS_SHA256%
