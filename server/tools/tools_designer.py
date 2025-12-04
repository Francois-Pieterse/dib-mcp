import logging

from mcp.types import ToolAnnotations
from typing import Literal

from env_variables import get_env, _to_bool
from mcp_instance import mcp
from session_auth import dib_session_client

logger = logger = logging.getLogger(__name__)
logger.setLevel(get_env("LOG_LEVEL", "INFO"))


@mcp.tool(
    name="get_all_avail_groups",
    title="Get All Available Groups",
    description=(
        "Retrieve all available groups in the Dropinbase designer."
        "This tool returns a list of groups available for selection when managing containers within the designer."
        "The selected group id is a necessary input in many other tools."
    ),
    annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ),
)
def get_all_avail_groups(
    request_verification_token: str = get_env("REQUEST_VERIFICATION_TOKEN"),
    page: int = 1,
    limit: int = 40,
):
    """Get all available groups in the designer."""

    url = (
        f"{get_env('BASE_URL', 'https://localhost')}"
        "/peff/Crud/componentlist"
        "?containerName=dibDesigner&containerItemId=3901&itemAlias=groupId"
        f"&page={page}&limit={limit}&activeFilter=null"
    )

    headers: dict[str, str] = {
        "Content-Type": "application/json",
        "RequestVerificationToken": request_verification_token,
    }

    response = dib_session_client.request("POST", url, headers=headers)

    try:
        return {"data": response.json()}
    except ValueError:
        return {
            "status_code": response.status_code,
            "response": response.text,
        }


@mcp.tool(
    name="get_all_avail_containers",
    title="Get All Available Containers",
    description=(
        "Retrieve all available containers in the Dropinbase designer."
        "This tool returns a list of containers available for selection when managing components within the designer."
        "The selected container id is a necessary input in many other tools."
    ),
    annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ),
)
def get_containers(
    request_verification_token: str = get_env("REQUEST_VERIFICATION_TOKEN"),
    page: int = 1,
    limit: int = 40,
    filter: str = "null",
):
    """Get all available containers in the designer."""

    url = (
        f"{get_env('BASE_URL', 'https://localhost')}"
        "/peff/Crud/componentlist"
        "?containerName=dibDesigner&containerItemId=3900&itemAlias=containerId"
        f"&page={page}&limit={limit}&activeFilter={filter}"
    )

    headers: dict[str, str] = {
        "Content-Type": "application/json",
        "RequestVerificationToken": request_verification_token,
    }

    response = dib_session_client.request("POST", url, headers=headers)

    try:
        return {"data": response.json()}
    except ValueError:
        return {
            "status_code": response.status_code,
            "response": response.text,
        }


@mcp.tool(
    name="get_project_tree",
    title="Get Designer Project Tree",
    description=(
        "Retrieve the project tree structure from Dropinbase to get node IDs and/or parent IDs of any component in the designer."
        "The nesting structure of the returned data reflects the hierarchy of components in the designer view based on the root container."
        "The response does not include detail up to the very last recursive level, identifiable by the 'expanded' field set to false."
        "If this 'expanded' field is false for a node, and 'has_children' is true, it indicates that there are additional nested components not included in the response."
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
    group_id: int,
    request_verification_token: str = get_env("REQUEST_VERIFICATION_TOKEN"),
) -> dict:
    """
    Retrieve the project tree structure from Dropinbase.
    """
    url = (
        f"{get_env('BASE_URL', 'https://localhost')}"
        "/dropins/dibAdmin/DDesignerItemStore/read"
        "?containerName=dibDesignerHtml&node=root"
    )

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

    try:
        return {"data": response.json()}
    except ValueError:
        return {
            "status_code": response.status_code,
            "response": response.text,
        }


@mcp.tool(
    name="get_node_info_from_id",
    title="Get Node Info from ID",
    description=(
        "Retrieve detailed information about a specific node in the designer project tree using its node ID."
        "This tool returns all available data for the specified node, which can include properties, settings"
        "and other metadata associated with that node."
    ),
    annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ),
)
def get_node_info_from_id(
    node_id: str,
    request_verification_token: str = get_env("REQUEST_VERIFICATION_TOKEN"),
):

    url = (
        f"{get_env('BASE_URL', 'https://localhost')}"
        f"/dropins/dibAdmin/DDesignerAddOn/designerGetRecords"
        f"?containerName=dibDesignerHtml&table=pef_item&id={node_id}"
    )

    headers: dict[str, str] = {
        "Content-Type": "application/json",
        "RequestVerificationToken": request_verification_token,
    }

    response = dib_session_client.request("POST", url, headers=headers)

    try:
        return {"data": response.json()}
    except ValueError:
        return {
            "status_code": response.status_code,
            "response": response.text,
        }


@mcp.tool(
    name="update_node_info",
    title="Update Node Info",
    description=(
        "Update a specific field of a node in the designer project tree using its node ID."
        "This tool allows modification of properties, settings, or other metadata associated with that node."
        "The tool requires the node ID, the field name to be updated, and the new value for that field."
        "It requires exact value confirmations from the user as no server side validation is done which can"
        "cause breaking changes."
    ),
    annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=True,
        idempotentHint=False,
        openWorldHint=False,
    ),
)
def update_node_info(
    node_id: str,
    field_name: str,
    value: str,
    root_container_id: int,
    request_verification_token: str = get_env("REQUEST_VERIFICATION_TOKEN"),
):
    """
    Update a specific field of a node in the designer project tree.
    """

    # TODO: Implement/expand validation of field name and subsequent value type. Currently no
    # validation is done here or server-side, so invalid field names or value types
    # may lead to silent failures or unexpected behavior.
    # For example, the width can be set to "test" without error. Whilst, this may not have
    # been a problem when fields were set via the UI, it could lead to issues when the LLM
    # is setting fields programmatically. This becomes especially relevant for fields which
    # no example values are available when the get_node_info_from_id tool is used.

    url = (
        f"{get_env('BASE_URL', 'https://localhost')}"
        "/dropins/dibAdmin/DDesignerAddOn/designerUpdates/dibDesignerHtml"
    )

    headers: dict[str, str] = {
        "Content-Type": "application/json",
        "RequestVerificationToken": request_verification_token,
    }

    payload = {
        "clientData": {
            "table": "item",
            "field": field_name,
            "id": node_id,
            "value": value,
            "encode": True,
            "selectedContainerId": root_container_id,
        }
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


@mcp.tool(
    name="move_node_in_designer_tree",
    title="Move Node in Designer Tree",
    description=(
        "Move a node in the designer project tree either before or after another node in the designer view hierarchy."
        "The node to move and the stationary node are identified by their node IDs which can be obtained using the get_project_tree tool."
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
    url = (
        f"{get_env('BASE_URL', 'https://localhost')}"
        "/dropins/dibAdmin/DDesignerItemStore/drop"
        "?containerName=dibDesignerHtml"
    )

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
