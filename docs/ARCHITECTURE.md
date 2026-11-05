# Architecture

> The original audit design below is historical. The owner clarified the primary goal: local AI browser resolution and reusable site recovery. Implemented extension/service/browser/source-repair modules are described in [LOCAL_AI_EXTENSION.md](LOCAL_AI_EXTENSION.md); native playback telemetry remains planned.

## Goal and boundaries

MovieHub Universal Resolver is a separate, deterministic audit and repair coordinator for the MovieHub Android TV project. It is not an alternative video player or a built-in part of Cortana AI. The local browser agent uses a fixed, bounded set of observed-element actions.

The eventual components:

1. **Inventory importer** (planned): discover and preserve existing MovieHub provider IDs and supported content kinds. Record source revision and adapter version.
2. **Task controller** (partially implemented): one movie task and one series task per provider, with states, repair-attempt limits, history and JSON checkpoints.
3. **Evidence producers** (planned): browser/network observations plus **actual MovieHub LibVLC** decoded playback, identity, duration, seeking and audio signals.
4. **Evidence classifier** (implemented): group supplied observations by provider and kind; require all nine playback booleans to pass a route.
5. **Repair planner** (planned): bounded candidate selectors/host handlers; optional constrained local model proposals.
6. **Sandbox validator** (planned): compare before and after on the same titles and player, reject regressions, promote only approved and verified changes.
7. **Local service** (planned): exposes authenticated loopback-only API for a dashboard or optional Cortana extension.
8. **Cortana extension** (planned, separate package): installable adapter using generic Cortana extension APIs; not shipped in Cortana core.

```text
MovieHub inventory --> audit queue --> browser diagnostics
                           |                  |
                           |             candidate routes
                           v                  v
                     JSON checkpoint <-- native LibVLC observations
                           |
                      classifier
                           |
                    broken/partial?
                       /      \
                     no        yes
                     |          |
                   record    bounded repair proposal
                                |
                       isolated playback retest
                                |
                       review / promote / rollback
```

## Non-negotiable boundaries

- Site availability and HTTP success are **not** playback certification.
- A movie pass does **not** certify a series pass.
- Never delete providers, working source routes, user settings, or app data as a side effect of audit.
- Preserve the last known working configuration and log rejected proposals.
- Never bypass DRM, login, geoblocks, paywalls or access challenges.
- Do not run model-generated shell commands or arbitrary code.
- Cortana core stays generic; all MovieHub vocabulary and assets belong in its optional extension.

## Current implementation details

`controller.initialise(providers)` creates two tasks per provider, regardless of actual support. This is intentional for the baseline but **does not** imply every provider supports both kinds. A future inventory schema must explicitly record unsupported routes without treating them as broken.

`controller.record_check(...)` classifies supplied observations and maps partial/broken to `needs_repair`. `begin_repair(...)` increments an attempt counter; it does not execute a repair. `save/load` checkpoint JSON. There is no scheduler, lock, lease, retry timer, pause/resume API or native evidence producer yet.

`model.classify` currently labels a provider/kind **partial** if any observed alternative route fails, even when another route passes. This is a conservative route-set classification. Do not conflate it with a claim that the provider is unusable.

## Future module boundaries

`inventory/`: provider IDs, kinds, provenance, versioned capabilities.
`probes/`: authorized browser discovery and request diagnostics.
`players/`: Android/LibVLC telemetry adapter and test harness.
`repair/`: safe proposals, budget, validation, rollback.
`service/`: authenticated loopback API and event log.
`extensions/cortana/`: distributable extension manifest, tools and UI.

These paths are proposals, **not existing modules**.

## Implemented local extension path

`local_model.py`: structured local Ollama decisions. `browser.py`: ephemeral Chromium and DOM/iframe/media observations. `source_repair.py`: reads the real owner checkout, proposes exact replacements and applies/rolls back only hash-matching edits. `service.py`: authenticated loopback, async jobs, private proposal backups and recipe persistence. `extensions/cortana/manifest.json`: separately installed generic-host tool definitions. See LOCAL_AI_EXTENSION.md for limits. The older audit-controller API remains compatible.
