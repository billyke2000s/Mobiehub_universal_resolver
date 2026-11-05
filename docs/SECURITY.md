# Security and privacy

## Trust boundaries

- Website DOM, iframe messages, page scripts, video metadata and HTTP responses are **untrusted**.
- Local AI output is **untrusted**, even if produced on the user's PC.
- JSON checkpoint and audit inputs may be malformed or malicious.
- A Cortana extension must not inherit unrestricted OS permissions.

## Required controls for future implementations

- No DRM, authentication, paywall, CAPTCHA, geoblock or access-control bypass.
- No downloading or distributing protected media as part of tests.
- No executing arbitrary website scripts outside a sandbox or passing page text as agent instructions.
- Never run model-proposed Python, shell, PowerShell or JavaScript.
- Allow-list declarative repair types and bound selector length, URL schemes, response sizes, timeouts and redirects.
- Bind service to loopback, authenticate clients, check origin, apply CSRF protection where appropriate, and restrict CORS.
- Require explicit approval before publishing repairs or mutating MovieHub.
- Sanitize logs: redact credentials, signed query strings, cookies, tokens, session IDs and personal browsing data.
- Store only necessary evidence with defined retention; do not commit local audit logs or secrets.
- Version all config changes; maintain rollback and an append-only audit trail.
- Limit resource use, parallelism and retry budgets to avoid overloading sites or the user's PC.

## Current implementation caveats

The CLI reads local JSON and writes a report. The controller loads JSON checkpoints and validates only basic shape/state; it is **not hardened** for hostile inputs or concurrent writers. Do not expose it directly to untrusted network clients. No network listener exists today.

## Responsible operation

Only test sources and content you have permission to access. Respect website terms and rate limits. When a source blocks access, report the block rather than evading it.
