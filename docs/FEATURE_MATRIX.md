# Upstream feature matrix

**Snapshot:** 2026-11-24. This is a source/documentation audit, not a test performed by this repository.

Legend: **documented** = stated in inspected upstream source/docs; **partial** = known implementation with material gaps; **unknown** = not established by this audit.

| Area | XCL | VIctory | Leonida |
|---|---|---|---|
| Target | General Xbox Series X|S | GTA VI Xbox Series X|S | GTA VI Xbox Series X|S |
| Main language/build | Rust workspace, edition 2021 | Rust workspace, edition 2024 | C++/Python toolchain and native runtime; full build details in upstream README |
| License | GPL-2.0-only | GPL-3.0-or-later | GitHub declares GPL-3.0 |
| PE loading | Manual mapping and import resolver; TLS/exceptions documented in handoff | Prepares title image as DLL, lets Windows map it for TLS/unwind handling, then binds imports and invokes title entry path | PE loader/shims; stand-in fixture documented; real-title path/status is not consistent across README and current issue activity |
| Missing imports | Generated/logged stubs and structured run report | Generated stubs with trap/zero policy and crash diagnostics | Import shims and D3D12 trace path documented |
| Runtime services | Offline XGameRuntime subset, task queues, async, users, saves, package/system APIs | Offline runtime services, users, saves and title APIs | GDK/XGameRuntime shims, stand-in validation; detailed live coverage requires commit-pinned review |
| File system | Virtual console paths, copy-on-write overlay; game folder intended read-only | Console path mapping and save/data folders | Package/asset pipeline and runtime filesystem shims |
| Graphics API | D3D12.X to native host D3D12; real and null fallback backends | D3D12.X to host D3D12 | Xbox D3D12 to Vulkan |
| Shader path | RDNA2 to HLSL, compiled to DXIL with DXC | RDNA2 to DXIL/SM 6.6 | RDNA2 to SPIR-V |
| Mesh/wave concerns | Mesh shaders and Wave64 behavior are explicit GPU requirements and test areas | Mesh pipelines implemented; README lists untranslated world shaders and Wave64 gaps | Wave64 emulation and mesh-compute fallback documented; platform-specific limitations listed |
| Textures/assets | GFX10 tiling/detiling and RPF tools documented | Texture tiling/detiling in formats crate; some render-target metadata missing | RPF9, BCPack, texture pools, model/audio extraction tools documented |
| Audio | XAudio2 path; XMA/Opus handling described | Menu/video/loading audio; XMA/Opus decode; reverb/Opus verification gaps stated | AWC Opus/XMA2 export and decode tooling |
| Input | XInput and keyboard/mouse mapping | XInput and keyboard-as-pad | GameInput shim via SDL3 |
| Diagnostics | Detailed report with imports, called stubs, environment, shaders, D3D12, audio, runtime and VFS | Crash logs, trace controls, shader/frame capture and GPU diagnostics | Runtime traces, GPU tests, progress dashboard and extensive issue/PR activity |
| Synthetic tests | Unit, end-to-end test title and optional GPU tests | Workspace tests and stand-in HLE fixture | Stand-in loader test and GPU test suite |
| Real GTA VI evidence in inspected docs | Not claimed | README reports menus and world loading, but incomplete scene rendering and a GPU hang/reset warning | README's hand-written status says no boot; current issue activity discusses real retail startup blockers and measured boot traces. Treat README status as stale/ambiguous pending commit-specific validation. |

## Source-level observations

### XCL

At the audited commit, `crates/xcl/src/hle/d3d12x/mod.rs` exposes a real host-D3D12 backend and a null fallback. The null backend is explicitly documented as rendering nothing. Its `report.json` model records import resolution, called stubs, environment checks, VFS state, shader formats, DXC, D3D12, audio, XGameRuntime and DirectStorage statistics.

**Integration opportunity:** adapt the report's evidence fields into this repository's normalized report schema. Do not import XCL runtime code into a GPL-3.x runtime.

### VIctory

At the audited commit, `victory-loader` prepares a lightly patched image, maps it through the Windows loader for TLS/unwind behavior, resolves imports through HLE/host/title DLLs and routes unresolved calls to generated stubs. The D3D12.X shim delegates device/resource behavior to `victory-gpu`. The shader emitter targets host DXIL at shader model 6.6.

Its README reports that menus and loading work but the world is mostly missing, frames take seconds, and a real-GPU attempt can hang/reset the display driver. Treat that as a real risk, not as an instruction to test on the user's main PC.

**Integration opportunity:** use VIctory as the first GTA VI startup candidate for independent build/test comparison. Its logs and stage evidence need a neutral adapter; do not transplant the loader or graphics code.

### Leonida

The inspected README describes a Vulkan-backed D3D12.X layer, RDNA2-to-SPIR-V translation, Wave64 handling and asset pipelines. It also distinguishes translation from validation and GPU pipeline creation. The README's top-level status says the title does not boot, but recent public issue activity references a retail startup blocker and traces that progress through specific runtime calls. The hand-written status table is therefore not sufficient evidence of the current boot state.

**Integration opportunity:** study the Vulkan feature matrix, GPU test results, shader translation contract and asset-format research independently. Do not infer that all translated shaders render correctly or that the project is playable.

## Comparison decisions

1. **Do not merge runtimes now.** Their graphics backends and loader designs differ, and the license boundary is material.
2. **Build a common evidence adapter first.** XCL already has a detailed structured report; the other projects can be mapped into the same stage model without sharing implementation code.
3. **Use synthetic fixtures before title data.** This avoids long builds and protects user data while testing the report pipeline and host capabilities.
4. **Measure the RX 6600.** No inspected upstream evidence establishes the user's exact GPU/driver feature set or performance.
