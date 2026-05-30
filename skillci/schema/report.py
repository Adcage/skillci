from pydantic import BaseModel, Field

from skillci.schema.result import (
    JudgeDisagreement,
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
    judge_disagreement_count: int = 0
    judge_disagreements: list[JudgeDisagreement] = Field(default_factory=list)
    passed: bool
