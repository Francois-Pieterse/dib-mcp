# Dropinbase MCP Server

An MCP server that exposes Dropinbase functionality to LLM-based clients using the Model Context Protocol.
This server allows an MCP-compatible client to query Dropinbase data, retrieve documentation context, and perform controlled actions such as Designer updates and guided wizard flows via natural language.

This project does **not** host an LLM. It must be used together with an MCP client such as VS Code Copilot, Claude Desktop, or a custom MCP-enabled application.

## What this server provides

At a high level, the MCP server exposes:

* Authentication helpers for Dropinbase
* Read-only access to curated Dropinbase documentation
* Designer tree inspection and CRUD operations
* Wizard-driven workflows for application and event creation
* A preloaded agent prompt to guide LLM behaviour

The server is client-agnostic and follows the MCP specification.

## Requirements

* Python 3.12+
* Git
* `uv` installed globally or in your environment

## Setup

### Install dependencies

```bash
uv install
```

This installs all dependencies defined in `pyproject.toml`.

### Environment configuration

Copy `.env-example` to `.env` and configure the required variables.

At minimum, this typically includes Dropinbase credentials when using environment-based authentication.

## Authentication options

The server supports three authentication methods:

* Environment credentials (recommended)
* Credentials provided at runtime
* Existing PHP session ID

For most use cases, environment credentials are the simplest and most reliable option.

**Important:**
Dropinbase may enforce a single active session per user. If the MCP server and the GUI need to be logged in at the same time, either disable session enforcement for the user or create a dedicated Dropinbase user for the MCP server.

## Running the server

### Local development (stdio MCP)

```bash
uv run .\server\server.py
```

This is the mode typically used with VS Code MCP integration.

### VS Code integration

The `mcp.json` that can be [generated](https://code.visualstudio.com/docs/copilot/customization/mcp-servers) runs the server via `uv run .\server\server.py` using stdio transport. This is how the MCP runtime is launched from VS Code.

## Debugging

Set the environment variable:

```text
DEBUG_MODE=true
```

When enabled, the MCP runtime is not started. Instead, `debug_main()` in `main.py` is executed, allowing normal Python debugging with breakpoints.

## Deployment

The server supports both stdio and HTTP MCP modes.
Local development typically uses stdio, while containerised or production deployments should use HTTP mode. The transport is controlled via environment configuration and is already supported in `main.py`.

Docker deployment is a recommended approach for production environments.

## Extending the server

When adding new tools, resources, or prompts:

* Implement the new `.py` file
* Ensure it is imported in `main.py` so it is registered with the MCP runtime

Unimported modules will not be exposed to MCP clients.

## Full documentation

For architecture details, tool definitions, wizard internals, validation rules, and design, please refer to the full documentation.

## Notes

* SSL verification is currently disabled for trusted local development environments
* High-level instruction handling depends heavily on the MCP client and model behaviour
