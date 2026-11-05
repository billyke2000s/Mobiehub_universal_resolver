# Evidence, status and certification

## Implemented evidence contract

Each record requires a nonempty `provider` string and `kind` equal to `movie` or `series`. The current classifier recognizes these nine booleans:

| Field | Meaning |
|---|---|
| `identity_match` | The content played is the expected title/episode |
| `runtime_plausible` | Duration is plausible for that exact content |
| `decoded_frames` | Actual decoded video frames observed |
| `smooth_progress` | Playback advanced smoothly |
| `opening_audio` | Audio verified near the beginning |
| `midpoint_audio` | Audio verified near the middle |
| `late_audio` | Audio verified near the end |
| `midpoint_seek` | Seeking near the middle succeeded |
| `late_seek` | Seeking near the end succeeded |

**All nine must be literally `true`** for `route_passes`. Missing, false or truthy nonboolean values do not pass. The classifier does not itself measure these facts.

Example of a **synthetic fixture**, not real playback evidence:

```json
{
  "provider": "demo",
  "kind": "movie",
  "identity_match": true,
  "runtime_plausible": true,
  "decoded_frames": true,
  "smooth_progress": true,
  "opening_audio": true,
  "midpoint_audio": true,
  "late_audio": true,
  "midpoint_seek": true,
  "late_seek": true
}
```

Optional `error` values `http_403`, `access_challenge`, `geo_blocked` are treated as access blocks when **all** attempts have those errors. Any other error or `playback_attempted` with no passes yields `broken`.

## Status semantics

| Classifier result | Exact meaning |
|---|---|
| `working` | Every supplied route observation for that provider/kind passed all nine flags |
| `partial` | At least one passed, at least one did not |
| `blocked` | No passes; all attempts show recognized access-block errors |
| `broken` | No passes; at least one attempt has an error or playback was attempted |
| `unverified` | No pass and insufficient failure evidence |

The controller uses separate states: `pending`, `checking`, `working`, `needs_repair`, `repairing`, `blocked`, `unverified`, `failed`. It maps classifier `partial` and `broken` to `needs_repair`.

## Evidence provenance required for real certification (planned)

Future native observations should include: UTC timestamp, app build/commit, provider adapter revision, stable test title and episode IDs, expected and observed identity, stream/container/codec, actual resolution, duration, decoded-frame counts, buffering/stall intervals, audio sampling method, seek start/end positions, test device, player/decoder version, and anonymized error details. Include links or hashes to retained logs, never session tokens or full signed URLs.

A valid route should be tested on the **actual MovieHub Android LibVLC playback path**, not only desktop FFmpeg or a browser player. Compare like-for-like test content before and after a repair. Preserve failing alternatives in the report.

## Known limitations

- The current CLI accepts self-reported booleans; there is no signature, trusted producer or provenance validation.
- No actual duration thresholds, audio measurements, stall thresholds or content fingerprinting are implemented.
- No series inventory, unsupported-kind status or certification expiry exists.
- Never report a synthetic fixture, historical HTTP pass or resolved URL as a verified live site.
