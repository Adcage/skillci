from pydantic import BaseModel, Field

from skillci.schema.result import (
    LLMTriggerResult,
    LocalTriggerResult,
    StaticHealthResult,
    TriggerMetrics,
)


class SkillCIReport(BaseModel):
    skill_name: str
    skill_path: str
    static_health: StaticHealthResult
    local_results: list[LocalTriggerResult] = Field(default_factory=list)
    llm_results: list[LLMTriggerResult] = Field(default_factory=list)
    local_metrics: TriggerMetrics | None = None
    llm_metrics: TriggerMetrics | None = None
    llm_average_confidence: float | None = None
    passed: bool
