# Proposed integration architecture

**Status:** proposal, not an implemented runtime.  
**Decision:** integrate evidence and tooling first; keep upstream runtimes independent until license and technical gates are satisfied.

## 1. Why this is not one source-code merge

The audited projects have three different technical shapes:

- XCL and VIctory target host D3D12 and translate console shaders to HLSL/DXIL.
- Leonida targets Vulkan and translates console shaders to SPIR-V.
- XCL is GPL-2.0-only; VIctory and Leonida declare GPL-3.x terms.

A single binary made by copying pieces from all three would create both license and engineering problems. A common test/report format is useful; a common runtime implementation is not yet justified.

## 2. Proposed repository layout

```text
Gta6-Windows-/
├── README.md
├── CONTRIBUTING.md
├── docs/
│   ├── UPSTREAMS.md
│   ├── ARCHITECTURE.md
│   ├── INTEGRATION_PLAN.md
│   └── evidence/
├── manifests/
│   └── upstreams.json
├── schemas/
│   └── run-report.schema.json
├── tools/
│   ├── host_probe/
│   ├── report/
│   └── orchestration/
└── upstreams/
    └── README.md
```

This is a target layout. Directories and tools should be added when there is working content for them, not as empty scaffolding.

### Repository responsibilities

- `docs/`: explain findings, decisions, evidence and unresolved questions.
- `manifests/upstreams.json`: pin source URLs, revisions, licenses and local checkout locations.
- `schemas/`: define a stable, project-owned report format.
- `tools/host_probe/`: read-only host capability inventory; it must not inspect or modify game files.
- `tools/report/`: validate and normalize logs/reports that the user chooses to provide.
- `tools/orchestration/`: invoke separately installed upstream tools, capture exit codes and output, and never combine their libraries into one process.
- `upstreams/`: documentation and optional Git submodule pointers only. No copied upstream source by default.

## 3. Runtime boundary

Each upstream remains an independent program and build:

```text
                  Our orchestration / evidence layer
                 ┌──────────────────────────────────┐
                 │ source pins • host probe         │
                 │ run records • report validator   │
                 └───────────────┬──────────────────┘
                                 │ normalized reports
              ┌──────────────────┼──────────────────┐
              │                  │                  │
        ┌─────▼─────┐      ┌─────▼─────┐      ┌─────▼─────┐
        │    XCL    │      │  VIctory  │      │  Leonida  │
        │ separate  │      │ separate  │      │ separate  │
        │ process   │      │ process   │      │ process   │
        └─────┬─────┘      └─────┬─────┘      └─────┬─────┘
              │                  │                  │
         D3D12 host         D3D12 host          Vulkan host
         DXIL shaders       DXIL shaders        SPIR-V shaders
```

The orchestration layer may pass ordinary command-line arguments and collect text/JSON outputs. It must not inject DLLs, patch binaries, bypass authentication, or transfer private game data between projects.

## 4. Common evidence contract

Every test run should produce a JSON record with:

- schema version and run ID;
- UTC timestamp;
- upstream name, exact commit SHA, dirty/clean checkout state and build configuration;
- host OS/build, CPU model/features, RAM and commit limit, GPU model/driver/VRAM;
- graphics API and feature checks actually queried;
- test name, input class (synthetic fixture or user-owned local data), exit code and duration;
- stage reached: `not_started`, `process_started`, `loader_initialized`, `runtime_initialized`, `menu_presented`, `world_loaded`, `scene_rendered`, `playable`;
- artifact references that point only to local paths chosen by the user, never uploaded game data;
- warnings, errors, crash code, log path and a concise human conclusion.

A stage must never be inferred from the previous one. A successful process exit, a present counter, a non-empty frame dump or a translated shader count is not proof of correct rendering or gameplay.

## 5. Host capability probe

Before any large build or runtime attempt, gather a read-only inventory:

| Capability | Why it matters |
|---|---|
| Windows version/build and architecture | Runtime and SDK compatibility |
| CPU model and AVX2 | VIctory/Leonida prerequisites and shader/tool workloads |
| Installed RAM and Windows committed/commit limit | Loader and asset-processing headroom |
| GPU model, VRAM and driver | Actual graphics backend and memory limits |
| D3D12 feature level, shader model and mesh shader tier | XCL/VIctory graphics requirements |
| Vulkan API version, extensions, subgroup size and mesh shader support | Leonida's Vulkan backend and Wave64 strategy |
| Free space on selected work/output volumes | Avoid unexpectedly starting multi-hundred-GB jobs |

The probe must not scan for game packages, inspect private directories, change the page file, install SDKs, download drivers, or launch an upstream runtime. It reports facts and recommendations only.

### Known host to evaluate

The user has reported a Ryzen 5 5500, Radeon RX 6600, 16 GB RAM and a 1 TB SATA SSD. This is a starting inventory, not a compatibility verdict. The actual Windows build, GPU driver, feature support, available committed memory and free disk space still need to be measured on the PC.

## 6. Data and security boundaries

- All game packages and any derived assets stay on the user's machine.
- Only files the user is authorized to access and that are already readable by the supported upstream tools may be used.
- No decryption, key extraction, DRM/authentication bypass, anti-cheat bypass or online-service impersonation.
- No game executable, proprietary asset, key, save, shader dump or extracted resource is committed or uploaded.
- Treat downloaded executables and build artifacts as untrusted; inspect provenance and hashes, use an isolated test environment, and do not run unknown binaries on a primary PC.
- The orchestration layer stores logs and reports in a user-selected output folder and redacts usernames and absolute paths before sharing.

## 7. How to choose a lead runtime

Do not select a winner based on stars, claims or shader counts. Use the same evidence gates:

1. clean checkout at a pinned commit;
2. reproducible build using documented dependencies;
3. upstream synthetic tests pass;
4. loader initializes a project-owned test fixture;
5. authorized local title data passes read-only validation;
6. runtime reaches each stage with logs and crash diagnostics;
7. frame captures show expected scene content, not merely a present call;
8. stable repeatable gameplay without driver resets or data corruption.

VIctory is the first candidate to investigate for GTA VI boot progress because its inspected README reports reaching the world. Leonida is a parallel candidate for Vulkan, shader, asset and GPU-test research. XCL is a general Xbox Series reference and possible independent runtime candidate. This is a test priority, not a claim that any one project is complete or compatible with the user's PC.

## 8. Explicit non-goals for this repository

- Rehosting or mirroring the game.
- Bundling proprietary game files or leaked executables.
- Making an unsupported claim that GTA VI is playable.
- Combining incompatible licensed code into one binary.
- Modifying the original upstream repositories.
- Automatically running game binaries or long GPU/asset workloads.
