# Integration and execution plan

**Baseline date:** 2026-11-24  
**Current phase:** upstream audit, report tooling and host diagnostics  
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

**Status: in progress — XCL and VIctory pinned; Leonida source pin blocked**

- [ ] Pin Leonida to a full 40-character commit SHA and capture its full LICENSE, third-party notices and submodule revisions.
- [x] Pin XCL and VIctory to full commit SHAs and inspect key loader, runtime, D3D12 and shader source files at those revisions.
- [ ] Record top-level and dependency licenses, including submodules and generated/test data.
- [x] Compare the documented loader, TLS, import resolution, filesystem, runtime services, D3D12.X, shader translation, audio and input paths for XCL and VIctory.
- [ ] Complete the same file-level comparison for Leonida after its source revision is reachable.
- [ ] Separate synthetic tests, tests using public samples, and tests requiring user-owned title data.
- [ ] Inspect CI workflows and recent failures; distinguish passing tests from skipped tests.

**Exit evidence:** a revision-pinned comparison matrix with a file-level provenance ledger. No code copied.

## Milestone 2 — Host capability inventory

**Status: Windows artifact build configured; target-PC execution pending**

The read-only PowerShell inventory and native C++ CPUID/D3D12 probe are committed. They record OS, CPU instruction flags, RAM, GPU adapter/VRAM, D3D12 shader model, WaveOps, mesh-shader tier and disk capacity. Optional Vulkan summary capture is available. GitHub Actions now builds and publishes a ready-to-run Windows executable artifact. The current host-probe revision compiled and published successfully in [validation run #58](https://github.com/Vithin44/Gta6-Windows-/actions/runs/45330101418); its `windows-host-probe` artifact expires 2026-12-08. It includes committed-memory/pagefile metrics and the precise AVX-state flag. Use the newest successful workflow artifact, not an older run. The probe has not yet been run on the target PC.

Create a read-only Windows host probe. First target the user's reported hardware:

- AMD Ryzen 5 5500;
- AMD Radeon RX 6600;
- 16 GB system RAM;
- 1 TB SATA SSD.

The probe must collect actual Windows version, CPU feature flags, installed/committed memory, GPU driver and VRAM, D3D12 shader model/mesh-shader tier, Vulkan extensions/subgroup properties and free disk space. The current Vulkan capture is summary text; structured extension/subgroup parsing remains future work.

**Exit evidence:** a timestamped JSON and readable summary. No upstream runtime launched; no SDK or driver installed; no game folders scanned.

## Milestone 3 — Independent source checkout and clean builds

**Status: XCL and VIctory pinned smoke tests passed; Leonida remains unpinned**

- [x] Add pinned XCL and VIctory source references to an isolated GitHub Actions workflow.
- [x] Keep each upstream in its own ephemeral checkout and build directory; no upstream source is committed here.
- [x] Restrict XCL tests to the upstream-supported no-title-data suite and skip its retail title end-to-end test.
- [x] Build VIctory with `cargo build --workspace --locked`, then run its documented `cargo test --workspace --locked` suite; no title data is used.
- [x] Capture successful build/test logs and confirm skipped GPU tests are clearly reported. XCL: 700 passed, 0 failed, 41 ignored; 86 GPU tests skipped for no Wave64 and 2 for no GPU UMA. VIctory: 264 passed, 0 failed, 4 ignored.
- [ ] Add Leonida only after its exact revision and full dependency/license provenance can be verified.
- [ ] Do not build or run leaked executables or unknown prebuilt binaries.

**Exit evidence:** [successful workflow run #2](https://github.com/Vithin44/Gta6-Windows-/actions/runs/45329732775) and its 14-day log artifacts. The tests used no title data and ran on a hosted Windows Server 2025 runner; XCL GPU tests skipped because that runner has no Wave64/GPU UMA. Leonida remains blocked on exact source revision and dependency provenance.

## Milestone 4 — Shared report and diagnostics tooling

**Status: schema, validator and XCL/VIctory adapters implemented; latest regression run pending**

- [x] Implement a versioned JSON run-report schema.
- [x] Add a validator for project-owned reports and a synthetic fixture.
- [x] Validate the manifest, report fixture and PowerShell syntax in GitHub Actions; build and publish the native C++ probe artifact in Windows CI.
- [x] Add conservative normalizers for XCL report.json and VIctory crash/console logs.
- [ ] Add a Leonida adapter after its test artifact formats and exact revision are verified.
- [ ] Preserve original logs; normalized reports link to local copies instead of replacing them.
- [ ] Record the exact commit, host, driver, test and stage for every run.
- [ ] Add redaction for usernames and absolute paths before sharing reports.

**Exit evidence:** XCL and VIctory adapter fixtures validate without game files; Leonida remains pending until its export format is inspected at a pinned revision.

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
| RX 6600 feature support not measured | A backend may fail before game-specific code runs | Host capability probe first |
| 16 GB RAM vs upstream-reported 36–40 GB commit growth | XCL world-loading tests may exhaust commit or stall | Measure commit limit/free memory; do not start title runs until synthetic builds and memory requirements are understood |
| Leonida full asset stage requires about 400 GiB free | A full asset build could consume most of the 1 TB SSD | Prefer the documented reduced check/shader/runtime stages first; measure free disk space |
| 16 GB RAM and unknown free disk space | Build/runtime may exhaust commit or storage | Measure first; avoid full asset build by default |
| Driver hang/reset risk | System instability or lost work | Synthetic tests, diagnostic fallback, stop on reset |
| User data could be accidentally committed | Copyright/privacy/security risk | Keep all game data outside repo; ignore output folders |

## Immediate next actions

1. Finish the latest Windows CI run, verify the standalone host-probe bundle, and publish its current run link.
2. Complete the new VIctory build-plus-test run and retain its build/test logs.
3. Obtain Leonida's exact commit, full LICENSE and submodule/dependency provenance through a verified source endpoint; keep it excluded until then.
4. Use the standalone probe once on the target PC to collect CPU flags, free/committed RAM, commit limit, RX 6600 driver, D3D12 features and optional Vulkan summary.
5. Compare the real host report with VIctory's AVX2/SM 6.6/mesh requirements, XCL's memory pressure and Leonida's Vulkan/Wave64 requirements.
6. Add Leonida report normalization and graphics-specific synthetic comparisons only after its source and artifact formats are pinned.
