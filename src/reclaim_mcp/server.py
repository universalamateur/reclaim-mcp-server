"""FastMCP server for Reclaim.ai integration."""

from fastmcp import FastMCP

mcp = FastMCP("Reclaim.ai")


@mcp.tool
def health_check() -> str:
    """Check if the server is running."""
    return "OK"


def main() -> None:
    """Entry point for the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
