import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATEGORY_CONTENT_DIR = ROOT / "content" / "category-pages"
CREATURE_CONTENT_DIR = ROOT / "content" / "creatures"
IMAGES_DIR = ROOT / "images" / "creatures"
OUTPUT_DIR = ROOT / "generated-categories"
TEMPLATE = ROOT / "templates" / "category.html"
CATEGORY_NAMES = ROOT / "content" / "categories.json"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

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


def parse_markdown(path):
    text = path.read_text(encoding="utf-8")
    frontmatter, body = {}, text
    if text.startswith("---"):
        _, raw, body = text.split("---", 2)
        for line in raw.strip().splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                frontmatter[key.strip()] = value.strip()
    return frontmatter, body.strip()


def paragraphs(body):
    return [item.strip() for item in re.split(r"\n\s*\n", body) if item.strip()]


def photo_files(category, creature_id):
    directory = IMAGES_DIR / category / PHOTO_DIR_ALIASES.get((category, creature_id), creature_id)
    if not directory.is_dir():
        return []
    return sorted(
        path.relative_to(ROOT).as_posix()
        for path in directory.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    )


def card_description(body):
    source = " ".join(paragraphs(body)[1:] or paragraphs(body))
    return source[:86].rstrip("。") + ("。" if source else "情報を準備中です。")


def card_status(category, danger):
    if category == "kuwagata":
        return "採集禁止" if "禁止" in danger else "観察して楽しもう"
    return danger or "観察情報準備中"


def card_html(category, creature, generated_creature_keys):
    name = html.escape(creature["name"])
    if creature["photos"]:
        photos = html.escape(json.dumps(creature["photos"]), quote=True)
        image = (
            f'<div class="creature-image" data-photos="{photos}">'
            f'<img src="../{creature["photos"][0]}" alt="{name}"></div>'
        )
    else:
        image = '<div class="creature-image"><div class="photo-placeholder">写真準備中</div></div>'

    key = (category, creature["id"])
    if key in generated_creature_keys:
        opening = f'<a href="../generated-creatures/{category}/{creature["id"]}.html">'
        closing = "</a>"
        link = "VIEW CREATURE →"
        card_class = ""
    else:
        opening = "<div>"
        closing = "</div>"
        link = "PAGE PREPARING"
        card_class = " card-disabled"

    status = card_status(category, creature["danger"])
    danger_class = (
        " danger"
        if "猛毒" in status or ("毒" in status and "無毒" not in status) or "採集禁止" in status
        else ""
    )
    return (
        f'<article class="creature-card{card_class}">{opening}'
        f'<div class="creature-info">'
        f'<div class="creature-meta"><span>{html.escape(category.upper())}</span>'
        f'<span class="{danger_class.strip()}">{html.escape(status)}</span></div>'
        f'<span class="creature-name">{name}</span>'
        f'<p class="creature-description">{html.escape(card_description(creature["body"]))}</p></div>'
        f'{image}<span class="creature-link">{link}</span>{closing}</article>'
    )


def creatures_in_category(category):
    result = []
    directory = CREATURE_CONTENT_DIR / category
    for path in sorted(directory.glob("*.md")):
        metadata, body = parse_markdown(path)
        creature_id = metadata.get("id", path.stem)
        result.append({
            "id": creature_id,
            "name": metadata.get("name", creature_id),
            "danger": metadata.get("danger", ""),
            "body": body,
            "photos": photo_files(category, creature_id),
        })
    return result


def category_buttons(category, available_categories):
    categories = json.loads(CATEGORY_NAMES.read_text(encoding="utf-8"))
    buttons = []
    for category_id, name in categories.items():
        escaped_name = html.escape(name)
        if category_id == category:
            buttons.append(f'<span class="category-button is-current">{escaped_name}</span>')
        elif category_id in available_categories:
            buttons.append(
                f'<a class="category-button" href="{category_id}.html">{escaped_name} →</a>'
            )
        else:
            buttons.append(
                f'<span class="category-button is-pending">{escaped_name}'
                '<small>準備中</small></span>'
            )
    return "".join(buttons)


def main():
    generated_creature_keys = {
        (path.parent.name, path.stem)
        for path in (ROOT / "generated-creatures").glob("*/*.html")
    }
    template = TEMPLATE.read_text(encoding="utf-8")
    content_paths = sorted(CATEGORY_CONTENT_DIR.glob("*.md"))
    available_categories = {
        parse_markdown(content_path)[0].get("id", content_path.stem)
        for content_path in content_paths
    }
    for content_path in content_paths:
        metadata, body = parse_markdown(content_path)
        category = metadata.get("id", content_path.stem)
        creatures = creatures_in_category(category)
        page = template.format(
            name=html.escape(metadata["name"]),
            eyebrow=html.escape(metadata["eyebrow"]),
            hero_title=html.escape(metadata["hero_title"]),
            hero_lead=html.escape(metadata["hero_lead"]),
            intro_title=html.escape(metadata["intro_title"]),
            intro_body="".join(f"<p>{html.escape(item)}</p>" for item in paragraphs(body)),
            safety_title=html.escape(metadata["safety_title"]),
            safety_text=html.escape(metadata["safety_text"]),
            list_label=html.escape(metadata["list_label"]),
            list_title=html.escape(metadata["list_title"]),
            list_lead=html.escape(metadata["list_lead"]),
            cards="".join(card_html(category, creature, generated_creature_keys) for creature in creatures),
            category_buttons=category_buttons(category, available_categories),
        )
        OUTPUT_DIR.mkdir(exist_ok=True)
        output_path = OUTPUT_DIR / f"{category}.html"
        output_path.write_text(page, encoding="utf-8")
        print(output_path.relative_to(ROOT))


if __name__ == "__main__":
    main()
