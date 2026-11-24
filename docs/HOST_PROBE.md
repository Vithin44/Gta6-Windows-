# Windows host capability probe

The host probe measures the actual PC before an upstream build or runtime is selected. It does not inspect game folders, launch game processes, change system settings or install software.

## 1. Download the standalone bundle

The GitHub Actions workflow builds the native probe with a statically linked C/C++ runtime and packages it together with the two PowerShell scripts and a quick-start file.

1. Open the repository's [Actions page](https://github.com/Vithin44/Gta6-Windows-/actions/workflows/validate-research.yml).
2. Open the latest successful **Validate research artifacts** run.
3. In **Artifacts**, download `windows-host-probe-bundle`.
4. Extract the ZIP to a folder on your Windows PC.
5. Open PowerShell in the extracted folder (the folder containing `README.txt`).

The bundle is generated from this repository's own source. Its README records the source commit, workflow run and SHA-256 of `host_caps.exe`. Check that the run belongs to the expected repository before using it. No Visual Studio installation is required to run the packaged probe.

If you already cloned this repository, you can instead download the smaller `windows-host-probe` artifact and extract `host_caps.exe` into `tools\host_probe\`, beside the PowerShell scripts.

## 2. Run the inventory

From the extracted bundle root, run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\host_probe\Collect-HostInfo.ps1 -IncludeD3D12Info
```

The JSON report is saved to `reports\host-probe.json`. To print a human-readable summary and flag known upstream requirements, run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\host_probe\Summarize-HostInfo.ps1
```

The summary is a screening aid, not a compatibility verdict. You can choose another report path:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\host_probe\Collect-HostInfo.ps1 -IncludeD3D12Info -OutputPath "$env:USERPROFILE\Desktop\host-probe.json"
```

The native program reads CPUID and asks DXGI/D3D12 for hardware-adapter capabilities. It records the exact PCI vendor/device IDs and a deliberately small AMD target hint table. For example, AMD's RX 6600 (Navi 23) is identified as `gfx1032`, not `gfx1030`; unknown IDs are never guessed. The target hint is a cross-check, not proof that a shader translator supports that GPU. It records:

- AVX/AVX2 hardware support and whether Windows has enabled the required AVX state;
- SSE4A, CLWB, CLZERO, MONITORX/MWAITX, CLFLUSHOPT, FMA3, BMI1 and BMI2;
- GPU adapter name, vendor/device IDs and dedicated VRAM reported by DXGI;\n- a conservative AMD RDNA2 target hint for a small set of known PCI IDs (unknown IDs remain unknown; this is not a full PCI database);
- D3D12 availability and feature level;
- highest queried shader model, WaveOps/lane range and mesh-shader tier.

It creates a D3D12 device to query capabilities but submits no rendering or compute work.

## 3. Optional Vulkan inventory

If `vulkaninfo` is already installed and on PATH, capture its summary too:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\host_probe\Collect-HostInfo.ps1 -IncludeD3D12Info -IncludeVulkanInfo
```

The Vulkan summary is retained as text. It is not yet a complete automated pass/fail check for every extension or subgroup behavior needed by Leonida.

## Output and privacy

The JSON report includes the machine name, Windows version, CPU model, installed RAM, current committed memory, commit limit, page-file usage, GPU/driver details and disk capacity/free space. Review it before sharing; redact the machine name and any details you do not want public. The default output folder is ignored by Git.

## Limitations

- The probe is compiled and exercised in Windows CI but has not yet been run on the target PC.
- The WMI adapter-memory field in the basic inventory can be capped or inaccurate; use the native DXGI value when available.
- Feature support is only a capability check. It does not prove that a driver is bug-free or that a particular game workload will run correctly.
- No performance benchmark is performed.
- The GitHub artifact expires after 14 days; use the latest successful workflow run if it has expired.

## Safety

The PowerShell script collects system inventory only. The C++ program reads CPU feature flags and enumerates graphics adapters/device capabilities. It does not scan game packages, extract assets, launch a game, install drivers/SDKs, change the page file, change settings, or make network requests. Build output `host_caps.exe` is ignored by Git.


## Wave64 compatibility warning

The native D3D12 probe records `WaveLaneCountMin` and `WaveLaneCountMax`. The readable summary warns when the maximum lane count is below 64 because VIctory documents that some world compute programs need 64-lane waves. It also notes that XCL documents a 32-lane emulation path, with performance and shader-behavior caveats. This is a capability warning, not a definitive incompatibility verdict; the actual runtime and shader path must still be tested.

The CI workflow runs a synthetic 32-lane fixture to ensure the warning remains visible. The fixture is synthetic and does not represent the user's RX 6600.


## One-click Windows runner

The standalone CI artifact includes `Run-HostProbe.bat` at its root. Extract the ZIP and double-click it; it runs the read-only collector and summary without changing system settings. The wrapper was exercised end-to-end in CI on Windows PowerShell 5.1, including native probe execution and JSON output. Review `reports/host-probe.json` before sharing because it includes the PC name and hardware/software details.
