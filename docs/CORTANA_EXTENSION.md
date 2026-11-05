# Optional Cortana AI extension

> Design only. No extension installer, manifest loader, Cortana integration, or local API is implemented.

## User experience

Normal Cortana installations have **zero MovieHub references**. A user explicitly installs and enables the separately distributed MovieHub Resolver extension. Only then may Cortana discover its tools, show its settings or act on resolver requests. Disabling/uninstalling must unregister tools and menus without altering unrelated Cortana data.

## Separation

- Cortana core owns generic extension discovery, permissions, approval, status, UI slots and tool dispatch.
- Resolver owns provider inventory, audits, repair proposals, playback evidence and checkpoint state.
- The optional extension owns MovieHub-specific names, tool descriptions, icons and API client.
- The local service should bind to loopback and require authenticated requests. Never assume localhost alone is a security boundary.

## Proposed extension manifest (not a current supported format)

```json
{
  "manifest_version": 1,
  "id": "moviehub.universal-resolver",
  "name": "MovieHub Universal Resolver",
  "version": "0.1.0",
  "permissions": ["audit.read", "audit.start", "repair.propose"],
  "service": {"transport": "loopback-http", "url": "http://127.0.0.1:PORT"}
}
```

`PORT` is a placeholder, not a valid endpoint. An actual installer must validate origin, manifest signature/trust, port, executable path and permissions. No arbitrary extension code should run with full Cortana privileges by default.

## Intended tools

- `resolver_status`: read-only counts and per-kind results.
- `resolver_start_audit`: start an approved bounded audit.
- `resolver_pause_audit` / `resolver_resume_audit`: control current run.
- `resolver_propose_repair`: produce a non-executable candidate and evidence.
- `resolver_approve_repair`: explicit user approval after validation; never automatic.

Use natural language tool selection rather than hardcoded phrases. Tool availability must reflect installed/enabled permissions.

## Integration checklist

1. Read Cortana's full `AGENTS.md`, `app/tools.py`, `app/runtime.py`, `app/server.py`, `app/pages.js`, build manifest and tests before editing.
2. Add generic extension manager and deny-by-default permission model.
3. Confirm no MovieHub text appears when extension absent.
4. Test Windows EXE packaging and normal Cortana offline tests.
5. Test enable, disable, uninstall, service unavailable, API failure, approval denial and mobile paired-client access restrictions.
6. Keep MovieHub extension in its own repository/package.

See `docs/INTEGRATION.md` for the proposed local API.
