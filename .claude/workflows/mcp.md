---
description: Add or manage MCP servers for this project
---

## Adding an MCP Server to This Project

MCP servers for Claude Code are configured in `.mcp.json` at the project root.

### Steps

1. Open `.mcp.json` at the project root (create it if it doesn't exist).
2. Add your server under the `"mcpServers"` key using the format below.
3. Restart Claude Code for the changes to take effect.

### Format

```json
{
  "mcpServers": {
    "<server-name>": {
      "command": "<command>",
      "args": ["<arg1>", "<arg2>"],
      "env": {
        "ENV_VAR": "value"
      }
    }
  }
}
```

### Current MCP Servers

| Name    | Command | Args                              |
|---------|---------|-----------------------------------|
| gitlab  | npx     | -y @structured-world/gitlab-mcp   |

### Notes for Claude Desktop

Claude Desktop reads MCP config from:
`%APPDATA%\Claude\claude_desktop_config.json`

Add the same `"mcpServers"` block under `"mcpServers"` in that file to make the server available globally in Claude Desktop.
