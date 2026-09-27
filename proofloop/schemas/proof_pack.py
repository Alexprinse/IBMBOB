"""Proof Pack schema — the final assembled evidence artifact."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from proofloop.schemas.adversarial_report import AdversarialReport
from proofloop.schemas.change_contract import ChangeContract
from proofloop.schemas.repair_log import RepairLog
from proofloop.schemas.verification_evidence import VerificationEvidence


class ProofPackStatus(str, Enum):  # noqa: UP042
    verified = "VERIFIED"
    verified_with_warnings = "VERIFIED_WITH_WARNINGS"
    failed = "FAILED"
    incomplete = "INCOMPLETE"


class EvidenceItem(BaseModel):
    """A single evidence entry in the Proof Pack summary."""

    requirement_id: str = Field(..., description="e.g. req-01 or inv-01")
    requirement_description: str
    evidence_category: str = Field(
        ..., description="'deterministic' or 'llm_reasoning'"
    )
    met: bool
    is_blocking: bool
    detail: str = Field(..., description="Concise statement of what was observed")
    tool_exit_code: int | None = None


class VerificationSummary(BaseModel):
    pytest_passed: bool
    pytest_tests_total: int
    pytest_tests_failed: int
    mypy_passed: bool
    mypy_error_count: int
    ruff_passed: bool
    ruff_violation_count: int
    all_deterministic_pass: bool


class AdversarialSummary(BaseModel):
    total_findings: int
    critical_findings: int
    high_findings: int
    open_blocking_findings: int
    all_blocking_resolved: bool


class ProofPack(BaseModel):
    """Final assembled evidence artifact for a ProofLoop session."""

    pack_id: str = Field(..., description="e.g. pp-s01-001")
    contract_id: str
    scenario_id: str
    assembled_at: datetime
    final_status: ProofPackStatus

    # Embedded sub-artifacts (full detail).
    # verification_evidence is Optional: it may be absent if verify --all has not
    # been run yet, in which case final_status will be INCOMPLETE.
    change_contract: ChangeContract
    adversarial_report: AdversarialReport
    repair_log: RepairLog
    verification_evidence: VerificationEvidence | None = None

    # Summaries for quick scanning
    verification_summary: VerificationSummary | None = None
    adversarial_summary: AdversarialSummary
    evidence_items: list[EvidenceItem] = Field(default_factory=list)

    # Human-readable conclusion
    conclusion: str = Field(
        ...,
        description="One paragraph explaining the final status with specific evidence",
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Non-blocking issues that should be noted but did not prevent VERIFIED",
    )
    missing_artifacts: list[str] = Field(
        default_factory=list,
        description="Names of session artifact files that were absent at assembly time",
    )

    @classmethod
    def compute_status(
        cls,
        verification: VerificationEvidence | None,
        adversarial: AdversarialReport,
        repair: RepairLog,
    ) -> ProofPackStatus:
        """Deterministically compute the final status from the evidence.

        Rules (in priority order):
        1. verification_evidence absent → INCOMPLETE
        2. Open blocking (critical/high) adversarial finding → FAILED
        3. Any deterministic tool failure (pytest/mypy/ruff) → FAILED
        4. Non-blocking open findings remain → VERIFIED_WITH_WARNINGS
        5. All checks pass, all findings resolved → VERIFIED
        """
        # Missing verification evidence → cannot claim VERIFIED
        if verification is None:
            return ProofPackStatus.incomplete

        from proofloop.schemas.adversarial_report import FindingSeverity, FindingStatus

        # Open blocking findings → FAILED
        open_blocking = sum(
            1
            for f in adversarial.findings
            if f.status == FindingStatus.open
            and f.severity in (FindingSeverity.critical, FindingSeverity.high)
        )
        if open_blocking > 0:
            return ProofPackStatus.failed

        # Any deterministic tool failure → FAILED
        if not verification.all_deterministic_pass:
            return ProofPackStatus.failed

        # Non-blocking open findings → VERIFIED_WITH_WARNINGS
        open_non_blocking = sum(
            1
            for f in adversarial.findings
            if f.status == FindingStatus.open
            and f.severity not in (FindingSeverity.critical, FindingSeverity.high)
        )
        if open_non_blocking > 0:
            return ProofPackStatus.verified_with_warnings

        return ProofPackStatus.verified

    def model_dump_json_safe(self) -> dict[str, Any]:
        """Dump to a JSON-serialisable dict (datetimes as ISO strings)."""
        return self.model_dump(mode="json")
