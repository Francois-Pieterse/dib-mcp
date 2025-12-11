from typing import Any, Callable
import re

ValidationError = dict[str, str]
FieldCfg = dict[str, Any]


def _add_error(errors: list[ValidationError], field: str, message: str) -> None:
    errors.append({"field": field, "message": message})


def _validate_string(
    field: FieldCfg, value: Any, errors: list[ValidationError]
) -> None:
    name = field["name"]
    if not isinstance(value, str):
        _add_error(errors, name, f"'{name}' must be a string value.")


def _validate_enum(field: FieldCfg, value: Any, errors: list[ValidationError]) -> None:
    name = field["name"]
    options = field.get("options") or []
    allowed_values = [opt.get("value") for opt in options if isinstance(opt, dict)]
    if allowed_values and value not in allowed_values:
        allowed = ", ".join(map(str, allowed_values))
        _add_error(errors, name, f"'{name}' must be one of: {allowed}.")


def _validate_identifier(
    field: FieldCfg, value: Any, errors: list[ValidationError]
) -> None:
    name = field["name"]
    if not isinstance(value, str):
        _add_error(errors, name, f"'{name}' must be a string value.")
        return

    if not re.fullmatch(r"[a-z][a-zA-Z0-9]*", value):
        _add_error(
            errors,
            name,
            (
                "Name must start with a lowercase letter and contain only "
                "letters and digits, with no spaces."
            ),
        )


def _validate_table_settings(
    field: FieldCfg, value: Any, errors: list[ValidationError]
) -> None:
    name = field["name"]
    rows = value or []

    if not isinstance(rows, list):
        _add_error(errors, name, f"'{name}' must be a list of table settings.")
        return

    ENFORCED_SETTINGS = ["id", "name", "ignore"]
    BOOL_SETTINGS = ["ignore", "create_grid", "create_form"]

    for idx, row in enumerate(rows):
        if not isinstance(row, dict):
            _add_error(
                errors,
                name,
                f"Row {idx} in '{name}' must be an object with table settings.",
            )
            return

        missing = [key for key in ENFORCED_SETTINGS if key not in row]
        if missing:
            required = ", ".join(ENFORCED_SETTINGS)
            missing_str = ", ".join(missing)
            _add_error(
                errors,
                name,
                f"Each table setting must include: {required}. Missing: {missing_str}.",
            )
            return

        for key in BOOL_SETTINGS:
            if key in row and not isinstance(row[key], (bool, int)):
                _add_error(
                    errors,
                    name,
                    f"'{key}' in '{name}' must be a boolean or 0/1 value.",
                )
                return


TYPE_VALIDATORS: dict[str, Callable] = {
    "string": _validate_string,
    "enum": _validate_enum,
    "table_settings": _validate_table_settings,
    "identifier": _validate_identifier,
}


def validate_step_answers(
    step_cfg: dict[str, Any], answers: dict[str, Any]
) -> list[ValidationError]:
    """
    Return a list of validation errors. Each error is a dict with 'field' and 'message'.
    """
    errors: list[ValidationError] = []

    required_inputs = step_cfg.get("required_inputs") or []
    for field in required_inputs:
        name = field.get("name")
        ftype = field.get("type")
        value = answers.get(name)

        # Required presence check
        if value is None or value == "":
            _add_error(errors, name, f"'{name}' is required for this step.")
            continue

        # Type specific validation
        validator = TYPE_VALIDATORS.get(ftype)
        if validator:
            validator(field, value, errors)

    return errors
