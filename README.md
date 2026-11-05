# MovieHub Universal Resolver

**A standalone, evidence-driven audit and repair framework for MovieHub sources.**

> **Development status: early foundation.** The Python CLI, evidence classifier, bounded repair-task state machine and JSON checkpoints exist. Live extraction, self-healing, native playback telemetry, scheduler, API, and Cortana extension are **not implemented**. No real website is certified by the example data.

## Why this exists

MovieHub has a large and changing set of source adapters. Repeated manual audits are slow, expensive and prone to wasting time on already-working providers. The goal is to **check, skip passing routes, diagnose failures, attempt bounded repairs, verify playback and checkpoint progress**, without repeatedly requiring an AI assistant.

The resolver stays separate from MovieHub's Android app. An optional Cortana AI extension is planned, but normal Cortana installations must never contain MovieHub-specific menus or tools.

## What works today

| Capability | Status |
|---|---|
| Classify supplied evidence per provider and movie/series | Implemented |
| Strict nine-signal playback evidence policy | Implemented as a classifier; signals are **not measured** |
| JSON CLI report | Implemented |
| Create independent movie and series tasks | Implemented |
| Record check results and reserve limited repair attempts | Implemented |
| Save/load JSON checkpoints | Implemented |
| Import current MovieHub provider inventory | Planned |
| Browser extraction and native Android/LibVLC evidence collection | Planned |
| Automatic diagnosis, repair, validation and rollback | Planned |
| Local API, scheduled audits and dashboard | Planned |
| Installable Cortana extension | Planned |

## Quick start

Python 3.10+; current code uses the standard library only.

```bash
git clone https://github.com/billyke2000s/Mobiehub_universal_resolver.git
cd Mobiehub_universal_resolver
python -m unittest discover -s tests -v
python -m resolver.cli --input examples/sample-results.json --output audit-report.json
```

The sample observations are **synthetic**. A green report does not prove any live site works. The CLI only classifies input.

### Controller API example

```python
from resolver.controller import initialise, record_check, begin_repair, save

state = initialise(["example-provider"])
record_check(state, "example-provider", "movie", [
    {"provider": "example-provider", "kind": "movie", "error": "decoder_failure"}
])
if begin_repair(state, "example-provider", "movie", max_attempts=2):
    print("Attempt reserved; repair execution is not implemented")
save(state, "audit-state.json")
```

## Documentation

| Guide | Purpose |
|---|---|
| [Getting started](docs/GETTING_STARTED.md) | Installation, commands and current API |
| [Architecture](docs/ARCHITECTURE.md) | Component boundaries and implementation status |
| [Evidence and status](docs/EVIDENCE_AND_STATUS.md) | Exact classifier fields, results and certification policy |
| [Inventory and adapters](docs/INVENTORY_AND_ADAPTERS.md) | Preserving existing MovieHub sources and planned adapter schema |
| [Repair engine](docs/REPAIR_ENGINE.md) | Strict self-healing sequence, limits, approval and rollback |
| [Roadmap](docs/ROADMAP.md) | Milestones, gates and definition of done |
| [Cortana extension](docs/CORTANA_EXTENSION.md) | Optional plugin design; no changes to Cortana core |
| [Integration API](docs/INTEGRATION.md) | Proposed local API; not yet available |
| [Security](docs/SECURITY.md) | Untrusted sites/models, access controls and privacy |
| [Testing](docs/TESTING.md) | Tests and native playback acceptance criteria |
| [Troubleshooting](docs/TROUBLESHOOTING.md) | Common issues and limitations |
| [Contributing](CONTRIBUTING.md) | Engineering and preservation rules |
| [AI agent rules](AGENTS.md) | Scope discipline, checkpoints and truthful reporting |

## Core rules

- **Movie and series are independent.** Never infer one from the other.
- A URL, HTTP 200 or passing unit test is **not** playback verification.
- Real certification requires actual MovieHub Android/LibVLC identity, duration, decoded frames, smooth playback, audio at three points and successful seeking.
- Preserve existing providers, user data, failed alternatives and last known good configuration.
- No bypassing DRM, authentication, geoblocks or access challenges.
- Keep repairs bounded, reviewable and reversible.
- Cortana integration is optional and separately installed.

## Next concrete milestone

Import the exact provider inventory from MovieHub at a pinned commit, explicitly record supported kinds, then implement native playback evidence collection for a small authorized test set. **Do not label all 74 sites working without real verification.**
