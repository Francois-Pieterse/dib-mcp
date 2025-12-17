import json

from pathlib import Path
from typing import Any

from server.tools.wizard_engine.option_provider_base import (
    enrich_step_with_options,
)


class StepManager:
    def __init__(self, steps_cfg: dict[str, Any]) -> None:
        self._cfg = steps_cfg
        self._steps = steps_cfg.get("steps", [])

    @classmethod
    def load(cls, file: str | Path) -> "StepManager":
        if isinstance(file, str):
            file = Path(file)

        with file.open("r", encoding="utf-8") as f:
            cfg = json.load(f)
        return cls(cfg)

    def first(self) -> dict[str, Any] | None:
        return self._steps[0] if self._steps else None

    def get(self, step_id: str) -> dict[str, Any] | None:
        for step in self._steps:
            if step.get("id") == step_id:
                return step
        return None

    def next_after(self, step_id: str) -> dict[str, Any] | None:
        for idx, step in enumerate(self._steps):
            if step.get("id") == step_id:
                return self._steps[idx + 1] if idx + 1 < len(self._steps) else None
        return None

    def enrich(
        self, step_cfg: dict[str, Any], wizard_state: dict[str, Any]
    ) -> dict[str, Any]:
        return enrich_step_with_options(
            step_cfg, context={"wizard_state": wizard_state}
        )
