# Windows host capability probe

The host probe is designed to measure the actual PC before attempting an upstream build or runtime. It is read-only with respect to system settings and game data.

## 1. Basic inventory

Open PowerShell at the repository root and run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\host_probe\Collect-HostInfo.ps1
```

This records Windows version/build, CPU model, RAM, display driver details and fixed-disk capacity/free space.

## 2. Native CPU and D3D12 feature check

For the deeper check, open **Developer PowerShell for Visual Studio 2022** at the repository root and compile the small native probe:

```powershell
cl /nologo /std:c++17 /EHsc /W4 .\tools\host_probe\host_caps.cpp /link d3d12.lib dxgi.lib /Fe:tools\host_probe\host_caps.exe
```

Then run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\host_probe\Collect-HostInfo.ps1 -IncludeD3D12Info
```

The native probe reads CPUID and asks DXGI/D3D12 for hardware-adapter capabilities. It records:

- AVX/AVX2 hardware support and whether Windows has enabled the required AVX state;
- SSE4A, CLWB, CLZERO, MONITORX/MWAITX, CLFLUSHOPT, FMA3, BMI1 and BMI2;
- GPU adapter name, vendor/device IDs and dedicated VRAM reported by DXGI;
- D3D12 availability and feature level;
- highest queried shader model, WaveOps/lane range and mesh-shader tier.

It creates a D3D12 device to query capabilities but submits no rendering or compute work.

## 3. Optional Vulkan inventory

If `vulkaninfo` is already installed and on PATH, capture its summary too:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\host_probe\Collect-HostInfo.ps1 -IncludeD3D12Info -IncludeVulkanInfo
```

The Vulkan summary is retained as text. It is not yet a complete automated pass/fail check for every extension or subgroup behavior needed by Leonida.

## Output

The default output is `reports/host-probe.json`. Choose another path with `-OutputPath`. The output folder is created if necessary.

## Limitations

- The script has not yet been executed on the target Windows PC.
- The WMI adapter-memory field in the basic inventory can be capped or inaccurate; use the native DXGI value when available.
- If the PowerShell/.NET runtime cannot query AVX2, its value is `null`; that does not mean AVX2 is absent.
- Feature support is only a capability check. It does not prove that a driver is bug-free or that a particular game workload will run correctly.
- No performance benchmark is performed.

## Safety

Neither probe scans for game files, reads game packages, extracts assets, launches a game, installs software, changes the page file, changes system settings or makes network requests. The C++ program only reads CPU feature flags and enumerates graphics adapters/device capabilities. Build output `host_caps.exe` is ignored by Git.
