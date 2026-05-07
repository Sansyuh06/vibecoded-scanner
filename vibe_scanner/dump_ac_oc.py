
import re

file_path = r"d:\fyeshi\project\PII\vibe_scanner\ref_report.html"
out_path = r"d:\fyeshi\project\PII\vibe_scanner\ac_oc_code.txt"

try:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    patterns = [
        r"function\s+AC\(",
        r"const\s+AC\s*=",
        r"var\s+AC\s*=",
        r"const\s+OC\s*=",
        r"var\s+OC\s*="
    ]

    result = ""
    for p in patterns:
        match = re.search(p, content)
        if match:
            start = match.start()
            end = min(len(content), start + 15000) 
            # Try to be smarter about end? No, just dump chunk.
            result += f"\n--- Match for {p} ---\n"
            result += content[start:end]
            result += "\n"
        else:
            print(f"Pattern {p} not found.")
            
    with open(out_path, "w", encoding="utf-8") as out:
        out.write(result)
    print(f"Dumped to {out_path}")

except Exception as e:
    print(f"Error: {e}")
