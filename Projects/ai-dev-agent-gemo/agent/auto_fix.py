import subprocess
import sys
import json
from pathlib import Path
from logger import log_event
from reporting import save_run
from diff_tools import generate_diff
from ai_reasoner import generate_report
from confidence import compute_confidence
from ai_memory import record_run, Memory
from decision_engine import DecisionEngine
from github_bot import open_pull_request


BUG_DB = Path("agent/bug_db.json")


# -------------------------
# Bug database
# -------------------------


def load_bugs():
    if not BUG_DB.exists():
        return []
    try:
        with open(BUG_DB, "r", encoding="utf8") as f:
            return json.load(f)
    except:
        return []


def save_bugs(bugs):
    BUG_DB.parent.mkdir(parents=True, exist_ok=True)
    with open(BUG_DB, "w", encoding="utf8") as f:
        json.dump(bugs, f, indent=2)


# -------------------------
# Test runner
# -------------------------


def run_tests():
    result = subprocess.run(["pytest", "-q"], capture_output=True, text=True)
    return result.returncode, result.stdout + result.stderr


# -------------------------
# Bug detection
# -------------------------


def detect_bug(output, bugs):
    for bug in bugs:
        if bug["signature"] in output:
            return bug
    return None


# -------------------------
# Safe function replace
# -------------------------


def replace_function(code, func_name, new_func_code):
    start = code.find(f"def {func_name}")
    if start == -1:
        return code

    end = code.find("\n\n", start)
    if end == -1:
        end = len(code)

    return code[:start] + new_func_code + "\n\n" + code[end:]


# -------------------------
# MAIN
# -------------------------

if __name__ == "__main__":

    memory = Memory()
    decision_engine = DecisionEngine(memory)

    bugs = load_bugs()

    with open("app/calculator.py", "r", encoding="utf8") as f:
        before_code = f.read()

    code, output = run_tests()

    if code == 0:
        print("✅ All tests passed.")
        sys.exit(0)

    # -------------------------
    # Known bug
    # -------------------------

    bug = detect_bug(output, bugs)

    if bug:
        print(f"🧠 Known bug detected: {bug['name']}")

        log_event(
            {
                "type": "bug_detected",
                "name": bug["name"],
                "function": bug["function"],
                "signature": bug["signature"],
            }
        )

        print("🔧 Applying fix...")

        new_code = replace_function(before_code, bug["function"], bug["patch"])

        with open("app/calculator.py", "w", encoding="utf8") as f:
            f.write(new_code)

        code2, output2 = run_tests()

        diff = generate_diff(before_code, new_code)
        confidence = compute_confidence(bug, diff, code2 == 0)
        report = generate_report(bug, code2 == 0, confidence, output2)

        save_run(before_code, new_code, output2, code2 == 0, diff, report)
        record_run(bug, diff, confidence, code2 == 0)

        # -------------------------
        # 🧠 AI DECISION GATE
        # -------------------------

        action, reason = decision_engine.decide(bug, code2 == 0, confidence, diff)

        log_event(
            {
                "type": "ai_decision",
                "action": action,
                "reason": reason,
                "bug": bug["name"],
            }
        )

        # -------------------------
        # ACTION EXECUTION
        # -------------------------

        if action == "auto_merge":
            open_pull_request(bug, before_code, new_code, diff, report)
            log_event(
                {
                    "type": "fix_applied",
                    "function": bug["function"],
                    "status": "success",
                    "confidence": confidence["confidence"],
                }
            )
            print("✅ Bug fixed and AI approved merge.")

        elif action == "rollback":
            with open("app/calculator.py", "w", encoding="utf8") as f:
                f.write(before_code)

            log_event(
                {
                    "type": "ai_rollback",
                    "function": bug["function"],
                    "reason": reason,
                }
            )

            print("🛑 AI rolled back the patch:", reason)

        elif action == "escalate":
            log_event(
                {
                    "type": "ai_escalation",
                    "function": bug["function"],
                    "reason": reason,
                }
            )

            print("🚨 AI escalated bug:", reason)

        # 🔥 FINAL STEP — always generate CI report
        subprocess.run(["python", "agent/run_report.py"])

    # -------------------------
    # Unknown bug → Learn
    # -------------------------

    else:
        print("🧠 Unknown bug — learning...")

        if "test_add" in output or "AssertionError" in output:
            patch = "def add(a, b):\n    return a + b\n"
            func = "add"
            signature = "AssertionError"
        elif "ZeroDivisionError" in output:
            patch = "def divide(a, b):\n    if b == 0:\n        return 0\n    return a / b\n"
            func = "divide"
            signature = "ZeroDivisionError"
        else:
            print("❌ No auto-fix available.")
            sys.exit(1)

        new_bug = {
            "name": f"Learned_{func}",
            "signature": signature,
            "function": func,
            "patch": patch,
        }

        bugs.append(new_bug)
        save_bugs(bugs)

        log_event({"type": "bug_learned", "function": func, "signature": signature})

        print("📚 Bug learned. Re-running agent...\n")
        subprocess.run(["python", "agent/auto_fix.py"])
        subprocess.run(["python", "agent/run_report.py"])
