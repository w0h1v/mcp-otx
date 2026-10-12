# Example workflows

Prompts you can give an agent with mcp-otx connected, and the tool calls they lead to. All of these work in the default read-only mode.

## Enrich an IP from an alert

> *"What does OTX know about 8.8.8.8? Reputation, passive DNS, and any pulses that mention it."*

1. `get_indicator_details` with `{"indicator_type": "IPv4", "indicator_value": "8.8.8.8", "section": "general"}`: pulse count, related pulses, validation notes.
2. The same call with `"section": "reputation"`, then `"passive_dns"` (passive DNS can take 20–60 s on busy IPs).

## Investigate a file hash

> *"Is 275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f malicious, and what did the sandbox see?"*

1. `get_indicator_details` with `{"indicator_type": "file", "indicator_value": "<hash>", "section": "general"}`.
2. The same call with `"section": "analysis"` for sandbox results.

MD5, SHA-1, SHA-256, PEHASH and IMPHASH all use `indicator_type: "file"`.

## Research a malware family or campaign

> *"Find recent OTX pulses about Emotet and list their indicators."*

1. `search_pulses` with `{"query": "emotet", "limit": 5}`.
2. `get_pulse_details` with the `id` of the most relevant pulse.
3. `get_pulse_indicators` with that `pulse_id` to page through all of its indicators.
4. `get_related_pulses` to find other pulses sharing those indicators.

## Track an adversary

> *"What has OTX published about APT28 lately?"*

1. `search_related_pulses` with `{"adversary": "APT28", "limit": 10}`.
2. `get_pulse_details` on the pulses worth reading.

## Check a CVE

> *"Is there OTX intelligence on CVE-2021-44228?"*

1. `get_indicator_details` with `{"indicator_type": "cve", "indicator_value": "CVE-2021-44228", "section": "general"}`: CVSS, exploits, affected products and related pulses.

## Keep a feed in sync

> *"Export the domains and IPs from my subscribed pulses that changed since yesterday."*

1. `export_indicators` with `{"types": ["domain", "IPv4"], "modified_since": "2026-10-11T00:00:00"}`.
2. Page with `page` until there's no `next`.

This uses your subscriptions, so subscribe to pulses or users on OTX first (or with the write tools).

## Vet a source

> *"Who is AlienVault on OTX and what have they published recently?"*

1. `get_user` with `{"username": "AlienVault"}`.
2. `list_user_pulses` with `{"username": "AlienVault", "limit": 5}`.
