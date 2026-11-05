# AI agent operating contract — MovieHub Universal Resolver

**Read this file, README.md, CONTRIBUTING.md and the relevant docs before modifying code.**

## Mission

Build a universal browser resolver driven by local AI, with reusable navigation recipes and a separate optional Cortana extension. Help the owner repair their actual MovieHub sources without repeated whole-site manual audits. Native playback evidence is required for any claim that a provider is fixed.

## Scope discipline

1. Follow the user's explicit task. Do not invent side quests, redesign unrelated UI or audit already-certified routes repeatedly without reason.
2. Start by reading actual repository files and current status. Never claim the 74-provider inventory was imported until verified from MovieHub at a pinned revision.
3. Check each provider **separately** for movie and series, respecting actual supported kinds once inventory is implemented.
4. Skip fully verified working tasks; prioritize failures. Retest working routes only when required for regression coverage.
5. Limit repair attempts (default 2), time and compute. Stop and report unresolved issues instead of looping.
6. Save checkpoint and a concise evidence record after each provider/kind.
7. Never mark a site working based on HTTP 200, extracted URL, search results, screenshots, simulated fixtures or a green build.
8. Certify only after **real MovieHub Android/LibVLC** video identity, duration, decoded frames, smoothness, opening/mid/late audio and seeking are observed.
9. Keep before/after evidence, rejected alternatives, exact failures and a rollback target. Preserve all existing providers, user data and working features.
10. Never bypass DRM, login, paywalls, CAPTCHA, geo restrictions or other access controls.
11. Never execute AI-generated arbitrary code or commands. Validate declarative proposals and require approval for persistent changes.
12. Do not modify Cortana core to mention MovieHub. The integration must be optional, disabled by default and separately installable.
13. Read all files affected before changing them. Keep changes minimal, add tests and run the suite before and after.
14. Commit in small reviewable increments; do not merge/release incomplete or unverified repairs.
15. Report precisely: **changed files, tests actually run, real playback actually verified, outstanding blockers**. Never say 'all good' without evidence.

## Existing commands

```bash
python -m unittest discover -s tests -v
python -m resolver.cli --input examples/sample-results.json --output audit-report.json
```

## Current status

The classifier, checkpoint controller and CLI remain. Local browser/AI navigation, recipe replay, authenticated loopback jobs, actual-checkout source proposals/apply/rollback and a separately installable Cortana extension now exist. See docs/LOCAL_AI_EXTENSION.md for installation and explicit limits. Native Android playback telemetry and automatic APK deployment are not implemented. Do not describe an applied source patch as a verified provider fix.

## Read next

- `docs/LOCAL_AI_EXTENSION.md`
- `docs/ARCHITECTURE.md`
- `docs/EVIDENCE_AND_STATUS.md`
- `docs/REPAIR_ENGINE.md`
- `docs/INVENTORY_AND_ADAPTERS.md`
- `docs/CORTANA_EXTENSION.md`
- `docs/SECURITY.md`
- `docs/TESTING.md`
