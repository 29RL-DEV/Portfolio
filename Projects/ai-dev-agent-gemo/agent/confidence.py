def compute_confidence(bug, diff, tests_passed):
    """
    Returns:
    {
        "confidence": float (0.0 - 1.0),
        "decision": "auto_merge" | "needs_review",
        "reason": str
    }
    """

    score = 1.0

    # 1️⃣ Test result (most important)
    if not tests_passed:
        score -= 0.6

    # 2️⃣ Diff size penalty
    lines_changed = len(diff.splitlines())
    if lines_changed > 30:
        score -= 0.3
    elif lines_changed > 10:
        score -= 0.15

    # 3️⃣ Learned bug penalty
    if bug["name"].startswith("Learned"):
        score -= 0.2

    # 4️⃣ Dangerous function penalty
    if bug["function"] in ["auth", "payment", "security"]:
        score -= 0.3

    # Clamp score
    score = max(0.0, min(1.0, score))

    decision = "auto_merge" if score >= 0.75 else "needs_review"

    reason = build_reason(bug, lines_changed, tests_passed)

    return {
        "confidence": round(score, 2),
        "decision": decision,
        "reason": reason,
    }


def build_reason(bug, lines_changed, tests_passed):
    reasons = []

    if tests_passed:
        reasons.append("all tests passed")
    else:
        reasons.append("tests failed")

    if bug["name"].startswith("Learned"):
        reasons.append("bug was learned dynamically")
    else:
        reasons.append("bug was known")

    if lines_changed <= 10:
        reasons.append("small patch")
    else:
        reasons.append("large patch")

    return ", ".join(reasons)
