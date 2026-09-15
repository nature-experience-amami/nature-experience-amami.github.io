"""
content/category-pages/カテゴリID.<lang>.md をもとに、ヘビ・カエル・クワガタのような
フルページ形式のカテゴリーページの翻訳版を生成する。

出力先: <lang>/categories/カテゴリID.html
実行方法: python scripts/generate_category_pages_i18n.py
"""
import html
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_category_pages import (  # noqa: E402
    ROOT, CREATURE_CONTENT_DIR, PHOTO_DIR_ALIASES,
    parse_markdown, paragraphs, photo_files,
)
from generate_creature_pages_i18n import (  # noqa: E402
    load_lang, LANGS, AVAILABLE_CATEGORY_PAGES,
)
from category_header import render_category_strip  # noqa: E402

CATEGORY_CONTENT_DIR = ROOT / "content" / "category-pages"
TEMPLATE = ROOT / "templates" / "category.i18n.html"
OUTPUT_DIR_NAME = "categories"
FULL_PAGE_CATEGORIES = ["hebi", "kaeru", "kuwagata", "honyuurui"]

GROUP_ORDER = {"frog": 0, "newt": 1}
GROUP_LABEL_KEYS = {"frog": "group_frog", "newt": "group_newt"}


def escape(value):
    return html.escape(str(value), quote=True)


def card_description(body, strings):
    source = " ".join(paragraphs(body)[1:] or paragraphs(body))
    if not source:
        return strings["strings"]["info_prep"]
    return source[:86].rstrip("。.") + "."


def card_status(category, ja_danger, display_danger, strings):
    s = strings["strings"]
    if category == "kuwagata":
        return s["collecting_prohibited"] if "禁止" in ja_danger else s["enjoy_observing"]
    return display_danger or s["observation_info_prep"]


def creatures_in_category_lang(category, lang):
    result = []
    directory = CREATURE_CONTENT_DIR / category
    for path in sorted(directory.glob("*.md")):
        if path.name.endswith((".en.md", ".es.md", ".zh.md")):
            continue
        ja_data, _ = parse_markdown(path)
        creature_id = ja_data.get("id", path.stem)
        translated_path = directory / f"{creature_id}.{lang}.md"
        if translated_path.exists():
            data, body = parse_markdown(translated_path)
        else:
            data, body = ja_data, path.read_text(encoding="utf-8").split("---", 2)[-1].strip()
        result.append({
            "id": creature_id,
            "name": data.get("name", creature_id),
            "danger": data.get("danger", ""),
            "danger_ja": ja_data.get("danger", ""),
            "group": ja_data.get("group", ""),
            "body": body,
            "photos": photo_files(category, creature_id),
            "translated": translated_path.exists(),
        })
    return result


def cards_html(category, creatures, generated_keys, lang, strings):
    ordered = sorted(creatures, key=lambda c: GROUP_ORDER.get(c.get("group") or "", 0))
    parts = []
    last_group = None
    for creature in ordered:
        group = creature.get("group") or ""
        if group != last_group and group in GROUP_LABEL_KEYS:
            label = escape(strings["strings"][GROUP_LABEL_KEYS[group]])
            parts.append(f'<div class="group-divider">{label}</div>')
        parts.append(card_html(category, creature, generated_keys, lang, strings))
        last_group = group
    return "".join(parts)


def card_html(category, creature, generated_keys, lang, strings):
    s = strings["strings"]
    name = escape(creature["name"])
    if creature["photos"]:
        photos = escape(json.dumps(creature["photos"]))
        image = (
            f'<div class="creature-image" data-photos="{photos}">'
            f'<img src="../../{creature["photos"][0]}" alt="{name}"></div>'
        )
    else:
        image = f'<div class="creature-image"><div class="photo-placeholder">{escape(s["photo_prep"])}</div></div>'

    key = (lang, category, creature["id"])
    if key in generated_keys:
        opening = f'<a href="../creatures/{category}/{creature["id"]}.html">'
        closing = "</a>"
        link = "VIEW CREATURE →"
        card_class = ""
    else:
        opening = "<div>"
        closing = "</div>"
        link = "PAGE PREPARING"
        card_class = " card-disabled"

    status = card_status(category, creature["danger_ja"], creature["danger"], strings)
    ja_text = creature["danger_ja"]
    danger_class = (
        " danger"
        if "禁止" in ja_text or ("毒" in ja_text and "無毒" not in ja_text)
        else ""
    )
    return (
        f'<article class="creature-card{card_class}">{opening}'
        f'<div class="creature-info">'
        f'<div class="creature-meta"><span>{escape(category.upper())}</span>'
        f'<span class="{danger_class.strip()}">{escape(status)}</span></div>'
        f'<span class="creature-name">{name}</span>'
        f'<p class="creature-description">{escape(card_description(creature["body"], strings))}</p></div>'
        f'{image}<span class="creature-link">{link}</span>{closing}</article>'
    )


