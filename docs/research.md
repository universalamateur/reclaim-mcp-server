# Reclaim.ai MCP Server: One Community Implementation Exists

**One working MCP server for Reclaim.ai exists—an unofficial community project**. No official MCP integration is available from Reclaim.ai, and the major MCP registries (modelcontextprotocol.io, mcp.run, smithery.ai, glama.ai) do not list any Reclaim-specific servers. However, the community solution is functional, published to npm, and actively maintained.

## The only working implementation: jj3ny/reclaim-mcp-server

The sole MCP server for Reclaim.ai is **jj3ny/reclaim-mcp-server**, a TypeScript implementation that wraps Reclaim's public REST API. With **9 GitHub stars** and **5 forks**, it represents the only option for integrating Reclaim.ai with MCP-capable AI clients like Claude Desktop, Cursor, or Continue.

| Attribute | Details |
|-----------|---------|
| **GitHub** | https://github.com/jj3ny/reclaim-mcp-server |
| **npm package** | `reclaim-mcp-server` |
| **Language** | TypeScript (90%), JavaScript (10%) |
| **License** | MIT |
| **Requirements** | Node.js ≥ 18, Reclaim API key |

The server provides **14 tools** focused on task management: `reclaim_list_tasks`, `reclaim_get_task`, `reclaim_create_task`, `reclaim_update_task`, `reclaim_mark_complete`, `reclaim_mark_incomplete`, `reclaim_delete_task`, `reclaim_add_time`, `reclaim_start_timer`, `reclaim_stop_timer`, `reclaim_log_work`, `reclaim_clear_exceptions`, and `reclaim_prioritize`. It also exposes a `tasks://active` resource for accessing active tasks.

Installation requires adding this configuration to Claude Desktop:

```json
{
  "mcpServers": {
    "reclaim": {
      "command": "npx",
      "args": ["reclaim-mcp-server"],
      "env": { "RECLAIM_API_KEY": "your_api_key_here" }
    }
  }
}
```

API keys can be generated at https://app.reclaim.ai/settings/developer.

## Official MCP registries show no Reclaim servers

Searches across the four major MCP registries yielded no results for Reclaim.ai:

- **modelcontextprotocol.io** — The official MCP registry focuses on reference servers (Filesystem, Git, Memory); no calendar-specific or Reclaim integrations
- **mcp.run** — Now pivoted to "Turbo MCP," an enterprise gateway platform rather than a public registry; mentions calendar integrations generically but lists no Reclaim server
- **smithery.ai** — Lists calendar servers for Google Calendar, Outlook, and Microsoft 365 Bookings, but nothing for Reclaim
- **glama.ai** — Features a dedicated calendar-management category with Google Calendar, CalDAV, and macOS Calendar servers; no Reclaim option

The community server is instead listed on secondary MCP directories: **mcp.so**, **MCPlane**, **Creati.ai**, **MCP Aibase**, and **mcpstore.co**. It has not yet been added to major curated lists like punkpeye/awesome-mcp-servers.

## Reclaim.ai offers no official MCP or AI assistant integration

Reclaim.ai's official integrations page (https://reclaim.ai/integrations) includes Google Calendar, Outlook, task managers (Todoist, Asana, Jira, ClickUp, Linear), Slack, Zoom, and a Raycast extension—but **no mention of MCP, Claude, or ChatGPT integrations**. The site states "Coming soon! We're always on the lookout for new tools."

Third-party workflow platforms like **Make.com** and **Zapier** can connect Reclaim.ai to OpenAI/ChatGPT, but these are automation triggers rather than MCP implementations. No native AI assistant integrations exist through official channels.

## GitHub and npm searches confirm a single implementation

GitHub searches for "reclaim mcp," "reclaim-ai mcp server," and similar queries return only the jj3ny repository. The official Reclaim.ai GitHub organization (https://github.com/reclaim-ai) maintains 7 repositories, none related to MCP.

On npm, the only relevant package is `reclaim-mcp-server`. Related packages like `@berlm/reclaim-mcp-server` (14 years old, unrelated) and `@recallnet/mcp` (Recall Network blockchain, different product) do not provide Reclaim.ai functionality. No official `@modelcontextprotocol/server-reclaim` package exists.

## Known limitations and caveats

The community server carries an explicit disclaimer: **"UNOFFICIAL & UNAFFILIATED – This project is not endorsed, sponsored, or supported by Reclaim.ai. It simply uses Reclaim's public API."** Users should comply with Reclaim's Terms of Service.

A notable behavioral quirk: Reclaim marks tasks as `COMPLETE` when their scheduled time block ends, even if the work isn't finished. This can confuse AI assistants when users ask for "open" or "active" tasks. Explicitly prompting to "include tasks with status COMPLETE" may be necessary.

## Conclusion

For users seeking MCP integration with Reclaim.ai today, **jj3ny/reclaim-mcp-server is the only option**—a working, npm-published, MIT-licensed community project with 14 task management tools. Official support does not exist, and major MCP registries don't list Reclaim servers. The gap suggests an opportunity for either Reclaim.ai to develop official MCP support or for the community solution to gain wider adoption and curation listing.