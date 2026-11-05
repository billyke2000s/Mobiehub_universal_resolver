# Troubleshooting

## Python cannot find `resolver`

Run commands from the repository root using `python -m resolver.cli`, not `python resolver/cli.py`.

## Report says working but the site fails

The current CLI **trusts input booleans**; it never plays media. Inspect provenance and confirm the observation was collected by a real native player. Synthetic fixtures must not be used for certification.

## A provider is partial despite one working route

The classifier is conservative: any failed alternative makes the provider/kind `partial`. Check `passing_routes`, `attempted_routes` and individual attempts. A future policy may distinguish primary route health from optional alternatives.

## A series is marked broken for a movie-only site

The controller currently creates both kinds for every provider. Explicit unsupported-kind inventory support is planned; do not try to repair an intentionally unsupported kind.

## A repair never happens

`begin_repair` only reserves an attempt. It does not contain repair logic. No browser runner or local AI is connected yet.

## Cannot resume a running job

Checkpoint save/load exists, but a scheduler and pause/resume service do not. A new process can load saved state programmatically; it cannot yet resume in-flight browser work.

## Site returns 403, challenge or geo block

Record `blocked`. Do not try to bypass access controls. Test authorized sources instead.

## Cortana does not show the extension

The Cortana extension is **not built or installable**. The integration documents are a design, not installation instructions.

## JSON errors

Validate JSON syntax, ensure the input is an array, include a nonempty provider and a kind of `movie` or `series`. Nine literal boolean flags are needed for a route to pass.

## Reporting a bug

Provide sanitized traceback, exact command, Python version, expected vs actual output, provider/kind, and a small synthetic reproduction. Never share cookies, credentials or signed media URLs.
