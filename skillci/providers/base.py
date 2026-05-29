from skillci.schema.config import JudgeConfig, SkillTestCase
from skillci.schema.result import LLMTriggerResult
from skillci.schema.skill import Skill


class JudgeProvider:
    def judge_trigger(
        self,
        skill: Skill,
        case: SkillTestCase,
        config: JudgeConfig,
    ) -> LLMTriggerResult:
        raise NotImplementedError
