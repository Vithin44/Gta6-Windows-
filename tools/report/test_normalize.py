from __future__ import annotations

import json
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from normalize_upstream import normalize_victory, normalize_xcl


ROOT = Path(__file__).resolve().parents[2]
SCHEMA = json.loads((ROOT / "schemas" / "run-report.schema.json").read_text(encoding="utf-8"))
VALIDATOR = Draft202012Validator(SCHEMA, format_checker=FormatChecker())


def common_args(source: Path, upstream: str) -> Namespace:
    return Namespace(
        upstream=upstream,
        source=source,
        input_class="synthetic_fixture",
        host_report=None,
        commit="0123456789abcdef0123456789abcdef01234567",
        run_id=f"test-{upstream}",
        timestamp="2026-11-24T12:00:00Z",
        command_label="synthetic test input",
        log_reference=None,
        privacy_reviewed=True,
        output=source.with_suffix(".normalized.json"),
        console_log=None,
    )


class NormalizeUpstreamTests(unittest.TestCase):
    def assert_valid_schema(self, report: dict) -> None:
        errors = sorted(VALIDATOR.iter_errors(report), key=lambda error: error.message)
        self.assertEqual([], [error.message for error in errors])

    def test_xcl_report_is_normalized_without_paths_or_raw_crash_text(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "report.json"
            source.write_text(json.dumps({
                "xcl_version": "0.1.0",
                "title": "Synthetic Title",
                "exe": "C:/private/user/game.exe",
                "crash": None,
                "exit_code": 0,
                "modules": [{"name": "synthetic.exe", "base": "0x1000", "size": "0x2000"}],
                "stubbed_imports": [{"dll": "synthetic.dll", "function": "Missing"}],
                "called_stubs": [{"dll": "synthetic.dll", "function": "Missing", "calls": 2}],
                "notes": ["synthetic note"],
            }), encoding="utf-8")
            report = normalize_xcl(common_args(source, "xcl"))

            self.assertEqual("passed", report["result"]["status"])
            self.assertEqual("loader_initialized", report["result"]["stage_reached"])
            self.assertNotIn("C:/private/user/game.exe", json.dumps(report))
            self.assertIsNotNone(report["upstream"]["commit"])
            self.assert_valid_schema(report)

    def test_xcl_crash_is_failed_and_raw_crash_is_not_copied(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "report.json"
            source.write_text(json.dumps({
                "xcl_version": "0.1.0",
                "title": "Synthetic Title",
                "exe": "D:/private/game.exe",
                "crash": "0xc0000005 at D:/private/game.exe",
                "exit_code": None,
                "modules": [],
            }), encoding="utf-8")
            report = normalize_xcl(common_args(source, "xcl"))

            self.assertEqual("failed", report["result"]["status"])
            self.assertEqual("0xc0000005", report["result"]["crash_code"])
            self.assertNotIn("D:/private/game.exe", json.dumps(report))
            self.assert_valid_schema(report)

    def test_victory_crash_log_and_loader_marker_are_conservative(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "crashes.log"
            console = Path(directory) / "console.txt"
            source.write_text(
                "unix time 1795521600, process 1234\n"
                "unhandled exception 0xc0000005 at 0x12345678\n",
                encoding="utf-8",
            )
            console.write_text("mapped at 0x100000 (preferred 0x400000)\n", encoding="utf-8")
            args = common_args(source, "victory")
            args.console_log = console
            report = normalize_victory(args)

            self.assertEqual("failed", report["result"]["status"])
            self.assertEqual("loader_initialized", report["result"]["stage_reached"])
            self.assertEqual("0xc0000005", report["result"]["crash_code"])
            self.assertNotIn("0x12345678", json.dumps(report))
            self.assert_valid_schema(report)

    def test_victory_without_evidence_does_not_claim_a_boot(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "crashes.log"
            source.write_text("", encoding="utf-8")
            args = common_args(source, "victory")
            report = normalize_victory(args)

            self.assertEqual("unknown", report["result"]["status"])
            self.assertEqual("not_started", report["result"]["stage_reached"])
            self.assert_valid_schema(report)


if __name__ == "__main__":
    unittest.main()
