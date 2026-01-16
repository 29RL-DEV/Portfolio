import json
from datetime import datetime
from pathlib import Path

BASE = Path("agent_output")
LOGS = BASE / "logs"
PATCHES = BASE / "patches"

LOGS.mkdir(parents=True, exist_ok=True)
PATCHES.mkdir(parents=True, exist_ok=True)


def log_event(event):
    ts = datetime.utcnow().isoformat()
    event["timestamp"] = ts

    log_file = LOGS / f"{ts.replace(':', '_')}.json"
    with open(log_file, "w") as f:
        json.dump(event, f, indent=2)
