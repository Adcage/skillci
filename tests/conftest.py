import pytest

from skillci.evaluator import llm_trigger_judge


@pytest.fixture(autouse=True)
def isolate_mock_provider():
    """确保每个测试都使用正确的 MockJudgeProvider，防止测试间污染。"""
    original_providers = llm_trigger_judge._PROVIDERS.copy()
    original_cache = llm_trigger_judge._cache

    yield

    llm_trigger_judge._PROVIDERS.clear()
    llm_trigger_judge._PROVIDERS.update(original_providers)
    llm_trigger_judge._cache = original_cache
