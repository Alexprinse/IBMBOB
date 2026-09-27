"""Pytest verifier — runs pytest and captures structured evidence."""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

from proofloop.schemas.verification_evidence import PytestEvidence, TestResult


def run_pytest(test_paths: list[str] | None = None) -> PytestEvidence:
    """
    Run pytest with JSON report output and return a PytestEvidence object.

    Requires pytest-json-report to be installed for structured output;
    falls back to parsing stdout summary if the plugin is absent.
    """
    paths = test_paths or ["checkoutlab/tests"]
    report_file = Path(".proofloop") / "session" / "_pytest_report.json"
    report_file.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable, "-m", "pytest",
        *paths,
        "-v",
        "--tb=short",
        "--json-report",
        f"--json-report-file={report_file}",
        "--json-report-omit=collectors",
        "-q",
    ]

    start = time.monotonic()
    proc = subprocess.run(  # noqa: S603
        cmd,
        capture_output=True,
        text=True,
    )
    duration = time.monotonic() - start

    # Try to parse the JSON report
    if report_file.exists():
        try:
            return _parse_json_report(report_file, proc.returncode, duration)
        except Exception:  # noqa: S110 BLE001
            pass  # fall through to stdout parsing

    # Fallback: parse stdout summary line
    return _parse_stdout_summary(proc.stdout + proc.stderr, proc.returncode, duration)


def _parse_json_report(
    report_file: Path, exit_code: int, duration: float
) -> PytestEvidence:
    """Parse a pytest-json-report output file."""
    data = json.loads(report_file.read_text())
    summary = data.get("summary", {})
    tests_total = summary.get("total", 0)
    tests_passed = summary.get("passed", 0)
    tests_failed = summary.get("failed", 0)
    tests_errors = summary.get("error", 0)
    tests_skipped = summary.get("skipped", 0)
    report_duration = data.get("duration", duration)

    results: list[TestResult] = []
    for t in data.get("tests", []):
        results.append(
            TestResult(
                node_id=t.get("nodeid", ""),
                outcome=t.get("outcome", "unknown"),
                duration_seconds=t.get("duration", 0.0),
                failure_message=_extract_failure(t),
            )
        )

    raw_summary = _build_raw_summary(
        tests_total, tests_passed, tests_failed, tests_errors, tests_skipped
    )

    return PytestEvidence(
        exit_code=exit_code,
        tests_total=tests_total,
        tests_passed=tests_passed,
        tests_failed=tests_failed,
        tests_errors=tests_errors,
        tests_skipped=tests_skipped,
        duration_seconds=report_duration,
        results=results,
        raw_summary=raw_summary,
    )


def _parse_stdout_summary(
    output: str, exit_code: int, duration: float
) -> PytestEvidence:
    """Minimal fallback: count passed/failed from the pytest summary line."""
    passed = failed = errors = skipped = 0

    for line in reversed(output.splitlines()):
        line = line.strip()
        if "passed" in line or "failed" in line or "error" in line:
            import re

            for match in re.finditer(r"(\d+)\s+(passed|failed|error|skipped)", line):
                count, label = int(match.group(1)), match.group(2)
                if label == "passed":
                    passed = count
                elif label == "failed":
                    failed = count
                elif label == "error":
                    errors = count
                elif label == "skipped":
                    skipped = count
            break

    total = passed + failed + errors + skipped
    raw_summary = _build_raw_summary(total, passed, failed, errors, skipped)

    return PytestEvidence(
        exit_code=exit_code,
        tests_total=total,
        tests_passed=passed,
        tests_failed=failed,
        tests_errors=errors,
        tests_skipped=skipped,
        duration_seconds=duration,
        results=[],
        raw_summary=raw_summary,
    )


def _extract_failure(test_data: dict) -> str | None:  # type: ignore[type-arg]
    call = test_data.get("call", {})
    if call.get("outcome") in ("failed", "error"):
        longrepr = call.get("longrepr", "")
        if isinstance(longrepr, dict):
            crash = longrepr.get("reprcrash", {})
            if isinstance(crash, dict):
                return str(crash.get("message", str(longrepr)))
            return str(longrepr)
        return str(longrepr)
    return None


def _build_raw_summary(
    total: int, passed: int, failed: int, errors: int, skipped: int
) -> str:
    parts = []
    if passed:
        parts.append(f"{passed} passed")
    if failed:
        parts.append(f"{failed} failed")
    if errors:
        parts.append(f"{errors} error{'s' if errors != 1 else ''}")
    if skipped:
        parts.append(f"{skipped} skipped")
    if not parts:
        parts = ["0 tests collected"]
    return ", ".join(parts) + f" in {total} total"
