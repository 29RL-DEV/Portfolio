import re


def replace_function(source_code: str, func_name: str, new_func_code: str) -> str:
    """
    Replaces a full function definition in source_code with new_func_code.
    Works safely even if file has multiple functions.
    """

    pattern = rf"def {func_name}\s*\(.*?\):\n(?:[ \t]+.*\n)*"
    match = re.search(pattern, source_code)

    if not match:
        raise ValueError(f"Function {func_name} not found")

    start, end = match.span()

    return source_code[:start] + new_func_code.strip() + "\n\n" + source_code[end:]
