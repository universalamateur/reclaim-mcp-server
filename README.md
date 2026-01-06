# Reclaim.ai MCP Server _(UNOFFICIAL)_

[![PyPI](https://img.shields.io/pypi/v/reclaim-mcp-server)](https://pypi.org/project/reclaim-mcp-server/) [![Downloads](https://img.shields.io/pypi/dm/reclaim-mcp-server)](https://pypi.org/project/reclaim-mcp-server/) [![Python](https://img.shields.io/pypi/pyversions/reclaim-mcp-server)](https://pypi.org/project/reclaim-mcp-server/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **UNOFFICIAL** – Not affiliated with Reclaim.ai. Uses their public API , use at your own risk.

Control your [Reclaim.ai](https://reclaim.ai) calendar, tasks, and habits from AI assistants via [MCP](https://modelcontextprotocol.io).

## What You Can Do

```text
"Create a 2-hour task to review the Q1 budget, due Friday"
"What's on my calendar tomorrow?"
"Mark my morning workout habit as done"
"Show me my productivity stats for last week"
"Start a focus block for the next 90 minutes"
```

**40 tools** across tasks, calendar, habits, focus time, and analytics. See [docs/TOOLS.md](docs/TOOLS.md) for complete reference.

## Quick Start

### 1. Get your API key: <https://app.reclaim.ai/settings/developer>

### 2. Install

```bash
pip install reclaim-mcp-server
```

### 3. Configure Claude Desktop (`~/Library/Application Support/Claude/claude_desktop_config.json`)

```json
   {
     "mcpServers": {
       "reclaim": {
         "command": "uvx",
         "args": ["reclaim-mcp-server"],
         "env": { "RECLAIM_API_KEY": "your_key_here" }
       }
     }
   }
```

### 4. Restart Claude Desktop

## Installation Options

| Method | Command |
|--------|---------|
| **uvx** (recommended) | `uvx reclaim-mcp-server` |
| **pip** | `pip install reclaim-mcp-server` |
| **Smithery** | `npx -y @smithery/cli install universalamateur/reclaim-mcp-server --client claude` |
| **Docker** | `docker pull universalamateur/reclaim-mcp-server` |
| **Source** | `git clone https://gitlab.com/universalamateur1/reclaim-mcp-server.git && cd reclaim-mcp-server && poetry install` |

**Registries:** [PyPI](https://pypi.org/project/reclaim-mcp-server/) · [Smithery](https://smithery.ai/server/universalamateur/reclaim-mcp-server) · [Glama](https://glama.ai/mcp/servers/@universalamateur/reclaim-mcp-server) · [GitHub](https://github.com/universalamateur/reclaim-mcp-server) · [GitLab](https://gitlab.com/universalamateur1/reclaim-mcp-server)

## Tool Profiles

Limit exposed tools via `RECLAIM_TOOL_PROFILE`:

| Profile | Tools | Use Case |
|---------|-------|----------|
| `minimal` | 20 | Basic task/habit management |
| `standard` | 32 | Daily productivity |
| `full` | 40 | All features (default) |

```json
{
  "mcpServers": {
    "reclaim": {
      "command": "uvx",
      "args": ["reclaim-mcp-server"],
      "env": {
        "RECLAIM_API_KEY": "your_key_here",
        "RECLAIM_TOOL_PROFILE": "standard"
      }
    }
  }
}
```

## Other Configurations

<details>
<summary>Docker</summary>

```json
{
  "mcpServers": {
    "reclaim": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "-e", "RECLAIM_API_KEY", "universalamateur/reclaim-mcp-server"],
      "env": { "RECLAIM_API_KEY": "your_key_here" }
    }
  }
}
```

</details>

<details>
<summary>Poetry (from source)</summary>

```json
{
  "mcpServers": {
    "reclaim": {
      "command": "/opt/homebrew/bin/poetry",
      "args": ["--directory", "/path/to/reclaim-mcp-server", "run", "reclaim-mcp-server"],
      "env": { "RECLAIM_API_KEY": "your_key_here" }
    }
  }
}
```

**Note**: Use `--directory` flag instead of `cwd` – Claude Desktop doesn't respect `cwd`.

</details>

<details>
<summary>Other MCP clients (Cursor, Continue, Zed, etc.)</summary>

Works with any MCP-compatible client. Generic stdio config:

```json
{
  "command": "uvx",
  "args": ["reclaim-mcp-server"],
  "env": { "RECLAIM_API_KEY": "your_key_here" }
}
```

</details>

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Invalid API key" | Verify key at <https://app.reclaim.ai/settings/developer> |
| Rate limited (429) | Server handles retries automatically; reduce request frequency |
| Tools not showing | Restart Claude Desktop after config change |
| Docker ARM64 warning | Use v0.8.1+ for native Apple Silicon support |

## Development

```bash
poetry install
poetry run pytest                    # Run tests
poetry run black src tests           # Format
poetry run mypy src                  # Type check
poetry run fastmcp dev src/reclaim_mcp/server.py  # Dev mode
```

## Links

- [Changelog](CHANGELOG.md)
- [Tool Reference](docs/TOOLS.md)
- [Contributing](CONTRIBUTING.md)
- [Report Issue](https://gitlab.com/universalamateur1/reclaim-mcp-server/-/issues/new)

## License

[MIT](LICENSE) – Falko Sieverding ([@UniversalAmateur](https://gitlab.com/UniversalAmateur))

---

<sub>Built with [FastMCP](https://gofastmcp.com) · Not affiliated with [Reclaim.ai](https://reclaim.ai)</sub>
