# DedSec — preliminary repository audit

**Audit date:** 2026-11-24  
**Candidate:** [Hylanderry/DedSec](https://github.com/Hylanderry/DedSec)  
**Audit level:** README and cached repository-page review only; source audit blocked.

## Executive finding

DedSec describes an ambitious Xbox Series → Windows route built around a native Windows/Direct3D 12 runtime. Its stated graphics direction is RDNA2 shader translation to HLSL/Shader Model 6.6 and DXIL. This is relevant to our work because it is architecturally closer to XCL and VIctory's D3D12/DXIL path than Leonida's Vulkan/SPIR-V path.

However, the available README explicitly marks the real game boot as **pending**, and marks in-game play as **not achieved**. The README also labels the PE loader/import shims partial and the Xbox D3D12 ABI proxy in progress. Therefore, "advanced port" should be interpreted as a broad collection of claimed subsystems, not a demonstrated bootable or playable port.

**Important access limitation:** the search index returned a cached GitHub page showing branch `dedsec-clean`, 37 commits and the file list, but direct GitHub page and GitHub API requests returned 404 during this audit. Individual source files, the LICENSE blob, build logs, workflow runs, releases, submodule configuration and exact commit SHA could not be retrieved. The cached page may be stale, or the repository may have become private, been removed, renamed, or be temporarily unavailable. We cannot distinguish these possibilities yet.

## What the README claims

| Area | README claim | Evidence status in this audit |
|---|---|---|
| Execution route | Xbox Series x86-64 title binary runs natively on Windows; no CPU emulation layer | Architecture claim only; no real-title boot |
| Graphics | RDNA2 `gfx1030` → HLSL SM 6.6 → DXIL → native D3D12 | Claimed implementation; source and output unavailable |
| Shader coverage | 26,503 game shaders and 1,630 RDNA2 instruction forms covered | Self-reported; corpus, generated output and validation logs unavailable |
| Xbox runtime | PE loader/import shims, GDK/XTaskQueue, UMA address translation | PE loader marked partial; D3D12 Xbox ABI proxy marked in progress |
| Assets | GDeflate streaming decompressor | Self-reported smoke-test result; no reproducible log inspected |
| Audio/input | XAudio2 shim; XInput plus mouse/keyboard mapping | Self-reported; source and tests unavailable |
| Rendering extras | FSR3 upscaling/frame generation, VRS, async compute, PSO pre-warming, shader cache, Hi-Z culling | Self-reported integration/testing; no GPU test evidence inspected |
| Game progress | Boot pending; in-game playable: no | Explicitly stated by the README |

The README describes tests for XBCH parsing, DEFLATE stored blocks, dynamic DXC loading, memory gating, input mapping and GDeflate. It also describes shader validation against a 26,503-shader corpus. Since neither test code nor logs could be inspected, these remain upstream claims, not results reproduced by our repository.

## What is technically useful to investigate

1. **D3D12/DXIL shader route.** This is the strongest architectural overlap with XCL and VIctory. Compare the translator's intermediate representation, instruction coverage, resource mapping, wave operations, atomics, image operations and DXIL validation against the existing translators. Do not assume that "1,630 forms" means semantic correctness for every real shader.
2. **GDeflate and package/container tooling.** A standalone, well-tested decompressor or parser could be useful as an independently tested tool. We must first inspect the implementation, input bounds, malformed-input handling, fuzz tests and license provenance.
3. **Xbox service shims.** XTaskQueue/XAsync, XAudio2 and input adapters could be useful reference implementations, but their API coverage and behavior need source-level review and conformance tests.
4. **D3D12 runtime diagnostics.** PSO cache metrics, shader cache behavior, resource/descriptor tracking and device-loss reporting could improve our normalized diagnostics if their output formats are inspectable.
5. **Hardware fallbacks.** The README's Wave64 mode and GPU-tier detection are worth comparing against the other projects, but must be tested on actual devices.

## Important mismatch for our target PC

The README emphasizes the `gfx1030` instruction target. AMD's own ROCm GPU architecture table lists the Radeon RX 6600 as **RDNA2 / gfx1032**, not gfx1030. The RX 6600 is in the same RDNA2 family, but we must not assume a translator or generated code path targeting gfx1030 is automatically correct or optimal for gfx1032. The native host probe should record the actual adapter and capabilities, then we need an explicit gfx1032 test path or a documented compatibility argument.

AMD reference: [ROCm GPU architecture specifications](https://rocmdocs.amd.com/en/docs-7.2.4/reference/gpu-arch-specs.html).

The README's "6 GB threshold" refers to its shader compilation memory gating; it is not evidence that the complete game runtime fits in 6 GB of system RAM. Our machine has 16 GB RAM and an RX 6600 with 8 GB VRAM, so XCL/VIctory's reported high system-commit use remains a separate risk.

## License and provenance

The cached README says the project uses the MIT License. The actual `LICENSE` file could not be fetched. The cached page also lists a `.gitmodules` file and a `third_party/` directory, but neither their contents nor their revisions were available.

**Disposition: treat MIT as unverified. Do not copy, vendor, build, or redistribute any DedSec source until the exact LICENSE text, commit SHA, submodule URLs/revisions and third-party notices have been reviewed.** If the MIT license is confirmed, individual components may be candidates for reuse subject to their own upstream licenses and provenance. A top-level MIT file would not automatically cover third-party code or generated artifacts.

## Comparison with our current candidates

| Project | Graphics direction | What is currently evidenced | Immediate relevance |
|---|---|---|---|
| XCL | D3D12.X → host D3D12; RDNA2 → HLSL/DXIL | Our pinned no-title-data test suite passed; upstream issue reports language screen/loading art then world-load failure | Baseline D3D12 runtime and HLE |
| VIctory | D3D12.X → host D3D12; RDNA2 → DXIL | Our pinned no-title-data test suite passed; upstream README reports menu/intro/world-load progress but no playable scene | Closest current title-specific D3D12 reference |
| Leonida | D3D12 → Vulkan; RDNA2 → SPIR-V | README reports shader validation and GPU tests; real game boot not achieved | Alternative graphics backend and shader-validation reference |
| DedSec | RDNA2 → HLSL SM 6.6 → DXIL; native D3D12 | README claims many subsystems; real boot explicitly pending; source inaccessible in this audit | Potential D3D12/shim/tooling candidate; not yet auditable |

A different graphics route does not by itself make DedSec superior. XCL and VIctory already use D3D12/DXIL, so any DedSec shader/runtime contribution must demonstrate better correctness, coverage, portability or performance on the same test inputs.

## Next actions

1. Recheck whether the public repository and its source API become accessible; capture its full 40-character HEAD SHA and immutable file URLs.
2. Fetch and review `LICENSE`, `.gitmodules`, `third_party/`, build workflows, release assets, test sources and build logs.
3. Verify the claimed 1,630 instruction forms against actual translator code and tests; identify unsupported instructions and semantics.
4. Compare shader translation using identical, non-copyrighted synthetic shader inputs and validation outputs. Keep any game-derived corpus outside our repository.
5. Inspect GDeflate, XBCH parsing, XTaskQueue, XAudio2 and input modules as separate candidates.
6. Add a separate isolated smoke workflow only after source provenance and license checks pass. Do not merge its runtime into XCL or VIctory merely because both target D3D12.

No DedSec code has been copied into this repository. No executable was downloaded or run. No game package or asset was accessed.
