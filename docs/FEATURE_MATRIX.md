# Upstream feature matrix

**Snapshot:** 2026-11-24. This is a source/documentation audit, not a test performed by this repository.

Legend: **documented** = stated in inspected upstream source/docs; **partial** = known implementation with material gaps; **unknown** = not established by this audit.

| Area | XCL | VIctory | Leonida |
|---|---|---|---|
| Target | General Xbox Series X|S | GTA VI Xbox Series X|S | GTA VI Xbox Series X|S |
| Main language/build | Rust workspace, edition 2021 | Rust workspace, edition 2024 | Python/C++ tools and Windows native runtime |
| License | GPL-2.0-only | GPL-3.0-or-later (Cargo metadata; LICENSE GPL v3) | GPLv3-or-later stated in README; exact LICENSE blob not fetched |
| PE loading | PE loader/import resolver; TLS and exception handling documented | Prepares title image as DLL, lets Windows map it for TLS/unwind, then binds imports and invokes title entry path | Stand-in PE loader/import-shim path runs end-to-end; real title executable explicitly untested |
| Missing imports | Generated/logged stubs and structured run report | Generated stubs with trap/zero policy and crash diagnostics | GDK/XMem/D3D12 import shims; D3D12 trace path |
| Runtime services | Offline XGameRuntime subset, task queues, async, users, saves, package/system APIs | Offline runtime services, users, saves and title APIs | GDK/XGameRuntime shims; stand-in validation |
| File system | Virtual console paths, copy-on-write overlay; game folder intended read-only | Console path mapping and separate save/data/cache folders | Package/asset pipeline and runtime filesystem shims |
| Graphics API | D3D12.X to native host D3D12; null fallback available | D3D12.X to host D3D12 | Xbox D3D12 to Vulkan; still in progress |
| Shader path | RDNA2 to HLSL, compiled to DXIL with DXC | RDNA2 to DXIL/SM 6.6 | RDNA2 to SPIR-V; README reports 26,503 translated |
| GPU validation | 370+ automated tests reported upstream, including instruction-level GPU comparisons; latest README reports 26,698 shader programs translated and 909/912 textures exact | Mesh pipelines and shader/pipeline diagnostics; world rendering incomplete | Small synthetic GPU test suite across 30+ GPU/driver combinations; all translated shaders separately checked with SPIR-V validation/pipeline creation |
| Mesh/wave concerns | Mesh shaders and Wave64 behavior are explicit GPU requirements/test areas | Mesh pipelines implemented; mesh shaders required for world; most world shaders still untranslated | Wave64 emulation for 32-wide subgroups; native Wave64 on suitable AMD GPUs; D3D12/Vulkan mesh support still in progress |
| Textures/assets | GFX10 tiling/detiling and RPF tools documented | Texture tiling/detiling in formats crate; some render-target metadata missing | RPF9, BCPack, texture pools, model/audio export tools; full asset stage is very large |
| Audio | XAudio2 path; XMA/Opus handling described | Menu/video/loading audio; XMA/Opus decode; reverb/Opus verification gaps stated | AWC Opus/XMA2 export and decode tools |
| Input | XInput and keyboard/mouse mapping | XInput and keyboard-as-pad | GameInput shim via SDL3 |
| CPU compatibility | x64 native execution; report/preflight records host environment | AVX2 required; source emulates selected CLZERO, MONITORX/MWAITX, CLWB patterns and SSE4A operations on CPUs lacking them | x86-64 native execution; exact CPU feature requirements not pinned in this audit |
| Diagnostics | Structured report with imports, called stubs, environment, shaders, D3D12, audio, runtime and VFS | Text crash log, console output, crash dumps and optional diagnostic captures | Runtime traces, GPU tests, progress dashboard |
| Synthetic tests | Unit, end-to-end test title and optional GPU tests | Workspace tests and stand-in HLE fixture | Stand-in loader test and extensive GPU/translator tests |
| Real GTA VI evidence in inspected docs | Older issue #646 reports a 1.0.2.1 run reaching language screen/loading art, then failing during world loading; peak commit around 36 GB is reported. Current README focuses on other retail titles and does not claim GTA VI is playable. | README reports menus, intro video and world loading; the first mission scene remains dark and real-GPU entry may hang/reset the driver. | README explicitly says the title does not boot and is not playable; real executable path is untested. |

