"""Repair Log schema — record of repairs applied after adversarial findings."""
from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class RepairStatus(str, Enum):  # noqa: UP042
    applied = "applied"
    verified = "verified"
    failed = "failed"


class RepairEntry(BaseModel):
    repair_id: str = Field(..., pattern=r"^rp-\d{2}$", description="e.g. rp-01")
    finding_id: str = Field(..., description="References AdversarialFinding.finding_id")
    applied_at: datetime
    description: str = Field(..., description="What was changed to fix the finding")
    files_modified: list[str] = Field(default_factory=list)
    status: RepairStatus
    post_repair_pytest_exit_code: int | None = None
    post_repair_mypy_exit_code: int | None = None
    notes: str | None = None


class RepairLog(BaseModel):
    log_id: str = Field(..., description="e.g. rl-s01-001")
    contract_id: str
    scenario_id: str
    repairs: list[RepairEntry] = Field(default_factory=list)

    @property
    def repair_count(self) -> int:
        return len(self.repairs)

    @property
    def all_verified(self) -> bool:
        return all(r.status == RepairStatus.verified for r in self.repairs)
