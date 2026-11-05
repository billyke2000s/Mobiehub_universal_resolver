# Local AI resolver extension

The owner's corrected goal is a reusable browser resolver driven by local AI, with a separately installable Cortana extension. The existing audit classifier is retained for evidence handling; running another whole-provider audit is not the main workflow.

## Start on your PC

Use the Cortana source branch containing its generic extension host. The existing v1.7.1 executable does not include that host. Windows build validation is provided by the extension-check workflow; do not assume an old downloaded EXE has this feature.

1. Have Python 3.11+, Ollama and your chosen local model installed. Default: `qwen3.5:9b`; choose another with `--model`.
2. Clone this repo and your actual `billyke2000s/moviehub` repo beside it. Double-click `Start Resolver.cmd`, or run `python launch.py --moviehub "D:\Projects\moviehub"`. The launcher creates a private venv, installs the pinned browser dependency and Chromium, then starts the service. Setup needs internet; model inference stays on the PC.
3. The service prints the path to `moviehub-extension.json` under `%LOCALAPPDATA%\MovieHubResolver` (or your home folder on Linux). Keep this private: it contains the service connection token.
4. In Cortana: Systems → Extensions → Import extension. Select that generated file, review the four tools, install and enable. Keep the resolver console open. The template manifest in this repo is not a configured connection file.

Advanced: `python -m resolver.service --moviehub PATH --model MODEL --headless --vision`. `--vision` sends ephemeral browser screenshots only to local Ollama; default is DOM observations without screenshots. `--browser` selects an installed Chromium executable. Ollama must use a literal loopback address; no cloud model fallback exists.

## Use naturally

Ask Cortana to find a specific title on a specific site, or to prepare a repair for a failing MovieHub source. The AI chooses the extension tools without fixed voice commands. For series, include the exact season and episode in the title/request. Examples:

- “Use the resolver to find Example Film, 2020, on this website: https://…”.
- “Show the actual MovieHub provider inventory, then prepare a repair for this source file. Its search selector no longer finds the results.”
- “Check that resolver job.”
- “Show the proposed diff, then apply it.”
- “Roll back that applied source patch.”

`start` returns a job ID immediately. Ask for its result/progress using `job`; no browser work blocks Cortana's HTTP request. `cancel` stops at the next action boundary. `apply` requires approval and the exact proposal digest. A long local model inference may take up to 60 seconds to return before cancellation is observed.

## What actually executes

- **Browser resolution:** fresh Chromium context, public-site navigation, cross-frame DOM observations, optional screenshots, current element IDs, local structured decisions and real media response capture. Allowed actions are observed-element click, search-title fill, Enter, wait, select captured media or stop. Popups are closed; downloads, WebSockets and service workers are blocked. No model-written JavaScript is evaluated. Login/challenge pages stop the job.
- **Reusable recipes:** successful navigation steps become a proposed recipe. Approval saves it by website/kind. Future browser runs try it first; mismatches fall back to fresh model decisions. Steps never contain the title itself. The previous recipe file is preserved.
- **Actual source edits:** reads the configured checkout's real provider source and optional browser observations; local AI proposes up to three exact replacements. Original text must match once; Python output must parse. The result is a unified diff with before/after hashes. After approval, applies only if the original file hash still matches. A private checkpoint keeps the original text; rollback refuses to overwrite newer edits. Generated code is never imported or executed by this service.
- **Actual inventory:** reads `moviehub_providers.json` as JSON and lists allowed source files without importing provider code. This reports registry records rather than claiming a particular number of independent websites. The checked revision is returned. Native providers defined separately in Python are not inferred by executing that file.

## Limits that matter

This implementation resolves in its PC browser and edits a local source checkout. It does **not** automatically rebuild, publish or install a MovieHub APK, and the Android app does not call this PC service. Saved recipes are used by the resolver service, not injected into Android. A source patch needs the normal MovieHub build/tests and installation before affecting the TV app.

`resolved_unverified`, `patch_proposed` and `patch_applied_unverified` are deliberately distinct from “site fixed”. Python syntax checking is not a functional repair test. Captured media can still be incorrect, expire, require cookies or fail in LibVLC. All native playback signals remain unverified. No production provider is certified by the fixture tests.

One job at a time; at most 18 browser decisions and a three-minute navigation budget (plus the current bounded browser/model operation), two source-proposal attempts, at most three replacements and a 32 KB source file. The resolver's Ollama helper uses a 12,288-token window; if Cortana uses another window for the same model Ollama may reallocate its cache between the two clients. Browser/site/model quality on the owner's GPU remains to be measured.

Public-address checks apply to each intercepted request and redirects, but browser DNS resolution is separate from the precheck; this is not hardened isolation against an actively malicious DNS-rebinding site. Use only sites you trust/are authorized to access. The local service token is not a sandbox for other local processes.

Patch previews are capped at 7,000 diff characters (9,000 after JSON escaping) so the complete proposed change fits Cortana’s deterministic result card before approval.
