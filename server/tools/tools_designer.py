import logging

from mcp.types import ToolAnnotations
from typing import Literal

from env_variables import get_env, _to_bool
from mcp_instance import mcp
from session_auth import dib_session_client

logger = logger = logging.getLogger(__name__)
logger.setLevel(get_env("LOG_LEVEL", "INFO"))


@mcp.tool(
    name="get_project_tree",
    title="Get Designer Project Tree",
    description=(
        "Retrieve the project tree structure from Dropinbase to get node IDs and/or parent IDs of any component in the designer." \
        "The nesting structure of the returned data reflects the hierarchy of components in the designer view based on the root container." \
        "The response does not include detail up to the very last recursive level, identifiable by the 'expanded' field set to false." \
        "If this 'expanded' field is false for a node, and 'has_children' is true, it indicates that there are additional nested components not included in the response." \
        "To retrieve these additional nested components (if required), subsequent calls to this tool can be made using the 'container_id' of the desired node."
    ),
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
    name="move_node_in_designer_tree",
    title="Move Node in Designer Tree",
    description=(
        "Move a node in the designer project tree either before or after another node in the designer view hierarchy." \
        "The node to move and the stationary node are identified by their node IDs which can be obtained using the get_project_tree tool." \
        "The tool can also be used to change the parent of a node by specifying a different parent ID."
    ),
    annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ),
)
def move_node_in_designer_tree(
    node_id_stationary: str,
    node_id_to_move: str,
    parent_id: str,
    container_id: int,
    group_id: str,
    drop_position: Literal["before", "after"],
    request_verification_token: str = get_env("REQUEST_VERIFICATION_TOKEN"),
):
    """
    Move a node in the designer project tree.
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
        "dropPosition": drop_position,
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