def category_buttons(category, strings):
    s = strings["strings"]
    cats = strings["categories"]
    buttons = [
        f'<a class="category-button" href="../highlights.html">{escape(s["highlights_nav"])} →</a>'
    ]
    for category_id, name in cats.items():
        if category_id == category:
            buttons.append(f'<span class="category-button is-current">{escape(name)}</span>')
        elif category_id in AVAILABLE_CATEGORY_PAGES:
            buttons.append(f'<a class="category-button" href="{category_id}.html">{escape(name)} →</a>')
    return "".join(buttons)


def render_lang_bar(lang, category):
    order = [("ja", "JA")] + [(code, load_lang(code)["lang_label"]) for code in LANGS]
    parts = []
    for code, label in order:
        if code == lang:
            parts.append(f'<span class="current">{escape(label)}</span>')
        elif code == "ja":
            parts.append(f'<a href="../../categories/{category}.html">{escape(label)}</a>')
        else:
            parts.append(f'<a href="../../{code}/categories/{category}.html">{escape(label)}</a>')
    return "".join(parts)


def main():
    generated_keys = set()
    for lang in LANGS:
        for path in (ROOT / lang / "creatures").glob("*/*.html"):
            generated_keys.add((lang, path.parent.name, path.stem))

    template = TEMPLATE.read_text(encoding="utf-8")

    for category in FULL_PAGE_CATEGORIES:
        ja_path = CATEGORY_CONTENT_DIR / f"{category}.md"
        if not ja_path.exists():
            print(f"スキップ（{category}: 日本語版のcontent/category-pagesが見つかりません）")
            continue
        ja_meta, _ = parse_markdown(ja_path)

        for lang in LANGS:
            translated_path = CATEGORY_CONTENT_DIR / f"{category}.{lang}.md"
            if not translated_path.exists():
                print(f"スキップ（{lang}/{category}: 翻訳Markdownが見つかりません）")
                continue
            strings = load_lang(lang)
            meta, body = parse_markdown(translated_path)
            creatures = creatures_in_category_lang(category, lang)

            page = template.format(
                html_lang=lang,
                name=escape(strings["categories"].get(category, category)),
                meta_description=escape(f'{strings["categories"].get(category, category)} of Amami Oshima — Nature Experience Amami.'),
                eyebrow=escape(ja_meta["eyebrow"]),
                hero_title=escape(meta["hero_title"]),
                hero_lead=escape(meta["hero_lead"]),
                intro_title=escape(meta["intro_title"]),
                intro_body="".join(f"<p>{escape(item)}</p>" for item in paragraphs(body)),
                safety_title=escape(meta["safety_title"]),
                safety_text=escape(meta["safety_text"]),
                list_label=escape(ja_meta["list_label"]),
                list_title=escape(meta["list_title"]),
                list_lead=escape(meta["list_lead"]),
                cards=cards_html(category, creatures, generated_keys, lang, strings),
                category_buttons=category_buttons(category, strings),
                category_strip=render_category_strip(strings["categories"], category, AVAILABLE_CATEGORY_PAGES),
                explore_more_title=escape(strings["strings"]["explore_more_title"]),
                explore_more_lead=escape(strings["strings"]["explore_more_lead"]),
                night_tour_title=escape(strings["strings"]["night_tour_title"]),
                night_tour_lead=escape(strings["strings"]["night_tour_lead"]),
                night_tour_cta=escape(strings["strings"]["night_tour_cta"]),
                footer_text=escape(strings["strings"]["footer_text"]),
                t_home=escape(strings["strings"]["home"]),
                t_highlights=escape(strings["strings"]["highlights_nav"]),
                t_contact=escape(strings["strings"]["contact"]),
                t_tour=escape(strings["strings"]["tour"]),
                t_category_nav_aria=escape(strings["strings"]["creature_category_nav_aria"]),
                lang_links=render_lang_bar(lang, category),
            )

            output_dir = ROOT / lang / OUTPUT_DIR_NAME
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f"{category}.html"
            output_path.write_text(page, encoding="utf-8")
            print(output_path.relative_to(ROOT))


if __name__ == "__main__":
    main()
