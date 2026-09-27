"""Mypy verifier — runs mypy and captures structured evidence."""
from __future__ import annotations

import subprocess
import sys

from proofloop.schemas.verification_evidence import MypyEvidence


def run_mypy(paths: list[str] | None = None) -> MypyEvidence:
    """Run mypy on the given paths and return structured evidence."""
    check_paths = paths or ["proofloop", "checkoutlab"]

    cmd = [sys.executable, "-m", "mypy", *check_paths, "--ignore-missing-imports"]

    proc = subprocess.run(  # noqa: S603
        cmd,
        capture_output=True,
        text=True,
    )

    raw_output = proc.stdout + proc.stderr
    errors = _parse_errors(raw_output)

    return MypyEvidence(
        exit_code=proc.returncode,
        error_count=len(errors),
        errors=errors,
        raw_output=raw_output.strip(),
    )


def _parse_errors(output: str) -> list[str]:
    """Extract error lines from mypy output."""
    error_lines = []
    for line in output.splitlines():
        # mypy error lines look like:  path/to/file.py:42: error: ...
        if ": error:" in line:
            error_lines.append(line.strip())
    return error_lines
