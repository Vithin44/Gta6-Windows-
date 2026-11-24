# Read-only Windows host inventory for GTA VI compatibility research.
# This script does not scan for game files, install software, change settings, or launch a game.
[CmdletBinding()]
param(
    [string]$OutputPath,
    [switch]$IncludeVulkanInfo,
    [switch]$IncludeD3D12Info
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($OutputPath)) {
    $OutputPath = Join-Path $PSScriptRoot "..\..\reports\host-probe.json"
}

function Get-SafeProperty {
    param(
        [object]$InputObject,
        [string]$Name
    )
    if ($null -eq $InputObject) { return $null }
    $property = $InputObject.PSObject.Properties[$Name]
    if ($null -eq $property) { return $null }
    return $property.Value
}

$os = Get-CimInstance -ClassName Win32_OperatingSystem
$computer = Get-CimInstance -ClassName Win32_ComputerSystem
$processors = @(Get-CimInstance -ClassName Win32_Processor)
$videoControllers = @(Get-CimInstance -ClassName Win32_VideoController)
$logicalDisks = @(Get-CimInstance -ClassName Win32_LogicalDisk -Filter "DriveType=3")
$memoryStats = $null
try {
    $memoryStats = Get-CimInstance -ClassName Win32_PerfFormattedData_PerfOS_Memory -ErrorAction Stop
} catch {
    $memoryStats = $null
}
$pageFileStats = @()
try {
    $pageFileStats = @(Get-CimInstance -ClassName Win32_PageFileUsage -ErrorAction Stop)
} catch {
    $pageFileStats = @()
}
$pageFileAllocatedMb = [int64]0
$pageFileCurrentUsageMb = [int64]0
$pageFilePeakUsageMb = [int64]0
foreach ($pageFile in $pageFileStats) {
    $pageFileAllocatedMb += [int64](Get-SafeProperty $pageFile "AllocatedBaseSize")
    $pageFileCurrentUsageMb += [int64](Get-SafeProperty $pageFile "CurrentUsage")
    $pageFilePeakUsageMb += [int64](Get-SafeProperty $pageFile "PeakUsage")
}

$cpuFeatures = [ordered]@{
    avx2 = $null
    nativeProbe = $null
    note = "Null means this PowerShell/.NET runtime could not query AVX2; it does not mean AVX2 is absent. The native CPUID probe can report additional flags."
}
try {
    $avx2Type = [System.Type]::GetType("System.Runtime.Intrinsics.X86.Avx2, System.Private.CoreLib", $false)
    if ($null -ne $avx2Type) {
        $isSupported = $avx2Type.GetProperty("IsSupported")
        if ($null -ne $isSupported) {
            $cpuFeatures.avx2 = [bool]$isSupported.GetValue($null)
        }
    }
} catch {
    $cpuFeatures.note = "AVX2 query unavailable in this PowerShell/.NET runtime: $($_.Exception.Message)"
}

$gpus = foreach ($gpu in $videoControllers) {
    [ordered]@{
        name = Get-SafeProperty $gpu "Name"
        videoProcessor = Get-SafeProperty $gpu "VideoProcessor"
        driverVersion = Get-SafeProperty $gpu "DriverVersion"
        driverDate = Get-SafeProperty $gpu "DriverDate"
        adapterRamReportedBytes = Get-SafeProperty $gpu "AdapterRAM"
        note = "Win32_VideoController AdapterRAM can be capped or inaccurate; verify dedicated VRAM with a GPU-specific tool."
    }
}

$disks = foreach ($disk in $logicalDisks) {
    [ordered]@{
        device = Get-SafeProperty $disk "DeviceID"
        volumeName = Get-SafeProperty $disk "VolumeName"
        sizeBytes = Get-SafeProperty $disk "Size"
        freeBytes = Get-SafeProperty $disk "FreeSpace"
    }
}

$vulkan = [ordered]@{
    queried = $false
    commandFound = $false
    summary = $null
    error = $null
}
if ($IncludeVulkanInfo) {
    $vulkanCommand = Get-Command "vulkaninfo" -ErrorAction SilentlyContinue
    if ($null -ne $vulkanCommand) {
        $vulkan.commandFound = $true
        try {
            $vulkanOutput = & $vulkanCommand.Source --summary 2>&1 | Out-String
            $vulkan.summary = $vulkanOutput.Trim()
            $vulkan.queried = $true
        } catch {
            $vulkan.error = $_.Exception.Message
        }
    } else {
        $vulkan.error = "vulkaninfo was not found on PATH; no software was installed."
    }
}

