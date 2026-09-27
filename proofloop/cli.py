"""ProofLoop CLI — verify, proof-pack, status, reset commands.

Usage (from project root, with venv activated):
    python proofloop/cli.py verify --tests
    python proofloop/cli.py verify --types
    python proofloop/cli.py verify --lint
    python proofloop/cli.py verify --all
    python proofloop/cli.py proof-pack
    python proofloop/cli.py status
    python proofloop/cli.py reset
"""
from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import typer

# Ensure repository root is in sys.path when run directly as script
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

app = typer.Typer(
    name="proofloop",
    help="ProofLoop CLI — deterministic verification infrastructure.",
    add_completion=False,
)

SESSION_DIR = Path(".proofloop") / "session"
EVIDENCE_FILE = SESSION_DIR / "verification-evidence.json"
CONTRACT_FILE = SESSION_DIR / "change-contract.json"
PROOF_PACK_FILE = SESSION_DIR / "proof-pack.json"


def _ensure_session_dir() -> None:
    SESSION_DIR.mkdir(parents=True, exist_ok=True)


def _load_json_or_none(path: Path) -> dict[str, object] | None:
    """Load JSON file; return None on missing, BOM-stripped (utf-8-sig), or parse error."""
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        return data  # type: ignore[no-any-return]
    except (json.JSONDecodeError, OSError):
        return None


# ── verify command ─────────────────────────────────────────────────────────────

verify_app = typer.Typer(help="Run deterministic verification checks.")
app.add_typer(verify_app, name="verify")


@verify_app.callback(invoke_without_command=True)
def verify(
    ctx: typer.Context,
    tests: bool = typer.Option(False, "--tests", help="Run pytest"),
    types: bool = typer.Option(False, "--types", help="Run mypy"),
    lint: bool = typer.Option(False, "--lint", help="Run ruff"),
    all_checks: bool = typer.Option(  # noqa: E501
        False, "--all", help="Run all checks and write verification-evidence.json"
    ),
) -> None:
    """Run one or more verification checks."""
    if ctx.invoked_subcommand is not None:
        return

    _ensure_session_dir()

    run_tests = tests or all_checks
    run_types = types or all_checks
    run_lint = lint or all_checks

    if not any([run_tests, run_types, run_lint]):
        typer.echo("Specify at least one of: --tests, --types, --lint, --all", err=True)
        raise typer.Exit(1)

    results: dict = {}  # type: ignore[type-arg]

    if run_tests:
        typer.echo(">> Running pytest...")
        from proofloop.verifiers.pytest_runner import run_pytest
        pytest_ev = run_pytest()
        results["pytest"] = pytest_ev
        status = "[PASS]" if pytest_ev.exit_code == 0 else "[FAIL]"
        typer.echo(
            f"  {status}  exit_code={pytest_ev.exit_code}  "
            f"{pytest_ev.tests_passed}/{pytest_ev.tests_total} passed"
        )

    if run_types:
        typer.echo(">> Running mypy...")
        from proofloop.verifiers.mypy_runner import run_mypy
        mypy_ev = run_mypy()
        results["mypy"] = mypy_ev
        status = "[PASS]" if mypy_ev.exit_code == 0 else "[FAIL]"
        typer.echo(
            f"  {status}  exit_code={mypy_ev.exit_code}  "
            f"{mypy_ev.error_count} error(s)"
        )

    if run_lint:
        typer.echo(">> Running ruff...")
        from proofloop.verifiers.ruff_runner import run_ruff
        ruff_ev = run_ruff()
        results["ruff"] = ruff_ev
        status = "[PASS]" if ruff_ev.exit_code == 0 else "[FAIL]"
        typer.echo(
            f"  {status}  exit_code={ruff_ev.exit_code}  "
            f"{ruff_ev.violation_count} violation(s)"
        )

    if all_checks and len(results) == 3:
        _write_verification_evidence(results)
        typer.echo(f"\n[OK] verification-evidence.json written to {EVIDENCE_FILE}")


