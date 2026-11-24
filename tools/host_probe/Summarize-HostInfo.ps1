# Summarize a previously collected host-probe JSON report.
[CmdletBinding()]
param(
    [string]$InputPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($InputPath)) {
    $InputPath = Join-Path $PSScriptRoot "..\..\reports\host-probe.json"
}

function Get-Prop {
    param([object]$Object, [string]$Name)
    if ($null -eq $Object) { return $null }
    $property = $Object.PSObject.Properties[$Name]
    if ($null -eq $property) { return $null }
    return $property.Value
}

function Format-Gb {
    param([object]$Bytes)
    if ($null -eq $Bytes) { return "unknown" }
    return ("{0:N1} GiB" -f ([double]$Bytes / 1GB))
}

$resolved = [System.IO.Path]::GetFullPath($InputPath)
if (-not (Test-Path -LiteralPath $resolved -PathType Leaf)) {
    throw "Host report not found: $resolved"
}
$report = Get-Content -LiteralPath $resolved -Raw | ConvertFrom-Json

$cpu = @($report.processors)[0]
$gpu = @($report.graphics.adapters)[0]
$native = Get-Prop (Get-Prop $report.graphics "d3d12") "result"
$nativeCpu = Get-Prop $native "cpu"
$nativeGpu = $null
$nativeAdapters = Get-Prop $native "adapters"
if ($null -ne $nativeAdapters -and @($nativeAdapters).Count -gt 0) {
    $nativeGpu = @($nativeAdapters)[0]
}

$gpuName = Get-Prop $nativeGpu "name"
if (-not $gpuName) { $gpuName = Get-Prop $gpu "name" }
$gpuDriver = Get-Prop $gpu "driverVersion"
$gpuVram = Get-Prop $nativeGpu "dedicated_video_memory_bytes"
$commitLimit = Get-Prop $report.memory "commitLimitBytes"
$committed = Get-Prop $report.memory "committedBytes"
$freeRamKb = Get-Prop $report.memory "freePhysicalMemoryKb"
$ramFreeBytes = $null
if ($null -ne $freeRamKb) { $ramFreeBytes = [double]$freeRamKb * 1KB }
$ramAvailableMb = Get-Prop $report.memory "availableMBytes"
$commitLeft = $null
if ($null -ne $commitLimit -and $null -ne $committed) {
    $commitLeft = [math]::Max([double]0, [double]$commitLimit - [double]$committed)
}

Write-Host ""
Write-Host "GTA VI Windows Research — PC inventory"
$collectedAt = $report.collectedAtUtc
$osCaption = $report.operatingSystem.caption
$osBuild = $report.operatingSystem.buildNumber
$cpuName = Get-Prop $cpu "name"
$avx2Hardware = Get-Prop $nativeCpu "avx2_hardware"
$avxOsState = Get-Prop $nativeCpu "avx_os_state_enabled"
$clwb = Get-Prop $nativeCpu "clwb"
$clzero = Get-Prop $nativeCpu "clzero"
$monitorx = Get-Prop $nativeCpu "monitorx"
$sse4a = Get-Prop $nativeCpu "sse4a"
$cpuFlags = "AVX2={0}; AVX state={1}; CLWB={2}; CLZERO={3}; MONITORX={4}; SSE4A={5}" -f $avx2Hardware, $avxOsState, $clwb, $clzero, $monitorx, $sse4a
$ramTotal = Format-Gb $report.memory.totalPhysicalBytes
$ramFree = Format-Gb $ramFreeBytes
$ramAvailableText = "available {0} MB" -f $ramAvailableMb
$committedText = "{0} / {1}" -f (Format-Gb $committed), (Format-Gb $commitLimit)
$commitLeftText = Format-Gb $commitLeft
$pageFileAllocated = Get-Prop $report.memory "pageFileAllocatedMb"
$pageFileCurrentUsage = Get-Prop $report.memory "pageFileCurrentUsageMb"
$gpuArch = Get-Prop $nativeGpu "amd_gfx_target"
$d3d12Available = Get-Prop $nativeGpu "d3d12_available"
$shaderModel = Get-Prop $nativeGpu "shader_model"
$waveOps = Get-Prop $nativeGpu "wave_ops"
$waveLaneMin = Get-Prop $nativeGpu "wave_lane_min"
$waveLaneMax = Get-Prop $nativeGpu "wave_lane_max"
$meshTier = Get-Prop $nativeGpu "mesh_shader_tier"

