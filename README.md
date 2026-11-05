# MovieHub Universal Resolver

**A local AI browser resolver, with a separately installable Cortana extension.**

The goal is to handle changing search pages and real players with local AI, learn reusable navigation routes, and prepare small repairs against your actual MovieHub checkout. Repeating a whole-site audit is not the main workflow.

## Install and run

On Windows, double-click `Start Resolver.cmd`. It sets up Python/browser dependencies and asks for your MovieHub checkout if it cannot find one beside this repo. Or run:

```bash
python launch.py --moviehub /path/to/moviehub --model qwen3.5:9b
```

Keep the service open. In the updated Cortana: Systems → Extensions → Import extension → choose the private generated `moviehub-extension.json` path printed by the launcher → install → enable.

**[Full setup and exact limitations](docs/LOCAL_AI_EXTENSION.md)**. Cortana needs its matching generic extension-host update; the old v1.7.1 EXE does not contain it.

## What is implemented

| Capability | Current behaviour |
|---|---|
| Local AI browser navigation | Observed DOM elements/iframes, optional screenshots, constrained actions and media response capture |
| Learned navigation routes | Approval saves a recipe; later jobs replay it and recover from mismatches using fresh observations |
| Local MovieHub source repairs | Actual checkout input, small AI-proposed exact replacements, Python syntax checks, displayed diffs, approved apply and hash-checked rollback |
| Optional Cortana package | Four generic-host tools: start, job/inventory, apply/rollback, cancel |
| Local service | Authenticated loopback, bounded async jobs, private source checkpoints |
| Original evidence classifier/CLI | Retained; classifies supplied evidence without measuring native playback |
| Native MovieHub playback certification | Not implemented by this extension |
| Automatic APK build/deployment | Not implemented; use MovieHub's existing build/test workflow after reviewing source changes |

A discovered URL is `resolved_unverified`. A source edit is `patch_applied_unverified`. No real provider has been certified by the controlled fixture tests. Recipes run in the PC resolver; the Android app does not call this PC service.

## Tests

```bash
python -m pip install -r requirements.txt
python -m playwright install chromium
python -m unittest discover -s tests -v
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

## Native playback milestone

Extend the JSON registry inventory to include native provider definitions without executing them, and connect actual Android/LibVLC evidence collection. **Do not label all 74 sites working without real verification.**
