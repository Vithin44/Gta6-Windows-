# GTA VI Windows Research

[![Validate research artifacts](https://github.com/Vithin44/Gta6-Windows-/actions/workflows/validate-research.yml/badge.svg)](https://github.com/Vithin44/Gta6-Windows-/actions/workflows/validate-research.yml) [![Independent upstream smoke tests](https://github.com/Vithin44/Gta6-Windows-/actions/workflows/upstream-smoke.yml/badge.svg)](https://github.com/Vithin44/Gta6-Windows-/actions/workflows/upstream-smoke.yml)

Independent research and compatibility-engineering workspace.

## Objective

Study public research and independently developed Xbox Series compatibility projects to investigate lawful, reproducible Windows startup and rendering experiments.

This repository does not include Rockstar Games executables, game assets, proprietary source code, authentication tokens, or other copyrighted game files.

## Current direction

We are building an evidence and integration layer around three audited upstreams plus one preliminary candidate:

- **[VIctory](https://github.com/Marvisak/VIctory)** — GTA VI-specific Windows/D3D12 runtime research.
- **[Leonida](https://github.com/ProjectLeonida/Leonida)** — GTA VI-specific Vulkan, shader, asset-format and runtime research.
- **[XCL](https://github.com/ivall/xcl)** — general Xbox Series compatibility-layer research.
- **[DedSec](https://github.com/Hylanderry/DedSec)** — preliminary D3D12/DXIL and Xbox shim candidate; source and license currently unverified.

The projects remain separate. Their code is not being blindly copied or combined: XCL declares GPL-2.0-only, while VIctory and Leonida declare GPL-3.x licenses. DedSec's README claims MIT, but its LICENSE file could not be verified. See [the upstream audit](docs/UPSTREAMS.md) and [the preliminary DedSec audit](docs/DEDSEC_AUDIT.md).

## Working principles

- Preserve upstream projects and their licenses; review license compatibility before copying code.
- Record upstream URLs, exact revisions, licenses, and provenance.
- Prefer reproducible tests, logs, and documented findings over unsupported claims.
- Do not bypass DRM, authentication, anti-cheat, or other access controls.
- Treat unknown executables as untrusted; do not run them on a primary machine.
- Keep game packages, keys, extracted assets, saves and generated game data outside this repository.
- Distinguish process launch, loader initialization, menu presentation, world loading, scene rendering and playable gameplay.

## Project status

**Status:** research and architecture stage

The repository now contains an upstream audit, a source-level feature matrix, an integration architecture, a staged execution plan, contribution rules, a pinned upstream manifest where source access permits, a normalized run-report schema, XCL/VIctory report adapters and a read-only Windows host probe. GitHub Actions validates the synthetic report and adapter tests, parses the PowerShell script, and builds a downloadable Windows probe executable.

The latest completed no-title-data smoke run on hosted Windows Server 2025 is [run #6](https://github.com/Vithin44/Gta6-Windows-/actions/runs/45331424599): XCL **700 passed, 0 failed, 41 ignored** (86 GPU tests skipped for lack of Wave64 and 2 for lack of GPU UMA); VIctory **264 passed, 0 failed, 4 ignored** with one test thread. The earlier parallel VIctory run crashed in `victory-shader` with Windows `0xc0000005`; the single-threaded pass makes a concurrency-sensitive issue plausible but does not prove the cause. XCL's upstream main has since advanced to `d208e14b765f469f4b56301b78afa8dac5378339`; the next smoke run is pinned to that revision to test its new semantic shader-cache implementation. The latest host probe passed CI validation in [run #92](https://github.com/Vithin44/Gta6-Windows-/actions/runs/45332397931); download the [standalone Windows host-probe bundle](https://github.com/Vithin44/Gta6-Windows-/actions/runs/45332397931/artifacts/14892442322). It has not yet been run on the target PC. No GTA VI launch or gameplay has been performed by this repository.

## Roadmap

1. Re-run XCL at its current main revision and validate the semantic shader-cache change.
2. Finish the remaining Leonida revision and dependency/license audit; recheck DedSec source, LICENSE and submodules.
3. Run the Windows capability probe on the target PC.
4. Compare loader, D3D12, shader and memory requirements against the RX 6600 host report.
5. Evaluate authorized local-data workflows only where supported by an upstream.
6. Track process startup, menu, world loading, scene rendering and playable gameplay as separate evidence gates.

See [docs/INTEGRATION_PLAN.md](docs/INTEGRATION_PLAN.md) for milestone exit criteria.

## Getting the complete workspace

The repository pins XCL and VIctory as separate Git submodules. Clone with:

```powershell
git clone --recurse-submodules https://github.com/Vithin44/Gta6-Windows-.git
```

Or initialize them after a normal clone with `git submodule update --init --recursive`. The submodules preserve their own histories and licenses; they are not merged into one executable. Leonida and DedSec remain documented candidates until their exact source revisions and provenance can be verified.

## Repository map

- [docs/UPSTREAMS.md](docs/UPSTREAMS.md) — project comparison, licenses, revisions and audit gaps.
- [docs/CURRENT_UPSTREAM_STATUS.md](docs/CURRENT_UPSTREAM_STATUS.md) — current XCL/VIctory/DedSec progress, verified CI results and next test targets.
- [docs/DEDSEC_AUDIT.md](docs/DEDSEC_AUDIT.md) — preliminary DedSec claims, verification gaps and candidate components.
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — proposed independent integration architecture.
- [docs/INTEGRATION_PLAN.md](docs/INTEGRATION_PLAN.md) — milestones, blockers and evidence gates.
- [docs/FEATURE_MATRIX.md](docs/FEATURE_MATRIX.md) — source-level comparison of the three source-audited upstreams; DedSec is documented separately until its source is reachable.
- [docs/HOST_PROBE.md](docs/HOST_PROBE.md) — how to collect a read-only Windows hardware inventory.
- [docs/REPORTS.md](docs/REPORTS.md) — how to normalize and validate upstream diagnostic logs.
- [upstream smoke workflow](.github/workflows/upstream-smoke.yml) — isolated, pinned XCL and VIctory tests without title data.
- [CONTRIBUTING.md](CONTRIBUTING.md) — security, provenance and contribution rules.
- [manifests/upstreams.json](manifests/upstreams.json) — machine-readable upstream records.
- [schemas/run-report.schema.json](schemas/run-report.schema.json) — normalized test-report schema.

## Hardware target

The user has reported an AMD Ryzen 5 5500, Radeon RX 6600, 16 GB RAM and a 1 TB SATA SSD. These are unverified starting details, not a compatibility verdict. The actual Windows build, driver, API features, available committed memory and free disk space must be measured before selecting a runtime or starting a large build. XCL issue reports describe 36–40 GB commit growth during world loading on other systems, so 16 GB RAM is a significant risk. Leonida estimates about 30 GiB for a reduced check/shader/runtime build and about 400 GiB for its full asset stage; do not start the full stage without checking free space.

## License

No license has yet been selected for original software in this repository. Upstream licenses apply only to their respective projects and covered material.
