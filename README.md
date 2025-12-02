# Minimal MCP Server for Dropinbase

## Quick Start

### Requirements
- Python 3.12+
- Git
- Ensure `uv` is installed globally or within your environment

### Clone
git clone <repo-url>  
cd dib-mcp

## Setup Environment

### Install dependencies
uv install  
This installs all dependencies defined in `pyproject.toml`.

### Environment file
Copy the `.env-example` to `.env` and set the appropriate variables.

## Run the Server

### Using uv
uv run .\server\server.py

## VS Code Integration
mcp.json includes a server entry that runs uv run .\server\server.py with stdio transport. This is how the MCP runtime is launched from VS Code.

### Debugging
Add a launch.json entry to run python -m server.server for breakpoints, or run uv in an integrated terminal for MCP-specific behaviour.

## Notes
- DEBUG_MODE=true triggers debug_main() instead of starting the MCP runtime, useful for step-through testing.  
- If you encounter TLS or self-signed certificate issues when connecting to Dropinbase, the session client currently disables SSL verification for trusted local development.
- If a new tool/resource/prompt `.py` file is added, it is important to import it in `main.py` so it gets registered.
