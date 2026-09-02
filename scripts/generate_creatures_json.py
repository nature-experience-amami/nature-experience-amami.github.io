"""
images/creatures/カテゴリ/生き物ID/生き物名_6桁の写真番号_YYYYMMDD_HH.jpg
というファイル構成から、
生き物ごとの「実際に観察できた月」を自動集計して data/creatures.json を作る。

実行方法: python scripts/generate_creatures_json.py
"""
import re
import json
from pathlib import Path

IMAGES_DIR = Path("images/creatures")
OUTPUT = Path("data/creatures.json")
DATE_RE = re.compile(r"^.+_\d{6}_(\d{4})(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])_([01]\d|2[0-3])$")
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}


def scan():
    creatures = []
    for category_dir in sorted(p for p in IMAGES_DIR.iterdir() if p.is_dir()):
        for species_dir in sorted(p for p in category_dir.iterdir() if p.is_dir()):
            months, photos = set(), []
            for photo in sorted(species_dir.iterdir()):
                if photo.suffix.lower() not in IMAGE_EXTS:
                    continue
                m = DATE_RE.match(photo.stem)
                if m:
                    months.add(int(m.group(2)))
                photos.append(str(photo.relative_to(".")).replace("\\", "/"))
            if photos:
                creatures.append({
                    "id": species_dir.name,
                    "category": category_dir.name,
                    "months": sorted(months),
                    "photos": photos,
                })
    return creatures


if __name__ == "__main__":
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    data = scan()
    OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(data)}種のデータを {OUTPUT} に書き出しました")
