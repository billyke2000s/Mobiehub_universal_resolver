# Engineering and audit rules

- Never mark a route working based only on a URL, HTTP 200, link count, screenshot, or green CI build.
- Keep the 74-site MovieHub inventory intact; do not silently remove providers, features, settings, accounts, or user data.
- Record **before** and **after** evidence for each repair; separate movie and series outcomes.
- Record exact title/ID, season/episode, source route, native decoder observations, seek outcomes, audio samples, failure reason, and evidence revision.
- Use the real Android/LibVLC playback path for certification; simulated fixtures are tests of the audit software only.
- Preserve all failures and unverified cases. Never inflate a 416x240 stream into a 720p claim.
- Save changes per provider with small reviewable commits and tests; do not merge/release unfinished audits.
- Never bypass DRM, authentication, access challenges, or other access controls.
