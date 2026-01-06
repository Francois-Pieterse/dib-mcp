from dataclasses import dataclass
from typing import Any, Callable, Protocol


class OptionProvider(Protocol):
    """
    A callable that returns a list of options for a wizard field.

    Signature:
        provider(*, context: dict | None = None, **kwargs) -> list[Any]
    """

    def __call__(
        self,
        *,
        context: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> list[Any]: ...


# Global registry of providers by name
OPTIONS_REGISTRY: dict[str, OptionProvider] = {}


def register_option_provider(name: str) -> Callable[[OptionProvider], OptionProvider]:
    """
    Decorator to register an option provider function under a given name.

    Usage:

        @register_option_provider("get_db_types")
        def get_db_types(*, context: dict | None = None, include_deprecated: bool = False) -> list[Any]:
            ...
    """

    def decorator(func: OptionProvider) -> OptionProvider:
        key = name or func.__name__
        if key in OPTIONS_REGISTRY:
            raise ValueError(f"Option provider '{key}' is already registered")
        OPTIONS_REGISTRY[key] = func
        return func

    return decorator


@dataclass
class OptionSource:
    """
    Parsed representation of the `options_source` block from wizard_steps.json.

    Expected JSON structure:

      {
        "type": "static",
        "values": ["a", "b", "c"]
      }

    or

      {
        "type": "function",
        "name": "get_db_types",
        "args": { "include_deprecated": false }
      }
    """

    type: str
    name: str | None = None
    values: list[Any] | None = None
    args: dict[str, Any] | None = None

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "OptionSource":
        src_type = raw.get("type")
        if not src_type:
            raise ValueError("options_source.type is required")

        if src_type == "static":
            values = raw.get("values")
            if values is None:
                raise ValueError("options_source.values is required for type 'static'")
            return cls(type="static", values=list(values))

        if src_type == "function":
            name = raw.get("name")
            if not name:
                raise ValueError("options_source.name is required for type 'function'")
            args = raw.get("args") or {}
            if not isinstance(args, dict):
                raise ValueError("options_source.args must be an object when provided")
            return cls(type="function", name=name, args=args)

        raise ValueError(f"Unknown options_source.type '{src_type}'")


def _get_by_path(data: dict[str, Any], path: str) -> Any:
    cur: Any = data.get("wizard_state", {})
    for part in path.split("."):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
    return cur


def resolve_dynamic_args(args: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    resolved: dict[str, Any] = {}
    for key, val in (args or {}).items():
        if isinstance(val, dict) and "$from" in val:
            resolved[key] = _get_by_path(ctx, str(val["$from"]))
        else:
            resolved[key] = val
    return resolved


def resolve_options(
    source_cfg: dict[str, Any] | None,
    *,
    context: dict[str, Any] | None = None,
) -> list[Any]:
    """
    Resolve options based on an options_source config from wizard_steps.json.

    Returns a list of options suitable for a field, for example:
    - simple strings
    - dicts with { "value": ..., "label": ... }

    If source_cfg is None or empty, an empty list is returned.
    """
    if not source_cfg:
        return []

    source = OptionSource.from_dict(source_cfg)
    ctx = context or {}

    if source.type == "static":
        return source.values or []

    if source.type == "function":
        if not source.name:
            raise ValueError("Function options_source missing 'name'")
        provider = OPTIONS_REGISTRY.get(source.name)
        if provider is None:
            raise KeyError(f"No option provider registered with name '{source.name}'")
        kwargs = resolve_dynamic_args(dict(source.args or {}), ctx)
        return provider(context=ctx, **kwargs)

    raise ValueError(f"Unsupported options_source.type '{source.type}'")


def enrich_field_with_options(
    field_cfg: dict[str, Any],
    *,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Given a single field config from wizard_steps.json, resolve its options
    (if an options_source is present) and return an updated field dict.

    Example input field:

        {
          "name": "db_type",
          "type": "enum",
          "prompt": "Which database should this application use?",
          "options_source": {
            "type": "function",
            "name": "get_db_types",
            "args": { "include_deprecated": false }
          }
        }

    Example output field (options added):

        {
          "name": "db_type",
          "type": "enum",
          "prompt": "Which database should this application use?",
          "options": [
            {"value": "postgres", "label": "PostgreSQL"},
            {"value": "mysql", "label": "MySQL"}
          ]
        }
    """
    options_source_cfg = field_cfg.get("options_source")
    if not options_source_cfg:
        return field_cfg

    resolved = resolve_options(options_source_cfg, context=context)
    new_field = dict(field_cfg)
    new_field["options"] = resolved
    return new_field


def enrich_step_with_options(
    step_cfg: dict[str, Any],
    *,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Apply enrich_field_with_options to every field in a step config.

    Expects a structure like:

        {
          "id": "choose_db",
          "title": "Choose a database",
          "required_inputs": [ ...fields... ]
        }
    """
    new_step = dict(step_cfg)
    inputs = step_cfg.get("required_inputs") or []
    new_step["required_inputs"] = [
        enrich_field_with_options(f, context=context) for f in inputs
    ]
    return new_step


def extract_options_from_records(records: list) -> list:
    """
    Extract options from records fetched from the server.

    Records should be a list of dictionaries, each containing 'id' and 'id_display_value' keys.
    """
    options = []
    for record in records:
        db_id = record.get("id")
        db_name = record.get("id_display_value")

        if db_id is not None and db_name is not None:
            options.append({"value": str(db_id), "label": db_name})
    return options


def extract_records_from_response(
    response: Any,
    topic: str = "data",
) -> list:
    """
    Extract records from a server response.

    Expects the response to have a JSON body with 'success' and 'records' fields.
    Raises ValueError if the response is unsuccessful or malformed.
    """
    try:
        data = response.json()

        # Check for success
        if not data.get("success"):
            raise ValueError(f"Failed to fetch {topic}: Unsuccessful response")

        records = data.get("records", [])

        if records is None:
            raise ValueError(f"Failed to fetch {topic}: No records field found")

    except ValueError:
        raise ValueError(f"Failed to parse response JSON for {topic}")

    return records


def extract_options_from_response(
    response: Any,
    topic: str = "data",
) -> list:
    """
    Extract options from a server response.

    Expects the response to have a JSON body with 'success' and 'records' fields.
    Raises ValueError if the response is unsuccessful or malformed.
    """
    records = extract_records_from_response(response, topic=topic)
    options = extract_options_from_records(records)
    return options
