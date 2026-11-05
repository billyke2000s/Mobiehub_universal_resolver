# Optional Cortana integration design

**Status:** Architecture only; no Cortana files have been changed or installed.

The resolver runs as a separate local process. Cortana should gain a **generic** extension loader rather than MovieHub-specific tools. Extensions are disabled unless installed and explicitly enabled.

Manifest fields: id, name, version, capabilities, localhost endpoint. Capabilities: audit.read, audit.start, repair.propose, repair.approve. Reject untrusted manifests and deny arbitrary shell execution. Require user approval for mutations and keep the current Cortana pairing/origin protections.

Proposed resolver API (not implemented yet):
- GET /v1/status: counts by status and kind
- POST /v1/audits: start bounded run, returns run ID
- GET /v1/audits/{id}: progress and per-site evidence
- POST /v1/audits/{id}/pause and /resume
- POST /v1/repairs/{id}/approve: explicit local approval after validation

Cortana should not mention MovieHub, load the resolver, or expose its tools when the extension is absent. Keep the integration in a separately installable package. Do not change Cortana's app/server.py, app/tools.py, app/runtime.py or UI until their contracts and full AGENTS.md have been reviewed and offline tests run.

The controller in resolver/controller.py is deterministic, checkpointable, and does not claim real browser/player integration. Next work: import inventory and native evidence producer; then a local service and optional Cortana extension.
