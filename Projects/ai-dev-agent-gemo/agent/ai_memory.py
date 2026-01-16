import json
from pathlib import Path
from datetime import datetime

HISTORY_FILE = Path("agent/history.json")


def load_history():
    if not HISTORY_FILE.exists():
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf8") as f:
            return json.load(f)
    except:
        return []


def save_history(history):
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_FILE, "w", encoding="utf8") as f:
        json.dump(history, f, indent=2)


def record_run(bug, diff, confidence, success):
    history = load_history()

    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "bug_name": bug["name"],
        "function": bug["function"],
        "signature": bug["signature"],
        "confidence": confidence["confidence"],
        "decision": confidence["decision"],
        "success": success,
        "reason": confidence["reason"],
        "lines_changed": len(diff.splitlines()),
    }

    history.append(entry)
    save_history(history)
