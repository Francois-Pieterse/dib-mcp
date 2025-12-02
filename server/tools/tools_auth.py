import logging

from mcp.types import ToolAnnotations

from env_variables import get_env, _to_bool
from mcp_instance import mcp
from session_auth import dib_session_client

logger = logger = logging.getLogger(__name__)
logger.setLevel(get_env("LOG_LEVEL", "INFO"))


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