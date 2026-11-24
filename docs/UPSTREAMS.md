# Upstream project audit

**Audit date:** 2026-11-24  
**Scope:** public repository metadata and documentation only. No upstream source has been copied, built, or executed.

## Executive summary

These projects overlap in their target platform and Xbox Series compatibility work, but they are not interchangeable modules. They use different graphics paths, have different maturity claims, and carry incompatible copyleft licenses for a single combined derivative.

| Project | Declared license | Main approach | GTA VI status stated by upstream | Audit disposition |
|---|---|---|---|---|
| [XCL](https://github.com/ivall/xcl) | GPL-2.0-only | Native x64 execution; Xbox services/HLE; D3D12.X-to-host-D3D12; RDNA2-to-HLSL/DXIL | General Xbox Series compatibility layer. Its README reports other retail-title results; issue #646 separately reports GTA VI reaching the language screen/loading art before world-loading failure. | Independent reference/runtime candidate; no code import. |
| [VIctory](https://github.com/Marvisak/VIctory) | GPL-3.0-or-later | Native x64 loader; HLE; D3D12.X-to-host-D3D12; RDNA2-to-DXIL | README dated 2026-11-23 reports menus and loading into the world, but most world rendering is missing and the project is not playable. | Strongest documented GTA VI boot/rendering lead in this audit; investigate as a standalone upstream. |
| [Leonida](https://github.com/ProjectLeonida/Leonida) | GPL-3.0 | Native recompilation; Xbox services; D3D12-to-Vulkan; RDNA2-to-SPIR-V | README says no playable game and lists boot as not working, while current issue/PR activity discusses retail startup blockers and runtime validation. Its hand-written status table may lag development. | Important GTA VI-specific shader, asset, Vulkan and test research; verify current main before relying on status. |

## Revision records

Revisions are immutable commit identifiers where the GitHub connector exposed them. Do not silently replace these with a moving branch name.

| Project | Branch | Audited revision | Evidence |
|---|---|---|---|
| XCL | `main` | `64b3f35599bb7102f55d640e1a791e7d6dd3b175` | GitHub commit search, 2026-11-24; README, Cargo.toml, LICENSE, HANDOFF.md, design document and THIRD_PARTY.md fetched from main. |
| VIctory | `main` | `d2a4bae1f49533ef5cb512fd1b1ba1513f2e1989` | GitHub commit search, 2026-11-24; README, Cargo.toml, LICENSE and docs/architecture.md fetched from main. |
| Leonida | `main` | **Not pinned yet** | Public GitHub page and current README were inspected. The GitHub connector returned 404 for repository metadata/content, so an exact SHA and raw LICENSE file could not be independently captured through that interface. GitHub page declares GPL-3.0. |

Before importing or pinning any source, refresh all three revisions and inspect their complete license and third-party notices. A branch can change after this audit.

## Technical comparison

### XCL

- Rust workspace; `Cargo.toml` declares `GPL-2.0-only`.
- Its own design document describes a general Xbox Series X|S compatibility layer, not a GTA VI port.
- Uses a PE loader, data-driven import resolver, HLE modules, virtual filesystem with copy-on-write overlay, and a report of unresolved/stubbed calls.
- Its README describes D3D12.X graphics on host D3D12 and RDNA2 shader recompilation to HLSL/DXIL.
- The README explicitly distinguishes presentation counters from proof of visible rendering.
- Issue [#646](https://github.com/ivall/xcl/issues/646) reports GTA VI 1.0.2.1 reaching the language screen and rendering loading art on an RTX 3060 12 GB, then failing during world loading after memory growth (reported peak commit: 36 GB). This is an issue report, not a result independently reproduced here.
- The handoff/design notes document a development/test environment with an RX 9070; this is not evidence that the same performance or feature coverage exists on an RX 6600.
- `THIRD_PARTY.md` lists additional provenance and compatibility constraints. In particular, it says GPL-3.0 and LGPL-3.0 code cannot be incorporated into this GPL-2.0-only project.

### VIctory

- Rust workspace; `Cargo.toml` declares `GPL-3.0-or-later`, Rust 2024 edition and Rust 1.88 minimum.
- Its architecture separates PE loading, HLE, GPU, shader translation, formats, pipeline/cache and GTA VI-specific code.
- Its 2026-11-23 README reports first-boot screens, intro video, profile/saves and loading into the world. It also says the world is mostly dark, many shaders are not translated, frames are very slow, and entering the world on a real GPU can hang/reset the display driver.
- The README reports testing on Windows 11 with an RX 6700 XT. That does not establish compatibility with every RDNA2 GPU.
- The README says several GiB of available Windows commit are needed. Its diagnostic WARP mode is a software-rendering fallback, not a performance solution.
- Current issues report illegal-instruction crashes on CPUs missing CLWB, CLZERO, MONITORX/MWAITX or SSE4A; issue #85 describes a proposed compatibility/emulation approach for an Intel host. The user's Ryzen 5 5500 officially lists AVX2 and SSE4A, but the remaining flags must be checked with CPUID before selecting a build.

### Leonida

- GitHub describes it as a GTA VI-specific native recompilation project.
- The README describes RDNA2-to-SPIR-V translation and an Xbox D3D12-to-Vulkan runtime.
- The README reports a large shader corpus translated and SPIR-V validation, but explicitly says shader translation and validation do not by themselves prove correct rendering.
- It reports an independent PE loader/import-shim stand-in test, but marks that path untested against the real executable in the README section inspected.
- The same README states that the project is not playable and lists boot as not working; current issue activity also discusses retail startup blockers. Treat this status as a potentially stale hand-written summary until a commit-specific test record resolves the discrepancy.
- The full asset-export path is documented as requiring roughly 400 GiB of free work space; the README says a reduced check/shader/runtime path can require around 30 GiB. These are upstream estimates, not guarantees for this machine.
- The project says it expects the user's own readable Xbox Series package and does not distribute game files or keys.

## License and integration constraints

1. XCL is GPL-2.0-only. VIctory is GPL-3.0-or-later. Leonida declares GPL-3.0.
2. GPL-2.0-only and GPL-3.0 are not automatically compatible for one combined derivative. Do not copy XCL code into a GPL-3.0 combined binary, or GPL-3.0 code into XCL, without an explicit compatible permission from every relevant rightsholder.
3. Separate repositories/processes and neutral report interchange may be a safer engineering boundary, but whether a particular arrangement is legally independent depends on its implementation and distribution. This document is not legal advice.
4. Third-party dependencies, generated tables, test vectors, submodules and copied snippets have their own terms. An upstream project's top-level license is not the entire provenance audit.
5. This research repository currently has no chosen software license. Do not assume that an upstream license automatically licenses this repository or its original material.

## Next audit tasks

- Obtain and pin Leonida's exact main commit and full license/provenance files.
- Compare current loader/import/HLE coverage using source-level evidence, not README claims alone.
- Compare shader translator test methodology and actual supported GPU features.
- Track CPU feature compatibility (AVX2, CLWB, CLZERO, MONITORX/MWAITX, SSE4A) separately from GPU compatibility.
- Inspect each project's CI workflows and test fixtures; separate tests requiring game data from tests that use synthetic fixtures.
- Record any upstream code considered for reuse as a file-level provenance entry with original path, commit, license and intended modifications.
- Keep all game executables, package files, keys, extracted assets, shader dumps and saves outside this repository.
