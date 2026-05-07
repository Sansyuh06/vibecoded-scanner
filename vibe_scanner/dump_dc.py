
import re

file_path = r"d:\fyeshi\project\PII\vibe_scanner\ref_report.html"
out_path = r"d:\fyeshi\project\PII\vibe_scanner\dc_code.txt"

try:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    patterns = [
        r"function\s+DC\(",
        r"const\s+DC\s*=",
        r"var\s+DC\s*="
    ]

    for p in patterns:
        match = re.search(p, content)
        if match:
            start = match.start()
            end = min(len(content), start + 15000) 
            with open(out_path, "w", encoding="utf-8") as out:
                out.write(content[start:end])
            print(f"Dumped to {out_path}")
            break
    else:
        print("DC definition not found.")

except Exception as e:
    print(f"Error: {e}")
