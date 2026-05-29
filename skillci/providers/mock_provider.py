from skillci.providers.base import JudgeProvider
from skillci.schema.config import JudgeConfig, SkillTestCase
from skillci.schema.result import LLMTriggerResult
from skillci.schema.skill import Skill


class MockJudgeProvider(JudgeProvider):
    def judge_trigger(
        self,
        skill: Skill,
        case: SkillTestCase,
        config: JudgeConfig,
    ) -> LLMTriggerResult:
        actual_trigger = case.expected_trigger
        return LLMTriggerResult(
            case_name=case.name,
            expected_trigger=case.expected_trigger,
            actual_trigger=actual_trigger,
            confidence=0.92 if actual_trigger else 0.88,
            passed=True,
            reason="mock judge returned expected result",
        )
