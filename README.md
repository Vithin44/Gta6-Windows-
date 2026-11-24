# GTA VI Windows Research

Independent research and compatibility-engineering workspace.

## Objective

Study public research and independently developed Xbox Series compatibility projects to investigate lawful, reproducible Windows startup and rendering experiments.

This repository does not include Rockstar Games executables, game assets, proprietary source code, authentication tokens, or other copyrighted game files.

## Current direction

We are building an evidence and integration layer around three independent upstream projects:

- **[VIctory](https://github.com/Marvisak/VIctory)** — GTA VI-specific Windows/D3D12 runtime research.
- **[Leonida](https://github.com/ProjectLeonida/Leonida)** — GTA VI-specific Vulkan, shader, asset-format and runtime research.
- **[XCL](https://github.com/ivall/xcl)** — general Xbox Series compatibility-layer research.

The projects remain separate. Their code is not being blindly copied or combined: XCL declares GPL-2.0-only, while VIctory and Leonida declare GPL-3.x licenses. See [the upstream audit](docs/UPSTREAMS.md).

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

The repository now contains an upstream audit, a source-level feature matrix, an integration architecture, a staged execution plan, contribution rules, an upstream manifest, a normalized run-report schema and a read-only Windows host probe. GitHub Actions has compiled the native CPU/D3D12 probe and validated the PowerShell syntax and synthetic report.

The host probe has not yet been run on the target PC. No GTA VI launch or gameplay has been performed by this repository. Upstream status statements are attributed to their respective projects and are not our own test results.

## Roadmap

1. Finish revision-pinned source and license audits.
2. Build a read-only Windows capability probe for the target PC.
3. Add independent upstream checkouts and reproducible synthetic builds/tests.
4. Normalize test reports and compare loader/graphics behavior.
5. Evaluate authorized local-data workflows only where supported by the upstream projects.
6. Track runtime startup, rendering and gameplay as separate evidence gates.

See [docs/INTEGRATION_PLAN.md](docs/INTEGRATION_PLAN.md) for milestone exit criteria.

## Repository map

- [docs/UPSTREAMS.md](docs/UPSTREAMS.md) — project comparison, licenses, revisions and audit gaps.
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — proposed independent integration architecture.
- [docs/INTEGRATION_PLAN.md](docs/INTEGRATION_PLAN.md) — milestones, blockers and evidence gates.
- [docs/FEATURE_MATRIX.md](docs/FEATURE_MATRIX.md) — source-level comparison of the three upstreams.
- [docs/HOST_PROBE.md](docs/HOST_PROBE.md) — how to collect a read-only Windows hardware inventory.
- [CONTRIBUTING.md](CONTRIBUTING.md) — security, provenance and contribution rules.
- [manifests/upstreams.json](manifests/upstreams.json) — machine-readable upstream records.
- [schemas/run-report.schema.json](schemas/run-report.schema.json) — normalized test-report schema.

## Hardware target

The user has reported an AMD Ryzen 5 5500, Radeon RX 6600, 16 GB RAM and a 1 TB SATA SSD. These are unverified starting details, not a compatibility verdict. The actual Windows build, driver, API features, available committed memory and free disk space must be measured before selecting a runtime or starting a large build.

## License

No license has yet been selected for original software in this repository. Upstream licenses apply only to their respective projects and covered material.
