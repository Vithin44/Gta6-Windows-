# Windows host inventory probe

The script `tools/host_probe/Collect-HostInfo.ps1` collects a read-only machine inventory for compatibility planning.

## Run

Open PowerShell on the Windows PC, change to the root of this repository, and run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\host_probe\Collect-HostInfo.ps1
```

To also capture the output of `vulkaninfo --summary` when the Vulkan SDK/tool is already installed:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\host_probe\Collect-HostInfo.ps1 -IncludeVulkanInfo
```

The default output is `reports/host-probe.json`. You can choose another path with `-OutputPath`.

## What it records

- Windows edition/version/build and architecture;
- CPU model, core/thread counts and an AVX2 query when the installed PowerShell/.NET runtime exposes it;
- total/free physical memory;
- display adapters, driver versions and the raw WMI adapter-memory value;
- fixed-volume capacity and free space;
- optional Vulkan summary output if `vulkaninfo` is already present.

## Important limitations

- The WMI adapter-memory field can be capped or inaccurate; do not treat it as authoritative VRAM.
- AVX2 is `null` when the PowerShell/.NET runtime cannot query it; `null` does not mean unsupported.
- This first version does not query D3D12 shader model, feature level or mesh-shader tier. Those fields are explicitly marked as not queried.
- A Vulkan summary is not a complete validation of every feature the runtime needs.
- The script has not yet been executed on the target Windows PC. Review the generated JSON before sharing it.

## Safety

The script does not scan for game files, read game packages, launch a game, install software, change system settings, change the page file, or make network requests. It writes only the JSON report at the output path you choose.
