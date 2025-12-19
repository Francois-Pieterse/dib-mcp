import re
from typing import Any, Callable


from tools.wizards.base.validation_base import (
    FieldCfg,
    ValidationError,
    _add_error,
    validate_step_answers as base_validate,
)


# WIZARD_SPECIFIC_TYPE_VALIDATORS: dict[str, Callable] = {
# }


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
        type_validators=None,
    )
