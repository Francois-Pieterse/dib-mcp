import re
from typing import Any, Callable


from tools.wizards.base.validation_base import (
    FieldCfg,
    ValidationError,
    _add_error,
    validate_step_answers as base_validate,
)


# Event Wizard specific validators
def _validate_class_name(
    field: FieldCfg, value: Any, errors: list[ValidationError]
) -> bool:
    name = field["name"]
    if not isinstance(value, str):
        _add_error(errors, name, f"'{name}' must be a string value.")
        return

    # Ensure the class name starts with a letter, preferably uppercase, and contains only valid characters
    pattern = r"^[A-Z][A-Za-z0-9_.]*$"
    if not re.match(pattern, value):
        _add_error(
            errors,
            name,
            (
                "Class name must start with an uppercase letter and contain only "
                "letters, digits, and underscores, with no spaces."
            ),
        )

    # Class name must end with 'Controller.php'
    if not value.endswith("Controller.php"):
        _add_error(
            errors,
            name,
            "Class name must end with 'Controller.php'. e.g. MyNewController.php",
        )


WIZARD_SPECIFIC_TYPE_VALIDATORS: dict[str, Callable] = {
    "class_name": _validate_class_name,
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
