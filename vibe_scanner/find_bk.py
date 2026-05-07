
import re

file_path = r"d:\fyeshi\project\PII\vibe_scanner\ref_home.html"

try:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    patterns = [
        r"function\s+bk\(",
        r"const\s+bk\s*="
    ]

    for p in patterns:
        match = re.search(p, content)
        if match:
            print(f"Found match for '{p}' at {match.start()}")
            # Print from match start forwards
            start = match.start()
            end = min(len(content), start + 4000) 
            print(f"Code:\n{content[start:end]}")
            break
    else:
        print("bk definition not found.")

except Exception as e:
    print(f"Error: {e}")
