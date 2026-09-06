import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT_DIR = ROOT / "content" / "creatures"
IMAGES_DIR = ROOT / "images" / "creatures"
OUTPUT_DIR = ROOT / "generated-creatures"
TEMPLATE = ROOT / "templates" / "creature.html"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}

# 写真フォルダ名がMarkdownのidと違う生き物の対応表（(カテゴリ, Markdownのid): 実際の写真フォルダ名）
PHOTO_DIR_ALIASES = {
    ("hebi", "ryukyu-ao-hebi"): "ryuukyuu-aohebi",
    ("hebi", "takachiho-hebi"): "amami-takachiho-hebi",
    ("kaeru", "hanasaki-gaeru"): "amami-hanasaki-gaeru",
    ("kaeru", "ishikawa-gaeru"): "amami-ishikawa-gaeru",
    ("kuwagata", "marubane-kuwagata"): "amami-marubane-kuwagata",
    ("kuwagata", "nebuto-kuwagata"): "amami-nebuto-kuwagata",
    ("kuwagata", "nokogiri-kuwagata"): "amami-nokogiri-kuwagata",
    ("kuwagata", "shika-kuwagata"): "amami-shika-kuwagata",
    ("kuwagata", "miyama-kuwagata"): "amami-miyama-kuwagata",
    ("kuwagata", "ko-kuwagata"): "amami-ko-kuwagata",
}

# 生成対象。カテゴリ全種類を作りたい場合は all_creatures() の結果をそのまま使う。
TARGETS = None  # None = 見つかった生き物すべて

COMMON_SAFETY_MESSAGE = (
    "奄美の生き物は、写真におさめて楽しみましょう。生き物によっては、法律や条例で捕獲・採集・"
    "持ち出しが禁止されています。国立公園内の特別保護区では、採集そのものが禁止されているエリア"
    "もあります。それぞれの生き物のページで注意事項を確認し、訪れる場所のルールも事前に確認して"
    "から観察してください。"
)


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
                frontmatter[key.strip()] = [
                    item.strip().strip("\"'") for item in value[1:-1].split(",") if item.strip()
                ]
            else:
                frontmatter[key.strip()] = value
    return frontmatter, body.strip()


def split_paragraphs(body):
    return [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]


def render_latin_inline(paragraph):
    # "*学名*" のイタリック表記だけ<em>に変換し、それ以外はエスケープする
    parts = re.split(r"\*(.+?)\*", paragraph)
    rendered = []
    for i, part in enumerate(parts):
        if i % 2 == 1:
            rendered.append(f"<em>{escape(part)}</em>")
        else:
            rendered.append(escape(part))
    return "".join(rendered)


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
                "months": data.get("months") or months_from_text(body) or months_from_photos(photos),
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
    return selected[:8]


def render_card(item, current, generated_keys):
    if item["photos"]:
        image = f'<img src="../../{item["photos"][0]}" alt="{escape(item["name"])}">'
    else:
        image = '<div class="placeholder">写真準備中</div>'
    is_generated = (item["category"], item["id"]) in generated_keys
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


def danger_block_and_flag(category, danger_text):
    """危険度メーター(ヘビ)または保護・採集バッジ(それ以外)のHTMLを返す。"""
    text = (danger_text or "").strip()
    prohibited = "禁止" in text

    if category == "hebi":
        if not text:
            level, label = 0, "情報準備中"
        elif "無毒" in text:
            level, label = 15, "無毒"
        elif "猛毒" in text:
            level, label = 90, "猛毒"
        elif "毒" in text:
            level, label = 60, "毒あり"
        else:
            level, label = 30, "情報準備中"
        block = (
            '<div class="meter-block">'
            f'<div class="meter-label"><span>危険度</span><strong>{escape(label)}</strong></div>'
            f'<div class="meter-track"><div class="meter-fill" style="width:{level}%"></div></div>'
            '</div>'
        )
        return block, prohibited

    if not text:
        tone, label = "neutral", "情報準備中"
    elif prohibited:
        tone, label = "warning", text
    elif "無毒" in text:
        tone, label = "safe", "無毒"
    elif "採集可" in text:
        tone, label = "neutral", "観察できる生き物"
    else:
        tone, label = "neutral", text
    block = f'<span class="status-badge {tone}">{escape(label)}</span>'
    return block, prohibited


