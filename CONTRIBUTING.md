# Contributing

Thanks for helping with the GTA VI Windows research workspace.

This repository is an independent compatibility-engineering and evidence project. It does not distribute the game or replace the upstream projects.

## Ground rules

1. **Do not upload game data.** Never commit executables, game packages, keys, proprietary source, extracted assets, saves, shader dumps, crash dumps containing game memory, or generated runtime data derived from the game.
2. **Do not bypass access controls.** No DRM, authentication, anti-cheat, encryption or license-check bypasses; no online-service impersonation.
3. **Preserve upstream projects.** Do not push changes to XCL, VIctory or Leonida from this repository. Work in our own tools/docs or a clearly identified fork only when permitted.
4. **Audit before copying.** Record the exact upstream commit, source file, author/provenance, license and third-party notices before reusing any code or data.
5. **Do not combine incompatible licenses.** XCL declares GPL-2.0-only; VIctory declares GPL-3.0-or-later; Leonida declares GPL-3.0. Treat these as incompatible for one combined derivative unless explicit additional permission resolves the issue.
6. **Do not overstate results.** Distinguish build success, process launch, loader initialization, menu presentation, world loading, scene rendering and playable gameplay.
7. **Treat binaries as untrusted.** Do not execute unknown or leaked executables on a primary machine. Prefer reproducible builds from pinned public source and isolated test environments.
8. **Keep reports reproducible.** Record exact revisions, commands, toolchain versions, host/driver details, exit codes and logs. Record skips and failures as well as passes.

## Safe contributions

- Documentation and source comparison with citations.
- License and provenance inventories.
- Read-only host capability probes.
- Synthetic PE, shader, filesystem and graphics fixtures that contain no proprietary game data.
- JSON report schemas and validators.
- Tests using project-owned synthetic fixtures.
- Bug reports that describe reproducible behavior without attaching copyrighted files or secrets.

## Before opening a change

- Check whether the relevant upstream already has an implementation or open pull request.
- Link to the exact upstream commit or issue.
- Explain whether the contribution is original code, factual research, generated material or adapted code.
- Add tests before changing behavior.
- Keep user-specific absolute paths and usernames out of committed logs.
- Ensure generated files and local work directories are ignored.

## Evidence format

A useful test report includes:

- upstream and full commit SHA;
- clean/dirty checkout state;
- operating system and build;
- CPU, RAM/commit and GPU/driver;
- exact test command and tool versions;
- whether the input was a synthetic fixture or user-owned local data;
- exit code, duration, pass/fail/skip;
- stage reached and expected result;
- log/report path, with sensitive paths redacted.

Never attach game packages, extracted assets, keys, proprietary binaries, or memory dumps to issues or pull requests.

## Licensing note

The repository has not yet selected a license for its original software. Until that is decided, do not assume that the files here may be redistributed under an upstream project's license. This document is project policy, not legal advice.
