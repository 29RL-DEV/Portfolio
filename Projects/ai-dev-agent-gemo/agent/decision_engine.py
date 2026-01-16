from datetime import datetime


class DecisionEngine:
    """
    Central AI brain that decides what to do with a proposed fix.
    """

    def __init__(self, memory=None):
        self.memory = memory

    def decide(self, bug, test_passed, confidence, diff):
        """
        Returns:
            action: "auto_merge" | "rollback" | "learn" | "escalate"
            reason: human readable reason
        """

        # If tests failed → never merge
        if not test_passed:
            return "rollback", "Tests failed after patch"

        # If confidence system rejected it
        if confidence["decision"] != "auto_merge":
            return (
                "rollback",
                f"Confidence system rejected patch: {confidence['reason']}",
            )

        # Patch too big → risky
        if self._diff_too_large(diff):
            return "rollback", "Patch too large, risky change"

        # If bug keeps reappearing → escalate
        if self.memory and self._bug_is_flapping(bug["name"]):
            return "escalate", "Bug keeps reappearing across runs"

        return "auto_merge", "All safety gates passed"

    # -------------------------
    # Safety heuristics
    # -------------------------

    def _diff_too_large(self, diff):
        lines = diff.count("\n")
        return lines > 50  # simple but effective for demo

    def _bug_is_flapping(self, bug_name):
        history = self.memory.get_history()
        recent = [h for h in history[-5:] if h.get("bug") == bug_name]
        return len(recent) >= 3
