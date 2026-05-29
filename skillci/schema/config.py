from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, Field


class RunMode(StrEnum):
    local = "local"
    llm = "llm"
    both = "both"


class ThresholdConfig(BaseModel):
    trigger_score: float = 0.6
    trigger_f1: float = 0.8
    llm_confidence: float = 0.7


class JudgeConfig(BaseModel):
    provider: str = "openai"
    model: str = "gpt-4.1-mini"
    temperature: float = 0
    timeout: int = 30
    cache: bool = True


class SkillTestCase(BaseModel):
    name: str
    input: str
    expected_trigger: bool
    tags: list[str] = Field(default_factory=list)


class SkillCIConfig(BaseModel):
    skill: Path
    mode: RunMode = RunMode.local
    judge: JudgeConfig = Field(default_factory=JudgeConfig)
    thresholds: ThresholdConfig = Field(default_factory=ThresholdConfig)
    cases: list[SkillTestCase]