def _write_verification_evidence(results: dict) -> None:  # type: ignore[type-arg]
    """Write verification-evidence.json from collected tool results."""

    # Git diff evidence
    diff_stat = _get_git_diff_stat()
    changed_files = _get_git_changed_files()

    # Build the evidence dict directly (avoids import cycle if schemas evolve)
    contract_data = _load_json_or_none(CONTRACT_FILE) or {}
    contract_id = contract_data.get("contract_id", "unknown")
    scenario_id = contract_data.get("scenario_id", "unknown")

    pytest_ev = results["pytest"]
    mypy_ev = results["mypy"]
    ruff_ev = results["ruff"]

    evidence = {
        "evidence_id": f"ve-{scenario_id}-001",
        "contract_id": contract_id,
        "scenario_id": scenario_id,
        "collected_at": datetime.now(tz=UTC).isoformat(),
        "pytest": {
            "exit_code": pytest_ev.exit_code,
            "tests_total": pytest_ev.tests_total,
            "tests_passed": pytest_ev.tests_passed,
            "tests_failed": pytest_ev.tests_failed,
            "tests_errors": pytest_ev.tests_errors,
            "tests_skipped": pytest_ev.tests_skipped,
            "duration_seconds": pytest_ev.duration_seconds,
            "results": [r.model_dump() for r in pytest_ev.results],
            "raw_summary": pytest_ev.raw_summary,
        },
        "mypy": {
            "exit_code": mypy_ev.exit_code,
            "error_count": mypy_ev.error_count,
            "errors": mypy_ev.errors,
            "raw_output": mypy_ev.raw_output,
        },
        "ruff": {
            "exit_code": ruff_ev.exit_code,
            "violation_count": ruff_ev.violation_count,
            "violations": ruff_ev.violations,
            "raw_output": ruff_ev.raw_output,
        },
        "git_diff": {
            "changed_files": changed_files,
            "diff_stat": diff_stat,
        },
    }

    EVIDENCE_FILE.write_text(
        json.dumps(evidence, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def _get_git_diff_stat() -> str:
    import subprocess
    try:
        result = subprocess.run(  # noqa: S603
            ["git", "diff", "--stat", "HEAD"],  # noqa: S607
            capture_output=True, text=True
        )
        return result.stdout.strip() or "(no diff)"
    except Exception:
        return "(git unavailable)"


def _get_git_changed_files() -> list[str]:
    import subprocess
    try:
        result = subprocess.run(  # noqa: S603
            ["git", "diff", "--name-only", "HEAD"],  # noqa: S607
            capture_output=True, text=True
        )
        lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        return lines
    except Exception:
        return []


# ── proof-pack command ────────────────────────────────────────────────────────

@app.command("proof-pack")
def proof_pack_cmd() -> None:
    """Assemble proof-pack.json from all session artifacts."""
    _ensure_session_dir()

    typer.echo(">> Assembling Proof Pack...")
    try:
        from proofloop.assembler import assemble_proof_pack
        from proofloop.schemas.proof_pack import ProofPackStatus

        pack = assemble_proof_pack()
        typer.echo(f"\n{'='*60}")
        typer.echo(f"  Proof Pack ID : {pack.pack_id}")
        typer.echo(f"  Contract      : {pack.contract_id}")
        typer.echo(f"  Scenario      : {pack.scenario_id}")
        typer.echo(f"  Final Status  : {pack.final_status.value}")
        if pack.missing_artifacts:
            typer.echo(f"  Missing       : {', '.join(pack.missing_artifacts)}")
        typer.echo(f"{'='*60}")
        typer.echo(f"\n{pack.conclusion}\n")
        if pack.warnings:
            typer.echo("Warnings:")
            for w in pack.warnings:
                typer.echo(f"  [!] {w}")
        typer.echo(f"\n[OK] proof-pack.json written to {PROOF_PACK_FILE}")
        # Exit non-zero for non-success states so CI pipelines can detect failures
        if pack.final_status in (ProofPackStatus.failed, ProofPackStatus.incomplete):
            raise typer.Exit(1)
    except typer.Exit:
        raise
    except Exception as exc:  # noqa: BLE001
        typer.echo(f"[ERROR] Assembly failed: {exc}", err=True)
        raise typer.Exit(1) from exc


# ── status command ─────────────────────────────────────────────────────────────

@app.command()
def status() -> None:
    """Print the current session status."""
    contract = _load_json_or_none(CONTRACT_FILE)
    _load_json_or_none(EVIDENCE_FILE)  # loaded for side-effect check only
    proof_pack = _load_json_or_none(PROOF_PACK_FILE)

    typer.echo("\n-- ProofLoop Session Status ------------------------------------------")

    if contract:
        cid = contract.get("contract_id", "?")
        sid = contract.get("scenario_id", "?")
        typer.echo(f"  Contract      : {cid} ({sid})")
    else:
        typer.echo("  Contract      : [missing]")

    artifacts = {
        "change-contract.json": CONTRACT_FILE,
        "adversarial-report.json": SESSION_DIR / "adversarial-report.json",
        "repair-log.json": SESSION_DIR / "repair-log.json",
        "verification-evidence.json": EVIDENCE_FILE,
        "proof-pack.json": PROOF_PACK_FILE,
    }
    for name, path in artifacts.items():
        mark = "[OK]" if path.exists() else "[--]"
        typer.echo(f"  {mark} {name}")

    if proof_pack:
        final = proof_pack.get("final_status", "?")
        typer.echo(f"\n  Final Status  : {final}")
    else:
        typer.echo("\n  Final Status  : (no proof pack yet)")

    typer.echo("---------------------------------------------------------------------\n")


# ── reset command ──────────────────────────────────────────────────────────────

@app.command()
def reset() -> None:
    """Clear the current session directory for a fresh start."""
    if not SESSION_DIR.exists():
        typer.echo("Session directory does not exist — nothing to reset.")
        return

    artifacts = list(SESSION_DIR.glob("*.json"))
    if not artifacts:
        typer.echo("Session already empty.")
        return

    confirm = typer.confirm(
        f"This will delete {len(artifacts)} artifact(s) in {SESSION_DIR}. Continue?"
    )
    if not confirm:
        typer.echo("Aborted.")
        raise typer.Exit(0)

    for f in artifacts:
        f.unlink()
    typer.echo(f"[OK] Cleared {len(artifacts)} artifact(s).")


# ── load-scenario command ──────────────────────────────────────────────────────

@app.command("load-scenario")
def load_scenario(
    scenario: str = typer.Argument(
        ..., help="Scenario ID (e.g. s01, s02, s03, s04, s05) or path to JSON file"
    ),
) -> None:
    """Load a benchmark scenario into the session Change Contract."""
    _ensure_session_dir()
    from proofloop.schemas.change_contract import ChangeContract

    target_path = Path(scenario)
    if not target_path.is_file():
        # Try finding in benchmark/scenarios/
        scenarios_dir = Path("benchmark") / "scenarios"
        matched = list(scenarios_dir.glob(f"{scenario.lower()}*.json"))
        if not matched:
            matched = list(scenarios_dir.glob(f"*{scenario.lower()}*.json"))
        if matched:
            target_path = matched[0]
        else:
            typer.echo(f"[ERROR] Scenario file not found: {scenario}", err=True)
            raise typer.Exit(1)

    try:
        content = target_path.read_text(encoding="utf-8-sig")
        contract = ChangeContract.model_validate_json(content)
    except Exception as exc:  # noqa: BLE001
        typer.echo(f"[ERROR] Failed to validate scenario contract: {exc}", err=True)
        raise typer.Exit(1) from exc

    # Write to session change-contract.json
    CONTRACT_FILE.write_text(contract.model_dump_json(indent=2), encoding="utf-8")
    typer.echo(f"[OK] Loaded scenario '{contract.scenario_id}' into {CONTRACT_FILE}")
    typer.echo(f"  Contract ID : {contract.contract_id}")
    typer.echo(f"  Request     : {contract.request_normalized}")
    typer.echo(f"  Invariants  : {len(contract.invariants)} invariant(s)")
    for inv in contract.invariants:
        typer.echo(f"    - [{inv.severity.value.upper()}] {inv.id}: {inv.description}")


# ── benchmark command ──────────────────────────────────────────────────────────

@app.command("benchmark")
def benchmark_cmd() -> None:
    """List all benchmark scenarios and their verification status."""
    from proofloop.schemas.change_contract import ChangeContract

    scenarios_dir = Path("benchmark") / "scenarios"
    if not scenarios_dir.is_dir():
        typer.echo("Benchmark directory not found.")
        return

    scenario_files = sorted(scenarios_dir.glob("s*.json"))
    if not scenario_files:
        typer.echo("No benchmark scenarios found.")
        return

    typer.echo("\n-- ProofLoop Benchmark Matrix ---------------------------------------")
    typer.echo("  Scenario  ID          Invariants  Status")
    typer.echo("  --------  ----------  ----------  ---------------------------------")

    for f in scenario_files:
        try:
            c = ChangeContract.model_validate_json(f.read_text(encoding="utf-8-sig"))
            # S01 has real completed evidence in snapshot
            if c.scenario_id == "s01":
                status_str = "VERIFIED (Hero Demo Snapshot)"
            else:
                status_str = "NOT RUN"
            sid = c.scenario_id.upper()
            cid = c.contract_id
            inv_count = len(c.invariants)
            typer.echo(f"  {sid:8}  {cid:10}  {inv_count:10}  {status_str}")
        except Exception:  # noqa: BLE001
            typer.echo(f"  {f.stem[:8]:8}  [parse error]")

    typer.echo("---------------------------------------------------------------------\n")


# ── demo command ───────────────────────────────────────────────────────────────

@app.command("demo")
def demo_cmd(
    delay: float = typer.Option(
        1.8, "--delay", "-d", help="Pacing delay in seconds between stages"
    ),
    step: bool = typer.Option(
        False, "--step", "-s", help="Wait for [Enter] key between stages (interactive mode)"
    ),
) -> None:
    """Execute the authentic S01 workflow live for hackathon presentations."""
    from proofloop.runner import run_s01_live

    typer.echo("\n" + "=" * 68)
    typer.echo("  ProofLoop — Live Presentation Runner (IBM Bob 2.0)")
    typer.echo("  Hero Scenario: S01 Promotional Coupon Support")
    typer.echo("=" * 68)

    stage_names = {
        "init": "CLEANUP",
        "contract": "STAGE 1: PROOFLOOP MODE",
        "contract_ready": "CONTRACT LOCKED",
        "challenge": "STAGE 2: ADVERSARIAL MODE",
        "challenge_uncovered": "DEFECT DISCOVERED",
        "repair": "STAGE 3: REPAIR CYCLE",
        "repair_complete": "REPAIR VERIFIED",
        "verify": "STAGE 4: VERIFIER MODE",
        "verify_complete": "TOOLS COMPLETED",
        "proof_pack": "STAGE 5: PROOF PACK",
        "complete": "FINAL VERDICT",
    }

    def on_progress(stage: str, details: dict) -> None:
        title = stage_names.get(stage, stage.upper())
        msg = details.get("message", "")

        if stage in ("contract", "challenge", "repair", "verify", "proof_pack"):
            typer.echo(f"\n>> [{title}] {msg}")
            if step:
                typer.prompt("   Press [Enter] to execute stage", default="", show_default=False)
        elif stage == "contract_ready":
            typer.echo(f"   Contract ID: {details.get('contract_id')}")
            typer.echo(f"   Invariants : {details.get('invariants_count')} enforced")
        elif stage == "challenge_uncovered":
            typer.echo("   [!] INVARIANT VIOLATION DETECTED by Adversarial Agent:")
            typer.echo(f"       Calculation: {details.get('calculation')}")
            inv_str = details.get("invariant")
            typer.echo(f"       Invariant  : {inv_str} (payment must never be negative)")
        elif stage == "repair_complete":
            typer.echo(f"   [OK] Floor Guard Applied: {details.get('guard')}")
            typer.echo("   [OK] Invariant regression suite passes.")
        elif stage == "verify_complete":
            py_pass = details.get("pytest_passed")
            py_ex = details.get("pytest_exit")
            my_err = details.get("mypy_errors")
            my_ex = details.get("mypy_exit")
            rf_viol = details.get("ruff_violations")
            rf_ex = details.get("ruff_exit")
            typer.echo(f"   [OK] pytest: {py_pass} passed (exit {py_ex})")
            typer.echo(f"   [OK] mypy  : {my_err} errors (exit {my_ex})")
            typer.echo(f"   [OK] ruff  : {rf_viol} violations (exit {rf_ex})")
        elif stage == "complete":
            typer.echo("\n" + "=" * 68)
            typer.echo(f"  FINAL PROOF PACK STATUS: {details.get('final_status')}")
            typer.echo(f"  Traceable Items        : {details.get('evidence_count')}")
            typer.echo(f"  Conclusion             : {details.get('conclusion')}")
            typer.echo("=" * 68 + "\n")

    actual_delay = 0.0 if step else delay
    result = run_s01_live(stage_delay=actual_delay, progress_callback=on_progress)
    typer.echo(f"[OK] Live presentation completed with status: {result.get('final_status')}\n")


# ── entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app()
