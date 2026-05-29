from datetime import datetime
from pathlib import Path

from skillci.runner import run_local_test


def run_snapshot(skill_path: Path, baseline_root: Path | None = None) -> Path:
    baseline_root = (baseline_root or Path(".skillci/baselines")).resolve()
    report = run_local_test(skill_path)

    skill_dir = baseline_root / report.skill_name
    skill_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    snapshot_path = skill_dir / f"{timestamp}.json"
    latest_path = skill_dir / "latest.json"

    snapshot_path.write_text(report.model_dump_json(indent=2), encoding="utf-8")
    latest_path.write_text(report.model_dump_json(indent=2), encoding="utf-8")
    return snapshot_path
