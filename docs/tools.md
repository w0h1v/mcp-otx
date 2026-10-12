# Tool reference

29 tools: 20 read tools that are always available, and 9 write tools (marked **write**) that only appear with `--read-write`. Every tool returns JSON. Large OTX objects are summarized and long lists capped, with the API's total counts kept.

Sample outputs are real responses from the OTX API, captured on 2026-10-12 with public indicators. Long lists are cut to a few entries and marked `… N more`, and long strings end in `…`. Tools that return your own account's data (subscriptions, your pulses, submissions) and write tools have no sample.

| Tool | Group | Mode |
|---|---|---|
| [`search_pulses`](#search_pulses) | Search | read |
| [`search_users`](#search_users) | Search | read |
| [`get_indicator_details`](#get_indicator_details) | Indicators | read |
| [`validate_indicator`](#validate_indicator) | Indicators | read |
| [`list_indicator_types`](#list_indicator_types) | Indicators | read |
| [`export_indicators`](#export_indicators) | Indicators | read |
| [`get_pulse_details`](#get_pulse_details) | Pulses | read |
| [`get_pulse_indicators`](#get_pulse_indicators) | Pulses | read |
| [`get_related_pulses`](#get_related_pulses) | Pulses | read |
| [`search_related_pulses`](#search_related_pulses) | Pulses | read |
| [`list_pulse_activity`](#list_pulse_activity) | Pulses | read |
| [`list_subscribed_pulses`](#list_subscribed_pulses) | Pulses | read |
| [`get_subscribed_pulse_ids`](#get_subscribed_pulse_ids) | Pulses | read |
| [`get_pulse_events`](#get_pulse_events) | Pulses | read |
| [`create_pulse`](#create_pulse) | Pulses | **write** |
| [`subscribe_pulse`](#subscribe_pulse) | Pulses | **write** |
| [`unsubscribe_pulse`](#unsubscribe_pulse) | Pulses | **write** |
| [`get_user`](#get_user) | Users | read |
| [`list_user_pulses`](#list_user_pulses) | Users | read |
| [`get_current_user`](#get_current_user) | Users | read |
| [`list_my_pulses`](#list_my_pulses) | Users | read |
| [`subscribe_user`](#subscribe_user) | Users | **write** |
| [`unsubscribe_user`](#unsubscribe_user) | Users | **write** |
| [`follow_user`](#follow_user) | Users | **write** |
| [`unfollow_user`](#unfollow_user) | Users | **write** |
| [`list_submitted_urls`](#list_submitted_urls) | Submissions | read |
| [`list_submitted_files`](#list_submitted_files) | Submissions | read |
| [`submit_url`](#submit_url) | Submissions | **write** |
| [`submit_urls`](#submit_urls) | Submissions | **write** |

## Search

### `search_pulses`

Full-text search across all public OTX pulses. The best starting point for threat research: search for a malware family, actor, campaign or technology and get matching pulses with their IDs, then pull details or indicators.

| Parameter | Type | Required | Default | Notes |
|---|---|---|---|---|
| `query` | string | yes |  | Search terms. |
| `limit` | integer | no | `10` | Results per page (1-500). |
| `page` | integer | no | `1` | 1-based page number. |

<details markdown="1">
<summary>Sample output: <code>{"query": "emotet", "limit": 2}</code></summary>

```json
{
  "count": 2155,
  "results": [
    {
      "id": "5900f9e1afc8d868448457e1",
      "name": "Emotet / Nemucod Phishing Campaign 20170425",
      "description": "Widespread phishing campaign with pdf attachements that contain a link to various sites with malicious javascript file.",
      "author_name": "jonmega",
      "modified": "2017-04-26T21:32:22.428000",
      "created": "2017-04-26T19:49:53.911000",
      "tags": [],
      "references": [],
      "public": 1,
      "adversary": "",
      "targeted_countries": [],
      "malware_families": [],
      "attack_ids": [],
      "industries": [],
      "TLP": "white",
      "revision": 9,
      "groups": [],
      "in_group": false,
      "author": {
        "username": "jonmega",
        "id": "2445",
        "avatar_url": "https://otx.alienvault.com/assets/images/default-avatar.png",
        "is_subscribed": false,
        "is_following": false
      },
      "is_subscribing": null
    },
    {
      "id": "5900ff2120c314026661fac4",
      "name": "New Variant of Geodo/Emotet Banking Malware Targets UK | Forcepoint",
      "description": "The campaign appeared to peak on 18 April 2017 and primarily targeted email addresses associated with .UK TLDs. The subject line of the emails sent varied sl…",
      "author_name": "Gargomel",
      "modified": "2017-04-26T20:12:17.476000",
      "created": "2017-04-26T20:12:17.476000",
      "tags": [],
      "references": [],
      "public": 1,
      "adversary": "",
      "targeted_countries": [],
      "malware_families": [],
      "attack_ids": [],
      "industries": [],
      "TLP": "white",
      "revision": 1,
      "groups": [],
      "in_group": false,
      "author": {
        "username": "Gargomel",
        "id": "17466",
        "avatar_url": "https://otx.alienvault.com/assets/images/default-avatar.png",
        "is_subscribed": false,
        "is_following": false
      },
      "is_subscribing": null
    }
  ],
  "exact_match": "",
  "previous": null,
  "next": "https://otx.alienvault.com/api/v1/search/pulses?q=emotet&limit=2&page=2"
}
```

</details>

### `search_users`

Search OTX users by username.

| Parameter | Type | Required | Default | Notes |
|---|---|---|---|---|
| `query` | string | yes |  | Username (or fragment) to search for. |
| `limit` | integer | no | `10` | Results per page (1-500). |
| `page` | integer | no | `1` | 1-based page number. |

<details markdown="1">
<summary>Sample output: <code>{"query": "alienvault", "limit": 2}</code></summary>

```json
{
  "results": [
    {
      "subscriber_count": 0,
      "follower_count": 0,
      "member_since": "754 days ago ",
      "avatar_url": "https://otx.alienvault.com/assets/images/default-avatar.png",
      "award_count": 0,
      "awards": [],
      "user_id": 294284,
      "username": "1alienvaultuser",
      "indicator_count": 0,
      "pulse_count": 0,
      "accepted_edits_count": 0
    },
    {
      "subscriber_count": 2,
      "follower_count": 0,
      "member_since": "3267 days ago ",
      "avatar_url": "https://otx.alienvault.com/assets/images/default-avatar.png",
      "award_count": 0,
      "awards": [],
      "user_id": 45001,
      "username": "4979-AlienVault",
      "indicator_count": 0,
      "pulse_count": 0,
      "accepted_edits_count": 0
    }
  ],
  "count": 1233,
  "previous": null,
  "next": "https://otx.alienvault.com/api/v1/search/users?q=alienvault&limit=2&page=2"
}
```

</details>


## Indicators

### `get_indicator_details`

Get threat intelligence details for an indicator from AlienVault OTX. This is the primary indicator lookup tool. It covers every OTX indicator type and detail section in one call.

| Parameter | Type | Required | Default | Notes |
|---|---|---|---|---|
| `indicator_type` | string | yes |  | URL path type. One of: IPv4, IPv6, domain, hostname, file (any hash: MD5/SHA1/SHA256/PEHASH/IMPHASH), url, cve, nids, correlation-rule. |
| `indicator_value` | string | yes |  | The indicator itself (IP address, domain, file hash, URL, CVE id...). |
| `section` | string | no | `"general"` | Detail section to retrieve. Availability depends on type: IPv4/IPv6: general, geo, reputation, url_list, passive_dns, malware, nids_list, http_scans \| domain/hostname: general, geo, url_list, passive_dns, malware, whois, http_scans \| file: general, analysis (sandbox report) \| url: general, url_list, http_scans, screenshot \| cve: general, nids_list, malware. Use 'general' first: it includes pulse associations, reputation and geo summaries. |

Sections by indicator type:

| `indicator_type` | `section` values |
|---|---|
| `IPv4`, `IPv6` | `general`, `geo`, `reputation`, `url_list`, `passive_dns`, `malware`, `nids_list`, `http_scans` |
| `domain`, `hostname` | `general`, `geo`, `url_list`, `passive_dns`, `malware`, `whois`, `http_scans` |
| `file` (MD5, SHA-1, SHA-256, PEHASH, IMPHASH) | `general`, `analysis` |
| `url` | `general`, `url_list`, `http_scans`, `screenshot` |
| `cve` | `general`, `nids_list`, `malware` |

In the `general` section, related pulses are summarized (id, name, author, dates, TLP, tags, malware families, adversary, ATT&CK ids, indicator count) and capped at 10, with the total in `pulse_info.count`. For CVEs, the configuration tree becomes up to 30 affected CPEs, each with its version range (for example `cpe:2.3:a:apache:log4j:* (>= 2.0.1, < 2.3.1)`), and up to 10 platform CPEs: configurations the vulnerable product runs on, which are not affected themselves. Exploits and references are capped at 20.

<details markdown="1">
<summary>Sample output (IPv4, general): <code>{"indicator_type": "IPv4", "indicator_value": "8.8.8.8", "section": "general"}</code></summary>

```json
{
  "whois": "http://whois.domaintools.com/8.8.8.8",
  "reputation": 0,
  "indicator": "8.8.8.8",
  "type": "IPv4",
  "type_title": "IPv4",
  "base_indicator": {
    "id": 11911,
    "indicator": "8.8.8.8",
    "type": "IPv4",
    "title": "",
    "description": "",
    "content": "",
    "access_type": "public",
    "access_reason": ""
  },
  "pulse_info": {
    "count": 0,
    "pulses": [],
    "references": [],
    "related": {
      "alienvault": {
        "adversary": [],
        "malware_families": [],
        "industries": []
      },
      "other": {
        "adversary": [],
        "malware_families": [],
        "industries": []
      }
    },
    "pulses_shown": 0
  },
  "false_positive": [
    {
      "assessment": "accepted",
      "assessment_date": "2021-05-19T15:36:44.966000",
      "report_date": "2021-03-16T14:46:19.003000"
    }
  ],
  "validation": [
    {
      "source": "false_positive",
      "message": "Known False Positive",
      "name": "Known False Positive"
    },
    {
      "source": "whitelist",
      "message": "contained in whitelisted prefix",
      "name": "Whitelisted IP"
    }
  ],
  "asn": "AS15169 google llc",
  "city_data": true,
  "city": null,
  "region": null,
  "continent_code": "NA",
  "country_code3": "USA",
  "country_code2": "US",
  "subdivision": null,
  "latitude": 37.751,
  "postal_code": null,
  "longitude": -97.822,
  "accuracy_radius": 1000,
  "country_code": "US",
  "country_name": "United States of America",
  "dma_code": 0,
  "charset": 0,
  "area_code": 0,
  "flag_url": "/assets/images/flags/us.png",
  "flag_title": "United States of America",
  "sections": [
    "general",
    "geo",
    "reputation",
    "… 5 more"
  ]
}
```

</details>

<details markdown="1">
<summary>Sample output (File hash, general): <code>{"indicator_type": "file", "indicator_value": "275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f", "section": "general"}</code></summary>

```json
{
  "sections": [
    "general",
    "analysis"
  ],
  "type": "sha256",
  "type_title": "FileHash-SHA256",
  "indicator": "275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f",
  "validation": [],
  "base_indicator": {
    "id": 22820,
    "indicator": "44d88612fea8a8f36de82e1278abb02f",
    "type": "FileHash-MD5",
    "title": "",
    "description": "",
    "content": "",
    "access_type": "public",
    "access_reason": ""
  },
  "pulse_info": {
    "count": 50,
    "pulses": [
      {
        "id": "6aa8875963573e64ffa113bd",
        "name": "Umbald • Neconyd • Banker.LY • Ramnit  • Malicious Media (Credit OctoSeek 11/06/2026)",
        "author": "Q.Vashti",
        "created": "2026-09-14T23:46:33.025000",
        "modified": "2026-09-14T23:46:33.025000",
        "TLP": "green",
        "tags": [
          "whois record",
          "ssl certificate",
          "historical ssl",
          "… 7 more"
        ],
        "malware_families": [
          "Tsara Brashears",
          "Mitre Attack",
          "ET",
          "… 5 more"
        ],
        "attack_ids": [
          "T1056",
          "T1027",
          "T1090",
          "… 7 more"
        ],
        "indicator_count": 13104
      },
      {
        "id": "6a2d8d06c162afe209cca676",
        "name": "Auditoría_Servicios_Críticos_Jeff",
        "author": "YoungJr0707",
        "created": "2026-06-13T17:01:53.660000",
        "modified": "2026-07-13T17:04:00.535000",
        "TLP": "white",
        "adversary": [
          "Lab3"
        ],
        "indicator_count": 1
      },
      {
        "id": "698ccef65de079ed10f80c7a",
        "name": "Loki scan",
        "author": "skocherhan",
        "created": "2026-02-11T18:48:22.434000",
        "modified": "2026-07-10T00:07:38.655000",
        "TLP": "green",
        "indicator_count": 14144
      },
      "… 7 more"
    ],
    "references": [
      "http-robots.txt.nse",
      "rpc-grind.nse",
      "rmi-vuln-classloader.nse",
      "… 17 more"
    ],
    "related": {
      "alienvault": {
        "adversary": [],
        "malware_families": [],
        "industries": []
      },
      "other": {
        "adversary": [
          "Lab3",
          "Unknown"
        ],
        "malware_families": [
          "",
          "Trojanspy",
          "Ransom:win32/pottieq",
          "… 17 more"
        ],
        "industries": [
          "Education",
          "Defense",
          "Healthcare",
          "… 3 more"
        ]
      }
    },
    "pulses_shown": 10,
    "note": "Showing 10 of 50 related pulses; use get_pulse_details for one or search_pulses for more.",
    "references_total": 715
  },
  "false_positive": []
}
```

</details>

<details markdown="1">
<summary>Sample output (CVE, general): <code>{"indicator_type": "cve", "indicator_value": "CVE-2021-44228", "section": "general"}</code></summary>

```json
{
  "sections": [
    "general",
    "nids_list",
    "malware"
  ],
  "mitre_url": "https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2021-44228",
  "nvd_url": "https://web.nvd.nist.gov/view/vuln/detail?vulnId=CVE-2021-44228",
  "indicator": "CVE-2021-44228",
  "type_title": "CVE",
  "base_indicator": {
    "id": 3325076393,
    "indicator": "CVE-2021-44228",
    "type": "CVE",
    "title": "",
    "description": "",
    "content": "",
    "access_type": "public",
    "access_reason": ""
  },
  "pulse_info": {
    "count": 50,
    "pulses": [
      {
        "id": "6ac9101554900e3ae83df111",
        "name": "The Scalpel vs. The Sledgehammer: Lessons in Precision Triage from the .conf26 SOC",
        "author": "AlienVault",
        "created": "2026-10-09T16:02:29.260000",
        "modified": "2026-10-12T23:05:38.825000",
        "TLP": "white",
        "tags": [
          "conference network security",
          "cdn infrastructure",
          "precision blocking",
          "… 5 more"
        ],
        "attack_ids": [
          "T1568.002",
          "T1071.004",
          "T1071",
          "… 7 more"
        ],
        "indicator_count": 3
      },
      {
        "id": "6a99adbec32d94dc6cd05ee1",
        "name": "Chinese-Speaking Operator Uses AI Agents to Target Government and Education Systems Across Asia",
        "author": "AlienVault",
        "created": "2026-09-03T17:26:22.072000",
        "modified": "2026-10-03T17:09:01.416000",
        "TLP": "white",
        "tags": [
          "ai-assisted intrusions",
          "secbox",
          "steganographic payloads",
          "… 4 more"
        ],
        "malware_families": [
          "SecBox",
          "GLUTTON"
        ],
        "attack_ids": [
          "T1003",
          "T1133",
          "T1021.004",
          "… 7 more"
        ],
        "indicator_count": 50
      },
      {
        "id": "6accf71c088bad7be96a72c3",
        "name": "Actively_Exploited_Kev | Oct 13, 2026",
        "author": "LTNA-Australia",
        "created": "2026-10-12T15:05:00.640000",
        "modified": "2026-10-12T15:05:00.640000",
        "TLP": "white",
        "tags": [
          "actively_exploited_kev"
        ],
        "indicator_count": 1739
      },
      "… 7 more"
    ],
    "references": [
      "",
      "SHA-256: fc1fedce1419d4e2009828aad8644deca78b4eeed176e5b009797e0eb0d7d3ff — Detected as Win.Malware.Vtflooder / Trojan:Win32/Vflooder; UPX-packed PE32 execut…",
      "https://vtbehaviour.commondatastorage.googleapis.com/910c6d6b843dae92d9b13230244646f972dfbc3136b8455916c74e8d6da423ac_CAPE%20Sandbox.html?GoogleAccessId=7586…",
      "… 17 more"
    ],
    "related": {
      "alienvault": {
        "adversary": [],
        "malware_families": [
          "Glutton",
          "Secbox"
        ],
        "industries": [
          "Education",
          "Government",
          "Telecommunications"
        ]
      },
      "other": {
        "adversary": [
          "Adversary Profile: Salt Typhoon Alignment The architectural gap identified by mudoSO mirrors the act"
        ],
        "malware_families": [
          "Glutton",
          "Secbox"
        ],
        "industries": [
          "Critical_infrastructure",
          "Energy",
          "Healthcare",
          "… 4 more"
        ]
      }
    },
    "pulses_shown": 10,
    "note": "Showing 10 of 50 related pulses; use get_pulse_details for one or search_pulses for more.",
  … trimmed for the docs
```

</details>

<details markdown="1">
<summary>Sample output (Domain, whois): <code>{"indicator_type": "domain", "indicator_value": "example.com", "section": "whois"}</code></summary>

```json
{
  "data": [
    {
      "key": "name_servers",
      "name": "Name Servers",
      "value": "A.IANA-SERVERS.NET"
    },
    {
      "key": "creation_date",
      "name": "Creation Date",
      "value": "1995-08-14T00:00:00"
    },
    {
      "key": "domain_name",
      "name": "Domain Name",
      "value": "EXAMPLE.COM"
    },
    "… 9 more"
  ],
  "count": 12,
  "related": [
    {
      "domain": "internic.org",
      "related": "A.IANA-SERVERS.NET",
      "related_type": "hostname"
    },
    {
      "domain": "afralo.org",
      "related": "A.IANA-SERVERS.NET",
      "related_type": "hostname"
    },
    {
      "domain": "arpa-servers.org",
      "related": "A.IANA-SERVERS.NET",
      "related_type": "hostname"
    },
    "… 18 more"
  ]
}
```

</details>

### `validate_indicator`

Validate an indicator value/type pair before using it in a pulse.

| Parameter | Type | Required | Default | Notes |
|---|---|---|---|---|
| `indicator` | string | yes |  | The indicator value to validate. |
| `indicator_type` | string | yes |  | OTX indicator type name, e.g. IPv4, domain, FileHash-SHA256, URL, CVE, YARA, JA3, Mutex, CIDR, email. |
| `description` | string | no | `""` | Optional description used during validation. |

<details markdown="1">
<summary>Sample output: <code>{"indicator": "8.8.8.8", "indicator_type": "IPv4"}</code></summary>

```json
{
  "content": "",
  "description": "",
  "title": "",
  "access_type": "public",
  "access_reason": "",
  "access_groups": [],
  "expiration": "2026-11-11T16:00:00",
  "is_active": true,
  "role": null,
  "type": "IPv4",
  "indicator": "8.8.8.8",
  "status": "success",
  "message": "",
  "validation": [
    {
      "source": "false_positive",
      "message": "Known False Positive",
      "name": "Known False Positive"
    },
    {
      "source": "suspicious",
      "message": "suspiciously short IP (len: 7)",
      "name": "Suspicious IP format / Possible version number"
    },
    {
      "source": "whitelist",
      "message": "contained in whitelisted prefix",
      "name": "Whitelisted IP"
    }
  ]
}
```

</details>

### `list_indicator_types`

List every indicator type usable in OTX pulses, with descriptions. Use this to discover valid indicator_type values for validate_indicator and create_pulse.

No parameters.

<details markdown="1">
<summary>Sample output: <code>{}</code></summary>

```json
{
  "result": [
    {
      "name": "IPv4",
      "description": "An IPv4 address indicating the online location of a server or other computer.",
      "slug": "ip"
    },
    {
      "name": "IPv6",
      "description": "An IPv6 address indicating the online location of a server or other computer.",
      "slug": "ip"
    },
    {
      "name": "domain",
      "description": "A domain name for a website or server. Domains encompass a series of hostnames.",
      "slug": "domain"
    },
    "… 18 more"
  ]
}
```

</details>

### `export_indicators`

Bulk export indicators across all subscribed pulses (feed sync).

| Parameter | Type | Required | Default | Notes |
|---|---|---|---|---|
| `types` | string[] | no |  | Indicator type names to include (e.g. ["domain", "IPv4", "FileHash-SHA256"]); omit for all types. |
| `limit` | integer | no | `50` | Results per page (1-500). |
| `page` | integer | no | `1` | 1-based page number. |
| `modified_since` | string | no |  | ISO 8601 timestamp; only return indicators from pulses modified after this time. |


## Pulses

### `get_pulse_details`

Get full details of an OTX pulse by ID. Includes name, author, description, TLP, tags, references, threat categories (Adversary, Malware, TTPs) and the pulse's indicators.

| Parameter | Type | Required | Default | Notes |
|---|---|---|---|---|
| `pulse_id` | string | yes |  | 24-character hex pulse ID (from search results, activity feeds, or OTX URLs). |

<details markdown="1">
<summary>Sample output: <code>{"pulse_id": "6acce5442679f83db50e1656"}</code></summary>

```json
{
  "id": "6acce5442679f83db50e1656",
  "name": "HTTP Range in small image (S3#)",
  "description": "HTTP range in small image. The goal is to consume server resources. The same IP address may appear more than once a day.",
  "author_name": "BotnetExposer",
  "modified": "2026-10-12T13:48:52.618000",
  "created": "2026-10-12T13:48:52.618000",
  "tags": [
    "tcp",
    "http",
    "image",
    "… 4 more"
  ],
  "references": [],
  "public": 1,
  "adversary": "",
  "targeted_countries": [],
  "malware_families": [],
  "attack_ids": [],
  "industries": [],
  "TLP": "green",
  "indicators": [
    {
      "id": 4523604532,
      "indicator": "128.201.103.179",
      "type": "IPv4",
      "created": "2026-10-12T13:48:53",
      "content": "",
      "title": "",
      "description": "",
      "expiration": "2026-11-11T13:00:00",
      "is_active": 1
    },
    {
      "id": 3982961287,
      "indicator": "128.201.187.217",
      "type": "IPv4",
      "created": "2026-10-12T13:48:53",
      "content": "",
      "title": "",
      "description": "",
      "expiration": "2026-11-11T13:00:00",
      "is_active": 1
    },
    {
      "id": 3475435212,
      "indicator": "128.201.242.58",
      "type": "IPv4",
      "created": "2026-10-12T13:48:53",
      "content": "",
      "title": "",
      "description": "",
      "expiration": "2026-11-11T13:00:00",
      "is_active": 1
    },
    "… 48 more"
  ],
  "revision": 1,
  "groups": [],
  "in_group": false,
  "author": {
    "username": "BotnetExposer",
    "id": "80256",
    "avatar_url": "/otxapi/users/avatar_image/media/avatars/user_80256/resized/80/avatar_f1760e796f.png",
    "is_subscribed": true,
    "is_following": false
  },
  "is_subscribing": null
}
```

</details>

### `get_pulse_indicators`

List the indicators contained in a pulse (paginated).

| Parameter | Type | Required | Default | Notes |
|---|---|---|---|---|
| `pulse_id` | string | yes |  | 24-character hex pulse ID. |
| `limit` | integer | no | `100` | Results per page (1-1000). |
| `page` | integer | no | `1` | 1-based page number. |
| `include_inactive` | boolean | no | `false` | Include indicators the pulse author deactivated. |

<details markdown="1">
<summary>Sample output: <code>{"pulse_id": "6acce5442679f83db50e1656", "limit": 3}</code></summary>

```json
{
  "results": [
    {
      "pulse_key": "6acce5442679f83db50e1656",
      "id": 4523604532,
      "indicator": "128.201.103.179",
      "type": "IPv4",
      "created": "2026-10-12T13:48:53",
      "content": "",
      "title": "",
      "description": "",
      "expiration": "2026-11-11T13:00:00",
      "is_active": 1,
      "false_positive": {
        "assessment": null,
        "assessment_date": null,
        "report_date": null
      },
      "slug": "ip"
    },
    {
      "pulse_key": "6acce5442679f83db50e1656",
      "id": 3982961287,
      "indicator": "128.201.187.217",
      "type": "IPv4",
      "created": "2026-10-12T13:48:53",
      "content": "",
      "title": "",
      "description": "",
      "expiration": "2026-11-11T13:00:00",
      "is_active": 1,
      "false_positive": {
        "assessment": null,
        "assessment_date": null,
        "report_date": null
      },
      "slug": "ip"
    },
    {
      "pulse_key": "6acce5442679f83db50e1656",
      "id": 3475435212,
      "indicator": "128.201.242.58",
      "type": "IPv4",
      "created": "2026-10-12T13:48:53",
      "content": "",
      "title": "",
      "description": "",
      "expiration": "2026-11-11T13:00:00",
      "is_active": 1,
      "false_positive": {
        "assessment": null,
        "assessment_date": null,
        "report_date": null
      },
      "slug": "ip"
    }
  ],
  "count": 1566,
  "previous": null,
  "next": "https://otx.alienvault.com/api/v1/pulses/6acce5442679f83db50e1656/indicators?limit=3&page=2"
}
```

</details>

### `get_related_pulses`

Get pulses that share indicators (IOCs) with the given pulse.

| Parameter | Type | Required | Default | Notes |
|---|---|---|---|---|
| `pulse_id` | string | yes |  | 24-character hex pulse ID. |
| `limit` | integer | no | `10` | Results per page (1-500). |
| `page` | integer | no | `1` | 1-based page number. |

<details markdown="1">
<summary>Sample output: <code>{"pulse_id": "6acce5442679f83db50e1656", "limit": 2}</code></summary>

```json
{
  "count": 204,
  "results": [
    {
      "id": "6acc9ed9f4456563f0c565be",
      "name": "HTTP Range in small image (S3#)",
      "description": "HTTP range in small image. The goal is to consume server resources. The same IP address may appear more than once a day.",
      "author_name": "BotnetExposer",
      "modified": "2026-10-12T08:48:25.798000",
      "created": "2026-10-12T08:48:25.798000",
      "tags": [
        "tcp",
        "http",
        "image",
        "… 4 more"
      ],
      "references": [],
      "public": 1,
      "adversary": "",
      "targeted_countries": [],
      "malware_families": [],
      "attack_ids": [],
      "industries": [],
      "TLP": "green",
      "revision": 1,
      "groups": [],
      "in_group": false,
      "author": {
        "username": "BotnetExposer",
        "id": "80256",
        "avatar_url": "/otxapi/users/avatar_image/media/avatars/user_80256/resized/80/avatar_f1760e796f.png",
        "is_subscribed": true,
        "is_following": false
      },
      "is_subscribing": null,
      "indicator_count": 1639,
      "indicators_note": "Indicators omitted; use get_pulse_indicators for this pulse."
    },
    {
      "id": "6acc58200227829b399ae30f",
      "name": "HTTP Range in small image (S3#)",
      "description": "HTTP range in small image. The goal is to consume server resources. The same IP address may appear more than once a day.",
      "author_name": "BotnetExposer",
      "modified": "2026-10-12T03:46:40.134000",
      "created": "2026-10-12T03:46:40.134000",
      "tags": [
        "tcp",
        "http",
        "image",
        "… 4 more"
      ],
      "references": [],
      "public": 1,
      "adversary": "",
      "targeted_countries": [],
      "malware_families": [],
      "attack_ids": [],
      "industries": [],
      "TLP": "green",
      "revision": 1,
      "groups": [],
      "in_group": false,
      "author": {
        "username": "BotnetExposer",
        "id": "80256",
        "avatar_url": "/otxapi/users/avatar_image/media/avatars/user_80256/resized/80/avatar_f1760e796f.png",
        "is_subscribed": true,
        "is_following": false
      },
      "is_subscribing": null,
      "indicator_count": 1362,
      "indicators_note": "Indicators omitted; use get_pulse_indicators for this pulse."
    }
  ],
  "previous": null,
  "next": "https://otx.alienvault.com/api/v1/pulses/6acce5442679f83db50e1656/related?limit=2&page=2"
}
```

</details>

### `search_related_pulses`

Find pulses related to a pulse, malware family, or adversary. Pass exactly ONE of pulse_id, malware_family or adversary. For a pulse, returns other pulses sharing some of the same IOCs; for a malware family or adversary, returns pulses tagged with it.

| Parameter | Type | Required | Default | Notes |
|---|---|---|---|---|
| `pulse_id` | string | no |  | Pulse to find related pulses for. |
| `malware_family` | string | no |  | Malware family name. NOTE: OTX's malware_family filtering is currently unreliable (it returns no results regardless of value); use search_pulses with the family name instead. |
| `adversary` | string | no |  | Adversary name (e.g. "Equation Group"). |
| `limit` | integer | no | `10` | Results per page (1-500). |
| `page` | integer | no | `1` | 1-based page number. |

<details markdown="1">
<summary>Sample output: <code>{"adversary": "APT28", "limit": 2}</code></summary>

```json
{
  "count": 101,
  "results": [
    {
      "id": "5c0065158a36f90c7125d130",
      "name": "A BREXIT-themed lure document that delivers ZEKAPAB malware",
      "description": "As the United Kingdom (UK) Prime Minister Theresa May announced the initial BREXIT draft agreement with the\nEuropean Union (EU), iDefense analysts identified…",
      "author_name": "AlienVault",
      "modified": "2018-12-21T16:34:21.621000",
      "created": "2018-11-29T22:15:49.025000",
      "tags": [
        "Zebrocy",
        "APT28",
        "ZEKAPAB",
        "… 3 more"
      ],
      "references": [
        "https://www.accenture.com/t20181129T203820Z__w__/us-en/_acnmedia/PDF-90/Accenture-snakemackerel-delivers-zekapab-malware.pdf#zoom=50",
        "https://www.vkremez.com/2018/12/lets-learn-dissecting-apt28sofacy.html"
      ],
      "public": 1,
      "adversary": "APT28",
      "targeted_countries": [],
      "malware_families": [],
      "attack_ids": [],
      "industries": [],
      "TLP": "white",
      "revision": 3,
      "groups": [],
      "in_group": false,
      "author": {
        "username": "AlienVault",
        "id": "2",
        "avatar_url": "/otxapi/users/avatar_image/media/avatars/user_2/resized/80/avatar_dacfad0ca8.png",
        "is_subscribed": true,
        "is_following": false
      },
      "is_subscribing": null,
      "indicator_count": 13,
      "indicators_note": "Indicators omitted; use get_pulse_indicators for this pulse."
    },
    {
      "id": "5f3581cc4138be1d82c183b8",
      "name": "Russian GRU 85th GTsSS Deploys Previously Undisclosed Drovorub Malware",
      "description": "Drovorub is a Linux malware toolset consisting of an implant coupled with a kernel module rootkit, a file transfer and port forwarding tool, and a Command an…",
      "author_name": "AlienVault",
      "modified": "2020-09-12T00:01:57.830000",
      "created": "2020-08-13T18:09:16.421000",
      "tags": [
        "Fancy Bear",
        "APT28",
        "Strontium",
        "… 1 more"
      ],
      "references": [
        "https://media.defense.gov/2020/Aug/13/2002476465/-1/-1/0/CSA_DROVORUB_RUSSIAN_GRU_MALWARE_AUG_2020.PDF"
      ],
      "public": 1,
      "adversary": "APT28",
      "targeted_countries": [],
      "malware_families": [
        "Drovorub",
        "Drovorub-server",
        "Drovorub-client",
        "… 1 more"
      ],
      "attack_ids": [
        "T1014",
        "T1041",
        "T1059",
        "… 2 more"
      ],
      "industries": [],
      "TLP": "white",
      "revision": 1,
      "groups": [],
      "in_group": false,
      "author": {
        "username": "AlienVault",
        "id": "2",
        "avatar_url": "/otxapi/users/avatar_image/media/avatars/user_2/resized/80/avatar_dacfad0ca8.png",
        "is_subscribed": true,
        "is_following": false
      },
      "is_subscribing": null,
      "indicator_count": 4,
      "indicators_note": "Indicators omitted; use get_pulse_indicators for this pulse."
    }
  ],
  "previous": null,
  "next": "https://otx.alienvault.com/api/v1/pulses/related?adversary=APT28&limit=2&page=2"
}
```

</details>

### `list_pulse_activity`

List the latest pulses across the whole OTX community.

| Parameter | Type | Required | Default | Notes |
|---|---|---|---|---|
| `limit` | integer | no | `10` | Results per page (1-500). |
| `page` | integer | no | `1` | 1-based page number. |
| `modified_since` | string | no |  | ISO 8601 timestamp cutoff. |

<details markdown="1">
<summary>Sample output: <code>{"limit": 2}</code></summary>

```json
{
  "count": 239073,
  "results": [
    {
      "id": "6acce5442679f83db50e1656",
      "name": "HTTP Range in small image (S3#)",
      "description": "HTTP range in small image. The goal is to consume server resources. The same IP address may appear more than once a day.",
      "author_name": "BotnetExposer",
      "modified": "2026-10-12T13:48:52.618000",
      "created": "2026-10-12T13:48:52.618000",
      "tags": [],
      "references": [],
      "public": 1,
      "adversary": "",
      "targeted_countries": [],
      "malware_families": [],
      "attack_ids": [],
      "industries": [],
      "TLP": "green",
      "revision": 1,
      "groups": [],
      "in_group": false,
      "author": {
        "username": "BotnetExposer",
        "id": "80256",
        "avatar_url": "/otxapi/users/avatar_image/media/avatars/user_80256/resized/80/avatar_f1760e796f.png",
        "is_subscribed": true,
        "is_following": false
      },
      "is_subscribing": null,
      "indicator_count": 1566,
      "indicators_note": "Indicators omitted; use get_pulse_indicators for this pulse."
    },
    {
      "id": "6acce52f45b5135f141b4c95",
      "name": "Open an aggressive number of TCP connections (S3#)",
      "description": "Open of agressive number of TCP connections. The goal is to consume server resources. The same IP address may appear more than once a day.",
      "author_name": "BotnetExposer",
      "modified": "2026-10-12T13:48:31.836000",
      "created": "2026-10-12T13:48:31.836000",
      "tags": [],
      "references": [],
      "public": 1,
      "adversary": "",
      "targeted_countries": [],
      "malware_families": [],
      "attack_ids": [],
      "industries": [],
      "TLP": "green",
      "revision": 1,
      "groups": [],
      "in_group": false,
      "author": {
        "username": "BotnetExposer",
        "id": "80256",
        "avatar_url": "/otxapi/users/avatar_image/media/avatars/user_80256/resized/80/avatar_f1760e796f.png",
        "is_subscribed": true,
        "is_following": false
      },
      "is_subscribing": null,
      "indicator_count": 3,
      "indicators_note": "Indicators omitted; use get_pulse_indicators for this pulse."
    }
  ],
  "previous": null,
  "next": "https://otx.alienvault.com/api/v1/pulses/activity?limit=2&page=2"
}
```

</details>

### `list_subscribed_pulses`

List pulses from your OTX subscriptions. Includes pulses you subscribed to, pulses from users and groups you follow, and pulses you created.

| Parameter | Type | Required | Default | Notes |
|---|---|---|---|---|
| `limit` | integer | no | `10` | Results per page (1-500). |
| `page` | integer | no | `1` | 1-based page number. |
| `modified_since` | string | no |  | ISO 8601 timestamp; only pulses created or modified after this time. |

### `get_subscribed_pulse_ids`

Get just the IDs of your subscribed pulses (lightweight sync).

| Parameter | Type | Required | Default | Notes |
|---|---|---|---|---|
| `limit` | integer | no | `500` | Results per page (1-500). |
| `page` | integer | no | `1` | 1-based page number. |

### `get_pulse_events`

List events from your subscription stream (pulse lifecycle changes). Useful for incremental sync: each event carries an `action` field (e.g. remove_pulse) naming what happened to which pulse.

| Parameter | Type | Required | Default | Notes |
|---|---|---|---|---|
| `limit` | integer | no | `10` | Results per page (1-500). |
| `page` | integer | no | `1` | 1-based page number. |
| `modified_since` | string | no |  | ISO 8601 timestamp cutoff. |

### `create_pulse`

!!! warning "Write tool"
    Only available with `--read-write`. It changes your OTX account.

Create a new OTX pulse owned by the authenticated user. Validate indicators with validate_indicator first. Each indicator is {"type": <indicator type name>, "indicator": <value>, "description": "..."}.

| Parameter | Type | Required | Default | Notes |
|---|---|---|---|---|
| `name` | string | yes |  | Pulse title. |
| `description` | string | no | `""` | Markdown description of the threat. |
| `public` | boolean | no | `false` | Whether the pulse is publicly visible. |
| `tlp` | string | no | `"amber"` | TLP marking: white, green, amber or red. |
| `tags` | string[] | no |  | Threat tags (e.g. ["malware", "rat"]). |
| `references` | string[] | no |  | Reference URLs. |
| `indicators` | object[] | no |  | Indicators to include; see validate_indicator. |

### `subscribe_pulse`

!!! warning "Write tool"
    Only available with `--read-write`. It changes your OTX account.

Subscribe to a pulse so its indicators enter your feeds.

| Parameter | Type | Required | Default | Notes |
|---|---|---|---|---|
| `pulse_id` | string | yes |  |  |

### `unsubscribe_pulse`

!!! warning "Write tool"
    Only available with `--read-write`. It changes your OTX account.

Unsubscribe from a pulse.

| Parameter | Type | Required | Default | Notes |
|---|---|---|---|---|
| `pulse_id` | string | yes |  |  |


## Users

### `get_user`

Get an OTX user's profile.

| Parameter | Type | Required | Default | Notes |
|---|---|---|---|---|
| `username` | string | yes |  | OTX username. |
| `detailed` | boolean | no | `true` | Include the user's recent pulses in the response. |

<details markdown="1">
<summary>Sample output: <code>{"username": "AlienVault", "detailed": false}</code></summary>

```json
{
  "subscriber_count": 408529,
  "follower_count": 6668,
  "member_since": "4259 days ago ",
  "avatar_url": "/otxapi/users/avatar_image/media/avatars/user_2/resized/80/avatar_dacfad0ca8.png",
  "award_count": 0,
  "user_id": 2,
  "username": "AlienVault",
  "indicator_count": 558541,
  "pulse_count": 9203
}
```

</details>

### `list_user_pulses`

List pulses authored by a specific OTX user.

| Parameter | Type | Required | Default | Notes |
|---|---|---|---|---|
| `username` | string | yes |  | OTX username. |
| `limit` | integer | no | `10` | Results per page (1-500). |
| `page` | integer | no | `1` | 1-based page number. |

<details markdown="1">
<summary>Sample output: <code>{"username": "AlienVault", "limit": 2}</code></summary>

```json
{
  "count": 9203,
  "results": [
    {
      "id": "6ac8a46214e2077a0bfe7409",
      "name": "NEBULA: Seven Fake AI SDK Packages on npm Install a Windows RAT That Needs No DLL",
      "description": "In late September 2026, an actor deployed seven malicious npm packages masquerading as a NebulaAI software development kit to deliver a Windows remote-access…",
      "modified": "2026-10-09T08:26:24.879000",
      "created": "2026-10-09T08:22:58.387000",
      "tags": [],
      "references": [],
      "public": 1,
      "adversary": "",
      "targeted_countries": [],
      "malware_families": [],
      "attack_ids": [],
      "industries": [],
      "TLP": "white",
      "cloned_from": null,
      "export_count": 0,
      "upvotes_count": 0,
      "downvotes_count": 0,
      "votes_count": 0,
      "locked": false,
      "pulse_source": "api",
      "validator_count": 0,
      "comment_count": 0,
      "follower_count": 0,
      "vote": 0,
      "author": {
        "username": "AlienVault",
        "id": "2",
        "avatar_url": "/otxapi/users/avatar_image/media/avatars/user_2/resized/80/avatar_dacfad0ca8.png",
        "is_subscribed": true,
        "is_following": false
      },
      "indicator_type_counts": {
        "FileHash-SHA256": 4,
        "IPv4": 1,
        "URL": 1,
        "domain": 2,
        "hostname": 1
      },
      "indicator_count": 9,
      "is_author": false,
      "is_subscribing": null,
      "subscriber_count": 408529,
      "modified_text": "3 days ago ",
      "is_modified": false,
      "groups": [],
      "in_group": false,
      "threat_hunter_scannable": true,
      "threat_hunter_has_agents": 1
    },
    {
      "id": "6ac8a22f8d0ad1ea5f056ddc",
      "name": "Unknown Threat Actor Uses AI-Driven ARTEX to Target South Korean Finance",
      "description": "An unidentified threat actor, likely Chinese-speaking and financially motivated, conducted targeted attacks against South Korean financial institutions betwe…",
      "modified": "2026-10-09T08:19:50.747000",
      "created": "2026-10-09T08:13:35.684000",
      "tags": [],
      "references": [],
      "public": 1,
      "adversary": "",
      "targeted_countries": [],
      "malware_families": [],
      "attack_ids": [],
      "industries": [],
      "TLP": "white",
      "cloned_from": null,
      "export_count": 0,
      "upvotes_count": 0,
      "downvotes_count": 0,
      "votes_count": 0,
      "locked": false,
      "pulse_source": "api",
      "validator_count": 0,
      "comment_count": 0,
      "follower_count": 0,
      "vote": 0,
      "author": {
        "username": "AlienVault",
        "id": "2",
        "avatar_url": "/otxapi/users/avatar_image/media/avatars/user_2/resized/80/avatar_dacfad0ca8.png",
        "is_subscribed": true,
        "is_following": false
      },
      "indicator_type_counts": {
        "IPv4": 10,
        "domain": 1
      },
      "indicator_count": 11,
      "is_author": false,
      "is_subscribing": null,
      "subscriber_count": 408529,
      "modified_text": "3 days ago ",
      "is_modified": true,
      "groups": [],
      "in_group": false,
      "threat_hunter_scannable": true,
      "threat_hunter_has_agents": 1
    }
  ],
  "previous": null,
  "next": "https://otx.alienvault.com/api/v1/pulses/user/AlienVault?limit=2&page=2"
}
```

</details>

### `get_current_user`

Get the authenticated user's own OTX profile (whoami). Handy to confirm which account the API key belongs to.

No parameters.

### `list_my_pulses`

List pulses authored by the authenticated user (your own pulses).

| Parameter | Type | Required | Default | Notes |
|---|---|---|---|---|
| `limit` | integer | no | `10` | Results per page (1-500). |
| `page` | integer | no | `1` | 1-based page number. |

### `subscribe_user`

!!! warning "Write tool"
    Only available with `--read-write`. It changes your OTX account.

Subscribe to a user; their pulses enter your subscribed feed.

| Parameter | Type | Required | Default | Notes |
|---|---|---|---|---|
| `username` | string | yes |  |  |

### `unsubscribe_user`

!!! warning "Write tool"
    Only available with `--read-write`. It changes your OTX account.

Unsubscribe from a user.

| Parameter | Type | Required | Default | Notes |
|---|---|---|---|---|
| `username` | string | yes |  |  |

### `follow_user`

!!! warning "Write tool"
    Only available with `--read-write`. It changes your OTX account.

Follow a user (their activity shows in your OTX dashboard).

| Parameter | Type | Required | Default | Notes |
|---|---|---|---|---|
| `username` | string | yes |  |  |

### `unfollow_user`

!!! warning "Write tool"
    Only available with `--read-write`. It changes your OTX account.

Unfollow a user.

| Parameter | Type | Required | Default | Notes |
|---|---|---|---|---|
| `username` | string | yes |  |  |


## Submissions

### `list_submitted_urls`

List URLs previously submitted for analysis by your account.

| Parameter | Type | Required | Default | Notes |
|---|---|---|---|---|
| `limit` | integer | no | `10` | Results per page (1-500). |
| `page` | integer | no | `1` | 1-based page number. |

### `list_submitted_files`

List files previously submitted for analysis by your account.

| Parameter | Type | Required | Default | Notes |
|---|---|---|---|---|
| `limit` | integer | no | `10` | Results per page (1-500). |
| `page` | integer | no | `1` | 1-based page number. |

### `submit_url`

!!! warning "Write tool"
    Only available with `--read-write`. It changes your OTX account.

Submit a URL to OTX for analysis. OTX will visit the URL and analyze returned content. Results appear via get_indicator_details with indicator_type "url".

| Parameter | Type | Required | Default | Notes |
|---|---|---|---|---|
| `url` | string | yes |  | The URL to analyze. |
| `tlp` | string | no | `"amber"` | TLP marking for the submission: white, green, amber or red. |

### `submit_urls`

!!! warning "Write tool"
    Only available with `--read-write`. It changes your OTX account.

Submit multiple URLs to OTX for bulk analysis.

| Parameter | Type | Required | Default | Notes |
|---|---|---|---|---|
| `urls` | string[] | yes |  | URLs to analyze. |
| `tlp` | string | no | `"amber"` | TLP marking for the submissions: white, green, amber or red. |
