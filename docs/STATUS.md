# Current status — 5 November 2026

The owner's corrected goal is implemented as a first local extension path: generic Cortana tools connect to a separate local AI/browser resolver, with reusable recipes and reviewable source patches against the actual owner checkout. The original audit classifier is retained; repeated whole-site audits are not the main workflow.

Implemented: local Ollama JSON decisions, real Chromium DOM/frame/media discovery, optional ephemeral screenshots, bounded actions, recipe replay/fallback, actual-checkout inventory, small source proposals, Python parsing, approved apply/rollback, authenticated local service, async jobs, private restart checkpoints, generated Cortana connection file, and Windows/source launcher.

Verified locally: 24 tests pass, including actual Chromium on controlled search/player fixtures and real cross-repo HTTP transport using a scripted model response. The actual MovieHub checkout inspected was commit `08343545afd7b535f8c9112f818ad60ee4432bd4`; its JSON registry has 68 adapter records and the allowlisted folders contain 82 source files. These are different counts from websites; native Python-defined providers are not imported by executing them. No MovieHub source file was modified during this implementation.

Unverified: actual Qwen 4B/9B navigation/repair quality, owner's GPU/Windows setup, live production provider correctness and actual native MovieHub playback. Not implemented: APK rebuilding/deployment, TV installation, or Android calling this PC service. Source changes must pass MovieHub's normal build/playback workflow before any claim of a provider fix.

See LOCAL_AI_EXTENSION.md for exact setup, capabilities and limits.
