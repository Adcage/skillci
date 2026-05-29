from enum import StrEnum

from pydantic import BaseModel, Field


class Severity(StrEnum):
    info = "info"
    warning = "warning"
    error = "error"


class LintIssue(BaseModel):
    code: str
    severity: Severity
    message: str
    file: str | None = None
    line: int | None = None


class StaticHealthResult(BaseModel):
    passed: bool
    issues: list[LintIssue] = Field(default_factory=list)


class LocalTriggerResult(BaseModel):
    case_name: str
    expected_trigger: bool
    actual_trigger: bool
    trigger_score: float
    passed: bool
    reason: str
    matched_terms: list[str] = Field(default_factory=list)
    missing_terms: list[str] = Field(default_factory=list)


class TriggerMetrics(BaseModel):
    true_positive: int = 0
    false_positive: int = 0
    true_negative: int = 0
    false_negative: int = 0
    precision: float = 0
    recall: float = 0
    f1: float = 0
    accuracy: float = 0


class LLMTriggerResult(BaseModel):
    case_name: str
    expected_trigger: bool
    actual_trigger: bool | None = None
    confidence: float | None = None
    passed: bool = False
    reason: str | None = None
    raw_response: str | None = None
    error: str | None = None
