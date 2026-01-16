def generate_report(bug, success, confidence, test_output):
    lines = []

    lines.append("## 🧠 AI Fix Report\n")
    lines.append(f"**Bug name:** {bug['name']}")
    lines.append(f"**Function:** {bug['function']}")
    lines.append(f"**Signature:** {bug['signature']}\n")

    # Root cause
    lines.append("### Root Cause Analysis")
    lines.append(
        f"The function `{bug['function']}` did not behave according to the test expectations "
        "or violated its logical contract."
    )

    # Patch explanation
    lines.append("\n### Patch Explanation")
    lines.append(
        f"The AI replaced the implementation of `{bug['function']}` with a corrected version "
        "that satisfies the detected test conditions."
    )

    # Test feedback
    lines.append("\n### Test Feedback")
    lines.append("```")
    lines.append(test_output.strip())
    lines.append("```")

    # Confidence
    lines.append("\n### Confidence Assessment")
    lines.append(f"**Score:** {confidence['confidence']}")
    lines.append(f"**Decision:** {confidence['decision']}")
    lines.append(f"**Reason:** {confidence['reason']}")

    # Result
    lines.append("\n### Result")
    lines.append(f"Status: **{'SUCCESS' if success else 'FAILED'}**")

    if success:
        lines.append("The patch was applied and all tests passed.")
    else:
        lines.append("The patch was applied but tests are still failing.")

    return "\n".join(lines)
