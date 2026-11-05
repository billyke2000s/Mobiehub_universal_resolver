# MovieHub Universal Resolver

Shared **source diagnostics and playback verification** for MovieHub. This repository is independent from the Android app and does not modify its 74 existing adapters.

## Purpose
1. Establish a baseline for each provider and **separately** for movie and series playback.
2. Run the same checks after any repair and record a before/after comparison.
3. Classify outcomes as working, partial, broken, blocked, or unverified.
4. Never confuse an extracted URL, successful HTTP request, or passing build with confirmed playback.
5. Preserve every failed attempt, evidence reference, and prior result.

## Quick start
Python 3.10+ required. Standard library only for the baseline CLI.

```sh
python -m unittest discover -s tests -v
python -m resolver.cli --input examples/sample-results.json --output audit-report.json
```

The CLI **classifies supplied evidence**; it does not pretend to play videos. A future Android/LibVLC evidence producer must supply decoded-frame, audio, seeking and runtime observations from real playback. No real-world site is marked working by the sample fixture.

## Evidence contract
Each observation contains provider ID, content kind (movie/series), expected and observed identity, runtime, native playback signals, audio samples, seek results, and optional errors. See `resolver/model.py`.

### Acceptance policy
A route passes only if identity matches, plausible runtime is recorded, decoded frames and smooth progress are measured, opening/midpoint/late audio are verified, and midpoint/late seeks succeed. A provider is **working** for a kind only with a passing route for that kind; failures of other routes remain visible. A provider with only movie evidence is not certified for series.

## Roadmap
- Import MovieHub's 74-provider inventory and historical receipts **without treating historical technical passes as current verification**.
- Implement an Android native evidence producer using MovieHub's actual player and seek guard.
- Group shared host/player patterns behind reusable, site-specific adapters; no bypass of access challenges or DRM.
- Add repeatable CI audit runs with per-site checkpoint artifacts and change detection.
- Wire confirmed improvements into MovieHub through reviewed PRs, never silently overwrite app code.

See [CONTRIBUTING.md](CONTRIBUTING.md) for verification and preservation rules.
