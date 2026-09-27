"""ProofLoop assembler — builds proof-pack.json from session artifacts.

Missing-artifact policy
-----------------------
- change-contract.json, adversarial-report.json, repair-log.json are REQUIRED.
  If any of these are absent, assembly raises AssemblerError immediately.

- verification-evidence.json is EXPECTED but not blocking for assembly.
  If it is absent, the Proof Pack is assembled with final_status=INCOMPLETE and
  verification_evidence=None.  The pack is still written to disk so the caller
  can inspect what is missing.

Evidence discipline
-------------------
- pytest/mypy/ruff output that was actually executed → deterministic
- Adversarial findings from Bob reasoning → llm_reasoning
These categories must never be conflated.  The assembler never fabricates
verification output.
"""
from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from proofloop.schemas.adversarial_report import AdversarialReport, FindingSeverity, FindingStatus
from proofloop.schemas.change_contract import ChangeContract
from proofloop.schemas.proof_pack import (
    AdversarialSummary,
    EvidenceItem,
    ProofPack,
    ProofPackStatus,
    VerificationSummary,
)
from proofloop.schemas.repair_log import RepairLog
from proofloop.schemas.verification_evidence import VerificationEvidence

SESSION_DIR = Path(".proofloop") / "session"


class AssemblerError(Exception):
    """Raised when a required session artifact is missing or malformed."""


