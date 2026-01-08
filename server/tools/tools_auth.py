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
    description=(
        "Authenticate/login to Dropinbase with provided credentials instead of those in environment."
        "This allows authentication with different user accounts as needed."
        "The tool returns whether a valid session has been established after login based on the returned PHPSESSID."
    ),
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
    # Clear any existing session
    dib_session_client.session.cookies.clear()

    dib_session_client.username = username
    dib_session_client.password = password
    dib_session_client.login()

    return {
        "has_session": dib_session_client.has_session,
    }


@mcp.tool(
    name="auth_with_env_credentials",
    title="Authenticate with Environment Credentials",
    description=(
        "Authenticate to Dropinbase with credentials from the environment."
        "This uses the DIB_USERNAME and DIB_PASSWORD environment variables for authentication."
        "The tool returns whether a valid session has been established after login based on the returned PHPSESSID."
    ),
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
    # Clear any existing session
    dib_session_client.session.cookies.clear()

    dib_session_client.username = get_env("DIB_USERNAME", "admin")
    dib_session_client.password = get_env("DIB_PASSWORD", "test")
    dib_session_client.login()

    return {
        "has_session": dib_session_client.has_session,
    }


@mcp.tool(
    name="auth_with_existing_session",
    title="Authenticate with Existing Session",
    description=(
        "Authenticate/login to Dropinbase using an existing PHPSESSID cookie value."
        "This allows reuse of an existing session without needing to provide username and password."
        "The tool returns whether a valid session has been established based on the provided PHPSESSID."
    ),
    annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ),
)
def auth_with_existing_session(phpsessid: str):
    """
    Authenticate to Dropinbase with an existing PHPSESSID cookie value.
    """
    # Clear any existing session
    dib_session_client.session.cookies.clear()

    dib_session_client.set_session_id(phpsessid)

    return {
        "has_session": dib_session_client.has_session,
    }
