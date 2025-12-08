from mcp.types import ToolAnnotations

from resources.dib_docs.resource_registry import DOCS_BY_NAME, DocResourceMeta
from resources.dib_docs.docs_resource_factory import fetch_endpoint_content

from mcp_instance import mcp

@mcp.tool(
    name="list_dib_doc_topics",
    title="List Dropinbase documentation topics",
    description=(
        "List all available Dropinbase documentation topics. "
        "Use this to see which topics exist before choosing one. "
        "After getting the list, use `list_dib_docs` to see the docs in a specific topic."
    ),
    annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ),
)
def list_dib_doc_topics() -> dict:
    """
    Return a list of available documentation topics.
    """
    topics = set()
    for meta in DOCS_BY_NAME.values():
        topics.add(meta.topic_id)

    return {"topics": list(topics)}


@mcp.tool(
    name="list_dib_docs",
    title="List Dropinbase documentation resources",
    description=(
        "List all available Dropinbase documentation entries. "
        "Use this to see which docs exist before choosing one. "
        "If a user asks what documentation is available, or which examples exist "
        "for a component or layout, call this tool."
        "After getting the list, use `load_dib_doc` to fetch the content of a specific doc by its `name`."
    ),
    annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ),
)
def list_dib_docs(
    topic: str | None = None,
    only_enabled: bool = True,
) -> dict:
    """
    Return a lightweight index of docs: name, title, uri, topic, description.
    """
    items = []
    for meta in DOCS_BY_NAME.values():
        if only_enabled and not meta.enabled:
            continue
        if topic and meta.topic_id != topic:
            continue
        items.append(
            {
                "name": meta.name,
                "title": meta.title,
                "uri": meta.uri,
                "topic": meta.topic_id,
                "description": meta.description,
            }
        )

    return {"docs": items}


@mcp.tool(
    name="load_dib_doc",
    title="Load Dropinbase documentation",
    description=(
        "Load a specific Dropinbase documentation page by its `name`. "
        "Always use this when a user asks about a feature, component, layout, validation, "
        "permissions or other behaviour that is covered by these docs. "
        "Also use this when designing a project or adding components in the Designer, "
        "so that your explanation and choices follow the recommended patterns."
        "Remember to first call `list_dib_docs` to find the available documentation names."
    ),
    annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ),
)
def load_dib_doc(
    name: str,
):
    """
    Fetch the doc content for the given registry `name`.
    """
    meta: DocResourceMeta | None = DOCS_BY_NAME.get(name)
    if meta is None:
        return {
            "error": f"Unknown documentation name: {name}",
        }

    if not meta.endpoint:
        return {
            "error": f"Documentation '{name}' has no endpoint configured.",
        }

    docs_content = fetch_endpoint_content(meta.endpoint, meta.payload)

    return docs_content
