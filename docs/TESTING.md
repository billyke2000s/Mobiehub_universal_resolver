# Testing and release criteria

## Current tests

```bash
python -m unittest discover -s tests -v
python -m resolver.cli --input examples/sample-results.json --output audit-report.json
```

The unit suite covers classifier flags, separate movie/series results, failed alternative routes, blocked cases, bounded repair attempts, and checkpoint persistence. These tests use **synthetic** evidence. Running them cannot prove a real provider works.

## Test pyramid (future)

1. **Unit:** input validation, classification, task transitions, budget limits, idempotence and serialization.
2. **Contract:** stable inventory IDs, evidence schema, local API, extension permissions, migration compatibility.
3. **Integration:** browser diagnostics, allowed media handler behaviour, native Android LibVLC telemetry.
4. **End-to-end:** representative movies and episodes, identity, plausible runtime, frames, smoothness, three audio checkpoints and two seeks.
5. **Regression:** previously passing routes remain passing after shared-handler or adapter updates.
6. **Security:** hostile site HTML, malicious model suggestions, malformed manifests, unauthorized requests and secret redaction.
7. **Packaging:** Windows Cortana EXE without plugin, with plugin, after plugin removal.

## Required before/after report

Every repaired provider/kind needs: initial status, exact failure, proposed change, test device, evidence timestamps, resulting status, regressions, rejected candidates and rollback target. Do not mark success based on build-only or URL-only checks.

## Honest status labels

- **Implemented:** code exists in repository.
- **Unit-tested:** tests actually executed and passed.
- **Integration-tested:** real components exercised.
- **Playback-verified:** native MovieHub player observed content and all acceptance signals.
- **Planned:** design only.
- **Blocked:** access or environmental limitation, not a pass.

Do not claim tests passed without a recorded run. CI is a separate task; this document does not imply CI currently exists.

## Local AI extension checks (5 November 2026)

`python -m unittest discover -s tests -v`: 24 tests passed locally, including real Chromium against a controlled changing-page/iframe fixture, recipe replay and challenge refusal. Source-proposal tests cover unique text, syntax, path/repository scope, explicit approval, stale-file refusal, restart recovery and rollback. HTTP tests cover token/Host/Origin/size checks, bounded workers and cancellation.

With the matching Cortana checkout beside this repo (or `CORTANA_CHECKOUT` set), the cross-repo contract test uses the actual Cortana host, resolver service and Ollama HTTP client with a scripted local model server. It prepares, approves, applies and rolls back a fixture source patch over real loopback HTTP. CI checks out both matching branches for this test.

These tests do not exercise real Qwen inference, live production sites, native Android playback, APK building or deployment. No site-fix certification follows from them.