def _load_json(path: Path) -> dict[str, object]:
    """Load and parse a JSON file. Raises AssemblerError on missing or invalid.

    Accepts both UTF-8 and UTF-8-with-BOM (utf-8-sig) files, which Windows
    PowerShell Set-Content may produce.
    """
    if not path.exists():
        raise AssemblerError(f"Required artifact missing: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        return data  # type: ignore[no-any-return]
    except json.JSONDecodeError as exc:
        raise AssemblerError(f"Invalid JSON in {path}: {exc}") from exc


def _try_load_json(path: Path) -> dict[str, object] | None:
    """Attempt to load a JSON file; return None if missing or invalid.

    Accepts both UTF-8 and UTF-8-with-BOM (utf-8-sig) files.
    """
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        return data  # type: ignore[no-any-return]
    except json.JSONDecodeError:
        return None


def load_session_artifacts() -> tuple[
    ChangeContract, AdversarialReport, RepairLog, VerificationEvidence | None, list[str]
]:
    """Load and validate session artifacts.

    Returns:
        (contract, adversarial, repair, evidence_or_None, missing_artifact_names)

    Required artifacts (raise AssemblerError if absent):
        change-contract.json, adversarial-report.json, repair-log.json

    Optional artifacts (None returned in their place if absent):
        verification-evidence.json
    """
    missing: list[str] = []

    contract = ChangeContract.model_validate(
        _load_json(SESSION_DIR / "change-contract.json")
    )
    adversarial = AdversarialReport.model_validate(
        _load_json(SESSION_DIR / "adversarial-report.json")
    )
    repair = RepairLog.model_validate(
        _load_json(SESSION_DIR / "repair-log.json")
    )

    evidence_data = _try_load_json(SESSION_DIR / "verification-evidence.json")
    evidence: VerificationEvidence | None
    if evidence_data is None:
        missing.append("verification-evidence.json")
        evidence = None
    else:
        evidence = VerificationEvidence.model_validate(evidence_data)

    return contract, adversarial, repair, evidence, missing


def _build_verification_summary(evidence: VerificationEvidence) -> VerificationSummary:
    return VerificationSummary(
        pytest_passed=evidence.pytest.exit_code == 0,
        pytest_tests_total=evidence.pytest.tests_total,
        pytest_tests_failed=evidence.pytest.tests_failed,
        mypy_passed=evidence.mypy.exit_code == 0,
        mypy_error_count=evidence.mypy.error_count,
        ruff_passed=evidence.ruff.exit_code == 0,
        ruff_violation_count=evidence.ruff.violation_count,
        all_deterministic_pass=evidence.all_deterministic_pass,
    )


def _build_adversarial_summary(adversarial: AdversarialReport) -> AdversarialSummary:
    open_blocking = sum(
        1
        for f in adversarial.findings
        if f.status == FindingStatus.open
        and f.severity in (FindingSeverity.critical, FindingSeverity.high)
    )
    return AdversarialSummary(
        total_findings=len(adversarial.findings),
        critical_findings=adversarial.critical_count,
        high_findings=adversarial.high_count,
        open_blocking_findings=open_blocking,
        all_blocking_resolved=open_blocking == 0,
    )


def _build_evidence_items(
    contract: ChangeContract,
    adversarial: AdversarialReport,
    evidence: VerificationEvidence | None,
) -> list[EvidenceItem]:
    """Build per-requirement evidence items.

    When verification_evidence is None (INCOMPLETE state), deterministic items
    are recorded as not met with a clear explanation — they are never fabricated.
    """
    items: list[EvidenceItem] = []

    # Functional requirements — backed by pytest (deterministic)
    if evidence is not None:
        pytest_pass = evidence.pytest.exit_code == 0
        pytest_detail = (
            f"pytest exit_code={evidence.pytest.exit_code}; "
            f"{evidence.pytest.tests_passed}/{evidence.pytest.tests_total} passed"
        )
        pytest_exit = evidence.pytest.exit_code
    else:
        pytest_pass = False
        pytest_detail = "verification-evidence.json not present; pytest not yet run"
        pytest_exit = None

    for req in contract.functional_requirements:
        items.append(
            EvidenceItem(
                requirement_id=req.id,
                requirement_description=req.description,
                evidence_category="deterministic",
                met=pytest_pass,
                is_blocking=req.priority == "must_have",
                detail=pytest_detail,
                tool_exit_code=pytest_exit,
            )
        )

    # Invariants — backed by adversarial findings (llm_reasoning)
    for inv in contract.invariants:
        related_findings = [
            f for f in adversarial.findings
            if inv.id in f.description or inv.id in f.evidence
        ]
        open_violations = [
            f for f in related_findings if f.status == FindingStatus.open
        ]
        is_met = len(open_violations) == 0
        detail = (
            f"No open adversarial findings referencing {inv.id}"
            if is_met
            else (
                f"{len(open_violations)} open finding(s): "
                + "; ".join(f.finding_id for f in open_violations)
            )
        )
        items.append(
            EvidenceItem(
                requirement_id=inv.id,
                requirement_description=inv.description,
                evidence_category="llm_reasoning",
                met=is_met,
                is_blocking=inv.severity in ("critical", "high"),
                detail=detail,
            )
        )

    # Type check — deterministic
    if evidence is not None:
        items.append(
            EvidenceItem(
                requirement_id="type-check",
                requirement_description="mypy type checking passes with no errors",
                evidence_category="deterministic",
                met=evidence.mypy.exit_code == 0,
                is_blocking=False,
                detail=(
                    f"mypy exit_code={evidence.mypy.exit_code}; "
                    f"{evidence.mypy.error_count} error(s)"
                ),
                tool_exit_code=evidence.mypy.exit_code,
            )
        )
        # Lint — deterministic
        items.append(
            EvidenceItem(
                requirement_id="lint",
                requirement_description="ruff lint passes with no violations",
                evidence_category="deterministic",
                met=evidence.ruff.exit_code == 0,
                is_blocking=False,
                detail=(
                    f"ruff exit_code={evidence.ruff.exit_code}; "
                    f"{evidence.ruff.violation_count} violation(s)"
                ),
                tool_exit_code=evidence.ruff.exit_code,
            )
        )
    else:
        items.append(
            EvidenceItem(
                requirement_id="type-check",
                requirement_description="mypy type checking passes with no errors",
                evidence_category="deterministic",
                met=False,
                is_blocking=False,
                detail="verification-evidence.json not present; mypy not yet run",
                tool_exit_code=None,
            )
        )
        items.append(
            EvidenceItem(
                requirement_id="lint",
                requirement_description="ruff lint passes with no violations",
                evidence_category="deterministic",
                met=False,
                is_blocking=False,
                detail="verification-evidence.json not present; ruff not yet run",
                tool_exit_code=None,
            )
        )

    return items


def _build_conclusion(
    status: ProofPackStatus,
    ver_summary: VerificationSummary | None,
    adv_summary: AdversarialSummary,
    contract: ChangeContract,
    missing: list[str],
) -> str:
    if status == ProofPackStatus.incomplete:
        return (
            f"Change contract {contract.contract_id} "
            f"(scenario {contract.scenario_id}) is INCOMPLETE. "
            f"Missing artifacts: {', '.join(missing)}. "
            "Run `python proofloop/cli.py verify --all` to produce "
            "verification-evidence.json and then re-run `proof-pack`."
        )
    assert ver_summary is not None  # guaranteed when status is not INCOMPLETE

    if status == ProofPackStatus.verified:
        return (
            f"Change contract {contract.contract_id} "
            f"(scenario {contract.scenario_id}) is VERIFIED. "
            f"All {ver_summary.pytest_tests_total} tests passed, "
            f"mypy reported {ver_summary.mypy_error_count} error(s), "
            f"ruff reported {ver_summary.ruff_violation_count} violation(s), "
            f"and all {adv_summary.total_findings} adversarial finding(s) were resolved."
        )
    if status == ProofPackStatus.verified_with_warnings:
        open_nb = adv_summary.total_findings - adv_summary.open_blocking_findings
        return (
            f"Change contract {contract.contract_id} is VERIFIED WITH WARNINGS. "
            f"All blocking requirements are met "
            f"({ver_summary.pytest_tests_total} tests, "
            f"{ver_summary.pytest_tests_failed} failed), "
            f"but {open_nb} non-blocking finding(s) remain open."
        )
    if status == ProofPackStatus.failed:
        reasons = []
        if not ver_summary.pytest_passed:
            reasons.append(f"{ver_summary.pytest_tests_failed} pytest failure(s)")
        if not ver_summary.mypy_passed:
            reasons.append(f"{ver_summary.mypy_error_count} mypy error(s)")
        if not ver_summary.ruff_passed:
            reasons.append(f"{ver_summary.ruff_violation_count} ruff violation(s)")
        if adv_summary.open_blocking_findings > 0:
            reasons.append(
                f"{adv_summary.open_blocking_findings} open blocking adversarial finding(s)"
            )
        return (
            f"Change contract {contract.contract_id} FAILED. "
            "Reasons: " + "; ".join(reasons) + "."
        )
    return f"Change contract {contract.contract_id} status unknown."


def assemble_proof_pack(pack_id: str | None = None) -> ProofPack:
    """Load all session artifacts and assemble a ProofPack.

    If verification-evidence.json is absent, the pack is assembled with
    final_status=INCOMPLETE and written to disk.  The caller can inspect
    missing_artifacts to know what still needs to run.

    Raises:
        AssemblerError: if any of the three required artifacts are missing
            or contain invalid JSON/schema.
    """
    contract, adversarial, repair, evidence, missing = load_session_artifacts()

    if pack_id is None:
        pack_id = f"pp-{contract.scenario_id}-001"

    status = ProofPack.compute_status(evidence, adversarial, repair)

    ver_summary = _build_verification_summary(evidence) if evidence is not None else None
    adv_summary = _build_adversarial_summary(adversarial)
    evidence_items = _build_evidence_items(contract, adversarial, evidence)
    conclusion = _build_conclusion(status, ver_summary, adv_summary, contract, missing)

    # Collect non-blocking warnings (only possible when evidence is present)
    warnings: list[str] = []
    if ver_summary is not None:
        if not ver_summary.mypy_passed:
            warnings.append(f"mypy: {ver_summary.mypy_error_count} type error(s) found")
        if not ver_summary.ruff_passed:
            warnings.append(f"ruff: {ver_summary.ruff_violation_count} lint violation(s) found")

    pack = ProofPack(
        pack_id=pack_id,
        contract_id=contract.contract_id,
        scenario_id=contract.scenario_id,
        assembled_at=datetime.now(tz=UTC),
        final_status=status,
        change_contract=contract,
        adversarial_report=adversarial,
        repair_log=repair,
        verification_evidence=evidence,
        verification_summary=ver_summary,
        adversarial_summary=adv_summary,
        evidence_items=evidence_items,
        conclusion=conclusion,
        warnings=warnings,
        missing_artifacts=missing,
    )

    out_path = SESSION_DIR / "proof-pack.json"
    out_path.write_text(
        json.dumps(pack.model_dump_json_safe(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return pack
