# Upstream checkouts

XCL and VIctory are pinned here as Git submodules. They remain independent upstream projects with their own histories and licenses.

## Initialized submodules

| Path | Upstream | Pinned commit | License |
|---|---|---|---|
| `upstreams/xcl` | https://github.com/ivall/xcl | `d208e14b765f469f4b56301b78afa8dac5378339` | GPL-2.0-only |
| `upstreams/victory` | https://github.com/Marvisak/VIctory | `d2a4bae1f49533ef5cb512fd1b1ba1513f2e1989` | GPL-3.0-or-later |

Initialize both with `git submodule update --init --recursive`, or clone the repository with `--recurse-submodules`.

## Other audited references

- Leonida: https://github.com/ProjectLeonida/Leonida — exact commit and complete dependency/license provenance still unpinned.
- DedSec: https://github.com/Hylanderry/DedSec — README-only candidate; direct source/API retrieval returned 404 and the MIT claim is unverified.

See `../manifests/upstreams.json` and `../docs/UPSTREAMS.md` for the audit snapshot and license records.

## Checkout policy

1. Keep each upstream in its own directory and preserve its immutable submodule commit.
2. Keep build output, caches, game data and generated assets outside this repository.
3. Do not patch upstream checkouts from this project.
4. Do not copy source files into this repository until a file-level license/provenance review is complete.
5. Do not use a floating `main` branch as a reproducible test input.
6. Do not combine GPL-2.0-only XCL and GPL-3.x VIctory code into one derivative without a separate legal compatibility review.

The submodule pointers make the sources available in one workspace without copying, rewriting or modifying either upstream.
