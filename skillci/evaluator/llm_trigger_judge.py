
from skillci.providers.base import JudgeProvider
from skillci.providers.mock_provider import MockJudgeProvider
from skillci.providers.openai_provider import OpenAIJudgeProvider
from skillci.schema.config import JudgeConfig, SkillTestCase, ThresholdConfig
from skillci.schema.result import LLMTriggerResult
from skillci.schema.skill import Skill

_PROVIDERS: dict[str, type[JudgeProvider]] = {
    "mock": MockJudgeProvider,
    "openai": OpenAIJudgeProvider,
}


def _provider_for_name(name: str) -> JudgeProvider:
    provider_cls = _PROVIDERS.get(name)
    if provider_cls is None:
        raise ValueError(f"Unsupported judge provider: {name}")
    return provider_cls()


def run_llm_judge(
    skill: Skill,
    case: SkillTestCase,
    thresholds: ThresholdConfig,
    provider_name: str = "openai",
    judge_config: JudgeConfig | None = None,
) -> LLMTriggerResult:
    provider = _provider_for_name(provider_name)
    config = judge_config or JudgeConfig()
    result = provider.judge_trigger(skill, case, config)

    if result.error:
        return result

    if result.actual_trigger is None:
        return LLMTriggerResult(
            case_name=case.name,
            expected_trigger=case.expected_trigger,
            actual_trigger=None,
            confidence=result.confidence,
            passed=False,
            reason=result.reason,
            raw_response=result.raw_response,
            error="LLM judge did not return should_trigger",
        )

    passed = result.actual_trigger == case.expected_trigger
    return LLMTriggerResult(
        case_name=case.name,
        expected_trigger=case.expected_trigger,
        actual_trigger=result.actual_trigger,
        confidence=result.confidence,
        passed=passed,
        reason=result.reason,
        raw_response=result.raw_response,
    )
