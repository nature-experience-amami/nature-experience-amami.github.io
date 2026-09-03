"""
images/creatures/カテゴリ/生き物ID/生き物ID_連番6桁_YYYYMMDD_HH.jpg
というファイル構成から、生き物ごとの「実際に観察できた月」を自動集計して
data/creatures.json を作る。

表示名(name)は content/creatures/カテゴリ/生き物ID.md のfrontmatterから読む。
(スクリプトに名前を直書きしない → 生き物が増えてもこのファイルは触らなくてよい)

実行方法: python scripts/generate_creatures_json.py
"""
import re
import json
from pathlib import Path

IMAGES_DIR = Path("images/creatures")
CONTENT_DIR = Path("content/creatures")
CATEGORY_NAMES_FILE = Path("content/categories.json")
OUTPUT = Path("data/creatures.json")
DATE_RE = re.compile(r"^.+_\d{6}_(\d{4})(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])_([01]\d|2[0-3])$")
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}
IGNORED_DIR_NAMES = {"failed"}
MARKDOWN_ID_ALIASES = {
    ("hebi", "ryuukyuu-aohebi"): "ryukyu-ao-hebi",
}


def read_creature_content(md_path: Path):
    if not md_path.exists():
        return {}, ""
    text = md_path.read_text(encoding="utf-8")
    body = text
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) == 3:
            body = parts[2]
    values = {}
    for key in ("name", "months"):
        m = re.search(rf"^{key}:\s*(.+)$", text, re.MULTILINE)
        if not m:
            continue
        value = m.group(1).strip()
        if key == "months" and value.startswith("[") and value.endswith("]"):
            try:
                values[key] = [int(item.strip()) for item in value[1:-1].split(",") if item.strip()]
            except ValueError:
                continue
        else:
            values[key] = value
    return values, body.strip()


def load_category_names():
    if CATEGORY_NAMES_FILE.exists():
        return json.loads(CATEGORY_NAMES_FILE.read_text(encoding="utf-8"))
    return {}


def scan():
    category_names = load_category_names()
    creatures = []
    for category_dir in sorted(p for p in IMAGES_DIR.iterdir() if p.is_dir()):
        for species_dir in sorted(
            p for p in category_dir.iterdir() if p.is_dir() and p.name not in IGNORED_DIR_NAMES
        ):
            months, photos = set(), []
            for photo in sorted(species_dir.iterdir()):
                if photo.suffix.lower() not in IMAGE_EXTS:
                    continue
                m = DATE_RE.match(photo.stem)
                if m:
                    months.add(int(m.group(2)))
                photos.append(str(photo.relative_to(".")).replace("\\", "/"))
            if photos:
                markdown_id = MARKDOWN_ID_ALIASES.get(
                    (category_dir.name, species_dir.name), species_dir.name
                )
                md_path = CONTENT_DIR / category_dir.name / f"{markdown_id}.md"
                # 説明文(.md)がまだ無くてもビルドは止めない。名前が無ければIDをそのまま表示名にする。
                frontmatter, description = read_creature_content(md_path)
                name = frontmatter.get("name") or species_dir.name
                category_name = category_names.get(category_dir.name, category_dir.name)
                creatures.append({
                    "id": species_dir.name,
                    "name": name,
                    "category": category_dir.name,
                    "category_name": category_name,
                    "months": frontmatter.get("months", sorted(months)),
                    "description": description,
                    "photos": photos,
                })
    return creatures


if __name__ == "__main__":
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    data = scan()
    OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(data)}種のデータを {OUTPUT} に書き出しました")
