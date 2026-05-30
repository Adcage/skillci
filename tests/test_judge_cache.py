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


def test_cache_key_varies_with_skill_description():
    case = SkillTestCase(name="case1", input="input", expected_trigger=True)
    config = JudgeConfig()
    skill1 = Skill(
        name="test",
        description="description A",
        body="body",
        path=Path("."),
        skill_md_path=Path("./SKILL.md"),
    )
    skill2 = Skill(
        name="test",
        description="description B",
        body="body",
        path=Path("."),
        skill_md_path=Path("./SKILL.md"),
    )
    key1 = build_judge_cache_key(skill1, case, config)
    key2 = build_judge_cache_key(skill2, case, config)
    assert key1 != key2


def test_cache_key_varies_with_case_input():
    skill = Skill(
        name="test",
        description="desc",
        body="body",
        path=Path("."),
        skill_md_path=Path("./SKILL.md"),
    )
    config = JudgeConfig()
    case1 = SkillTestCase(name="case1", input="input A", expected_trigger=True)
    case2 = SkillTestCase(name="case1", input="input B", expected_trigger=True)
    key1 = build_judge_cache_key(skill, case1, config)
    key2 = build_judge_cache_key(skill, case2, config)
    assert key1 != key2


def test_cache_key_varies_with_provider():
    skill = Skill(
        name="test",
        description="desc",
        body="body",
        path=Path("."),
        skill_md_path=Path("./SKILL.md"),
    )
    case = SkillTestCase(name="case1", input="input", expected_trigger=True)
    config1 = JudgeConfig(provider="openai")
    config2 = JudgeConfig(provider="anthropic")
    key1 = build_judge_cache_key(skill, case, config1)
    key2 = build_judge_cache_key(skill, case, config2)
    assert key1 != key2


def test_cache_key_varies_with_base_url():
    skill = Skill(
        name="test",
        description="desc",
        body="body",
        path=Path("."),
        skill_md_path=Path("./SKILL.md"),
    )
    case = SkillTestCase(name="case1", input="input", expected_trigger=True)
    config1 = JudgeConfig(base_url="https://api.openai.com/v1")
    config2 = JudgeConfig(base_url="https://custom-api.example.com/v1")
    key1 = build_judge_cache_key(skill, case, config1)
    key2 = build_judge_cache_key(skill, case, config2)
    assert key1 != key2


def test_cache_key_includes_prompt_version():
    from skillci.evaluator.prompt import PROMPT_VERSION

    skill = Skill(
        name="test",
        description="desc",
        body="body",
        path=Path("."),
        skill_md_path=Path("./SKILL.md"),
    )
    case = SkillTestCase(name="case1", input="input", expected_trigger=True)
    config = JudgeConfig()
    key = build_judge_cache_key(skill, case, config)

    assert isinstance(key, str)
    assert len(key) == 64
    assert PROMPT_VERSION is not None


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


def test_cache_creates_directory_on_set(tmp_path):
    cache_dir = tmp_path / "nested" / "cache"
    cache = JudgeCache(cache_dir=cache_dir)
    assert not cache_dir.exists()
    result = LLMTriggerResult(
        case_name="test",
        expected_trigger=True,
        score=0.9,
        reasoning="test",
    )
    cache.set("key", result)
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


def test_cache_overwrites_existing_key(tmp_path):
    cache = JudgeCache(cache_dir=tmp_path)

    result1 = LLMTriggerResult(
        case_name="test",
        expected_trigger=True,
        actual_trigger=True,
        passed=True,
        confidence=0.9,
    )
    cache.set("key", result1)

    result2 = LLMTriggerResult(
        case_name="test",
        expected_trigger=True,
        actual_trigger=False,
        passed=False,
        confidence=0.8,
    )
    cache.set("key", result2)

    cached = cache.get("key")
    assert cached is not None
    assert cached.actual_trigger is False
    assert cached.passed is False


def test_cache_multiple_keys(tmp_path):
    cache = JudgeCache(cache_dir=tmp_path)

    for i in range(5):
        result = LLMTriggerResult(
            case_name=f"case-{i}",
            expected_trigger=True,
            actual_trigger=True,
            passed=True,
        )
        cache.set(f"key-{i}", result)

    for i in range(5):
        cached = cache.get(f"key-{i}")
        assert cached is not None
        assert cached.case_name == f"case-{i}"


def test_cache_returns_none_for_corrupted_file(tmp_path):
    cache = JudgeCache(cache_dir=tmp_path)
    cache_path = tmp_path / "corrupted.json"
    cache_path.write_text("not valid json{", encoding="utf-8")

    assert cache.get("corrupted") is None


def test_cache_returns_none_for_empty_file(tmp_path):
    cache = JudgeCache(cache_dir=tmp_path)
    cache_path = tmp_path / "empty.json"
    cache_path.write_text("", encoding="utf-8")

    assert cache.get("empty") is None


def test_cache_handles_special_characters_in_key(tmp_path):
    cache = JudgeCache(cache_dir=tmp_path)
    result = LLMTriggerResult(
        case_name="test",
        expected_trigger=True,
        actual_trigger=True,
        passed=True,
    )

    special_key = "key_with_special_chars_123"
    cache.set(special_key, result)
    cached = cache.get(special_key)
    assert cached is not None


def test_cache_key_sha256_format():
    skill = Skill(
        name="test",
        description="desc",
        body="body",
        path=Path("."),
        skill_md_path=Path("./SKILL.md"),
    )
    case = SkillTestCase(name="case1", input="input", expected_trigger=True)
    config = JudgeConfig()
    key = build_judge_cache_key(skill, case, config)

    assert len(key) == 64
    assert all(c in "0123456789abcdef" for c in key)


def test_cache_key_varies_with_skill_body():
    case = SkillTestCase(name="case1", input="input", expected_trigger=True)
    config = JudgeConfig()

    skill1 = Skill(
        name="test",
        description="desc",
        body="body content A",
        path=Path("."),
        skill_md_path=Path("./SKILL.md"),
    )
    skill2 = Skill(
        name="test",
        description="desc",
        body="body content B",
        path=Path("."),
        skill_md_path=Path("./SKILL.md"),
    )

    key1 = build_judge_cache_key(skill1, case, config)
    key2 = build_judge_cache_key(skill2, case, config)
    assert key1 != key2


def test_cache_key_truncates_long_body():
    skill = Skill(
        name="test",
        description="desc",
        body="x" * 1000,
        path=Path("."),
        skill_md_path=Path("./SKILL.md"),
    )
    case = SkillTestCase(name="case1", input="input", expected_trigger=True)
    config = JudgeConfig()

    key = build_judge_cache_key(skill, case, config)
    assert len(key) == 64
