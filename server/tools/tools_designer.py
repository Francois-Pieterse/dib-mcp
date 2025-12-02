import logging

from mcp.types import ToolAnnotations

from env_variables import get_env, _to_bool
from mcp_instance import mcp
from session_auth import dib_session_client

logger = logger = logging.getLogger(__name__)
logger.setLevel(get_env("LOG_LEVEL", "INFO"))


@mcp.tool(
    name="get_project_tree",
    title="Get Project Tree",
    description="Retrieve the project tree structure from Dropinbase to get node IDs and/or parent IDs of any component.",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ),
)
def get_project_tree(
    container_id: int,
    group_id: int = 2,
    request_verification_token: str = get_env("REQUEST_VERIFICATION_TOKEN"),
) -> dict:
    """
    Retrieve the project tree structure from Dropinbase.
    """
    url = f"{get_env('BASE_URL', 'https://localhost')}/dropins/dibAdmin/DDesignerItemStore/read?containerName=dibDesignerHtml&node=root"

    headers: dict[str, str] = {
        "Content-Type": "application/json",
        "RequestVerificationToken": request_verification_token,
    }

    payload = {
        "clientData": {
            "treeData": {
                "containerId": container_id,
                "filterString": "",
                "groupId": group_id,
            }
        }
    }

    response = dib_session_client.request("POST", url, headers=headers, json=payload)

    logger.debug("Get Project Tree Response: %s", response.text)
    try:
        return {"data": response.json()}
    except ValueError:
        return {
            "status_code": response.status_code,
            "response": response.text,
        }


@mcp.tool(
    name="move_node_before",
    title="Move Node Before",
    description="Move a node before another node in the designer view hierarchy as defined by dib://project/tree resource.",
    annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ),
)
def move_node_before(
    node_id_stationary: str,
    node_id_to_move: str,
    parent_id: str,
    container_id: int,
    group_id: str = "2",
    request_verification_token: str = get_env("REQUEST_VERIFICATION_TOKEN"),
):
    """
    Move a node before another node.
    """
    url = f"{get_env('BASE_URL', 'https://localhost')}/dropins/dibAdmin/DDesignerItemStore/drop?containerName=dibDesignerHtml"

    headers: dict[str, str] = {
        "Content-Type": "application/json",
        "RequestVerificationToken": request_verification_token,
    }

    payload = {
        "clientData": {
            "alias_parent": {
                "containerId": container_id,
                "groupId": group_id,
            },
            "selected": [],
        },
        "sourceTreeId": "tree",
        "dropPosition": "before",
        "dropNodeId": node_id_stationary,
        "nodeId": node_id_to_move,
        "parentId": parent_id,
    }

    response = dib_session_client.request("POST", url, headers=headers, json=payload)

    try:
        data = response.json()
    except ValueError:
        data = response.text

    return {
        "status_code": response.status_code,
        "ok": response.ok,
        "response": data,
    }
