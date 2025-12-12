import json

from pathlib import Path
from typing import Any

ValidationError = dict[str, str]


class Validation:
    """
    Field/value validation driven by a JSON config.

    Config format (JSON array):

    [
      {
        "fields": ["width", "height"],
        "function": "_pos_int",
        "nullable": false
      },
      {
        "fields": ["caption"],
        "function": "_str",
        "nullable": true
      },
      {
        "fields": ["custom_css"],
        "function": "_validate_css_snippet",
        "nullable": true
      }
    ]

    - `fields`: list of field names that share the same rule.
    - `function`: name of a validator method on this class.
    - `nullable`: if true, empty values are allowed and skip further validation.
    """

    def __init__(self, config_path: Path) -> None:
        self.config_path = config_path
        self._rules: dict[str, dict] = {}
        self.load_config()

    def load_config(self) -> None:
        """
        Load or reload validation rules from the JSON config file.
        """
        if not self.config_path.exists():
            self._rules = {}
            return

        with self.config_path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        by_field: dict[str, dict[str, Any]] = {}

        for entry in data:
            fields = entry.get("fields") or []
            if not isinstance(fields, list):
                continue

            rule = {
                "function": entry.get("function")
                or "_str",  # default to string validator
                "nullable": bool(entry.get("nullable", True)),
            }

            for raw_name in fields:
                name = str(raw_name).strip()
                if not name:
                    continue
                # Last entry wins for duplicate field names
                by_field[name] = rule

        self._rules = by_field

    def validate(self, field: str, value: Any) -> tuple[bool, ValidationError | None]:
        """
        Validate a value for a given field.

        Returns (ok, error_dict_or_none).
        error_dict has keys: "field" and "message".
        """
        rule = self._rules.get(field)
        if not rule:
            # No rule configured means no validation
            return True, None

        func_name = rule["function"]
        nullable = rule["nullable"]

        if value is None or value == "":
            if nullable:
                return True, None
            return False, {
                "field": field,
                "message": f"'{field}' may not be empty.",
            }

        raw = str(value)

        validator = getattr(self, func_name, None)
        if not callable(validator):
            return False, {
                "field": field,
                "message": f"Validator '{func_name}' is not defined for '{field}'.",
            }

        ok, msg = validator(raw, field=field)
        if ok:
            return True, None
        return False, {"field": field, "message": msg}

    def _int(self, raw: str, *, field: str) -> tuple[bool, str]:
        try:
            int(raw)
            return True, ""
        except ValueError:
            return False, f"'{field}' must be an integer."

    def _pos_int(self, raw: str, *, field: str) -> tuple[bool, str]:
        try:
            value = int(raw)
        except ValueError:
            return False, f"'{field}' must be a positive integer."
        if value <= 0:
            return False, f"'{field}' must be a positive integer."
        return True, ""

    def _float(self, raw: str, *, field: str) -> tuple[bool, str]:
        try:
            float(raw)
            return True, ""
        except ValueError:
            return False, f"'{field}' must be a number."

    def _pos_float(self, raw: str, *, field: str) -> tuple[bool, str]:
        try:
            value = float(raw)
        except ValueError:
            return False, f"'{field}' must be a positive number."
        if value <= 0:
            return False, f"'{field}' must be a positive number."
        return True, ""

    def _str(self, raw: str, *, field: str) -> tuple[bool, str]:
        # Always valid as a string
        return True, ""

    def _bool(self, raw: str, *, field: str) -> tuple[bool, str]:
        TRUTHY = {"1"}
        FALSY = {"0"}
        lower = raw.strip().lower()
        if lower in TRUTHY or lower in FALSY:
            return True, ""
        return False, f"'{field}' must be a boolean value (true/false or 1/0)."

    def _wrap(self, raw: str, *, field: str) -> tuple[bool, str]:
        ALLOWED_VALUES = {"", "wrap", "nowrap", "wrap-reverse"}
        if raw in ALLOWED_VALUES:
            return True, ""
        return False, f"'{field}' must be one of: {', '.join(ALLOWED_VALUES)}."

    def _align_content(self, raw: str, *, field: str) -> tuple[bool, str]:
        ALLOWED_VALUES = {
            "",
            "flex-start",
            "flex-end",
            "center",
            "space-between",
            "space-around",
            "space-evenly",
            "stretch",
            "baseline",
        }
        if raw in ALLOWED_VALUES:
            return True, ""
        return False, f"'{field}' must be one of: {', '.join(ALLOWED_VALUES)}."


config_path = Path(__file__).parent / "validation_function_config.json"

validator = Validation(config_path)
