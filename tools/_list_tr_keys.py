import re
from pathlib import Path

pattern = re.compile(r"tr\(\s*\"([^\"]+)\"")
keys = set()
base = Path("gui")
for path in base.glob("**/*.py"):
    text = path.read_text(encoding="utf-8", errors="ignore")
    keys.update(pattern.findall(text))
for key in sorted(keys):
    print(key)
print(f"Total keys: {len(keys)}")
