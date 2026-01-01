This guide outlines best practices for developing MCP servers using `fastmcp`, specifically tailored for API wrappers that require authentication.

### **I. DOS \- Best Practices**

#### **1\. Code Organization & Server Structure**

* **Use Functional Decorators:** Leverage `@mcp.tool` and `@mcp.resource` to reduce boilerplate. Keep your tool definitions clean by delegating complex logic to a separate service layer or API client class.  
* **Context Injection:** Use the `Context` object for request-scoped data. If your tool needs access to metadata (like a request ID or logging), add `ctx: Context` as the first argument to your tool function. `fastmcp` will inject it automatically.  
* **Pydantic for Validation:** Rely on Python type hints (Pydantic models) for tool arguments. This automatically generates the JSON Schema required by the MCP protocol, ensuring the LLM sends structured, validated data.

#### **2\. Error Handling & Recovery**

* **Return "LLM-Readable" Errors:** Do not raise generic exceptions that crash the server. Instead, catch API errors and return a descriptive string that guides the LLM on how to fix it.  
    
* *Good:* `return "Error: City not found. Please check the spelling or try a major nearby city."`  
    
* *Bad:* `raise ValueError("404 Not Found")`  
    
* **Use `ToolError` for Control Flow:** If a tool *must* fail in a way that signals the client to stop, use specific exception types that `fastmcp` recognizes as "tool errors" (checking documentation for the specific version, or returning a structured error response).

#### **3\. Logging & Monitoring**

* **Use the Context Logger:** Avoid `print()` statements, especially in STDIO mode, as they can corrupt the JSON-RPC communication channel. Use `ctx.info()`, `ctx.warning()`, or the standard `logging` module configured to write to `stderr`.  
* **Sanitize Logs:** strictly filter logs to ensure API keys and user PII (Personally Identifiable Information) are never written to `stderr` or log files.

#### **4\. Rate Limiting & Throttling**

* **Handle Rate Limits Gracefully:** If the wrapped API returns a 429 (Too Many Requests), catch it and return a message telling the LLM to wait.  
    
* *Example:* `"Rate limit exceeded. Please wait 60 seconds before retrying this request."`  
    
* **Implement Caching:** Use `@functools.lru_cache` or a dedicated caching layer for `@mcp.resource` endpoints to prevent hammering the external API for static data (e.g., fetching a list of available categories).

#### **5\. Testing**

* **Use `pytest` with `fastmcp.Client`:** Write integration tests where you spin up your server and connect to it using the `Client` provided by `fastmcp`.  
* **Snapshot Testing:** Use `inline-snapshot` to verify the JSON structure of your tool results matches expectations without manually asserting every field.

---

### **II. DON'TS \- Anti-Patterns**

* **❌ The "Universal Proxy" Trap:** Do not blindly wrap every single endpoint of an API (e.g., `GET /api/*`). This confuses the LLM with too many choices.  
    
* *Fix:* Curate specific "high-value" tools that map to user intents (e.g., `search_products` instead of `get_product_by_id`, `get_product_list`, `get_product_categories`).  
    
* **❌ Hardcoded Credentials:** Never define API keys as default values in function arguments or global variables in your code.  
    
* **❌ Silent Failures:** Don't catch an exception and return `None` or an empty string. The LLM will hallucinate a success or get confused. Always return a message explaining *why* it failed.  
    
* **❌ Blocking the Event Loop:** If your API wrapper uses a synchronous library (like `requests`), do not run it directly in an `async def` tool. This blocks the server from handling other requests.  
    
* *Fix:* Use an asynchronous library like `httpx` or run synchronous code in a thread pool.  
    
* **❌ Over-reliance on "State":** Avoid trying to maintain complex conversation state inside the MCP server (global variables). MCP servers should ideally be stateless, relying on the client (LLM) to pass necessary context in each request.

---

### **III. API Key Specific Considerations**

Handling API keys in MCP servers requires balancing security with usability.

#### **1\. Storage & Injection (The "Configuration" Pattern)**

The standard way to handle API keys is via **Environment Variables** passed to the MCP server process by the client configuration (e.g., Claude Desktop config).

* **How it works:**  
1. The user configures their client (e.g., `claude_desktop_config.json`) with the API key in the `env` map.  
2. Your server reads this via `os.environ["API_KEY"]`.  
* **Why:** This keeps the key out of the tool arguments (which consumes context window tokens) and out of the git repository.

#### **2\. Handling User-Provided Keys (The "Argument" Pattern)**

If your server is public/multi-tenant and you cannot store the key (e.g., a "BYO Key" scenario), you must require the key as a tool argument.

* **Implementation:**

```py
@mcp.tool
def fetch_data(query: str, api_key: str) -> str:
    """
    Fetches data.
    args:
        query: The search query
        api_key: The user's API key (do not log this)
    """
    ...

```

* **Warning:** This is less secure as the key may appear in the LLM's conversation history or context logs. Use only if necessary.

#### **3\. Validation & Rotation**

* **Fail Fast:** Validate the API key availability at server startup (if using Env Vars). If it's missing, log a warning to `stderr` immediately so the user knows why the connection failed.  
* **Key Rotation:** Since MCP servers are often long-lived processes (daemon style), ensure your code re-reads the environment variable or configuration if the API returns an "Authentication Failed" error, or simply crash the process to force a restart with new config.

#### **4\. Architecture Diagram: API Wrapper Pattern**

1. **Client (Claude)** sends JSON-RPC request (`call_tool`).  
2. **MCP Server** validates request using Pydantic.  
3. **Tool Handler** retrieves API Key from `os.environ`.  
4. **HTTP Client** (`httpx`) calls External API with `Authorization` header.  
5. **MCP Server** sanitizes response (removes raw tokens) and returns result to Client.