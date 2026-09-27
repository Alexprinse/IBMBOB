"""Change Contract schema — the machine-readable specification of a developer request."""
from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class Priority(str, Enum):  # noqa: UP042
    must_have = "must_have"
    should_have = "should_have"
    nice_to_have = "nice_to_have"


class Severity(str, Enum):  # noqa: UP042
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"


class RegressionRisk(str, Enum):  # noqa: UP042
    low = "low"
    medium = "medium"
    high = "high"


class FunctionalRequirement(BaseModel):
    id: str = Field(..., pattern=r"^req-\d{2}$", description="e.g. req-01")
    description: str
    priority: Priority


class Invariant(BaseModel):
    id: str = Field(..., pattern=r"^inv-\d{2}$", description="e.g. inv-01")
    description: str
    severity: Severity


class RequiredEvidence(BaseModel):
    functional_tests: list[str] = Field(default_factory=list)
    invariant_checks: list[str] = Field(default_factory=list)
    type_check: list[str] = Field(default_factory=list)
    lint: list[str] = Field(default_factory=list)
    api_compatibility: list[str] = Field(default_factory=list)
    security_check: list[str] = Field(default_factory=list)
    regression_tests: list[str] = Field(default_factory=list)


class ChangeContract(BaseModel):
    contract_id: str = Field(..., description="Unique contract ID, e.g. cc-s01-001")
    created_at: datetime
    scenario_id: str = Field(..., description="Benchmark scenario ID, e.g. s01")
    request_raw: str = Field(..., description="Verbatim developer request")
    request_normalized: str = Field(..., description="Normalized single-sentence summary")
    intended_behavior: list[str] = Field(..., description="What should be true after this change")
    functional_requirements: list[FunctionalRequirement]
    invariants: list[Invariant]
    affected_components: list[str]
    api_implications: list[str] = Field(default_factory=list)
    data_schema_implications: list[str] = Field(default_factory=list)
    security_concerns: list[str] = Field(default_factory=list)
    required_evidence: RequiredEvidence
    estimated_regression_risk: RegressionRisk
    rollback_requirements: list[str] = Field(default_factory=list)
    notes: str | None = None
