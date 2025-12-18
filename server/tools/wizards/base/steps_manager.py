import json

from pathlib import Path
from typing import Any

from tools.wizards.base.option_provider_base import (
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

    @staticmethod
    def _is_included(
        step_cfg: dict[str, Any], previous_answers: dict[str, Any] | None = None
    ) -> bool:
        include_if = step_cfg.get("include_if")
        if not include_if:  # No conditions, always include
            return True

        if not previous_answers:  # No previous answers to evaluate conditions
            return False  # Rather exclude than include

        for key, expected_value in include_if.items():
            # Key is in format: "step_id.field_name"
            if "." not in key:
                return False

            step_id, field = key.split(".", 1)

            step_answers = previous_answers.get(step_id, {})
            actual_value = step_answers.get(field)

            if actual_value != expected_value:  # Logical AND for all conditions
                return False

        return True

    def next_after(
        self, step_id: str, previous_answers: dict[str, Any] | None = None
    ) -> dict[str, Any] | None:
        for idx, step in enumerate(self._steps):
            if step.get("id") != step_id:
                continue

            # Scan until the next included step is found
            for j in range(idx + 1, len(self._steps)):
                candidate = self._steps[j]
                if self._is_included(candidate, previous_answers):
                    return candidate
            return None
        return None

    def enrich(
        self, step_cfg: dict[str, Any], wizard_state: dict[str, Any]
    ) -> dict[str, Any]:
        return enrich_step_with_options(
            step_cfg, context={"wizard_state": wizard_state}
        )