## Source-level observations

### XCL

At the audited commit, `crates/xcl/src/hle/d3d12x/mod.rs` exposes a real host-D3D12 backend and a null fallback. The null backend is documented as rendering nothing. `crates/xcl/src/report.rs` defines a detailed `report.json` model, including imports, called stubs, environment, VFS, shader formats, DXC, D3D12, audio, XGameRuntime and DirectStorage.

Issue [#646](https://github.com/ivall/xcl/issues/646) reports a GTA VI run reaching the language screen and loading art before world-loading failure. The issue's test machine had 32 GB RAM and the report records peak commit around 36 GB. A comment describes another 12 GB GPU run reaching about 40 GB private commit and stalling in pipeline work. This is an important memory-pressure warning for a 16 GB host, not a proven hard minimum or a result reproduced by this repository.

**Integration opportunity:** normalize XCL's structured report. Do not import its GPL-2.0-only runtime into a GPL-3.x combined binary.

### VIctory

At the audited commit, `victory-loader` prepares a lightly patched image, maps it through the Windows loader for TLS/unwind behavior, resolves imports through HLE/host/title DLLs and routes unresolved calls to generated stubs. The D3D12.X shim delegates device/resource behavior to `victory-gpu`; the shader emitter targets host DXIL at shader model 6.6.

Its README reports menus, intro video and world loading, but the world remains dark and real-GPU entry can hang/reset the driver. The tested host is an RX 6700 XT, not an RX 6600.

The current crash handler explicitly emulates selected Zen 2-specific instructions on other CPUs: CLZERO, MONITORX/MWAITX, selected CLWB patterns and SSE4A operations. AVX2 remains a stated requirement. We should measure CPU flags, but must not repeat older issue claims as if these instruction paths remain wholly unimplemented.

**Integration opportunity:** build and test VIctory independently after host preflight. Normalize its `crashes.log` and optional console output; never infer a rendered scene from a clean exit.

### Leonida

The current public README describes a native recompilation project with RDNA2-to-SPIR-V translation and a Vulkan-backed Xbox D3D12 layer. It reports 26,503 translated shaders, documented SPIR-V validation reruns, and small GPU tests across more than 30 GPU/driver combinations. These results do not mean the GTA VI executable boots: the README explicitly says it does not boot, and the stand-in loader test is untested against the real executable.

The README describes Wave64 emulation for 32-wide subgroups and native Wave64 on suitable AMD hardware. It lists RX 5700 XT/RDNA1 GPU-suite evidence, not a direct RX 6600 test. The D3D12-to-Vulkan runtime remains in progress.

The full asset export is estimated around 400 GiB free space; the reduced check/shader/runtime path is estimated around 30 GiB. The large assets stage is optional for a first runtime-oriented build.

**Integration opportunity:** study the shader translator contract, GPU test methodology, Vulkan feature matrix, D3D12 proxy, and asset decoders. Do not classify Leonida as a boot candidate until its own README and real-executable test evidence change.

## Comparison decisions

1. **Do not merge runtimes now.** Their graphics backends and licenses differ.
2. **Build common report adapters first.** XCL has structured JSON; VIctory has text crash/console diagnostics; Leonida's progress dashboard and test artifacts need a separate adapter after its exact revision is pinned.
3. **Run synthetic tests before title data.** This validates our adapters and host capability probes without touching game files.
4. **Prioritize VIctory for independent boot-stage comparison; keep XCL as the second D3D12 reference.** Leonida is currently more valuable for Vulkan/shader/asset research than real-title boot.
5. **Measure the RX 6600 and available system commit.** A 16 GB host may be constrained by the memory growth reported in XCL's world-loading issue.
