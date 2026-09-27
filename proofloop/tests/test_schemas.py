"""Smoke tests for ProofLoop Pydantic schemas.

These tests verify that all schemas can be instantiated with valid data
and that key computed properties work correctly. They do not run any
external tools — they are pure Python unit tests.
"""
from __future__ import annotations

from datetime import UTC, datetime

import pytest

from proofloop.schemas.adversarial_report import (
    AdversarialFinding,
    AdversarialReport,
    EvidenceCategory,
    FindingCategory,
    FindingSeverity,
    FindingStatus,
)
from proofloop.schemas.change_contract import (
    ChangeContract,
    FunctionalRequirement,
    Invariant,
    Priority,
    RegressionRisk,
    RequiredEvidence,
    Severity,
)
from proofloop.schemas.proof_pack import (
    ProofPack,
    ProofPackStatus,
)
from proofloop.schemas.repair_log import RepairEntry, RepairLog, RepairStatus
from proofloop.schemas.verification_evidence import (
    GitDiffEvidence,
    MypyEvidence,
    PytestEvidence,
    RuffEvidence,
    VerificationEvidence,
)

# ── Helpers ────────────────────────────────────────────────────────────────────

def _make_change_contract() -> ChangeContract:
    return ChangeContract(
        contract_id="cc-s01-001",
        created_at=datetime.now(tz=UTC),
        scenario_id="s01",
        request_raw="Add coupon support.",
        request_normalized="Add coupon code support to checkout.",
        intended_behavior=["Checkout accepts optional coupon_code"],
        functional_requirements=[
            FunctionalRequirement(
                id="req-01",
                description="Checkout accepts coupon_code",
                priority=Priority.must_have,
            )
        ],
        invariants=[
            Invariant(
                id="inv-01",
                description="Payment amount must never be negative.",
                severity=Severity.critical,
            )
        ],
        affected_components=["checkoutlab/app/services/checkout.py"],
        required_evidence=RequiredEvidence(
            functional_tests=["test_coupon_percentage_discount_applied"],
            invariant_checks=["test_payment_never_negative_when_coupon_exceeds_subtotal"],
        ),
        estimated_regression_risk=RegressionRisk.medium,
    )


def _make_verification_evidence(
    pytest_exit: int = 0,
    mypy_exit: int = 0,
    ruff_exit: int = 0,
) -> VerificationEvidence:
    return VerificationEvidence(
        evidence_id="ve-s01-001",
        contract_id="cc-s01-001",
        scenario_id="s01",
        collected_at=datetime.now(tz=UTC),
        pytest=PytestEvidence(
            exit_code=pytest_exit,
            tests_total=10,
            tests_passed=10 if pytest_exit == 0 else 9,
            tests_failed=0 if pytest_exit == 0 else 1,
            tests_errors=0,
            tests_skipped=0,
            duration_seconds=1.23,
            raw_summary="10 passed in 10 total",
        ),
        mypy=MypyEvidence(
            exit_code=mypy_exit,
            error_count=0 if mypy_exit == 0 else 1,
            errors=[] if mypy_exit == 0 else ["file.py:1: error: something"],
            raw_output="Success: no issues found" if mypy_exit == 0 else "Found 1 error",
        ),
        ruff=RuffEvidence(
            exit_code=ruff_exit,
            violation_count=0 if ruff_exit == 0 else 2,
            violations=[],
            raw_output="All checks passed." if ruff_exit == 0 else "2 violations",
        ),
        git_diff=GitDiffEvidence(
            changed_files=["checkoutlab/app/services/checkout.py"],
            diff_stat="1 file changed, 10 insertions(+)",
        ),
    )


def _make_adversarial_report(
    findings: list[AdversarialFinding] | None = None,
) -> AdversarialReport:
    return AdversarialReport(
        report_id="ar-s01-001",
        contract_id="cc-s01-001",
        created_at=datetime.now(tz=UTC),
        scenario_id="s01",
        findings=findings or [],
        summary="0 findings" if not findings else f"{len(findings)} finding(s)",
    )


def _make_repair_log() -> RepairLog:
    return RepairLog(
        log_id="rl-s01-001",
        contract_id="cc-s01-001",
        scenario_id="s01",
        repairs=[],
    )


# ── ChangeContract ─────────────────────────────────────────────────────────────

def test_change_contract_instantiates() -> None:
    contract = _make_change_contract()
    assert contract.contract_id == "cc-s01-001"
    assert contract.scenario_id == "s01"
    assert len(contract.functional_requirements) == 1
    assert len(contract.invariants) == 1


def test_functional_requirement_id_pattern() -> None:
    with pytest.raises(Exception):  # noqa: B017
        FunctionalRequirement(
            id="bad-id",
            description="test",
            priority=Priority.must_have,
        )


def test_invariant_id_pattern() -> None:
    with pytest.raises(Exception):  # noqa: B017
        Invariant(
            id="i-1",  # wrong pattern
            description="test",
            severity=Severity.critical,
        )


# ── VerificationEvidence ───────────────────────────────────────────────────────

def test_verification_evidence_all_pass() -> None:
    ev = _make_verification_evidence(pytest_exit=0, mypy_exit=0, ruff_exit=0)
    assert ev.all_deterministic_pass is True
    assert ev.pytest_exit_code == 0
    assert ev.mypy_exit_code == 0
    assert ev.ruff_exit_code == 0


