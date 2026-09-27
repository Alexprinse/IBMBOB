"""Ruff verifier — runs ruff and captures structured evidence."""
from __future__ import annotations

import json
import subprocess
from typing import Any

from proofloop.schemas.verification_evidence import RuffEvidence


def run_ruff(paths: list[str] | None = None) -> RuffEvidence:
    """Run ruff check on the given paths and return structured evidence."""
    check_paths = paths or ["proofloop", "checkoutlab"]

    cmd = [
        "python", "-m", "ruff", "check",
        *check_paths,
        "--output-format=json",
    ]

    proc = subprocess.run(  # noqa: S603
        cmd,
        capture_output=True,
        text=True,
    )

    raw_output = (proc.stdout + proc.stderr).strip()
    violations = _parse_violations(proc.stdout)

    return RuffEvidence(
        exit_code=proc.returncode,
        violation_count=len(violations),
        violations=violations,
        raw_output=raw_output,
    )


def _parse_violations(stdout: str) -> list[dict[str, Any]]:
    """Parse ruff JSON output into a list of violation dicts."""
    if not stdout.strip():
        return []
    try:
        data = json.loads(stdout)
        if isinstance(data, list):
            return [
                {
                    "filename": v.get("filename", ""),
                    "row": v.get("location", {}).get("row", 0),
                    "col": v.get("location", {}).get("column", 0),
                    "code": v.get("code", ""),
                    "message": v.get("message", ""),
                }
                for v in data
            ]
    except json.JSONDecodeError:
        pass
    return []
