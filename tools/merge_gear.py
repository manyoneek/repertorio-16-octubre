#!/usr/bin/env python3
"""Junta los data/_gear_g*.json parciales en data/gear.json, en el orden de songs.json."""
import glob, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

entries = {}
for path in sorted(glob.glob(os.path.join(DATA, "_gear_g*.json"))):
    with open(path, encoding="utf-8") as f:
        chunk = json.load(f)
    for e in (chunk if isinstance(chunk, list) else chunk.values()):
        entries[e["title"]] = e

with open(os.path.join(DATA, "songs.json"), encoding="utf-8") as f:
    songs = json.load(f)

merged = [entries[s["title"]] for s in songs if s["title"] in entries]
with open(os.path.join(DATA, "gear.json"), "w", encoding="utf-8") as f:
    json.dump(merged, f, ensure_ascii=False, indent=1)

missing = [s["title"] for s in songs if s["title"] not in entries]
print(f"gear.json: {len(merged)}/{len(songs)} temas")
if missing:
    print("faltan:", ", ".join(missing))
