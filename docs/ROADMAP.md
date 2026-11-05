# Roadmap and definition of done

| Stage | Deliverable | Status | Acceptance gate |
|---|---|---|---|
| 0 | Evidence classifier, JSON CLI, bounded checkpoint controller | Partial | Unit tests executed and reviewed |
| 1 | Import exact current MovieHub provider inventory | Planned | All IDs accounted for at pinned revision; capabilities explicit |
| 2 | Trusted native Android LibVLC evidence producer | Planned | One movie and one episode tested with all required signals |
| 3 | Automated task runner and health report | Planned | Skip passing routes; checkpoint every provider/kind; bounded retries |
| 4 | Deterministic repair proposals | Planned | One real failure repaired and retested without unrelated changes |
| 5 | Optional local model suggestions | Planned | Proposals constrained, sanitized, tested and never directly executed |
| 6 | Safe promotion, regression gates, rollback | Planned | Failed proposals cannot replace known-good config |
| 7 | Local API, scheduling and dashboard | Planned | Pause/resume, auth, status, durable history and resource limits |
| 8 | Generic Cortana plugin support + optional resolver extension | Planned | Cortana without plugin has no MovieHub mentions/tools; enable/disable tested |
| 9 | MovieHub consumption of validated config | Planned | No loss of features or data; signed/versioned config and rollback |

## Immediate next milestone

Read the actual MovieHub repository and import its provider inventory without deleting or renaming providers. Then implement a **trusted native evidence producer** for a small, explicitly authorized test set. Do not claim a self-healing system exists until at least one real repair passes native retesting.

## Delivery checklist

- Reproducible tests executed
- Exact files and commits documented
- Supported kinds and known failures listed
- No silent feature deletion
- Security and permission review
- Before/after playback evidence
- Rollback tested
- Honest limitations and blockers
