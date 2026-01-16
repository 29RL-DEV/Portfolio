import os
from datetime import datetime


def save_run(before, after, output, success, diff, report):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder = f"agent_output/run_{ts}"

    os.makedirs(folder, exist_ok=True)

    with open(f"{folder}/before.py", "w", encoding="utf8") as f:
        f.write(before)

    with open(f"{folder}/after.py", "w", encoding="utf8") as f:
        f.write(after)

    with open(f"{folder}/diff.patch", "w", encoding="utf8") as f:
        f.write(diff)

    with open(f"{folder}/ai_report.md", "w", encoding="utf8") as f:
        f.write(report)

    with open(f"{folder}/report.txt", "w", encoding="utf8") as f:
        f.write("SUCCESS\n" if success else "FAIL\n")
        f.write("\n")
        f.write(output)
