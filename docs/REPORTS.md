# Normalized run reports

The repository uses one versioned JSON schema for evidence imported from independently maintained projects. The adapters do not change upstream output and do not copy raw executable paths, process IDs, memory addresses or log contents into the normalized report.

## Validate a report

Install the small Python dependency set once:

```powershell
python -m pip install -r tools/report/requirements.txt
```

Validate a normalized report:

```powershell
python tools/report/validate_report.py path\to\normalized-report.json
```

## Import an XCL report

XCL writes a structured `report.json`. Copy it to a local folder outside this repository, then run:

```powershell
python tools/report/normalize_upstream.py xcl "D:\logs\xcl\report.json" --input-class user_owned_local_data --output "D:\logs\normalized-xcl.json"
```

Supply `--commit` with the full 40-character XCL commit when known. Use `--host-report` to attach the output of the Windows host probe.

The adapter maps the exit/crash state and module/stub counts. It deliberately does not treat frame counters as proof of a visible scene. XCL's report has no run timestamp; pass `--timestamp` if you know when the run happened, otherwise the adapter records the normalization time and adds a warning.

## Import VIctory logs

VIctory writes `crashes.log` when a crash or panic is reported. If you also saved the console output, provide both files:

```powershell
python tools/report/normalize_upstream.py victory "D:\logs\victory\crashes.log" --console-log "D:\logs\victory\console.txt" --run-start-utc "2026-11-24T13:00:00Z" --input-class user_owned_local_data --output "D:\logs\normalized-victory.json"
```

The adapter recognizes explicit loader mapping and title-exit markers. If no crash timestamp is present, pass `--timestamp` for the run time. VIctory appends to its crash log, so use a run-specific copy or provide `--run-start-utc` to ignore older entries. A crash log alone proves only that the run produced a crash report; it does not prove which visual stage was reached.

## Input classification

Every import requires one of these labels:

- `synthetic_fixture`: test data created without a game package.
- `public_sample`: a publicly distributable sample that does not contain proprietary game data.
- `user_owned_local_data`: output from a local run using data the user is authorized to access.
- `host_probe`: a system capability inventory.

Never upload game packages, keys, extracted assets, generated shaders, saves or full unredacted logs to this repository.

## Evidence rules

The normalizer uses conservative stage labels:

- `loader_initialized` requires an explicit mapped-module record (XCL) or mapped-image console marker (VIctory).
- `runtime_initialized` is used only when VIctory prints its title-exit marker after execution.
- Neither adapter infers `menu_presented`, `world_loaded`, `scene_rendered` or `playable` from counters, a process exit, or the absence of a crash.
- Unknown values remain unknown. Do not replace missing evidence with assumptions.

Review the generated JSON before sharing it. `privacy_reviewed` remains false unless the caller explicitly supplies `--privacy-reviewed`.
