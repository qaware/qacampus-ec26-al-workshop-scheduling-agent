from fastmcp import FastMCP

mcp = FastMCP("EC26 Schedule")


if __name__ == "__main__":
    mcp.run(transport="sse", host="0.0.0.0", port=8000)
