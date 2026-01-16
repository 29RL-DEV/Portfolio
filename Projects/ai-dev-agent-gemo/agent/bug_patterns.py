import json
import os

BUG_FILE = "agent/bug_db.json"

if os.path.exists(BUG_FILE):
    with open(BUG_FILE, "r") as f:
        BUG_PATTERNS = json.load(f)
else:
    BUG_PATTERNS = [
        {
            "name": "DivideByZero",
            "signature": "ZeroDivisionError",
            "function": "divide",
            "patch": """def divide(a, b):
    if b == 0:
        return 0
    return a / b
""",
        },
        {
            "name": "WrongAdd",
            "signature": "test_add",
            "function": "add",
            "patch": """def add(a, b):
    return a + b
""",
        },
    ]


def save():
    with open(BUG_FILE, "w") as f:
        json.dump(BUG_PATTERNS, f, indent=2)