def render_safety(danger_text, prohibited):
    parts = [f"<p>{escape(COMMON_SAFETY_MESSAGE)}</p>"]
    if prohibited and danger_text:
        parts.append(
            f'<p class="warning-line">この生き物は「{escape(danger_text)}」に該当します。'
            f"触れることも持ち帰ることも法律・条例で禁止されています。</p>"
        )
    return "".join(parts), (" warning" if prohibited else "")


def category_navigation(current_category, categories):
    links = []
    for category_id, name in categories.items():
        category_page = ROOT / "content" / "category-pages" / f"{category_id}.md"
        if category_id != current_category and category_page.exists():
            links.append(
                f'<a href="../../generated-categories/{category_id}.html">{escape(name)}一覧</a>'
            )
    return "".join(links)


def render(item, creatures, generated_keys, categories):
    active = set(item["months"])
    ticks = "".join(
        f'<span class="season-tick{" active" if month in active else ""}"></span>'
        for month in range(1, 13)
    )
    photos = item["photos"]
    if photos:
        hero = f'<img src="../../{photos[0]}" alt="奄美大島の{escape(item["name"])}">'
        gallery_photos = photos[1:4]
        if gallery_photos:
            figures = "".join(
                f'<figure><img class="gallery-photo" src="../../{photo}" alt="{escape(item["name"])}"></figure>'
                for photo in gallery_photos
            )
            gallery = f'<div class="gallery">{figures}</div>'
        else:
            gallery = '<div class="gallery-empty">追加の写真は準備中です。</div>'
    else:
        hero = '<div class="placeholder">写真準備中</div>'
        gallery = '<div class="gallery-empty">写真は準備中です。生き物の情報はご覧いただけます。</div>'

    if item["category"] == "kaeru" and len(photos) > 1:
        photo_script = (
            f"var heroPhotos = {json.dumps(photos)};"
            'var heroImage = document.querySelector(".hero-photo img");'
            'heroImage.src = "../../" + heroPhotos[Math.floor(Math.random() * heroPhotos.length)];'
        )
    else:
        photo_script = ""

    paragraphs = split_paragraphs(item["body"])
    if paragraphs and "*" in paragraphs[0]:
        latin_line = f'<p class="latin">{render_latin_inline(paragraphs[0])}</p>'
        body_paragraphs = paragraphs[1:]
    else:
        latin_line = ""
        body_paragraphs = paragraphs
    body_html = "".join(f"<p>{escape(p)}</p>" for p in body_paragraphs)

    danger_block, prohibited = danger_block_and_flag(item["category"], item["danger"])
    safety_html, safety_class = render_safety(item["danger"], prohibited)

    related = related_cards(item, creatures)
    cards = "".join(render_card(candidate, item, generated_keys) for candidate in related)
    related_html = (
        f'<section class="related"><p class="section-label">DISCOVER MORE</p>'
        f'<h2>この生き物に興味がある方へ</h2><div class="related-grid">{cards}</div></section>'
        if cards else ""
    )
    return TEMPLATE.read_text(encoding="utf-8").format(
        title=escape(item["name"]),
        category=escape(item["category_name"]),
        category_slug=item["category"].upper(),
        latin_line=latin_line,
        danger_block=danger_block,
        months="・".join(f"{month}月" for month in item["months"]) if item["months"] else "観察時期情報を準備中",
        ticks=ticks,
        hero=hero,
        gallery=gallery,
        body=body_html,
        safety_html=safety_html,
        safety_class=safety_class,
        related=related_html,
        category_navigation=category_navigation(item["category"], categories),
        photo_script=photo_script,
    )


def main():
    categories = load_categories()
    creatures = all_creatures(categories)
    if TARGETS is None:
        targets = [(item["category"], item["id"]) for item in creatures]
    else:
        targets = TARGETS
    by_key = {(item["category"], item["id"]): item for item in creatures}
    generated_keys = set(targets)
    for category, creature_id in targets:
        item = by_key.get((category, creature_id))
        if not item:
            print(f"スキップ（Markdownが見つかりません）: {category}/{creature_id}")
            continue
        output = OUTPUT_DIR / category / f"{creature_id}.html"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(render(item, creatures, generated_keys, categories), encoding="utf-8")
        print(output.relative_to(ROOT))


if __name__ == "__main__":
    main()
