import json
from pathlib import Path
from metrics import compute_store

DATA_DIR = Path(__file__).parent / "Data"
results = {}
for store in sorted(DATA_DIR.glob("STORE*")):
    results[store.name] = compute_store(store)

with open("results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(list(results))
