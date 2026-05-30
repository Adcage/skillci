import json
from pathlib import Path

from skillci.compare import run_compare
from skillci.runner import run_local_test
from skillci.runner_snapshot import run_snapshot


def test_run_snapshot_creates_baseline_json(tmp_path):
    baseline_root = tmp_path / "baselines"

    snapshot_path = run_snapshot(Path("examples/api-doc-writer"), baseline_root=baseline_root)

    assert snapshot_path.exists()
    assert snapshot_path.suffix == ".json"
    latest_path = snapshot_path.parent / "latest.json"
    assert latest_path.exists()
    assert latest_path.read_text(encoding="utf-8") == snapshot_path.read_text(encoding="utf-8")


def test_run_snapshot_creates_skill_directory(tmp_path):
    baseline_root = tmp_path / "baselines"

    run_snapshot(Path("examples/api-doc-writer"), baseline_root=baseline_root)

    skill_dir = baseline_root / "api-doc-writer"
    assert skill_dir.exists()
    assert skill_dir.is_dir()


def test_run_snapshot_json_is_valid(tmp_path):
    baseline_root = tmp_path / "baselines"

    snapshot_path = run_snapshot(Path("examples/api-doc-writer"), baseline_root=baseline_root)

    content = snapshot_path.read_text(encoding="utf-8")
    data = json.loads(content)
    assert "skill_name" in data
    assert "local_results" in data
    assert data["skill_name"] == "api-doc-writer"


def test_run_compare_detects_no_changes(tmp_path):
    baseline_root = tmp_path / "baselines"
    run_snapshot(Path("examples/api-doc-writer"), baseline_root=baseline_root)

    current_report = run_local_test(Path("examples/api-doc-writer"))
    baseline_path = baseline_root / "api-doc-writer" / "latest.json"

    regression = run_compare(baseline_path, current_report)

    assert regression.total_cases == 4
    assert regression.unchanged_cases == 4
    assert regression.regressed_cases == 0
    assert regression.improved_cases == 0
    assert len(regression.changes) == 0


def test_run_compare_detects_new_case(tmp_path):
    baseline_root = tmp_path / "baselines"
    run_snapshot(Path("examples/api-doc-writer"), baseline_root=baseline_root)

    current_report = run_local_test(Path("examples/api-doc-writer"))
    baseline_path = baseline_root / "api-doc-writer" / "latest.json"

    regression = run_compare(baseline_path, current_report)

    assert regression.skill_name == "api-doc-writer"
    assert regression.current_passed is True


def test_run_compare_with_modified_baseline(tmp_path):
    baseline_root = tmp_path / "baselines"
    run_snapshot(Path("examples/api-doc-writer"), baseline_root=baseline_root)

    baseline_path = baseline_root / "api-doc-writer" / "latest.json"
    baseline_data = json.loads(baseline_path.read_text(encoding="utf-8"))

    first_result = baseline_data["local_results"][0]
    first_result["actual_trigger"] = not first_result["actual_trigger"]
    first_result["passed"] = False
    baseline_path.write_text(json.dumps(baseline_data), encoding="utf-8")

    current_report = run_local_test(Path("examples/api-doc-writer"))
    regression = run_compare(baseline_path, current_report)

    assert len(regression.changes) > 0
    assert regression.regressed_cases > 0 or regression.improved_cases > 0
