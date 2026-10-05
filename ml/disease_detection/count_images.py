from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parent / "dataset"
exts = {".jpg", ".jpeg", ".png"}

counts = Counter()
other = Counter()

for p in ROOT.rglob("*"):
    if not p.is_file() or p.name == ".gitkeep":
        continue
    folder = "/".join(p.relative_to(ROOT).parts[:-1])
    if p.suffix.lower() in exts:
        counts[folder] += 1
    else:
        other[p.suffix.lower()] += 1

print("Images per folder:")
for k, v in sorted(counts.items()):
    print(f"{v:5d}  {k}")
print("Total images:", sum(counts.values()))

if other:
    print("\nBija file types (images nathi):", dict(other))