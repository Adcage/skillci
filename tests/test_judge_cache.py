from pathlib import Path

from skillci.cache.cache_key import build_judge_cache_key
from skillci.cache.judge_cache import JudgeCache
from skillci.schema.config import JudgeConfig, SkillTestCase
from skillci.schema.result import LLMTriggerResult
from skillci.schema.skill import Skill


def test_cache_key_deterministic():
    skill = Skill(
        name="test",
        description="desc",
        body="body",
        path=Path("."),
        skill_md_path=Path("./SKILL.md"),
    )
    case = SkillTestCase(name="case1", input="input", expected_trigger=True)
    config = JudgeConfig()
    key1 = build_judge_cache_key(skill, case, config)
    key2 = build_judge_cache_key(skill, case, config)
    assert key1 == key2
    assert len(key1) == 64


def test_cache_key_varies_with_skill_name():
    case = SkillTestCase(name="case1", input="input", expected_trigger=True)
    config = JudgeConfig()
    skill1 = Skill(
        name="skill-a",
        description="desc",
        body="body",
        path=Path("."),
        skill_md_path=Path("./SKILL.md"),
    )
    skill2 = Skill(
        name="skill-b",
        description="desc",
        body="body",
        path=Path("."),
        skill_md_path=Path("./SKILL.md"),
    )
    key1 = build_judge_cache_key(skill1, case, config)
    key2 = build_judge_cache_key(skill2, case, config)
    assert key1 != key2


def test_cache_key_varies_with_model():
    skill = Skill(
        name="test",
        description="desc",
        body="body",
        path=Path("."),
        skill_md_path=Path("./SKILL.md"),
    )
    case = SkillTestCase(name="case1", input="input", expected_trigger=True)
    config1 = JudgeConfig(model="gpt-4o-mini")
    config2 = JudgeConfig(model="gpt-4o")
    key1 = build_judge_cache_key(skill, case, config1)
    key2 = build_judge_cache_key(skill, case, config2)
    assert key1 != key2


def test_cache_set_and_get(tmp_path):
    cache = JudgeCache(cache_dir=tmp_path)
    result = LLMTriggerResult(
        case_name="test",
        expected_trigger=True,
        actual_trigger=True,
        passed=True,
        confidence=0.9,
        reason="matches",
    )
    cache.set("testkey", result)
    cached = cache.get("testkey")
    assert cached is not None
    assert cached.case_name == "test"
    assert cached.actual_trigger is True
    assert cached.passed is True
    assert cached.confidence == 0.9
    assert cached.reason == "matches"


def test_cache_miss_returns_none(tmp_path):
    cache = JudgeCache(cache_dir=tmp_path)
    assert cache.get("nonexistent") is None


def test_cache_creates_directory(tmp_path):
    cache_dir = tmp_path / "nested" / "cache"
    JudgeCache(cache_dir=cache_dir)
    assert cache_dir.exists()


def test_cache_file_contains_cached_at(tmp_path):
    cache = JudgeCache(cache_dir=tmp_path)
    result = LLMTriggerResult(
        case_name="test",
        expected_trigger=True,
        actual_trigger=True,
        passed=True,
    )
    cache.set("testkey", result)
    import json

    data = json.loads((tmp_path / "testkey.json").read_text(encoding="utf-8"))
    assert "cached_at" in data


def test_cache_with_error_result(tmp_path):
    cache = JudgeCache(cache_dir=tmp_path)
    result = LLMTriggerResult(
        case_name="test",
        expected_trigger=True,
        actual_trigger=None,
        passed=False,
        error="API timeout",
    )
    cache.set("testkey", result)
    cached = cache.get("testkey")
    assert cached is not None
    assert cached.error == "API timeout"
    assert cached.actual_trigger is None
