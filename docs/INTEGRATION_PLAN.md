# Integration and execution plan

**Baseline date:** 2026-11-24  
**Current phase:** upstream audit and architecture definition  
**Rule:** each milestone has an observable exit condition. Do not report a milestone as complete without evidence.

## Milestone 0 — Establish project rules

**Status: complete**

- [x] Create the research repository README.
- [x] Record the initial safety, provenance and evidence rules.
- [x] Audit XCL and VIctory metadata, licenses and current documentation.
- [x] Inspect Leonida's public GitHub page and README; record the connector limitation on exact revision capture.
- [x] Define an independent orchestration architecture.
- [x] Create a source-level feature matrix for XCL and VIctory, with Leonida status caveats.

**Exit evidence:** `docs/UPSTREAMS.md`, `docs/ARCHITECTURE.md` and `docs/FEATURE_MATRIX.md` committed.

## Milestone 1 — Pin and deepen upstream audits

**Status: in progress**

- [ ] Pin Leonida to a full 40-character commit SHA and capture its full LICENSE, third-party notices and submodule revisions.
- [x] Pin XCL and VIctory to full commit SHAs and inspect key loader, runtime, D3D12 and shader source files at those revisions.
- [ ] Record top-level and dependency licenses, including submodules and generated/test data.
- [ ] Compare loader, TLS, import resolution, filesystem, runtime services, D3D12.X, shader translation, audio and input implementations.
- [ ] Separate synthetic tests, tests using public samples, and tests requiring user-owned title data.
- [ ] Inspect CI workflows and recent failures; distinguish passing tests from skipped tests.

**Exit evidence:** a revision-pinned comparison matrix with a file-level provenance ledger. No code copied.

## Milestone 2 — Host capability inventory

**Status: probe implemented; target-PC execution pending**

The read-only PowerShell inventory and native C++ CPUID/D3D12 probe are committed. They record OS, CPU instruction flags (including AVX2, CLWB, CLZERO, MONITORX/MWAITX and SSE4A), RAM, GPU adapter/VRAM, D3D12 shader model, WaveOps, mesh-shader tier and disk capacity. Optional Vulkan summary capture is available. The native probe compiled successfully in Windows CI; the PowerShell parser and report-schema validation also passed. It has not yet been run on the target PC.

Create a read-only Windows host probe. First target the user's reported hardware:

- AMD Ryzen 5 5500;
- AMD Radeon RX 6600;
- 16 GB system RAM;
- 1 TB SATA SSD.

The probe must collect actual Windows version, CPU feature flags, installed/committed memory, GPU driver and VRAM, D3D12 shader model/mesh-shader tier, Vulkan extensions/subgroup properties and free disk space. The current Vulkan capture is summary text; structured extension/subgroup parsing remains future work.

**Exit evidence:** a timestamped JSON and readable summary. No upstream runtime launched; no SDK or driver installed; no game folders scanned.

## Milestone 3 — Independent source checkout and clean builds

**Status: blocked on Milestone 1**

- [ ] Add pinned upstream references only after revision and license capture.
- [ ] Keep each upstream in its own checkout and build directory.
- [ ] Build only the upstream's documented tools and synthetic test fixtures.
- [ ] Capture compiler versions, commands, build output and exit codes.
- [ ] Do not build or run leaked executables or unknown prebuilt binaries.

**Exit evidence:** reproducible build records for each independently buildable upstream. A build failure is recorded as-is, not hidden.

## Milestone 4 — Shared report and diagnostics tooling

**Status: initial schema and validator implemented; upstream adapters pending**

- [x] Implement a versioned JSON run-report schema.
- [x] Add a validator for project-owned reports and a synthetic fixture.
- [x] Validate the manifest, report fixture and PowerShell syntax in GitHub Actions; compile the native C++ probe in Windows CI.
- [ ] Add a normalizer for reports voluntarily exported by the upstream tools.
- [ ] Preserve original logs; normalized reports link to local copies instead of replacing them.
- [ ] Record the exact commit, host, driver, test and stage for every run.
- [ ] Add redaction for usernames and absolute paths before sharing reports.

