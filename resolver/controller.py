"""Bounded, resumable audit controller. No simulated playback or unapproved code execution."""
import json
from pathlib import Path
from .model import classify

STATES = {"pending", "checking", "working", "needs_repair", "repairing", "blocked", "unverified", "failed"}
def initialise(providers):
    if not isinstance(providers, list) or not all(isinstance(p, str) and p.strip() for p in providers):
        raise ValueError("providers must be a list of nonempty IDs")
    if len(set(providers)) != len(providers):
        raise ValueError("duplicate provider IDs")
    return {"version": 1, "tasks": [{"provider": p, "kind": kind, "state": "pending", "attempts": 0,
                                     "history": []} for p in providers for kind in ("movie", "series")]}

def record_check(state, provider, kind, observations):
    task = next((t for t in state["tasks"] if t["provider"] == provider and t["kind"] == kind), None)
    if task is None:
        raise ValueError("unknown provider/kind")
    if not observations or any(o.get("provider") != provider or o.get("kind") != kind for o in observations):
        raise ValueError("observations must match task and be nonempty")
    result = classify(observations)[0]
    status = result["status"]
    task["history"].append({"event": "check", "status": status, "observations": observations})
    task["state"] = {"working": "working", "partial": "needs_repair",
                     "broken": "needs_repair", "blocked": "blocked",
                     "unverified": "unverified"}[status]
    return task

def next_task(state):
    return next((t for t in state["tasks"] if t["state"] == "pending"), None)

def begin_repair(state, provider, kind, max_attempts=2):
    task = next((t for t in state["tasks"] if t["provider"] == provider and t["kind"] == kind), None)
    if task is None or task["state"] != "needs_repair":
        raise ValueError("repair requires a failed or partial check")
    if not 1 <= max_attempts <= 10:
        raise ValueError("max_attempts must be between 1 and 10")
    if task["attempts"] >= max_attempts:
        task["state"] = "failed"
        return False
    task["attempts"] += 1
    task["state"] = "repairing"
    task["history"].append({"event": "repair_started", "attempt": task["attempts"]})
    return True

def save(state, path):
    """Atomic checkpoint; state is data only and never executable instructions."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temp = target.with_name(target.name + ".tmp")
    temp.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    temp.replace(target)

def load(path):
    state = json.loads(Path(path).read_text(encoding="utf-8"))
    if state.get("version") != 1 or not isinstance(state.get("tasks"), list):
        raise ValueError("unsupported checkpoint")
    for task in state["tasks"]:
        if task.get("state") not in STATES:
            raise ValueError("invalid task state")
    return state
