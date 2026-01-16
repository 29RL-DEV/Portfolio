def decide(confidence_result):
    if confidence_result["decision"] == "auto_merge":
        return "apply"
    if confidence_result["confidence"] >= 0.5:
        return "sandbox"
    return "reject"
