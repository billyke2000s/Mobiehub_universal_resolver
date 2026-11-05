# Local extension protocol

`python -m resolver.service` binds only `127.0.0.1` (default port 47831). Requests require the exact Host and bearer token and reject browser Origin headers. JSON body limit: 16 KB. No CORS. Generated connection files and tokens are private, excluded from Git.

All four endpoints use POST with `{"arguments":{...},"approved":false}`:

| Endpoint | Arguments | Behaviour |
|---|---|---|
| `/v1/start` | operation resolve/repair, kind movie/series, optional url/title/year/source_file/diagnosis | Requires approval. Returns job_id immediately. One worker. |
| `/v1/job` | optional job_id; action status/inventory | Returns job/proposal or the actual configured checkout inventory. |
| `/v1/apply` | job_id, action source/recipe/rollback, proposal_digest | Requires approval and the exact reviewed proposal hash. |
| `/v1/cancel` | job_id | Sets cancellation; next action/model boundary stops. |

Internal source backup fields never leave job responses. Media session URLs stay in memory and are not checkpointed. Native playback is never certified by these endpoints. Full installation and limitations: [LOCAL_AI_EXTENSION.md](LOCAL_AI_EXTENSION.md).
