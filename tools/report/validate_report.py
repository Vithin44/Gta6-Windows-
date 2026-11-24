#!/usr/bin/env python3
"""Validate one project-owned run report against the repository JSON Schema."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise RuntimeError(f"cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"invalid JSON in {path}: {exc}") from exc


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate a normalized GTA VI Windows Research run report."
    )
    parser.add_argument("report", type=Path, help="JSON report to validate")
    parser.add_argument(
        "--schema",
        type=Path,
        default=Path(__file__).resolve().parents[2]
        / "schemas"
        / "run-report.schema.json",
        help="JSON Schema file (defaults to this repository's schema)",
    )
    args = parser.parse_args()

    try:
        schema = load_json(args.schema)
        report = load_json(args.report)
        try:
            from jsonschema import Draft202012Validator, FormatChecker
        except ImportError as exc:
            raise RuntimeError(
                "missing dependency: install tools/report/requirements.txt"
            ) from exc

        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(
            schema, format_checker=FormatChecker()
        )
        errors = sorted(
            validator.iter_errors(report),
            key=lambda error: (
                tuple(str(part) for part in error.absolute_path),
                error.message,
            ),
        )
        if errors:
            for error in errors:
                location = ".".join(str(part) for part in error.absolute_path)
                print(f"INVALID {location or '<root>'}: {error.message}")
            return 1

        print(f"VALID: {args.report}")
        return 0
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # keep unexpected validator errors visible
        print(f"ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
