from typing import Any, Callable, Mapping

ValidationError = dict[str, str]
FieldCfg = dict[str, Any]
ValidatorFn = Callable[[FieldCfg, Any, list[ValidationError]], None]


def _add_error(errors: list[ValidationError], field: str, message: str) -> None:
    errors.append({"field": field, "message": message})


def _validate_string(field: FieldCfg, value: Any, errors: list[ValidationError]) -> None:
    name = field["name"]
    if not isinstance(value, str):
        _add_error(errors, name, f"'{name}' must be a string value.")


def _validate_boolean(field: FieldCfg, value: Any, errors: list[ValidationError]) -> None:
    # Allow bools and 0/1 integers
    name = field["name"]
    if not isinstance(value, bool) and value not in (0, 1):
        _add_error(errors, name, f"'{name}' must be a boolean value.")


def _validate_enum(field: FieldCfg, value: Any, errors: list[ValidationError]) -> None:
    name = field["name"]
    options = field.get("options") or []
    allowed_values = [opt.get("value") for opt in options if isinstance(opt, dict)]
    if allowed_values and value not in allowed_values:
        allowed = ", ".join(map(str, allowed_values))
        _add_error(errors, name, f"'{name}' must be one of: {allowed}.")


DEFAULT_TYPE_VALIDATORS: dict[str, ValidatorFn] = {
    "string": _validate_string,
    "enum": _validate_enum,
    "boolean": _validate_boolean,
}


def validate_step_answers(
    step_cfg: dict[str, Any],
    answers: dict[str, Any],
    *,
    type_validators: Mapping[str, ValidatorFn] | None = None,
) -> list[ValidationError]:
    """
    Validate answers for a step config.

    - Uses 'required_inputs' from the step config.
    - Runs a required presence check for each required input.
    - Applies type validators based on each input's 'type'.

    Extend/override type validation by passing 'type_validators'.
    """
    errors: list[ValidationError] = []

    merged_type_validators: dict[str, ValidatorFn] = dict(DEFAULT_TYPE_VALIDATORS)
    if type_validators:
        merged_type_validators.update(type_validators)

    required_inputs = step_cfg.get("required_inputs") or []
    for field in required_inputs:
        name = field.get("name")
        ftype = field.get("type")
        value = answers.get(name)

        if not name:
            # Ignore for now
            continue

        # Required presence check
        if value is None or value == "":
            _add_error(errors, name, f"'{name}' is required for this step.")
            continue

        # Type-specific validation (optional if type missing)
        validator = merged_type_validators.get(ftype)
        if validator:
            validator(field, value, errors)

    return errors
