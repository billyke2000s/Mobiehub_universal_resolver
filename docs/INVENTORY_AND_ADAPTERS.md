# Site inventory and adapter contracts

> Planned; no MovieHub inventory importer or universal adapter engine exists yet.

## Import rules

Import provider IDs from the actual MovieHub repository at a pinned revision. Do not fabricate a list from historical discussions. Preserve existing IDs, labels, movie/series capability, disabled flags, URLs, search configuration, player handling and user-facing settings. Report added/removed/renamed providers as a reviewable diff.

The initial controller generates both movie and series tasks for every supplied provider. That is **not** evidence of series support. A future inventory model should represent `supported`, `unsupported` and `unknown` explicitly and skip unsupported kinds without reporting them broken.

## Declarative adapter proposal (future schema, not accepted by current code)

```json
{
  "schema_version": 1,
  "provider_id": "example-provider",
  "revision": "1",
  "capabilities": ["movie"],
  "search": {"mode": "html", "selectors": ["form[role=search]"]},
  "results": {"selectors": ["a[data-title]"]},
  "player": {"handler": "html5-video"},
  "enabled": false
}
```

This is illustrative. Never interpret it as a working configuration or load arbitrary selectors into privileged code without validation.

## Shared handlers

Group common supported players and hosts, but retain per-site exceptions. A generic handler should be versioned, independently tested and rolled back if it regresses multiple sites. Only work with content the user is authorized to access.

## Verification matrix

For each provider: movie supported? series supported? representative movie identity? episode identity? search works? player discovered? decoded playback? audio beginning/middle/end? seeking? failure type? evidence timestamp? adapter revision? No empty cell should be silently interpreted as pass.

## Historical data

Previous MovieHub audits and receipts may be imported as **historical observations** with dates and provenance. They must not become current certification automatically. A claimed inventory count is not a proof that the importer has read all current providers.
