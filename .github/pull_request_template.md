## Summary

<!-- What changes, and why. Link the issue if one applies. -->

## Checks

- [ ] `pytest` passes
- [ ] For changes to API calls or tools: tried the tool against the real OTX API, or explain why not
- Tested with: <!-- tool and input, e.g. get_indicator_details IPv4 8.8.8.8 reputation -->

## Checklist

- [ ] New tools that change the OTX account are added to `WRITE_TOOL_NAMES` and hidden in read-only mode.
- [ ] Large responses are capped or summarized so they fit an LLM context.
- [ ] No API keys, tokens or data from private investigations in code, docs, tests or this description.
- [ ] README and `docs/` are updated where tools, parameters or requirements changed.
- [ ] Changes to tool schemas or defaults are noted in `CHANGELOG.md`.
