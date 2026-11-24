# Current upstream status and next test targets

**Snapshot:** 2026-11-24  
**Purpose:** distinguish upstream-reported progress from what this repository has actually built or tested.

## XCL — strongest general Xbox/D3D12 foundation

Current main HEAD: `d208e14b765f469f4b56301b78afa8dac5378339`  
License: GPL-2.0-only.

The current README lists Minecraft Preview and Unicorn Overlord as fully playable, Fortnite and XDefiant working within their offline/server limitations, and another unnamed retail title reaching menus/settings at 30 fps on a 32 GB system. It does **not** claim GTA VI is playable. Its current public results include:

- 26,698 RDNA2 shader programs (26,503 records) translated to HLSL, with random DXC samples compiling without errors;
- 370+ automated tests, including instruction-level GPU comparisons;
- 909 of 912 retail textures decoded byte-for-byte;
- the game's FSR 4 console upscaler running end-to-end on an RX 9070;
- a detailed HLE/runtime, D3D12.X, shader, texture, audio, input and diagnostic implementation.

These are upstream README claims and results, not reproduced by this repository. The RX 9070 FSR 4 test is not evidence for the user's RX 6600.

### New shader-cache change worth testing

The current main revision adds a build-time translator-source identity and combines it with the loaded DXC toolchain identity. Translated DXIL is placed in a versioned v2 cache namespace. This is designed to preserve cache entries across unrelated executable/profile changes while invalidating entries when translator semantics or DXC change. New tests check identity stability, source/toolchain separation, request inputs and legacy-cache isolation.

This is the most immediately useful recent XCL change to validate in our next CI run. It is an optimization and cache-correctness improvement, not a GTA VI boot fix.

### GTA VI relevance

An older XCL issue (#646) reports a GTA VI 1.0.2.1 attempt reaching the language screen and loading artwork before failing during world loading, with high memory-commit use reported. The current README's stronger retail-game results demonstrate the general Xbox runtime is maturing, but do not establish that the specific GTA VI world renderer works.

## VIctory — strongest GTA VI-specific boot progress

Current main HEAD: `d2a4bae1f49533ef5cb512fd1b1ba1513f2e1989`  
License: GPL-3.0-or-later.

Its README status dated 2026-11-23 reports first-boot screens and menus at 30 fps, intro video with sound, profile/saves, and loading into the world. The first mission intro reaches indirect draws and a title card, but the scene after it remains dark; frame times are reported at 0.5–1.8 seconds. It was tested on one Windows 11 / RX 6700 XT machine. The README warns that entering the world on a real GPU can hang the GPU and trigger a display-driver reset. This is not an RX 6600 test and not playable gameplay.

The source requires AVX2, D3D12 Shader Model 6.6 and mesh shaders for the world. Its diagnostics include DRED, GPU-based validation, frame capture, render-target dumps, pipeline skipping and WARP fallback.

## DedSec — promising claims, still not source-auditable

Repository: [Hylanderry/DedSec](https://github.com/Hylanderry/DedSec)  
Cached branch shown: `dedsec-clean`; cached page listed 37 commits.  
License: README claims MIT, but the actual LICENSE and third-party provenance remain unverified.

The cached README claims RDNA2-to-HLSL/DXIL, 26,503 shader records, 1,630 instruction forms, GDeflate, XTaskQueue, XAudio2, input shims and D3D12 optimizations. It explicitly says real boot is pending and in-game play has not been achieved. Direct GitHub API/page retrieval returned 404 in this audit, so there is no verified commit SHA, source tree, build log or submodule inventory. No DedSec code has been copied.

The README emphasizes gfx1030, whereas AMD's official ROCm architecture table identifies the Radeon RX 6600 as RDNA2 gfx1032. The same RDNA2 family does not prove exact-target compatibility. Our host probe records the adapter PCI ID, D3D12 shader model, WaveOps lane range and mesh-shader tier so that the local hardware can be measured rather than guessed.

## What our CI has actually proven

Completed [smoke run #6](https://github.com/Vithin44/Gta6-Windows-/actions/runs/45331424599), on hosted Windows Server 2025, without GTA VI title data:

| Project | Pinned revision | Build/tests | Result |
|---|---|---|---|
| XCL | `64b3f35599bb7102f55d640e1a791e7d6dd3b175` | upstream-supported build and tests | 700 passed, 0 failed, 41 ignored; 86 GPU tests skipped for no Wave64 and 2 for no GPU UMA |
| VIctory | `d2a4bae1f49533ef5cb512fd1b1ba1513f2e1989` | workspace build + single-threaded tests | 264 passed, 0 failed, 4 ignored |

VIctory's earlier parallel run crashed in `victory-shader` with Windows `0xc0000005`. The single-threaded pass suggests a possible concurrency-sensitive issue, but does not prove the cause or resolve the parallel-run failure.

The next smoke run is pinned to XCL's newer main revision `d208e14b765f469f4b56301b78afa8dac5378339` to validate its new cache code. The host probe passed CI validation in [run #92](https://github.com/Vithin44/Gta6-Windows-/actions/runs/45332397931); the [standalone bundle](https://github.com/Vithin44/Gta6-Windows-/actions/runs/45332397931/artifacts/14892442322) has not yet been run on the target PC.

## Integration decision

Do not merge the XCL GPL-2.0-only runtime and VIctory GPL-3.x runtime into one derivative. Keep upstreams isolated, preserve immutable revisions and provenance, and integrate through build orchestration, neutral diagnostic reports and independently implemented tests. Do not copy DedSec code until the source, exact license and third-party components can be audited.

The immediate order is: test latest XCL cache code; run the read-only host probe on the RX 6600 PC; compare actual CPU/D3D12/WaveOps/mesh/memory capabilities with upstream requirements; then decide whether any local, user-owned data validation is technically justified. Do not launch unknown binaries or assume that a successful unit-test suite means GTA VI boots.
