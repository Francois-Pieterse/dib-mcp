import logging

from mcp.types import ToolAnnotations
from typing import Literal, Any

from env_variables import get_env, _to_bool
from mcp_instance import mcp
from session_auth import dib_session_client

from tools.designer.validate import validator

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
    node_type: Literal['item', 'container'],
    request_verification_token: str = get_env("REQUEST_VERIFICATION_TOKEN"),
):

    url = (
        f"{get_env('BASE_URL', 'https://localhost')}"
        f"/dropins/dibAdmin/DDesignerAddOn/designerGetRecords"
        f"?containerName=dibDesignerHtml&table=pef_{node_type}&id={node_id}"
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

    # TODO: Implement/expand validation of field name and subsequent value type. Currently some validation is
    # done server-side, so invalid field names or value types are caught. However, the specific valid values of
    # this value type are not checked. This may lead to silent failures or unexpected behavior.
    # For example, the width can be set to "test" without error. Whilst, this may not have
    # been a problem when fields were set via the UI, it could lead to issues when the LLM
    # is setting fields programmatically. This becomes especially relevant for fields which
    # no example values are available when the get_node_info_from_id tool is used.
    # Another example is boolean fields which are checked for integer valeus server side, but the range is
    # not checked. So setting a boolean field to "2" would be accepted by the server.
    valid_ok, validation_error = validator.validate(field_name, value)

    if not valid_ok:
        return {
            "status_code": 400,
            "ok": False,
            "response": {
                "error": "Validation failed",
                "details": validation_error,
            },
        }

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


@mcp.tool(
    name="get_avail_components_to_add",
    title="Get Available Components to Add",
    description=(
        "Retrieve available components that can be added to a specific container in the Dropinbase designer."
        "This tool returns a list of components that can be added to the specified container, identified by its container ID."
        "Ideally the base or aprent container ID should be used, not the target container id."
        "The returned components include a property 'leaf', if it is set to 1, the component can be added directly;"
        "if set to 0, the component is actually a group with nested components inside and cannot be added directly."
    ),
    annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ),
)
def get_avail_components_to_add(
    container_id: str,
    request_verification_token: str = get_env("REQUEST_VERIFICATION_TOKEN"),
):
    """
    Retrieve available components that can be added to a specific container in the designer.
    """
    url: str = (
        f"{get_env('BASE_URL', 'https://localhost')}"
        "/dropins/dibAdmin/DDesignerComponentStore/read"
        "?containerName=dibDesignerHtml&node=root"
    )

    headers: dict[str, str] = {
        "Content-Type": "application/json",
        "RequestVerificationToken": request_verification_token,
    }

    payload: dict[str, Any] = {
        "clientData": {"treeData": {"containerId": container_id, "filterString": ""}}
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
    name="add_component_in_designer_tree",
    title="Add Component in Designer Tree",
    description=(
        "Add a component in the designer project tree either before or after another node in the designer view hierarchy."
        "The stationary node and parent is identified by their node IDs which can be obtained using the get_project_tree tool."
        "The component to add is identified by its component ID which can be obtained using the get_avail_components_to_add tool."
        "Where multiple possible components are probable for a given use case, the user should confirm the exact component to add."
        "Adding containers are not supported by this tool."
    ),
    annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=False,
        openWorldHint=False,
    ),
)
def add_component_in_designer_tree(
    node_id_stationary: str,
    component_id_to_add: str,
    parent_id: str,
    drop_position: Literal["before", "after"],
    request_verification_token: str = get_env("REQUEST_VERIFICATION_TOKEN"),
):
    """
    Add a component in the designer project tree.
    """
    url: str = (
        f"{get_env('BASE_URL', 'https://localhost')}"
        "/dropins/dibAdmin/DDesignerItemStore/drop"
        "?containerName=dibDesignerHtml"
    )

    headers: dict[str, str] = {
        "Content-Type": "application/json",
        "RequestVerificationToken": request_verification_token,
    }

    payload: dict[str, Any] = {
        "clientData": {
            "alias_parent": {},
            "selected": [],
        },
        "sourceTreeId": "treeH",
        "dropPosition": drop_position,
        "dropNodeId": node_id_stationary,
        "nodeId": component_id_to_add,
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


@mcp.tool(
    name="delete_node_in_designer_tree",
    title="Delete Node in Designer Tree",
    description=(
        "Delete a node in the designer project tree using its node ID."
        "This tool removes the specified node from the designer view hierarchy."
        "Confirmation from the user is required as this action is destructive and cannot be undone."
    ),
    annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=True,
        idempotentHint=True,
        openWorldHint=False,
    ),
)
def delete_node_in_designer_tree(
    node_id: str,
    request_verification_token: str = get_env("REQUEST_VERIFICATION_TOKEN"),
):
    """
    Delete a node in the designer project tree.
    """

    url: str = (
        f"{get_env('BASE_URL', 'https://localhost')}"
        "/dropins/dibAdmin/DibTasks/dibDesignerDeleteItem"
        "?containerName=dibDesignerHtml&itemEventId=ie178-dib"
    )

    headers: dict[str, str] = {
        "Content-Type": "application/json",
        "RequestVerificationToken": request_verification_token,
    }

    payload: dict[str, Any] = {
        "clientData": {
            "selected_self": [
                {
                    "id": node_id,
                }
            ]
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
    name="delete_nested_nodes_in_designer_tree",
    title="Delete Nested Nodes in Designer Tree",
    description=(
        "Delete all nested nodes under and including a parent node in the designer project tree."
        "This tool removes the specified parent node and all its child nodes from the designer view hierarchy."
        "When a delete confirmation action is required from the server, it is most likely a nested node - in such a case use this tool."
        "Confirmation from the user is required as this action is destructive and cannot be undone."
    ),
    annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=True,
        idempotentHint=True,
        openWorldHint=False,
    ),
)
def delete_nested_nodes_in_designer_tree(
    parent_node_id: str,
    request_verification_token: str = get_env("REQUEST_VERIFICATION_TOKEN"),
):
    """
    Delete all nested nodes under and including a parent node in the designer project tree.
    """

    url: str = (
        f"{get_env('BASE_URL', 'https://localhost')}"
        "/dropins/dibAdmin/DibTasks/dibDesignerDeleteItemMany"
        "?containerName=dibDesignerHtml&itemEventId=ie21-dib"
    )

    headers: dict[str, str] = {
        "Content-Type": "application/json",
        "RequestVerificationToken": request_verification_token,
    }

    payload: dict[str, Any] = {
        "clientData": {
            "selected_self": [
                {
                    "id": parent_node_id,
                }
            ],
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
