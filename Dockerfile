# Build stage: build a wheel from the source tree
FROM python:3.14-slim AS builder
WORKDIR /src
RUN pip install --no-cache-dir build
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN python -m build --wheel --outdir /dist

# Runtime stage: the installed package only, no dev dependencies
FROM python:3.14-slim
COPY --from=builder /dist/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/*.whl && rm -f /tmp/*.whl \
    && useradd --system --create-home --uid 10001 otx

# Default transport is stdio (docker run -i). The API key is supplied at
# runtime, never baked in: docker run -i --rm -e OTX_API_KEY=... <image>
#
# To serve streamable HTTP instead, listen on all interfaces inside the
# container, require a bearer token, and publish on localhost only:
#   docker run --rm -p 127.0.0.1:8000:8000 \
#     -e OTX_API_KEY=... \
#     -e OTX_MCP_TRANSPORT=streamable-http -e OTX_MCP_HOST=0.0.0.0 \
#     -e OTX_MCP_BEARER_TOKEN=... <image>
EXPOSE 8000

USER otx
ENTRYPOINT ["otx-mcp"]
