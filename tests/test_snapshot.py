from pathlib import Path

from skillci.runner_snapshot import run_snapshot


def test_run_snapshot_creates_baseline_json(tmp_path):
    baseline_root = tmp_path / "baselines"

    snapshot_path = run_snapshot(Path("examples/api-doc-writer"), baseline_root=baseline_root)

    assert snapshot_path.exists()
    assert snapshot_path.suffix == ".json"
    latest_path = snapshot_path.parent / "latest.json"
    assert latest_path.exists()
    assert latest_path.read_text(encoding="utf-8") == snapshot_path.read_text(encoding="utf-8")
