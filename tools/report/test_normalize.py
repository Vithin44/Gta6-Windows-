from __future__ import annotations

import json
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from normalize_upstream import normalize_victory, normalize_xcl, safe_log_reference


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
        run_start_utc=None,
    )


class NormalizeUpstreamTests(unittest.TestCase):
    def assert_valid_schema(self, report: dict) -> None:
        errors = sorted(VALIDATOR.iter_errors(report), key=lambda error: error.message)
        self.assertEqual([], [error.message for error in errors])

    def test_host_probe_is_mapped_into_normalized_host_fields(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "report.json"
            host = root / "host-probe.json"
            source.write_text(json.dumps({
                "xcl_version": "0.1.0",
                "title": "Synthetic Title",
                "crash": None,
                "exit_code": 0,
                "modules": [],
                "stubbed_imports": [],
                "called_stubs": [],
            }), encoding="utf-8")
            host.write_text(json.dumps({
                "operatingSystem": {"caption": "Windows 11", "buildNumber": "26100", "architecture": "64-bit"},
                "processors": [{"name": "AMD Ryzen 5 5500"}],
                "memory": {
                    "totalPhysicalBytes": 17179869184,
                    "freePhysicalMemoryKb": 8388608,
                    "availableMBytes": 8192,
                    "committedBytes": 8589934592,
                    "commitLimitBytes": 34359738368,
                },
                "cpuFeatures": {"avx2": True},
                "graphics": {
                    "adapters": [{"name": "AMD Radeon RX 6600", "driverVersion": "test-driver"}],
                    "d3d12": {
                        "queried": True,
                        "result": {
                            "cpu": {"avx2_hardware": True, "clwb": False},
                            "adapters": [{
                                "name": "AMD Radeon RX 6600",
                                "dedicated_video_memory_bytes": 8589934592,
                                "d3d12_available": True,
                                "shader_model": "6_7",
                                "wave_ops": True,
                                "wave_lane_min": 32,
                                "wave_lane_max": 64,
                                "mesh_shader_tier": "not_supported",
                            }],
                        },
                    },
                    "vulkan": {"queried": False},
                },
            }), encoding="utf-8")
            args = common_args(source, "xcl")
            args.host_report = host
            report = normalize_xcl(args)

            self.assertEqual("Windows 11", report["host"]["os"])
            self.assertEqual(16384, report["host"]["ram_total_mb"])
            self.assertEqual(8192, report["host"]["ram_free_mb"])
            self.assertEqual(8192, report["host"]["ram_available_mb"])
            self.assertEqual(8192, report["host"]["committed_mb"])
            self.assertEqual(32768, report["host"]["commit_limit_mb"])
            self.assertEqual(24576, report["host"]["commit_remaining_mb"])
            self.assertEqual("AMD Radeon RX 6600", report["host"]["gpu"])
            self.assertEqual(8192, report["host"]["gpu_vram_mb"])
            self.assertEqual("gfx1032", report["host"]["feature_checks"]["amd_gfx_target"])
            self.assertEqual("6_7", report["host"]["feature_checks"]["shader_model"])
            self.assertIn("avx2_hardware", report["host"]["cpu_features"])
            self.assert_valid_schema(report)

    def test_log_reference_rejects_absolute_and_parent_paths(self) -> None:
        with self.assertRaises(ValueError):
            safe_log_reference("C:\\private\\secret.log", Path("fallback.log"))
        with self.assertRaises(ValueError):
            safe_log_reference("../secret.log", Path("fallback.log"))

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

    def test_victory_can_ignore_old_appended_crash_records(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "crashes.log"
            console = Path(directory) / "console.txt"
            source.write_text(
                "unix time 1795521600, process 1234\n"
                "VIctory: unhandled exception 0xc0000005 at 0x12345678\n",
                encoding="utf-8",
            )
            console.write_text("mapped at 0x100000\n", encoding="utf-8")
            args = common_args(source, "victory")
            args.console_log = console
            args.run_start_utc = "2026-11-24T13:00:00Z"
            report = normalize_victory(args)

            self.assertEqual("unknown", report["result"]["status"])
            self.assertEqual("loader_initialized", report["result"]["stage_reached"])
            self.assertIsNone(report["result"]["crash_code"])
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
