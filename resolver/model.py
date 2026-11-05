"""Strict classification of externally collected playback evidence."""
from collections import defaultdict

VALID_KINDS = {"movie", "series"}
VALID_STATUSES = {"working", "partial", "broken", "blocked", "unverified"}

def route_passes(item):
    """A pass requires real player observations, never merely a resolved URL."""
    required = ("identity_match", "runtime_plausible", "decoded_frames",
                "smooth_progress", "opening_audio", "midpoint_audio",
                "late_audio", "midpoint_seek", "late_seek")
    return all(item.get(key) is True for key in required)

def classify(records):
    grouped = defaultdict(list)
    for record in records:
        provider = record.get("provider")
        kind = record.get("kind")
        if not isinstance(provider, str) or not provider.strip():
            raise ValueError("Every record needs a nonempty provider")
        if kind not in VALID_KINDS:
            raise ValueError("kind must be movie or series")
        grouped[(provider, kind)].append(record)
    output = []
    for (provider, kind), attempts in sorted(grouped.items()):
        passes = sum(route_passes(a) for a in attempts)
        blocked = all(a.get("error") in {"http_403", "access_challenge", "geo_blocked"} for a in attempts)
        if passes:
            status = "working" if passes == len(attempts) else "partial"
        elif blocked:
            status = "blocked"
        elif any(a.get("error") or a.get("playback_attempted") for a in attempts):
            status = "broken"
        else:
            status = "unverified"
        output.append({"provider": provider, "kind": kind, "status": status,
                       "passing_routes": passes, "attempted_routes": len(attempts),
                       "attempts": attempts})
    return output
