# Getting started

## Requirements

- Python 3.10 or newer.
- No external Python packages for the **current** classifier and checkpoint controller.
- Android/LibVLC playback, browser automation, GPU inference and Cortana integration are **not installed or operational**.

Clone and run from the repository root:

```bash
git clone https://github.com/billyke2000s/Mobiehub_universal_resolver.git
cd Mobiehub_universal_resolver
python -m unittest discover -s tests -v
python -m resolver.cli --input examples/sample-results.json --output audit-report.json
```

On Windows, `py -3` can replace `python` if needed. Open `audit-report.json` to inspect the grouped classifications.

**Important:** `examples/sample-results.json` contains synthetic observations, not evidence that any public site works. The CLI does not browse websites or play media.

## Python API example

```python
from resolver.controller import initialise, record_check, begin_repair, save, load

state = initialise(["example-provider"])
record_check(state, "example-provider", "movie", [
    {"provider": "example-provider", "kind": "movie", "error": "decoder_failure"}
])
if begin_repair(state, "example-provider", "movie", max_attempts=2):
    print("Repair attempt reserved; no repair has been executed")
save(state, "audit-state.json")
restored = load("audit-state.json")
print(restored["tasks"][0]["state"])
```

This records workflow state only. A future runner must supply actual checks and approved repair implementations.

## What to expect

Current results are deterministic classifications of supplied JSON. A `working` result means **the supplied booleans meet the classifier policy**, not that the tool independently witnessed playback. Trust depends on evidence provenance.

## Development workflow

1. Read `AGENTS.md`, `CONTRIBUTING.md` and relevant `docs/` pages.
2. Run existing tests before modifying code.
3. Make one small, reviewable change with a regression test.
4. Run tests again and report exact commands/results.
5. Keep unverified integration work labelled as such.
