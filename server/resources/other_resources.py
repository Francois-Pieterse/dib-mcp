from mcp_instance import mcp

# To expose these resources, import this module in main.py


@mcp.resource(
    uri="dib://example/resource",
    name="example_resource",
    title="Example Resource",
    description="This is an example resource.",
)
def example_resource():
    return {
        "content_type": "text/plain",
        "body": "This is the content of the example resource.",
    }
