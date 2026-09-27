"""Verification Evidence schema — deterministic tool outputs."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class TestResult(BaseModel):
    node_id: str
    outcome: str  # "passed" | "failed" | "error" | "skipped"
    duration_seconds: float
    failure_message: str | None = None


class PytestEvidence(BaseModel):
    exit_code: int
    tests_total: int
    tests_passed: int
    tests_failed: int
    tests_errors: int
    tests_skipped: int
    duration_seconds: float
    results: list[TestResult] = Field(default_factory=list)
    raw_summary: str = Field(..., description="Last line(s) of pytest output")


class MypyEvidence(BaseModel):
    exit_code: int
    error_count: int
    errors: list[str] = Field(default_factory=list)
    raw_output: str


class RuffEvidence(BaseModel):
    exit_code: int
    violation_count: int
    violations: list[dict[str, Any]] = Field(default_factory=list)
    raw_output: str


class GitDiffEvidence(BaseModel):
    changed_files: list[str]
    diff_stat: str


class VerificationEvidence(BaseModel):
    evidence_id: str = Field(..., description="e.g. ve-s01-001")
    contract_id: str
    scenario_id: str
    collected_at: datetime
    pytest: PytestEvidence
    mypy: MypyEvidence
    ruff: RuffEvidence
    git_diff: GitDiffEvidence

    @property
    def pytest_exit_code(self) -> int:
        return self.pytest.exit_code

    @property
    def mypy_exit_code(self) -> int:
        return self.mypy.exit_code

    @property
    def ruff_exit_code(self) -> int:
        return self.ruff.exit_code

    @property
    def all_deterministic_pass(self) -> bool:
        return (
            self.pytest.exit_code == 0
            and self.mypy.exit_code == 0
            and self.ruff.exit_code == 0
        )
