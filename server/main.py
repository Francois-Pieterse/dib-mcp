import os
import logging

from pathlib import Path

from env_variables import get_env, _to_bool
from mcp_instance import mcp


# Very important to import all tool/resource/prompt files so they get registered

# Tools
from tools.designer import tools_designer
from tools import (
    tools_auth,
)

from tools.application_wizard import tools_application_wizard
from tools.application_wizard.steps import option_providers_registration_app_wiz

if get_env("EXPOSE_DIB_DOCS_VIA_TOOLS", False, _to_bool):
    from tools import tools_docs_resource

# Resources
from resources.dib_docs.docs_resource_factory import register_dib_docs

RESOURCES_ROOT = Path("server/resources")
register_dib_docs(
    mcp,
    resources_root=RESOURCES_ROOT,
)

# Prompts
from prompts import system_prompt

logger = logging.getLogger(__name__)
logger.setLevel(get_env("LOG_LEVEL", "INFO"))


def debug_main() -> None:
    """Run a debug sequence of operations."""

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
