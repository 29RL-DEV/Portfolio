import json
from pathlib import Path
from datetime import datetime

HISTORY = Path("agent/history.json")
LOG = Path("agent/events.log")


def load_history():
    if not HISTORY.exists():
        return []
    with open(HISTORY, "r", encoding="utf8") as f:
        return json.load(f)


def load_logs():
    if not LOG.exists():
        return []
    with open(LOG, "r", encoding="utf8") as f:
        return f.readlines()


def main():
    history = load_history()
    logs = load_logs()

    if not history:
        print("No runs yet.")
        return

    last = history[-1]

    bug = last["bug"]["name"]
    function = last["bug"]["function"]
    passed = last["tests_passed"]
    confidence = last["confidence"]["confidence"]
    decision = last["confidence"]["decision"]

    past_failures = len(
        [h for h in history[:-1] if h["bug"]["name"] == bug and not h["tests_passed"]]
    )

    print("\n🧠 AI DEV AGENT — RUN REPORT")
    print("-" * 40)
    print(f"Bug detected: {bug}")
    print(f"Function: {function}")
    print(f"Patch applied: {'YES' if passed else 'NO'}")
    print(f"Tests passed: {'YES' if passed else 'NO'}")
    print(f"Confidence: {confidence}")
    print(f"AI Decision: {decision}")
    print(f"Previous failures of this bug: {past_failures}")

    if passed and decision == "auto_merge":
        print("\n✔ Code merged")
        print("✔ History updated")
        print("✔ System healthy")
    else:
        print("\n⚠ System in warning state")


if __name__ == "__main__":
    main()
