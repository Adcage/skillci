from skillci.cache.cache_key import build_judge_cache_key
from skillci.cache.judge_cache import JudgeCache
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

_cache: JudgeCache | None = None


def _get_cache() -> JudgeCache:
    global _cache
    if _cache is None:
        _cache = JudgeCache()
    return _cache


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
    config = judge_config or JudgeConfig()

    if config.cache:
        cache = _get_cache()
        cache_key = build_judge_cache_key(skill, case, config)
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

    provider = _provider_for_name(provider_name)
    result = provider.judge_trigger(skill, case, config)

    if result.error:
        return result

    if result.actual_trigger is None:
        final_result = LLMTriggerResult(
            case_name=case.name,
            expected_trigger=case.expected_trigger,
            actual_trigger=None,
            confidence=result.confidence,
            passed=False,
            reason=result.reason,
            raw_response=result.raw_response,
            error="LLM judge did not return should_trigger",
        )
    else:
        passed = result.actual_trigger == case.expected_trigger
        final_result = LLMTriggerResult(
            case_name=case.name,
            expected_trigger=case.expected_trigger,
            actual_trigger=result.actual_trigger,
            confidence=result.confidence,
            passed=passed,
            reason=result.reason,
            raw_response=result.raw_response,
        )

    if config.cache:
        cache.set(cache_key, final_result)

    return final_result
