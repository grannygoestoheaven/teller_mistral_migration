import os
import json
from pathlib import Path

def collect_titles(base_dir="src/data/stories"):
    titles = []
    for story_dir in Path(base_dir).iterdir():
        if story_dir.is_dir():
            json_path = story_dir / f"{story_dir.name}.json"
            if json_path.exists():
                with open(json_path, "r") as f:
                    data = json.load(f)
                    titles.append(data.get("story_title", story_dir.name))
    return titles

titles = collect_titles()
print(f"Found {len(titles)} titles. Sample: {titles[:300]}")
