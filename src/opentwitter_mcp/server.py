"""Entry point for the Twitter MCP server."""

from opentwitter_mcp.app import mcp

# Importing the tools module triggers registration of all @mcp.tool() decorators.
import opentwitter_mcp.tools  # noqa: F401


def main():
    """Run the MCP server (stdio transport by default)."""
    mcp.run()


if __name__ == "__main__":
    main()
