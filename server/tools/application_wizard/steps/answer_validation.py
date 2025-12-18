import re
from typing import Any, Callable


from server.tools.wizard_base.validation_base import (
    FieldCfg,
    ValidationError,
    _add_error,
    validate_step_answers as base_validate
)

# Application Wizard specific validators
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


WIZARD_SPECIFIC_TYPE_VALIDATORS: dict[str, Callable] = {
    "table_settings": _validate_table_settings,
    "identifier": _validate_identifier,
}


# Wrapper function to combine base validation with wizard-specific validators
def validate_step_answers(
    step_cfg: dict[str, Any], answers: dict[str, Any]
) -> list[ValidationError]:
    """
    Return a list of validation errors. Each error is a dict with 'field' and 'message'.
    """

    return base_validate(
        step_cfg,
        answers,
        type_validators=WIZARD_SPECIFIC_TYPE_VALIDATORS,
    )
