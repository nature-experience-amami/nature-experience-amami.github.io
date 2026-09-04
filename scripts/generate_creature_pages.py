import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT_DIR = ROOT / "content" / "creatures"
IMAGES_DIR = ROOT / "images" / "creatures"
OUTPUT_DIR = ROOT / "generated-creatures"
TEMPLATE = ROOT / "templates" / "creature.html"
TARGETS = [("hebi", "habu"), ("hebi", "akamata"), ("kaeru", "amami-aka-gaeru")]
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}
PHOTO_DIR_ALIASES = {
    ("hebi", "ryukyu-ao-hebi"): "ryuukyuu-aohebi",
}


def escape(value):
    return html.escape(str(value), quote=True)


def parse_markdown(path):
    text = path.read_text(encoding="utf-8")
    frontmatter = {}
    body = text
    if text.startswith("---"):
        _, raw, body = text.split("---", 2)
        for line in raw.strip().splitlines():
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            value = value.strip()
            if value.startswith("[") and value.endswith("]"):
                frontmatter[key.strip()] = [item.strip().strip("\"'") for item in value[1:-1].split(",") if item.strip()]
            else:
                frontmatter[key.strip()] = value
    return frontmatter, body.strip()


def markdown_paragraphs(body):
    paragraphs = re.split(r"\n\s*\n", body)
    return "".join(f"<p>{escape(paragraph.strip())}</p>" for paragraph in paragraphs if paragraph.strip())


def load_categories():
    path = ROOT / "content" / "categories.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def photo_files(category, creature_id):
    directory_name = PHOTO_DIR_ALIASES.get((category, creature_id), creature_id)
    directory = IMAGES_DIR / category / directory_name
    if not directory.is_dir():
        return []
    return sorted(
        str(path.relative_to(ROOT)).replace("\\", "/")
        for path in directory.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_EXTS
    )


def months_from_text(body):
    found = set()
    for match in re.finditer(r"(\d{1,2})月から(\d{1,2})月", body):
        start, end = int(match.group(1)), int(match.group(2))
        if start <= end:
            found.update(range(start, end + 1))
        else:
            found.update(range(start, 13))
            found.update(range(1, end + 1))
    for match in re.finditer(r"(\d{1,2})月(?:頃|が|に|まで)", body):
        found.add(int(match.group(1)))
    return sorted(month for month in found if 1 <= month <= 12)


def months_from_photos(photos):
    months = set()
    for photo in photos:
        match = re.search(r"_(\d{4})(0[1-9]|1[0-2])\d{2}_", Path(photo).stem)
        if match:
            months.add(int(match.group(2)))
    return sorted(months)


def all_creatures(categories):
    result = []
    for category_dir in sorted(path for path in CONTENT_DIR.iterdir() if path.is_dir()):
        for md in sorted(category_dir.glob("*.md")):
            data, body = parse_markdown(md)
            creature_id = data.get("id", md.stem)
            photos = photo_files(category_dir.name, creature_id)
            result.append({
                "id": creature_id,
                "name": data.get("name", creature_id),
                "category": category_dir.name,
                "category_name": categories.get(category_dir.name, category_dir.name),
                "danger": data.get("danger", ""),
                "months": months_from_text(body) or months_from_photos(photos),
                "photos": photos,
                "body": body,
                "related": data.get("related", []) if isinstance(data.get("related", []), list) else [],
            })
    return result


def related_cards(current, creatures):
    by_id = {item["id"]: item for item in creatures}
    selected = []
    for item_id in current["related"]:
        candidate = by_id.get(item_id)
        if candidate and candidate["id"] != current["id"] and candidate not in selected:
            selected.append(candidate)
    same_category = []
    other_categories = []
    for item in creatures:
        if item["id"] != current["id"] and item["category"] == current["category"] and item not in selected:
            same_category.append(item)
        elif item["id"] != current["id"] and item not in selected:
            other_categories.append(item)
    for item in same_category:
        selected.append(item)
    month_matches = []
    for item in other_categories:
        if set(item["months"]) & set(current["months"]):
            month_matches.append(item)
    for item in month_matches[:3]:
        selected.append(item)
    for item in other_categories:
        if item in month_matches[:3]:
            continue
        if len(selected) >= len(same_category) + 3:
            break
        if item not in selected:
            selected.append(item)
    return selected


