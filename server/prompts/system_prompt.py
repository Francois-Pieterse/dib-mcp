from mcp_instance import mcp


@mcp.prompt(
    name="dib_system_prompt",
    title="Dropinbase MCP Agent System Prompt",
    description="System prompt that defines how the Dropinbase MCP Agent should behave when using tools and resources.",
)
def dib_system_prompt() -> str:
    """
    Returns the system-level instructions for the Dropinbase MCP Agent.
    """
    FILEPATH: str = "server/prompts/files"
    FILENAME: str = "system_prompt.txt"

    with open(f"{FILEPATH}/{FILENAME}", "r", encoding="utf-8") as file:
        agent_system_prompt = file.read()

    return agent_system_prompt
