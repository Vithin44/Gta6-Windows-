# Upstream project audit

**Audit date:** 2026-11-24  
**Scope:** public repository metadata, READMEs, licenses and selected source files. No upstream game runtime has been executed by this repository.

## Executive summary

These projects overlap in Xbox Series compatibility work, but they are not interchangeable modules. XCL and VIctory/Leonida have copyleft license constraints; DedSec is a preliminary candidate whose README claims MIT but whose license and source could not be inspected in this audit. Their graphics paths and maturity claims differ.

| Project | Declared license | Main approach | GTA VI evidence in current public docs | Disposition |
|---|---|---|---|---|
| [XCL](https://github.com/ivall/xcl) | GPL-2.0-only | Xbox services/HLE; D3D12.X-to-host-D3D12; RDNA2-to-HLSL/DXIL | Issue #646 reports a 1.0.2.1 run reaching the language screen and loading art, then failing during world loading. | General Xbox compatibility reference and separate runtime candidate. |
| [VIctory](https://github.com/Marvisak/VIctory) | GPL-3.0-or-later in Cargo metadata; LICENSE is GPL v3 | Windows PE loader; HLE; D3D12.X-to-host-D3D12; RDNA2-to-DXIL | README reports menus, intro video and world loading, but no playable rendered scene; warns of real-GPU hangs/resets. | Strongest documented real-title boot progress in this audit; prioritize independent build/test comparison. |
| [Leonida](https://github.com/ProjectLeonida/Leonida) | GPLv3-or-later stated in README; GitHub page labels GPL-3.0 | Static recompilation; D3D12-to-Vulkan; RDNA2-to-SPIR-V; asset/shader tooling | README says GTA VI does not boot yet. It reports 26,503 shader translations and broad GPU tests, while the real executable path remains untested. | Valuable shader, Vulkan, GPU-test and asset-format research; not a boot-ready runtime. |
| [DedSec](https://github.com/Hylanderry/DedSec) | MIT claimed by README; LICENSE blob unverified | Xbox Series → Windows; RDNA2-to-HLSL/SM 6.6/DXIL; native D3D12 | README explicitly says boot pending and not playable; PE loader partial, D3D12 Xbox ABI proxy in progress. Source/API returned 404 during audit. | Candidate for D3D12 shader, GDeflate, XTaskQueue, audio/input and diagnostics comparison; no code reuse yet. |

## Revision records

Revisions are immutable commit identifiers where the GitHub connector exposed them. Do not silently replace them with a moving branch name.

| Project | Branch | Audited revision | Evidence and limitation |
|---|---|---|---|
| XCL | `main` | `64b3f35599bb7102f55d640e1a791e7d6dd3b175` | Rechecked against GitHub's main-branch API on 2026-11-24; README, Cargo.toml, LICENSE, HANDOFF/design docs, THIRD_PARTY.md and report source inspected. |
| VIctory | `main` | `d2a4bae1f49533ef5cb512fd1b1ba1513f2e1989` | Rechecked against GitHub's main-branch API on 2026-11-24; README, Cargo.toml, LICENSE, architecture, loader and crash-handler source inspected. |
| Leonida | `main` | **Not pinned** | The public page is available and its README was inspected, but GitHub API/file retrieval returned 404 through the connected GitHub interface. The README's clone URL is `https://github.com/ItsNotRexed/Leonida`; the page resolves to `ProjectLeonida/Leonida`. Exact SHA, LICENSE blob and submodule revisions remain unverified. |
| DedSec | `dedsec-clean` (cached page only) | **Not pinned** | Search index showed 37 commits and a repository tree, but direct GitHub page/API and raw source requests returned 404. No exact SHA, LICENSE blob, source or submodule revisions verified. See `docs/DEDSEC_AUDIT.md`. |

The manifest stores these states in `manifests/upstreams.json`. Null Leonida and DedSec SHAs are intentional; never invent a revision from a moving branch or cached page.

## XCL

- Rust workspace; top-level LICENSE is GNU GPL version 2 and Cargo metadata declares GPL-2.0-only.
- General Xbox Series X|S compatibility layer, not a GTA VI-only port.
- Uses a PE loader/import resolver, HLE modules, virtual filesystem and copy-on-write overlay.
- Graphics path: Xbox D3D12.X to host D3D12; RDNA2 shader recompilation to HLSL/DXIL. A null graphics backend exists for diagnostics but does not render.
- `crates/xcl/src/report.rs` defines a structured `report.json` with version/title/exit/crash data, environment checks, import resolution, called stubs, modules, VFS, shader, DXC, D3D12, audio, XGameRuntime and DirectStorage statistics. This is the first upstream format targeted by our report adapter.
- Issue [#646](https://github.com/ivall/xcl/issues/646) reports GTA VI 1.0.2.1 reaching the language screen and rendering loading art on an RTX 3060 12 GB, then failing during world loading. The issue reports peak system commit around 36 GB and local VRAM around 12.9 GB. It is an upstream issue report, not a result reproduced here.
- A later comment on that issue describes a separate 12 GB GPU run with 32 GB system RAM reaching roughly 40 GB private commit and stalling in shader pipeline work. Treat memory/commit pressure as a major risk for a 16 GB host, not as a proven hard minimum.
- The issue's run revision is `a6f5f7a` plus locally applied files from PRs; it is not the same evidence as our pinned source snapshot.
- Its own Windows CI builds the workspace and runs unit/integration tests without a GPU or game data. The upstream CI explicitly skips the retail title end-to-end test; game-data tests are skipped when their sample variables are unset, and unsupported GPU tests report SKIPPED.
- Our isolated smoke workflow reran the pinned revision: 700 tests passed, 0 failed, 41 ignored. The hosted Windows runner skipped 86 GPU tests for lack of Wave64 and 2 for lack of GPU UMA. This is not an RX 6600 GPU test.
- `THIRD_PARTY.md` lists additional provenance and compatibility constraints. It explicitly warns against bringing GPL-3.0/LGPL-3.0 code into this GPL-2.0-only project.

## VIctory

- Rust workspace; Cargo metadata declares GPL-3.0-or-later; top-level LICENSE is GNU GPL version 3.
- Architecture separates PE loading, HLE, GPU, shader translation, formats, pipeline/cache and title-specific code.
- README status dated 2026-11-23 reports boot screens, intro video with sound, profile/saves and loading into the world. The first mission scene remains dark, many shaders are untranslated, frames are slow, and real-GPU entry can hang/reset the display driver.
- README's tested machine is Windows 11 with an AMD RX 6700 XT. This does not establish RX 6600 compatibility.
- Requirements include Windows 10/11 x64, AVX2, D3D12 shader model 6.6, and mesh shaders for the world. Several GiB of available Windows commit are needed at startup.
- The current loader crash handler contains compatibility emulation for selected Zen 2-specific instructions on other CPUs: CLZERO, MONITORX/MWAITX, selected CLWB patterns and SSE4A operations. This reduces some instruction-set blockers but does not prove every CPU path or performance is compatible. AVX2 remains a stated requirement.
- The run path writes crash diagnostics to `crashes.log`; the loader maps the PE through Windows to preserve TLS/unwind behavior and resolves imports through HLE, host and title DLLs.
- The README documents `cargo test --workspace` as a no-game-data test suite. The repository pins Rust 1.98.1 in `rust-toolchain.toml`.
- Our first isolated smoke run at the pinned revision reported 264 tests passed, 0 failed, 4 ignored. A later repeat on the same pinned revision built successfully but the `victory-shader` test process terminated with Windows `0xc0000005` (access violation) after several tests, without a Rust assertion failure. XCL passed again. This makes VIctory's test result non-deterministic in our hosted Windows runner; we are rerunning its workspace suite single-threaded to isolate a possible race or unsafe-code issue. No title data was configured or used.
- No stable, versioned JSON run-report format was found in the inspected source. Our adapter therefore imports the text crash log and optional console output conservatively; it does not infer visual progress.

## DedSec — preliminary only

See the detailed [DedSec audit](DEDSEC_AUDIT.md). The cached README describes an Xbox-to-Windows/D3D12 implementation with RDNA2-to-HLSL/DXIL, GDeflate, XTaskQueue, audio/input shims and rendering optimizations. It explicitly states that real-title boot is pending and gameplay has not been achieved.

The search index showed branch `dedsec-clean`, 37 commits and a repository tree, but direct GitHub page/API access returned 404 during this audit. No exact commit SHA, LICENSE blob, source files, build logs, workflow runs, releases or submodule revisions could be verified. The README says MIT, but this is not license verification. Do not import code or add DedSec to build CI until access and provenance are restored.

AMD documents the RX 6600 as RDNA2 `gfx1032`, while DedSec's README emphasizes `gfx1030`. Treat exact-target support as an open compatibility test, not an automatic pass based on the shared RDNA2 family.

## Leonida

- The public README describes a native recompilation project: Xbox x86-64 title code runs natively while console services are reimplemented; RDNA2 programs are translated to SPIR-V for Vulkan.
- Current README status explicitly says the real game does not boot and nothing is playable yet.
- The README reports 26,503 shaders translated. It separately documents SPIR-V validation runs, including a Linux full-corpus run with all 26,503 passing. Translation and validation are distinct from correct rendering.
- Its small GPU test shaders have been exercised across more than 30 GPU/driver combinations. These tests validate translator/runtime contracts, not the output of every GTA VI shader.
- The Windows runtime and tools build; the Xbox D3D12-to-Vulkan layer is still in progress. A stand-in executable exercises the PE loader and import shims end-to-end, but the README says that path is untested against the real executable.
- The README documents Wave64 emulation for 32-wide subgroups (common on NVIDIA/Intel) and native Wave64 on suitable AMD GPUs. It lists AMD RDNA1/RX 5700 XT GPU-suite results; that is not a direct RX 6600 test.
- The README estimates about 400 GiB free for the full asset export. A reduced `check,shaders,runtime` workflow is estimated around 30 GiB; the large `assets` stage is optional for runtime startup. Measure free disk space before attempting either.
- Third-party provenance includes the `rpf9-explorer` submodule, Mesa-derived reference material, Microsoft's libHttpClient implementation, LLVM and SPIRV-Tools. Each component and submodule needs its own license/revision record before code reuse.
- The README says the project does not distribute the game, keys or executable and does not decrypt or bypass protection. Any local package use must follow the project's own requirements and applicable law.

## Our isolated smoke-test result

Workflow [run #2](https://github.com/Vithin44/Gta6-Windows-/actions/runs/45329732775) completed successfully on Windows Server 2025. XCL and VIctory were cloned at the exact revisions above into separate temporary folders; no upstream source was committed into this repository. Test logs are retained as 14-day workflow artifacts. These are software build/unit/integration results on a hosted runner, not evidence that either runtime works on the user's PC or that GTA VI is playable.

## License and integration constraints

1. XCL is GPL-2.0-only. VIctory and Leonida are GPL-3.x. Do not assume these can be combined into one derived executable.
2. Keep every upstream runtime in an independent checkout/process. This repository can provide orchestration, capability probes, normalized reports, test comparison and documentation without copying their runtime code.
3. Separate processes and a neutral interchange format are an engineering boundary, not an automatic legal conclusion for every distribution model. This document is not legal advice.
4. Third-party dependencies, generated tables, test vectors, submodules and copied snippets have their own terms. A top-level license is not a complete provenance audit.
5. This research repository has no selected software license. Do not assume an upstream license automatically licenses this repository or its original material.

## Next audit tasks

- Obtain Leonida's exact main commit, full LICENSE text, `.gitmodules` revisions and complete dependency license inventory.
- Compare XCL and VIctory import/HLE coverage, TLS, filesystem, runtime services, D3D12.X, shader translation, audio and input at pinned revisions.
- Inspect each project's CI workflows and test fixtures; distinguish tests requiring game data from synthetic/public-sample tests.
- Compare GPU feature requirements with the actual RX 6600 report, including shader model, mesh shaders, WaveOps and subgroup width.
- Keep all game executables, package files, keys, extracted assets, shader dumps and saves outside this repository.
