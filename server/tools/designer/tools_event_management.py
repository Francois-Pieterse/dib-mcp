import logging

from mcp.types import ToolAnnotations
from typing import Literal, Any

from env_variables import get_env, _to_bool
from mcp_instance import mcp
from session_auth import dib_session_client

from tools.designer.validate import validator

logger = logger = logging.getLogger(__name__)
logger.setLevel(get_env("LOG_LEVEL", "INFO"))


# ---------------------------------------------- #
# Events are added using the event wizard toolset.
# Aforementioned can be found at:
# server/tools/wizards/event_wizard/...
# ---------------------------------------------- #


@mcp.tool(
    name="delete_event_by_id",
    title="Delete Event by ID",
    description=("Delete an event in the designer by its unique ID."),
    annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=True,
        idempotentHint=True,
        openWorldHint=False,
    ),
)
def delete_event_by_id(
    event_id: str,
    request_verification_token: str = get_env("REQUEST_VERIFICATION_TOKEN"),
):
    """Delete an event in the designer by its unique ID."""

    url = (
        f"{get_env('BASE_URL', 'https://localhost')}"
        f"/dropins/dibAdmin/DibTasks/dibDesignerDeleteTableRecord/{event_id}/pef_container_event"
        "?containerName=dibDesignerHtml&itemEventId=ie162-dib"
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