def test_verification_evidence_pytest_fail() -> None:
    ev = _make_verification_evidence(pytest_exit=1)
    assert ev.all_deterministic_pass is False


def test_verification_evidence_mypy_fail() -> None:
    ev = _make_verification_evidence(mypy_exit=1)
    assert ev.all_deterministic_pass is False


# ── AdversarialReport ──────────────────────────────────────────────────────────

def test_adversarial_report_no_findings() -> None:
    report = _make_adversarial_report()
    assert report.critical_count == 0
    assert report.high_count == 0
    assert report.open_critical_count == 0


def test_adversarial_report_critical_finding() -> None:
    finding = AdversarialFinding(
        finding_id="af-01",
        severity=FindingSeverity.critical,
        category=FindingCategory.invariant_violation,
        description="inv-01: payment can be negative when coupon > subtotal",
        evidence="checkout.py line 95: final_total = subtotal - discount_amount",
        evidence_category=EvidenceCategory.llm_reasoning,
        suggested_repair="Add max(Decimal('0.00'), subtotal - discount_amount)",
        status=FindingStatus.open,
    )
    report = _make_adversarial_report([finding])
    assert report.critical_count == 1
    assert report.open_critical_count == 1
    assert report.high_count == 0


def test_adversarial_finding_resolved() -> None:
    finding = AdversarialFinding(
        finding_id="af-01",
        severity=FindingSeverity.critical,
        category=FindingCategory.invariant_violation,
        description="inv-01 violated",
        evidence="code analysis",
        evidence_category=EvidenceCategory.llm_reasoning,
        suggested_repair="Add floor guard",
        status=FindingStatus.resolved,
        resolved_by_repair_id="rp-01",
    )
    report = _make_adversarial_report([finding])
    assert report.open_critical_count == 0


# ── RepairLog ──────────────────────────────────────────────────────────────────

def test_repair_log_empty() -> None:
    log = _make_repair_log()
    assert log.repair_count == 0
    assert log.all_verified is True  # vacuously true for empty list


def test_repair_log_with_entry() -> None:
    entry = RepairEntry(
        repair_id="rp-01",
        finding_id="af-01",
        applied_at=datetime.now(tz=UTC),
        description="Added max(0, subtotal - discount) floor guard",
        files_modified=["checkoutlab/app/services/checkout.py"],
        status=RepairStatus.verified,
        post_repair_pytest_exit_code=0,
    )
    log = RepairLog(
        log_id="rl-s01-001",
        contract_id="cc-s01-001",
        scenario_id="s01",
        repairs=[entry],
    )
    assert log.repair_count == 1
    assert log.all_verified is True


# ── ProofPack status computation ───────────────────────────────────────────────

def test_proof_pack_status_verified() -> None:
    ev = _make_verification_evidence()
    report = _make_adversarial_report()
    repair = _make_repair_log()
    status = ProofPack.compute_status(ev, report, repair)
    assert status == ProofPackStatus.verified


def test_proof_pack_status_failed_pytest() -> None:
    ev = _make_verification_evidence(pytest_exit=1)
    report = _make_adversarial_report()
    repair = _make_repair_log()
    status = ProofPack.compute_status(ev, report, repair)
    assert status == ProofPackStatus.failed


def test_proof_pack_status_failed_open_critical() -> None:
    ev = _make_verification_evidence()
    finding = AdversarialFinding(
        finding_id="af-01",
        severity=FindingSeverity.critical,
        category=FindingCategory.invariant_violation,
        description="inv-01 violated",
        evidence="code",
        evidence_category=EvidenceCategory.llm_reasoning,
        suggested_repair="Fix it",
        status=FindingStatus.open,
    )
    report = _make_adversarial_report([finding])
    repair = _make_repair_log()
    status = ProofPack.compute_status(ev, report, repair)
    assert status == ProofPackStatus.failed


def test_proof_pack_status_verified_with_warnings() -> None:
    ev = _make_verification_evidence()
    finding = AdversarialFinding(
        finding_id="af-01",
        severity=FindingSeverity.low,
        category=FindingCategory.edge_case,
        description="minor edge case",
        evidence="observation",
        evidence_category=EvidenceCategory.llm_reasoning,
        suggested_repair="Consider adding a test",
        status=FindingStatus.open,
    )
    report = _make_adversarial_report([finding])
    repair = _make_repair_log()
    status = ProofPack.compute_status(ev, report, repair)
    assert status == ProofPackStatus.verified_with_warnings


def test_proof_pack_status_incomplete_when_no_evidence() -> None:
    """Missing verification evidence must produce INCOMPLETE, never VERIFIED."""
    report = _make_adversarial_report()
    repair = _make_repair_log()
    status = ProofPack.compute_status(None, report, repair)
    assert status == ProofPackStatus.incomplete


def test_proof_pack_status_incomplete_beats_open_critical() -> None:
    """INCOMPLETE takes priority: even with open critical findings, status is INCOMPLETE
    when evidence is absent (cannot determine FAILED without running the tools)."""
    finding = AdversarialFinding(
        finding_id="af-01",
        severity=FindingSeverity.critical,
        category=FindingCategory.invariant_violation,
        description="inv-01 violated",
        evidence="code",
        evidence_category=EvidenceCategory.llm_reasoning,
        suggested_repair="Fix it",
        status=FindingStatus.open,
    )
    report = _make_adversarial_report([finding])
    repair = _make_repair_log()
    status = ProofPack.compute_status(None, report, repair)
    assert status == ProofPackStatus.incomplete
