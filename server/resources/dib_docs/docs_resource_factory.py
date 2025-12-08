import json
import logging

from pathlib import Path
from typing import Any

from env_variables import get_env
from session_auth import dib_session_client

from .resource_registry import DocResourceMeta, DOCS_BY_NAME


logger = logging.getLogger(__name__)
logger.setLevel(get_env("LOG_LEVEL", "INFO"))


def _load_json(path: Path) -> dict:
    """Load a JSON file, returning an empty dict if it does not exist."""
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _load_master_config(config_root: Path) -> dict[str, bool]:
    """
    Load docs_master_config.json.

    Expected shape:
    {
      "enabled": {
        "docs_topic1": true,
        "docs_topic2": false
      }
    }
    """
    master_path = config_root / "docs_master_config.json"
    data = _load_json(master_path)
    return data.get("enabled", {})


def fetch_endpoint_content(endpoint: str, payload: Any | None = None) -> str:
    """
    Fetch the associated HTML for a documentation endpoint.
    Optionally a payload can be provided such as required by the 'Learn by Example' docs.

    `endpoint` is a path like '/dropins/dibDocs/Template/content/dibDocs/dib/?area=...'.
    """
    url = f"{get_env("BASE_URL", "https://localhost")}{endpoint}"

    headers: dict[str, str] = {
        "Content-Type": "application/json",
        "RequestVerificationToken": get_env("REQUEST_VERIFICATION_TOKEN"),
    }

    resp = dib_session_client.request("POST", url=url, headers=headers, json=payload)
    resp.raise_for_status()

    # Isolate response records containing content
    TARGET_FIELD = "records"
    if TARGET_FIELD in resp.json():
        records = resp.json()[TARGET_FIELD]

        return records

    logger.warning("Response JSON does not contain expected '%s' field.", TARGET_FIELD)
    return resp.text


def register_dib_docs(
    mcp_instance,
    resources_root: Path,
) -> None:
    """
    Register all Dropinbase docs resources using the config-driven approach.

    Directory layout under `resources_root`:

      dib_docs/
        configs/
          docs_master_config.json
          topics/
            docs_{topic1}.json
            docs_{topic2}.json
            ...

    This function:
      - reads docs_master_config to see which topics are enabled
      - for each *enabled* topic that has a JSON file, loads its topic config
      - for each enabled resource in that topic:
          * creates an MCP resource
          * when the resource is read, fetches the content from the configured endpoint
    """
    configs_root: Path = resources_root / "dib_docs" / "configs"
    topics_root: Path = configs_root / "topics"

    topic_enabled_map = _load_master_config(configs_root)

    for topic_id, topic_enabled in topic_enabled_map.items():
        if not topic_enabled:
            continue

        topic_path: Path = topics_root / f"docs_{topic_id}_config.json"
        if not topic_path.exists():
            logger.warning(
                "Topic %s enabled in master config, but %s not found",
                topic_id,
                topic_path,
            )
            continue

        topic_config = _load_json(topic_path)

        for resource_config in topic_config.get("resources", []):
            if not resource_config.get("enabled", False):
                continue

            uri = str(resource_config["uri"])
            name = str(resource_config["name"])
            title = str(resource_config["title"])
            description = str(resource_config["description"])
            endpoint = str(resource_config["endpoint"])
            payload: Any | None = resource_config["payload"] or None

            # Record in global registry
            DOCS_BY_NAME[name] = DocResourceMeta(
                name=name,
                title=title,
                uri=uri,
                topic_id=topic_id,
                enabled=True,
                description=description,
                endpoint=endpoint,
                payload=payload or {},
            )

            # Create the MCP resource
            def make_resource(
                _uri: str = uri,
                _name: str = name,
                _title: str = title,
                _description: str = description,
                _endpoint: str = endpoint,
                _payload: Any | None = payload,
            ):
                @mcp_instance.resource(
                    uri=_uri,
                    name=_name,
                    title=_title,
                    description=_description,
                )
                def dib_doc_resource() -> dict[str, Any]:
                    if not _endpoint:
                        raise ValueError(
                            f"No endpoint configured for documentation resource: {_name}."
                        )

                    docs_content = fetch_endpoint_content(_endpoint, _payload)
                    return {
                        "content_type": "text/html",
                        "body": docs_content,
                    }

                return dib_doc_resource

            make_resource()
