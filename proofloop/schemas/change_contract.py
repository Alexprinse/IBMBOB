"""Change Contract schema — the machine-readable specification of a developer request."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class Priority(str, Enum):
    must_have = "must_have"
    should_have = "should_have"
    nice_to_have = "nice_to_have"


class Severity(str, Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"


class RegressionRisk(str, Enum):
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
    functional_tests: List[str] = Field(default_factory=list)
    invariant_checks: List[str] = Field(default_factory=list)
    type_check: List[str] = Field(default_factory=list)
    lint: List[str] = Field(default_factory=list)
    api_compatibility: List[str] = Field(default_factory=list)
    security_check: List[str] = Field(default_factory=list)
    regression_tests: List[str] = Field(default_factory=list)


class ChangeContract(BaseModel):
    contract_id: str = Field(..., description="Unique contract ID, e.g. cc-s01-001")
    created_at: datetime
    scenario_id: str = Field(..., description="Benchmark scenario ID, e.g. s01")
    request_raw: str = Field(..., description="Verbatim developer request")
    request_normalized: str = Field(..., description="Normalized single-sentence summary")
    intended_behavior: List[str] = Field(..., description="What should be true after this change")
    functional_requirements: List[FunctionalRequirement]
    invariants: List[Invariant]
    affected_components: List[str]
    api_implications: List[str] = Field(default_factory=list)
    data_schema_implications: List[str] = Field(default_factory=list)
    security_concerns: List[str] = Field(default_factory=list)
    required_evidence: RequiredEvidence
    estimated_regression_risk: RegressionRisk
    rollback_requirements: List[str] = Field(default_factory=list)
    notes: Optional[str] = None
