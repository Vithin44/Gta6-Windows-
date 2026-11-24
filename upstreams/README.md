# Upstream checkouts

The projects listed here are independent upstreams, not vendored dependencies.

## Current references

- XCL: https://github.com/ivall/xcl
- VIctory: https://github.com/Marvisak/VIctory
- Leonida: https://github.com/ProjectLeonida/Leonida

See `../manifests/upstreams.json` for the audit snapshot and license records.

## Checkout policy

1. Pin a full commit SHA from the audit manifest.
2. Clone each project into its own directory, outside this repository or as a separately managed submodule.
3. Keep build output, caches, game data and generated assets outside this repository.
4. Do not patch upstream checkouts from this project.
5. Do not copy source files into this repository until a file-level license/provenance review is complete.
6. Do not use a floating `main` branch as a reproducible test input.

No upstream source is currently vendored or initialized as a submodule here. This is intentional: the license and revision audit must be complete first.
