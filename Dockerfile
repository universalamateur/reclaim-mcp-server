# =============================================================================
# Reclaim.ai MCP Server - Docker Image
# =============================================================================
# Multi-stage build for optimized production image
# Supports stdio transport for MCP protocol
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Builder
# -----------------------------------------------------------------------------
FROM python:3.12-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install poetry and export plugin
ENV POETRY_HOME="/opt/poetry"
ENV PATH="$POETRY_HOME/bin:$PATH"
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && poetry self add poetry-plugin-export

# Copy dependency files first for better caching
COPY pyproject.toml poetry.lock ./

# Export requirements (without dev dependencies)
RUN poetry export -f requirements.txt --without-hashes --without dev -o requirements.txt

# Build the wheel
COPY src/ src/
COPY README.md LICENSE ./
RUN poetry build -f wheel

# -----------------------------------------------------------------------------
# Stage 2: Runtime
# -----------------------------------------------------------------------------
FROM python:3.12-slim as runtime

# Security: Run as non-root user
RUN useradd --create-home --shell /bin/bash mcp

WORKDIR /app

# Install runtime dependencies only
COPY --from=builder /build/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install the built wheel
COPY --from=builder /build/dist/*.whl .
RUN pip install --no-cache-dir *.whl && rm *.whl requirements.txt

# Switch to non-root user
USER mcp

# MCP Registry metadata labels
# Required for ownership verification when publishing to registry.modelcontextprotocol.io
LABEL io.modelcontextprotocol.server.name="io.github.universalamateur/reclaim-mcp-server"
LABEL io.modelcontextprotocol.server.description="MCP server for Reclaim.ai calendar and task management"
LABEL org.opencontainers.image.source="https://github.com/universalamateur/reclaim-mcp-server"
LABEL org.opencontainers.image.description="Reclaim.ai MCP Server - Calendar and task management for AI assistants"
LABEL org.opencontainers.image.licenses="MIT"

# Environment configuration
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Health check - verify the package is importable
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from reclaim_mcp import __version__; print(__version__)" || exit 1

# MCP servers use stdio transport by default
# The RECLAIM_API_KEY must be provided at runtime
ENTRYPOINT ["reclaim-mcp-server"]
