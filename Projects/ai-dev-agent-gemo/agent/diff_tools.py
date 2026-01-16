import difflib


def generate_diff(old_code, new_code, filename="calculator.py"):
    old = old_code.splitlines(keepends=True)
    new = new_code.splitlines(keepends=True)

    diff = difflib.unified_diff(
        old, new, fromfile=f"a/{filename}", tofile=f"b/{filename}", lineterm=""
    )

    return "".join(diff)
