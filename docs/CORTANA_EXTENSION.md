# Optional Cortana extension

Implemented package: `extensions/cortana/manifest.json`, configured by `resolver.service` at startup. The generated private connection file can be imported into Cortana's generic extension manager. No MovieHub code or labels are bundled in Cortana core.

Tools: `start` (approved browser resolve/source proposal), `job` (status or actual checkout inventory), `apply` (approved source patch, recipe save or rollback) and `cancel`. Natural language selection uses the local model's normal tool interface. The resolver's own browser decisions use structured local Ollama requests.

See [LOCAL_AI_EXTENSION.md](LOCAL_AI_EXTENSION.md) for installation, exact capabilities and outstanding gaps. The extension host requires the corresponding Cortana source update; existing releases do not gain it automatically.