def render_card(item, current):
    if item["photos"]:
        image = f'<img src="../../{item["photos"][0]}" alt="{escape(item["name"])}">'
    else:
        image = '<div class="placeholder">写真準備中</div>'
    is_generated = (item["category"], item["id"]) in TARGETS
    if is_generated:
        href = (
            f'{item["id"]}.html'
            if item["category"] == current["category"]
            else f'../{item["category"]}/{item["id"]}.html'
        )
        opening = f'<a class="related-card" href="{href}">'
        closing = "</a>"
        link = '<span class="related-link">詳しく見る →</span>'
    else:
        opening = '<div class="related-card related-card-disabled">'
        closing = "</div>"
        link = '<span class="related-link">ページ準備中</span>'
    return (
        f'{opening}{image}<span class="related-category">{escape(item["category_name"])}</span>'
        f'<strong>{escape(item["name"])}</strong>{link}{closing}'
    )


def render(item, creatures):
    active = set(item["months"])
    ticks = "".join(
        f'<span class="season-tick{" active" if month in active else ""}"></span>'
        for month in range(1, 13)
    )
    photos = item["photos"]
    if photos:
        hero = f'<img src="../../{photos[0]}" alt="奄美大島の{escape(item["name"])}">'
        gallery = "".join(
            f'<figure><img src="../../{photo}" alt="{escape(item["name"])}"></figure>'
            for photo in photos[1:4]
        )
    else:
        hero = '<div class="placeholder hero-placeholder">写真準備中</div>'
        gallery = '<div class="gallery-empty">写真は準備中です。生き物の情報はご覧いただけます。</div>'
    photo_script = ""
    if photos:
        photo_urls = json.dumps([f"../../{photo}" for photo in photos], ensure_ascii=False)
        photo_script = f"""
(function () {{
  const photos = {photo_urls};
  const hero = document.getElementById('hero-photo');
  const gallery = document.getElementById('gallery');
  const shuffled = photos.slice().sort(() => Math.random() - 0.5);
  const alt = {json.dumps(item["name"], ensure_ascii=False)};
  if (hero) {{
    hero.innerHTML = '<img src="' + shuffled[0] + '" alt="奄美大島の' + alt + '">';
  }}
  if (gallery) {{
    gallery.innerHTML = shuffled.slice(1, 4).map(function (photo) {{
      return '<figure><img src="' + photo + '" alt="' + alt + '"></figure>';
    }}).join('');
  }}
}})();
""".strip()
    related = related_cards(item, creatures)
    cards = "".join(render_card(candidate, item) for candidate in related)
    related_html = (
        f'<section class="related"><p class="section-label">DISCOVER MORE</p>'
        f'<h2>この生き物に興味がある方へ</h2><div class="related-grid">{cards}</div></section>'
        if cards else ""
    )
    return TEMPLATE.read_text(encoding="utf-8").format(
        title=escape(item["name"]),
        category=escape(item["category_name"]),
        danger=escape(item["danger"] or "情報準備中"),
        months="・".join(f"{month}月" for month in item["months"]) if item["months"] else "観察時期情報を準備中",
        ticks=ticks,
        hero=hero,
        gallery=gallery,
        photo_count=len(photos),
        body=markdown_paragraphs(item["body"]),
        related=related_html,
        category_link=f"../../{item['category']}.html",
        photo_script=photo_script,
    )


def main():
    categories = load_categories()
    creatures = all_creatures(categories)
    by_key = {(item["category"], item["id"]): item for item in creatures}
    for category, creature_id in TARGETS:
        item = by_key[(category, creature_id)]
        output = OUTPUT_DIR / category / f"{creature_id}.html"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(render(item, creatures), encoding="utf-8")
        print(output.relative_to(ROOT))


if __name__ == "__main__":
    main()