**Exit evidence:** fixture reports from all three adapters validate without requiring any game files.

## Milestone 5 — Graphics and runtime comparison

**Status: not started**

Run project-owned synthetic tests where upstream tooling permits:

- PE loader and import resolver;
- TLS and exception handling;
- virtual filesystem and copy-on-write behavior;
- D3D12 resource/queue/descriptor operations;
- Vulkan resource/descriptor/command operations;
- shader translation and validator results;
- pipeline creation and known-output GPU tests;
- audio decode and input mapping.

Keep D3D12/DXIL and Vulkan/SPIR-V paths independent. Compare equivalent inputs and expected outputs, not implementation internals.

**Exit evidence:** per-feature matrix with pass/fail/skip and attached test logs. No GTA VI gameplay claim.

## Milestone 6 — Authorized local-data validation

**Status: not started; user-side prerequisite**

Only proceed if the user independently has lawful access to a supported, already-readable package and the selected upstream explicitly supports that format/version. This repository will not provide game files, keys, extraction instructions, DRM bypasses or executable downloads.

Start with non-executing validation and metadata checks. Keep package files, extracted assets and generated data outside this Git repository.

**Exit evidence:** local validation report with sensitive paths redacted. No package content is uploaded.

## Milestone 7 — Runtime startup and rendering gates

**Status: not started**

If an upstream's own documented workflow reaches this stage, record each stage separately:

1. process started;
2. PE image mapped and loader initialized;
3. required runtime services initialized;
4. menu presented;
5. world loaded;
6. expected scene rendered;
7. stable interactive gameplay.

For every stage capture the upstream revision, host/driver, logs, crash diagnostics, frame evidence and repeat count. A presentation counter or dark frame does not count as rendering success.

**Exit evidence:** repeatable, independently reviewable records. Stop if the real GPU hangs, the display driver resets, data is modified unexpectedly, or the executable's provenance is unclear.

## Milestone 8 — Decide whether a unified runtime is justified

**Status: not started**

Only consider a unified runtime after:

- the legal review confirms compatible licensing or separate independent processes;
- a specific subsystem gap is identified with reproducible evidence;
- the proposed implementation has a clear source/provenance record;
- a synthetic regression test exists before the change;
- upstream maintainers' licenses and attribution requirements are respected.

Otherwise, keep this repository as an orchestration, comparison and diagnostics layer. That is still a meaningful integration: one place to reproduce, compare and track all three projects without corrupting or forking their work.

## Current blockers and risks

| Risk | Consequence | Mitigation |
|---|---|---|
| GPL-2.0-only vs GPL-3.x | Cannot assume one combined derivative is distributable | Keep runtimes separate; review before code reuse |
| Leonida exact revision unavailable through current connector | Cannot claim a pinned source audit | Capture SHA and license through a verified Git source before pinning |
| README status may lag current upstream issue/PR activity | Maturity comparisons can be wrong | Use commit-specific tests, CI and recent issue evidence |
| RX 6600 feature support not measured | A backend may fail before game-specific code runs | Host capability probe first |
| 16 GB RAM and unknown free disk space | Build/runtime may exhaust commit or storage | Measure first; avoid full asset build by default |
| Driver hang/reset risk | System instability or lost work | Synthetic tests, diagnostic fallback, stop on reset |
| User data could be accidentally committed | Copyright/privacy/security risk | Keep all game data outside repo; ignore output folders |

## Immediate next actions

1. Finish the Leonida revision/license capture.
2. Complete the source-level feature matrix for XCL and VIctory.
3. Commit a pinned upstream manifest and the report schema.
4. Implement the read-only Windows host probe.
5. Only then decide which independent runtime to build first.
