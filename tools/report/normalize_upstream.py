#!/usr/bin/env python3
"""Normalize upstream diagnostic exports without copying raw paths or log contents.

This tool is deliberately conservative: counters and log presence do not prove
that a menu, world, rendered scene, or playable session was reached.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path, PureWindowsPath
from typing import Any


REPOSITORIES = {
    "xcl": "https://github.com/ivall/xcl",
    "victory": "https://github.com/Marvisak/VIctory",
    "leonida": "https://github.com/ProjectLeonida/Leonida",
}
INPUT_CLASSES = (
    "synthetic_fixture",
    "public_sample",
    "user_owned_local_data",
    "host_probe",
)


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except OSError as exc:
        raise ValueError(f"cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def first_dict(items: Any) -> dict[str, Any]:
    if isinstance(items, list):
        for item in items:
            if isinstance(item, dict):
                return item
    return {}


def host_record(host_path: Path | None) -> dict[str, Any]:
    if host_path is None:
        return {
            "os": "unknown",
            "architecture": "unknown",
            "cpu_features": [],
            "graphics_api": "unknown",
            "feature_checks": {},
        }

    source = read_json(host_path)
    os_info = source.get("operatingSystem") or {}
    processors = source.get("processors") or []
    cpu_info = first_dict(processors)
    memory = source.get("memory") or {}
    graphics = source.get("graphics") or {}
    wmi_gpu = first_dict(graphics.get("adapters"))
    d3d12 = graphics.get("d3d12") or {}
    native = d3d12.get("result") or {}
    native_cpu = native.get("cpu") or {}
    native_gpu = first_dict(native.get("adapters"))

    cpu_features: list[str] = []
    basic_avx2 = (source.get("cpuFeatures") or {}).get("avx2")
    if basic_avx2 is True:
        cpu_features.append("avx2")
    elif basic_avx2 is False:
        cpu_features.append("avx2=unsupported")
    for key, value in native_cpu.items():
        if key in {"brand", "vendor"}:
            continue
        if value is True:
            cpu_features.append(key.lower())
        elif value is False:
            cpu_features.append(f"{key.lower()}=unsupported")

    feature_checks: dict[str, Any] = {}
    for key in (
        "d3d12_available",
        "amd_gfx_target",
        "shader_model",
        "wave_ops",
        "wave_lane_min",
        "wave_lane_max",
        "mesh_shader_tier",
    ):
        value = native_gpu.get(key)
        if isinstance(value, (bool, int, float, str)) or value is None:
            feature_checks[key] = value

    total_ram = memory.get("totalPhysicalBytes")
    free_ram_kb = memory.get("freePhysicalMemoryKb")
    available_ram_mb = memory.get("availableMBytes")
    committed_bytes = memory.get("committedBytes")
    commit_limit_bytes = memory.get("commitLimitBytes")
    vram_bytes = native_gpu.get("dedicated_video_memory_bytes")
    if not isinstance(vram_bytes, (int, float)):
        vram_bytes = wmi_gpu.get("adapterRamReportedBytes")
    driver = wmi_gpu.get("driverVersion")
    if d3d12.get("queried") is True:
        graphics_api = "d3d12"
    elif (graphics.get("vulkan") or {}).get("queried") is True:
        graphics_api = "vulkan"
    else:
        graphics_api = "unknown"

    result: dict[str, Any] = {
        "os": os_info.get("caption") or "unknown",
        "os_build": str(os_info.get("buildNumber")) if os_info.get("buildNumber") is not None else None,
        "architecture": os_info.get("architecture") or "unknown",
        "cpu": cpu_info.get("name") or native_cpu.get("brand"),
        "cpu_features": sorted(set(cpu_features)),
        "ram_total_mb": int(total_ram // (1024 * 1024)) if isinstance(total_ram, (int, float)) else None,
        "ram_free_mb": int(free_ram_kb // 1024) if isinstance(free_ram_kb, (int, float)) else None,
        "ram_available_mb": int(available_ram_mb) if isinstance(available_ram_mb, (int, float)) else None,
        "committed_mb": int(committed_bytes // (1024 * 1024)) if isinstance(committed_bytes, (int, float)) else None,
        "commit_limit_mb": int(commit_limit_bytes // (1024 * 1024)) if isinstance(commit_limit_bytes, (int, float)) else None,
        "commit_remaining_mb": (
            int(max(0, commit_limit_bytes - committed_bytes) // (1024 * 1024))
            if isinstance(commit_limit_bytes, (int, float)) and isinstance(committed_bytes, (int, float))
            else None
        ),
        "gpu": native_gpu.get("name") or wmi_gpu.get("name"),
        "gpu_driver": str(driver) if driver is not None else None,
        "gpu_vram_mb": int(vram_bytes // (1024 * 1024)) if isinstance(vram_bytes, (int, float)) else None,
        "graphics_api": graphics_api,
        "feature_checks": feature_checks,
    }
    return result


def safe_log_reference(value: str | None, fallback: Path) -> str:
    candidate = Path(value) if value else Path(fallback.name)
    windows_candidate = PureWindowsPath(value) if value else PureWindowsPath(fallback.name)
    if (
        candidate.is_absolute()
        or windows_candidate.is_absolute()
        or ".." in candidate.parts
        or ".." in windows_candidate.parts
        or (windows_candidate.drive and not windows_candidate.root)
    ):
        raise ValueError("log reference must be a relative path without '..' or a drive prefix")
    return candidate.as_posix()


def validate_commit(value: str | None) -> str | None:
    if value is None:
        return None
    if not re.fullmatch(r"[0-9a-fA-F]{40}", value):
        raise ValueError("--commit must be a full 40-character hexadecimal SHA")
    return value.lower()


def base_report(
    *,
    upstream: str,
    input_class: str,
    source_path: Path,
    host_path: Path | None,
    commit: str | None,
    run_id: str | None,
    timestamp: str | None,
    command_label: str,
    log_reference: str | None,
    privacy_reviewed: bool,
) -> dict[str, Any]:
    if input_class not in INPUT_CLASSES:
        raise ValueError(f"--input-class must be one of: {', '.join(INPUT_CLASSES)}")
    when = timestamp or utc_now()
    try:
        parsed_time = datetime.fromisoformat(when.replace("Z", "+00:00"))
        if parsed_time.tzinfo is None:
            raise ValueError("timestamp has no timezone")
        if "T" not in when:
            raise ValueError("timestamp has no time component")
    except ValueError as exc:
        raise ValueError("--timestamp must be a timezone-aware ISO 8601 date-time") from exc
    generated_id = run_id or f"{upstream}-{source_path.stem}-{when.replace(':', '').replace('-', '')}"
    return {
        "schema_version": 1,
        "run_id": generated_id,
        "timestamp_utc": when,
        "upstream": {
            "id": upstream,
            "repository": REPOSITORIES[upstream],
            "commit": validate_commit(commit),
            "working_tree_clean": None,
            "build_configuration": None,
        },
        "host": host_record(host_path),
        "test": {
            "name": f"{upstream.upper()} imported diagnostic",
            "input_class": input_class,
            "command": command_label,
            "tool_versions": {},
            "duration_ms": None,
        },
        "result": {
            "status": "unknown",
            "exit_code": None,
            "stage_reached": "not_started",
            "summary": "",
            "warnings": [],
            "errors": [],
            "crash_code": None,
            "log_reference": safe_log_reference(log_reference, source_path),
        },
        "privacy_reviewed": bool(privacy_reviewed),
    }


def normalize_xcl(args: argparse.Namespace) -> dict[str, Any]:
    source = read_json(args.source)
    report = base_report(
        upstream="xcl",
        input_class=args.input_class,
        source_path=args.source,
        host_path=args.host_report,
        commit=args.commit,
        run_id=args.run_id,
        timestamp=args.timestamp,
        command_label=args.command_label or "Imported XCL report.json; original run command not captured",
        log_reference=args.log_reference,
        privacy_reviewed=args.privacy_reviewed,
    )

    modules = source.get("modules") if isinstance(source.get("modules"), list) else []
    called_stubs = source.get("called_stubs") if isinstance(source.get("called_stubs"), list) else []
    stubbed_imports = source.get("stubbed_imports") if isinstance(source.get("stubbed_imports"), list) else []
    crash = source.get("crash")
    crash_present = isinstance(crash, str) and bool(crash.strip())
    exit_code = source.get("exit_code")
    if not isinstance(exit_code, int):
        exit_code = None

    if crash_present or (exit_code is not None and exit_code != 0):
        status = "failed"
    elif exit_code == 0:
        status = "passed"
    else:
        status = "unknown"

    if modules:
        stage = "loader_initialized"
    elif source.get("title") or source.get("exe"):
        stage = "process_started"
    else:
        stage = "not_started"

    crash_match = re.search(r"0x[0-9a-fA-F]{8}", crash or "")
    version = source.get("xcl_version") or "unknown"
    title = source.get("title") or "title not identified"
    summary = (
        f"XCL {version}; {len(modules)} mapped modules; "
        f"{len(stubbed_imports)} statically stubbed imports; "
        f"{len(called_stubs)} runtime stub entries. Title: {title}. "
        "No visual stage is inferred from counters."
    )
    warnings = [
        "This adapter intentionally omits executable paths, module addresses and raw crash text.",
        "Presentation counters do not prove that a scene rendered; no menu, world or gameplay stage is inferred.",
    ]
    if not args.timestamp:
        warnings.append("XCL report.json has no run timestamp; timestamp_utc is the normalization time unless --timestamp is supplied.")
    if called_stubs:
        warnings.append(f"XCL recorded {len(called_stubs)} runtime stub entries; inspect the original report locally.")
    if stubbed_imports:
        warnings.append(f"XCL recorded {len(stubbed_imports)} imports resolved to generated stubs.")
    errors = ["XCL recorded a crash; raw crash text was omitted for privacy."] if crash_present else []

    result = report["result"]
    result.update({
        "status": status,
        "exit_code": exit_code,
        "stage_reached": stage,
        "summary": summary,
        "warnings": warnings,
        "errors": errors,
        "crash_code": crash_match.group(0).lower() if crash_match else None,
    })
    report["test"]["tool_versions"] = {"xcl": str(version)}
    return report


def normalize_victory(args: argparse.Namespace) -> dict[str, Any]:
    crash_text = args.source.read_text(encoding="utf-8-sig", errors="replace")
    console_text = ""
    if args.console_log:
        console_text = args.console_log.read_text(encoding="utf-8-sig", errors="replace")
    run_start = None
    if args.run_start_utc:
        try:
            run_start = datetime.fromisoformat(args.run_start_utc.replace("Z", "+00:00"))
            if run_start.tzinfo is None or "T" not in args.run_start_utc:
                raise ValueError("timezone and time are required")
        except ValueError as exc:
            raise ValueError("--run-start-utc must be a timezone-aware ISO 8601 date-time") from exc

    if run_start is not None:
        sections = re.split(r"(?m)(?=^unix time \d+, process \d+\s*$)", crash_text)
        selected = []
        for section in sections:
            match = re.search(r"(?m)^unix time (\d+), process \d+\s*$", section)
            if match and datetime.fromtimestamp(int(match.group(1)), tz=timezone.utc) >= run_start:
                selected.append(section)
        crash_text = "".join(selected)

    combined = console_text + "\n" + crash_text

    report = base_report(
        upstream="victory",
        input_class=args.input_class,
        source_path=args.source,
        host_path=args.host_report,
        commit=args.commit,
        run_id=args.run_id,
        timestamp=args.timestamp,
        command_label=args.command_label or "Imported VIctory console/crash logs; original run command not captured",
        log_reference=args.log_reference,
        privacy_reviewed=args.privacy_reviewed,
    )

    mapped = "mapped at" in console_text.lower()
    exited = re.search(r"title exited with (-?\d+)", console_text, re.IGNORECASE)
    exit_code = int(exited.group(1)) if exited else None
    crash_present = bool(crash_text.strip())
    crash_match = re.search(r"0x[0-9a-fA-F]{8}", combined)

    if crash_present or (exit_code is not None and exit_code != 0):
        status = "failed"
    elif exit_code == 0:
        status = "passed"
    else:
        status = "unknown"

    if exited:
        stage = "runtime_initialized"
    elif mapped:
        stage = "loader_initialized"
    elif crash_present:
        stage = "process_started"
    else:
        stage = "not_started"

    unix_times = re.findall(r"unix time (\d+)", crash_text)
    if not args.timestamp and unix_times:
        stamp = datetime.fromtimestamp(int(unix_times[-1]), tz=timezone.utc)
        report["timestamp_utc"] = stamp.isoformat(timespec="seconds").replace("+00:00", "Z")

    warnings = [
        "VIctory's crash log and console output do not establish that a menu, world, scene or playable session was rendered.",
        "Raw log text, absolute paths, process IDs and memory addresses are not copied into the normalized report.",
    ]
    if not args.timestamp and not unix_times:
        warnings.append("No run timestamp was present; timestamp_utc is the normalization time unless --timestamp is supplied.")
    if crash_present and not args.run_start_utc:
        warnings.append("VIctory appends crash records; confirm this input is a run-specific copy or supply --run-start-utc to exclude older records.")
    errors = ["VIctory produced a crash log; raw crash text was omitted for privacy."] if crash_present else []
    report["result"].update({
        "status": status,
        "exit_code": exit_code,
        "stage_reached": stage,
        "summary": (
            f"Imported VIctory diagnostics; {len(crash_text.splitlines())} crash-log lines; "
            f"loader-mapped marker: {mapped}; title-exit marker: {bool(exited)}."
        ),
        "warnings": warnings,
        "errors": errors,
        "crash_code": crash_match.group(0).lower() if crash_match else None,
    })
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="upstream", required=True)
    for upstream in ("xcl", "victory"):
        sub = subparsers.add_parser(upstream)
        sub.add_argument("source", type=Path, help="XCL report.json or VIctory crashes.log")
        if upstream == "victory":
            sub.add_argument("--console-log", type=Path, help="optional captured VIctory console output")
            sub.add_argument("--run-start-utc", help="ignore appended crash-log entries older than this timezone-aware ISO 8601 time")
        sub.add_argument("--host-report", type=Path, help="optional Collect-HostInfo.ps1 JSON output")
        sub.add_argument("--commit", help="full 40-character upstream commit SHA")
        sub.add_argument("--run-id")
        sub.add_argument("--timestamp", help="ISO 8601 timestamp; defaults to current UTC")
        sub.add_argument("--input-class", required=True, choices=INPUT_CLASSES)
        sub.add_argument("--command-label")
        sub.add_argument("--log-reference", help="relative path to a local log copy; defaults to the source filename")
        sub.add_argument("--privacy-reviewed", action="store_true")
        sub.add_argument("--output", type=Path, required=True, help="normalized JSON output path")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        normalized = normalize_xcl(args) if args.upstream == "xcl" else normalize_victory(args)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(normalized, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Normalized report written to {args.output}")
        print(f"Status: {normalized['result']['status']}; stage: {normalized['result']['stage_reached']}")
        if not normalized["privacy_reviewed"]:
            print("Review the output for privacy before sharing it.")
        return 0
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
