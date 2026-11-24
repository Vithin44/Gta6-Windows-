from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "manifests" / "upstreams.json"
SUBMODULES = {
    "xcl": ROOT / "upstreams" / "xcl",
    "victory": ROOT / "upstreams" / "victory",
}


def git(*args: str, cwd: Path = ROOT) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def normalized_url(value: str) -> str:
    return value.removesuffix(".git").rstrip("/").lower()


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    records = {item["id"]: item for item in manifest["upstreams"]}

    status = git("submodule", "status", "--recursive").splitlines()
    if any(line.startswith(("-", "+", "U")) for line in status):
        raise RuntimeError("A submodule is uninitialized, modified, or conflicted.")

    for upstream_id, path in SUBMODULES.items():
        record = records[upstream_id]
        expected_commit = record.get("commit")
        if not expected_commit:
            raise RuntimeError(f"{upstream_id} has no immutable commit in the manifest.")

        actual_commit = git("rev-parse", "HEAD", cwd=path)
        if actual_commit.lower() != expected_commit.lower():
            raise RuntimeError(
                f"{upstream_id} commit mismatch: expected {expected_commit}, got {actual_commit}"
            )

        actual_url = git("remote", "get-url", "origin", cwd=path)
        expected_url = record["repository"]
        if normalized_url(actual_url) != normalized_url(expected_url):
            raise RuntimeError(
                f"{upstream_id} URL mismatch: expected {expected_url}, got {actual_url}"
            )

        print(f"{upstream_id}: {actual_commit} verified ({actual_url})")

    print("All initialized upstream submodules match the manifest.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (KeyError, OSError, subprocess.CalledProcessError, RuntimeError, ValueError) as error:
        print(f"submodule validation failed: {error}", file=sys.stderr)
        raise SystemExit(1)
