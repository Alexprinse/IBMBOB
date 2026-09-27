"""Adversarial Report schema — findings from the Adversarial Agent."""
from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class FindingSeverity(str, Enum):  # noqa: UP042
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"


class FindingCategory(str, Enum):  # noqa: UP042
    invariant_violation = "invariant_violation"
    edge_case = "edge_case"
    security = "security"
    api_contract = "api_contract"
    missing_test = "missing_test"


class EvidenceCategory(str, Enum):  # noqa: UP042
    deterministic = "deterministic"
    llm_reasoning = "llm_reasoning"


class FindingStatus(str, Enum):  # noqa: UP042
    open = "open"
    resolved = "resolved"
    accepted_risk = "accepted_risk"


class AdversarialFinding(BaseModel):
    finding_id: str = Field(..., pattern=r"^af-\d{2}$", description="e.g. af-01")
    severity: FindingSeverity
    category: FindingCategory
    description: str
    evidence: str = Field(..., description="What was observed in code or reasoning")
    evidence_category: EvidenceCategory
    suggested_repair: str
    status: FindingStatus = FindingStatus.open
    resolved_by_repair_id: str | None = None


class AdversarialReport(BaseModel):
    report_id: str = Field(..., description="e.g. ar-s01-001")
    contract_id: str = Field(..., description="References ChangeContract.contract_id")
    created_at: datetime
    scenario_id: str
    findings: list[AdversarialFinding]
    summary: str = Field(..., description="One-line summary of findings count")

    @property
    def critical_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == FindingSeverity.critical)

    @property
    def high_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == FindingSeverity.high)

    @property
    def open_critical_count(self) -> int:
        return sum(
            1 for f in self.findings
            if f.severity == FindingSeverity.critical and f.status == FindingStatus.open
        )

    @property
    def open_high_count(self) -> int:
        return sum(
            1 for f in self.findings
            if f.severity == FindingSeverity.high and f.status == FindingStatus.open
        )
