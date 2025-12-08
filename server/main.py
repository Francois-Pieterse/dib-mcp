import os
import logging

from pathlib import Path

from env_variables import get_env, _to_bool
from mcp_instance import mcp

from resources.dib_docs.docs_resource_factory import register_dib_docs

# Very important to import all tool/resource/prompt files so they get registered
from tools import (
    tools_auth,
    tools_designer,
)

if get_env("EXPOSE_DIB_DOCS_VIA_TOOLS", False, _to_bool):
    from tools import tools_docs_resource


resources_root = Path("server/resources")

register_dib_docs(
    mcp,
    resources_root=resources_root,
)


logger = logging.getLogger(__name__)
logger.setLevel(get_env("LOG_LEVEL", "INFO"))


def debug_main() -> None:
    """Run a debug sequence of operations."""

    # result = get_project_tree()
    # logger.info("Get Project Tree Result: %s", result)

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
