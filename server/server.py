import os
import logging

from mcp.types import ToolAnnotations
from mcp.server.fastmcp import FastMCP

from env_variables import _load_env_file, get_env, _to_bool
from session_auth import DibClientAuth


# ------------------------------------
# Initialise Environment
# ------------------------------------
_load_env_file()

# Config values
BASE_URL = get_env("DIB_BASE_URL", "https://localhost")

logger = logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ------------------------------------
# MCP and Session Client Initialisation
# ------------------------------------

mcp = FastMCP(
    name="DIB MCP Server",
)

dib_session_client = DibClientAuth(
    username=get_env("DIB_USERNAME", "admin"),
    password=get_env("DIB_PASSWORD", "test"),
    login_page_url=get_env(
        "DIB_LOGIN_PAGE_URL",
        f"{BASE_URL}/login",
    ),
    login_endpoint_url=get_env(
        "DIB_LOGIN_ENDPOINT_URL",
        f"{BASE_URL}/dropins/dibAuthenticate/Site/login",
    ),
)

# ------------------------------------
# MCP Resource Definitions
# ------------------------------------


# ------------------------------------
# MCP Tool Definitions
# ------------------------------------
@mcp.tool(
    name="auth_with_other_credentials",
    title="Authenticate with Other Credentials",
    description="Authenticate to Dropinbase with provided credentials instead of those in environment.",
    annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ),
)
def auth_with_other_credentials(
    username: str,
    password: str,
):
    """
    Authenticate to Dropinbase with provided credentials instead of those in environment.
    """
    dib_session_client.username = username
    dib_session_client.password = password
    dib_session_client.login()

    return {
        "has_session": dib_session_client.has_session,
    }


@mcp.tool(
    name="auth_with_env_credentials",
    title="Authenticate with Environment Credentials",
    description="Authenticate to Dropinbase with credentials from the environment.",
    annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ),
)
def auth_with_env_credentials():
    """
    Authenticate to Dropinbase with credentials from the environment.
    """
    dib_session_client.username = get_env("DIB_USERNAME", "admin")
    dib_session_client.password = get_env("DIB_PASSWORD", "test")
    dib_session_client.login()

    return {
        "has_session": dib_session_client.has_session,
    }


@mcp.tool(
    name="move_node_before",
    title="Move Node Before",
    description="Move a node before another node in the designer view hierarchy.",
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
    container_id: int = 374,
    group_id: str = "1",
    request_verification_token: str = get_env("REQUEST_VERIFICATION_TOKEN"),
):
    """
    Move a node before another node.
    """
    url = f"{BASE_URL}/dropins/dibAdmin/DDesignerItemStore/drop?containerName=dibDesignerHtml"

    headers: dict[str, str] = {
        "Content-Type": "application/json",
    }

    if request_verification_token:
        headers["RequestVerificationToken"] = request_verification_token

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

    resp = dib_session_client.request("POST", url, headers=headers, json=payload)

    try:
        data = resp.json()
    except ValueError:
        data = resp.text

    return {
        "status_code": resp.status_code,
        "ok": resp.ok,
        "response": data,
    }


def debug_main() -> None:
    """Run a debug sequence of operations."""

    result = move_node_before(
        node_id_stationary="9265",
        node_id_to_move="9264",
        parent_id="c374",
    )
    logger.info("Move Node Before Result: %s", result)

    # Additional debug operations can be before this
    # ----------------------------------------------

    logger.info("Debug run complete. Exiting.")


if __name__ == "__main__":
    if get_env("DEBUG_MODE", False, _to_bool):
        debug_main()
    else:
        transport = os.getenv("MCP_TRANSPORT", "stdio")
        if transport == "http":
            mcp.run(transport="streamable-http")
        else:
            mcp.run(transport="stdio")
