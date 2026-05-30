import json
from datetime import datetime, timezone
from pathlib import Path

from skillci.schema.result import LLMTriggerResult


class JudgeCache:
    def __init__(self, cache_dir: Path | None = None):
        self.cache_dir = cache_dir or Path(".skillci/cache")

    def _cache_path(self, key: str) -> Path:
        return self.cache_dir / f"{key}.json"

    def get(self, key: str) -> LLMTriggerResult | None:
        path = self._cache_path(key)
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            data.pop("cached_at", None)
            return LLMTriggerResult(**data)
        except (json.JSONDecodeError, OSError, TypeError):
            return None

    def set(self, key: str, result: LLMTriggerResult) -> None:
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        path = self._cache_path(key)
        data = result.model_dump()
        data["cached_at"] = datetime.now(timezone.utc).isoformat()
        path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