Write-Host ("Collected: {0}" -f $collectedAt)
Write-Host ("Windows:   {0} (build {1})" -f $osCaption, $osBuild)
Write-Host ("CPU:       {0}" -f $cpuName)
Write-Host ("CPU flags: {0}" -f $cpuFlags)
Write-Host ("RAM:       {0}" -f $ramTotal)
Write-Host ("RAM free:  {0} ({1})" -f $ramFree, $ramAvailableText)
Write-Host ("Committed: {0}" -f $committedText)
Write-Host ("Commit left: {0}" -f $commitLeftText)
Write-Host ("Pagefile:  {0} MB allocated; {1} MB in use" -f $pageFileAllocated, $pageFileCurrentUsage)
Write-Host ("GPU:       {0}" -f $gpuName)
Write-Host ("GPU arch:  {0}" -f $gpuArch)
Write-Host ("Driver:    {0}" -f $gpuDriver)
Write-Host ("VRAM:      {0}" -f (Format-Gb $gpuVram))
Write-Host ("D3D12:     {0}" -f $d3d12Available)
Write-Host ("Shader:    {0}" -f $shaderModel)
Write-Host ("WaveOps:   {0} (lanes {1}-{2})" -f $waveOps, $waveLaneMin, $waveLaneMax)
Write-Host ("Mesh:      {0}" -f $meshTier)
Write-Host ""


$warnings = [System.Collections.Generic.List[string]]::new()
$avx2 = Get-Prop $nativeCpu "avx2_hardware"
if ($null -eq $avx2) { $avx2 = Get-Prop $report.cpuFeatures "avx2" }
if ($avx2 -eq $false) {
    $warnings.Add("AVX2 was not detected. VIctory lists AVX2 as a requirement.")
} elseif ($avx2 -eq $true) {
    Write-Host "CPU check: AVX2 detected."
} else {
    $warnings.Add("AVX2 could not be confirmed; run the native capability probe.")
}

if ($null -eq $nativeGpu) {
    $warnings.Add("D3D12 capabilities were not collected. Run Collect-HostInfo.ps1 with -IncludeD3D12Info.")
} else {
    $shader = [string](Get-Prop $nativeGpu "shader_model")
    if ($shader -match '^(\d+)_(\d+)$') {
        $major = [int]$Matches[1]
        $minor = [int]$Matches[2]
        if ($major -lt 6 -or ($major -eq 6 -and $minor -lt 6)) {
            $warnings.Add("Shader Model $shader is below VIctory's documented 6.6 requirement.")
        }
    } else {
        $warnings.Add("D3D12 shader model could not be confirmed.")
    }
    if ((Get-Prop $nativeGpu "mesh_shader_tier") -eq "not_supported") {
        $warnings.Add("D3D12 mesh shaders were not reported; VIctory's world-rendering path requires them.")
    }
    if ((Get-Prop $nativeGpu "wave_ops") -ne $true) {
        $warnings.Add("D3D12 WaveOps were not confirmed.")
    }
    $waveMax = Get-Prop $nativeGpu "wave_lane_max"
    if ($null -eq $waveMax) {
        $warnings.Add("D3D12 WaveOps lane range is unknown; native 64-lane wave support could not be confirmed.")
    } elseif ([int]$waveMax -lt 64) {
        $warnings.Add("D3D12 WaveOps max lane count is $waveMax; VIctory reports some world compute programs need 64-lane waves. XCL documents a 32-lane emulation path with performance and shader-behavior caveats.")
    }
}

if ($null -ne $commitLimit -and [double]$commitLimit -lt 36GB) {
    $warnings.Add("Commit limit is below the roughly 36–40 GiB peak reported in an XCL world-loading issue; this is a comparison point, not a guaranteed minimum.")
}

$maxFree = 0.0
foreach ($disk in @($report.fixedDisks)) {
    if ($null -ne $disk.freeBytes -and [double]$disk.freeBytes -gt $maxFree) {
        $maxFree = [double]$disk.freeBytes
    }
}
if ($maxFree -lt 30GB) {
    $warnings.Add("No fixed disk has 30 GiB free; Leonida estimates about 30 GiB for its reduced check/shader/runtime stages.")
} elseif ($maxFree -lt 400GB) {
    $warnings.Add("No fixed disk has 400 GiB free; Leonida's full asset-export stage estimates about 400 GiB. The full assets stage is optional.")
}

if ((Get-Prop (Get-Prop $report.graphics "vulkan") "queried") -ne $true) {
    $warnings.Add("Vulkan device/subgroup details were not collected; Leonida's Vulkan compatibility remains unmeasured.")
}

if ($warnings.Count -eq 0) {
    Write-Host "No obvious capability blockers were detected by these limited checks."
} else {
    Write-Host "Items to investigate:"
    foreach ($warning in $warnings) {
        Write-Warning $warning
    }
}

Write-Host ""
Write-Host "This is a capability screen, not proof that any upstream runtime or game will work."
Write-Host "No game files were scanned and no game process was launched."
