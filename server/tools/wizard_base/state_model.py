import json

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

STATE_FILE = Path("server/tools/application_wizard/state/wizard_state.json")


@dataclass
class WizardState:
    current_step_id: str | None = None
    completed_step_ids: list[str] = field(default_factory=list)
    answers: dict[str, dict[str, Any]] = field(default_factory=dict)
    meta: dict[str, Any] = field(default_factory=dict)
    completed: bool = False

    @classmethod
    def load(cls) -> "WizardState":
        if not STATE_FILE.exists():
            return cls()
        with STATE_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(
            current_step_id=data.get("current_step_id"),
            completed_step_ids=data.get("completed_step_ids", []),
            answers=data.get("answers", {}),
            meta=data.get("meta", {}),
            completed=data.get("completed", False),
        )

    def save(self) -> None:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with STATE_FILE.open("w", encoding="utf-8") as f:
            json.dump(
                {
                    "current_step_id": self.current_step_id,
                    "completed_step_ids": self.completed_step_ids,
                    "answers": self.answers,
                    "meta": self.meta,
                    "completed": self.completed,
                },
                f,
                indent=2,
            )

    @classmethod
    def reset(cls, meta: dict[str, Any] | None = None) -> "WizardState":
        state = cls(meta=meta or {})
        state.save()
        return state
