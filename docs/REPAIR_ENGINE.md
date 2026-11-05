# Self-healing and bounded repairs

> This document specifies intended behaviour. **Automatic repairs are not implemented.**

## Strict sequence

1. Read current inventory and previous checkpoint.
2. Check one provider/kind against a fixed test title or episode.
3. If fully working, record and skip; do not rework it.
4. If blocked by access controls, record `blocked` and stop; do not attempt bypass.
5. If partial/broken, classify failure stage (search, result navigation, iframe, media URL, decoder, audio, seek, identity).
6. Try safe, deterministic recovery candidates first: known selectors, supported DOM structure alternatives, shared host/player handlers, and previously validated patterns.
7. Optionally ask a local model to **propose a bounded declarative change** from sanitized evidence. The model must not execute arbitrary code or request secrets.
8. Test the proposal in isolation with the same native player and content. Compare against baseline; reject regressions.
9. Require approval before changing persistent configuration or MovieHub code. Save a versioned artifact and rollback reference.
10. Checkpoint and move to the next task, including failures.

## Budget and anti-drift rules

- Default maximum **two repair attempts per provider/kind** in the existing controller; valid range 1–10.
- A repair attempt must be attached to one provider/kind and one diagnosed failure.
- Never loop endlessly on CAPTCHA, authentication, geo restriction, DRM or ambiguous content identity.
- Never add unrelated features or rewrite working adapters during a repair.
- Stop on exhausted budget, missing evidence, unknown access conditions, or safety regression.
- Persist status before starting the next task; do not discard a partial run.
- Show what changed and why, not only a commit count.

## Proposal shape (planned)

```json
{
  "provider": "example-provider",
  "kind": "movie",
  "base_revision": "example-sha",
  "failure_stage": "player_discovery",
  "proposal_type": "selector_fallback",
  "candidate": {"selector": "video"},
  "rationale": "Illustrative only; not an observed repair"
}
```

All fields require schema validation and an explicit allow-list. Never accept executable JavaScript, shell commands, arbitrary Python, browser security overrides, or credentials as a proposed patch.

## Acceptance and rollback (planned)

A repair can be promoted only after native verification on the affected kind, regression checks on previously working kinds, review of before/after evidence, and explicit authorization for changes. Retain last known good configuration. A failed or unverified candidate is not published.

## Model use

A small local model is optional. The deterministic engine must function without it. A model should receive a minimal diagnosis, constrained candidate choices, and no raw private tokens. GPU availability does not imply repair reliability.

## Current code reality

`begin_repair` only changes task state and increments attempts. There is no automatic diagnosis, selector fallback, LLM call, site patching, player test, promotion or rollback yet.
