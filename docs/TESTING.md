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