$d3d12 = [ordered]@{
    queried = $false
    executableFound = $false
    result = $null
    error = $null
}
if ($IncludeD3D12Info) {
    $capsExecutable = Join-Path $PSScriptRoot "host_caps.exe"
    if (Test-Path -LiteralPath $capsExecutable) {
        $d3d12.executableFound = $true
        try {
            $capsOutput = & $capsExecutable 2>&1 | Out-String
            $capsExitCode = $LASTEXITCODE
            if ($capsExitCode -eq 0) {
                $d3d12.result = $capsOutput | ConvertFrom-Json
                $d3d12.queried = $true
                $cpuFeatures.nativeProbe = $d3d12.result.cpu
            } else {
                $d3d12.error = "host_caps.exe exit code $capsExitCode; output: $($capsOutput.Trim())"
            }
        } catch {
            $d3d12.error = $_.Exception.Message
        }
    } else {
        $d3d12.error = "host_caps.exe was not found. Build it using the instructions in docs/HOST_PROBE.md."
    }
}

$report = [ordered]@{
    reportVersion = 1
    collectedAtUtc = (Get-Date).ToUniversalTime().ToString("o")
    machineName = $env:COMPUTERNAME
    operatingSystem = [ordered]@{
        caption = Get-SafeProperty $os "Caption"
        version = Get-SafeProperty $os "Version"
        buildNumber = Get-SafeProperty $os "BuildNumber"
        architecture = Get-SafeProperty $os "OSArchitecture"
    }
    memory = [ordered]@{
        totalPhysicalBytes = Get-SafeProperty $computer "TotalPhysicalMemory"
        freePhysicalMemoryKb = Get-SafeProperty $os "FreePhysicalMemory"
        totalVisibleMemorySizeKb = Get-SafeProperty $os "TotalVisibleMemorySize"
        committedBytes = Get-SafeProperty $memoryStats "CommittedBytes"
        commitLimitBytes = Get-SafeProperty $memoryStats "CommitLimit"
        availableMBytes = Get-SafeProperty $memoryStats "AvailableMBytes"
        pageFileAllocatedMb = $pageFileAllocatedMb
        pageFileCurrentUsageMb = $pageFileCurrentUsageMb
        pageFilePeakUsageMb = $pageFilePeakUsageMb
    }
    processors = @(
        foreach ($cpu in $processors) {
            [ordered]@{
                name = Get-SafeProperty $cpu "Name"
                manufacturer = Get-SafeProperty $cpu "Manufacturer"
                cores = Get-SafeProperty $cpu "NumberOfCores"
                logicalProcessors = Get-SafeProperty $cpu "NumberOfLogicalProcessors"
                addressWidth = Get-SafeProperty $cpu "AddressWidth"
            }
        }
    )
    cpuFeatures = $cpuFeatures
    graphics = [ordered]@{
        adapters = @($gpus)
        d3d12 = $d3d12
        d3d12FeatureLevel = "See graphics.d3d12.result.adapters when queried"
        shaderModel = "See graphics.d3d12.result.adapters when queried"
        meshShaderTier = "See graphics.d3d12.result.adapters when queried"
        vulkan = $vulkan
    }
    fixedDisks = @($disks)
    safety = [ordered]@{
        gameFilesScanned = $false
        gameProcessesLaunched = $false
        settingsChanged = $false
        softwareInstalled = $false
        networkUsed = $false
    }
}

$resolvedOutputPath = [System.IO.Path]::GetFullPath($OutputPath)
$outputDirectory = Split-Path -Parent $resolvedOutputPath
if (-not (Test-Path -LiteralPath $outputDirectory)) {
    New-Item -ItemType Directory -Path $outputDirectory -Force | Out-Null
}

$json = $report | ConvertTo-Json -Depth 10
[System.IO.File]::WriteAllText($resolvedOutputPath, $json, (New-Object System.Text.UTF8Encoding($false)))

Write-Host "Host inventory saved to: $resolvedOutputPath"
Write-Host "This probe did not scan game files, launch a game, install software, or change system settings."
if (-not $IncludeD3D12Info) {
    Write-Host "For CPU instruction flags and D3D12 feature levels, rerun with -IncludeD3D12Info."
} elseif (-not $d3d12.queried) {
    Write-Warning ("The native D3D12 probe did not complete: " + [string]$d3d12.error)
}
