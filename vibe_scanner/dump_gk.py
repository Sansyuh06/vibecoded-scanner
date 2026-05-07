
import re

file_path = r"d:\fyeshi\project\PII\vibe_scanner\ref_home.html"
out_path = r"d:\fyeshi\project\PII\vibe_scanner\gk_code.txt"

try:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    patterns = [
        r"function\s+gk\(",
        r"const\s+gk\s*=",
        r"var\s+gk\s*="
    ]

    for p in patterns:
        match = re.search(p, content)
        if match:
            start = match.start()
            end = min(len(content), start + 10000) 
            with open(out_path, "w", encoding="utf-8") as out:
                out.write(content[start:end])
            print(f"Dumped to {out_path}")
            break
    else:
        print("gk definition not found.")

except Exception as e:
    print(f"Error: {e}")
