from skillci.runner_init import run_init


def test_run_init_creates_default_config(tmp_path):
    target = tmp_path / "demo-skill"
    target.mkdir()
    (target / "SKILL.md").write_text(
        "---\nname: demo\ndescription: Demo skill for unit tests.\n---\n# Demo\n",
        encoding="utf-8",
    )

    config_path = run_init(target)

    assert config_path.exists()
    content = config_path.read_text(encoding="utf-8")
    assert "cases" in content
    assert "trigger_score" in content


def test_run_init_does_not_overwrite_existing_config(tmp_path):
    target = tmp_path / "demo-skill"
    target.mkdir()
    (target / "SKILL.md").write_text(
        "---\nname: demo\ndescription: Demo skill for unit tests.\n---\n# Demo\n",
        encoding="utf-8",
    )
    config_path = target / "skillci.yaml"
    config_path.write_text("skill: .\nmode: local\ncases: []\n", encoding="utf-8")

    result_path = run_init(target)

    assert result_path == config_path
    assert config_path.read_text(encoding="utf-8") == "skill: .\nmode: local\ncases: []\n"
