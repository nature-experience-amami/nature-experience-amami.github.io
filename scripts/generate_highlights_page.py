"""
「奄美を代表する生き物」ページ (highlights.html) を生成する。

カテゴリーページ(generate_category_pages.py)とは違い、複数カテゴリーを
またいで、厳選した生き物だけを1ページに集める。サイトのトップ階層に
置く前提（generated-categories/ の中ではない）なので、パスの組み立て方が
generate_category_pages.py とは少し異なる。

掲載する生き物を増やしたいときは、下の HIGHLIGHT_CREATURES に
(カテゴリー, id) のペアを1行追加するだけでよい。

実行方法: python scripts/generate_highlights_page.py
"""
import html
import json
from pathlib import Path

from generate_category_pages import (
    ROOT,
    CATEGORY_CONTENT_DIR,
    CREATURE_CONTENT_DIR,
    CATEGORY_NAMES,
    parse_markdown,
    photo_files,
    card_description,
    card_status,
)

TEMPLATE = ROOT / "templates" / "highlights.html"
OUTPUT = ROOT / "highlights.html"

# 掲載する生き物。増やしたいときはここに (カテゴリー, id) を追加するだけでよい。
HIGHLIGHT_CREATURES = [
    ("honyuurui", "amami-kuro-usagi"),
    ("honyuurui", "kenaga-nezumi"),
    ("tori", "ruri-kakesu"),
    ("tori", "oosuton-ooakagera"),
    ("tori", "amami-yamashigi"),
    ("kaeru", "ishikawa-gaeru"),
]

EYEBROW = "CREATURES / HIGHLIGHTS"
HERO_TITLE = "奄美を代表する生き物"
HERO_LEAD = (
    "アマミノクロウサギをはじめ、奄美大島だけに暮らす個性的な生き物たち。"
    "ここで紹介しきれないほど、島の夜には驚くほど豊かな生態系が広がっています。"
)
INTRO_TITLE = "奄美大島の代表的な固有種たち"
INTRO_PARAGRAPHS = [
    "奄美大島は、大陸と切り離された長い年月の中で、ここにしかいない生き物たちを育んできました。中でもアマミノクロウサギやルリカケスは、島を象徴する存在として知られています。",
    "奄美市の生物多様性地域戦略でも、アマミノクロウサギ・アマミイシカワガエル・ルリカケスなどが代表的な固有種として挙げられています。",
    "ここで紹介しているのは、その中のほんの一部です。奄美の夜の森には、ヘビやカエル、クワガタなど、もっとたくさんの生き物たちが暮らしています。",
]
SAFETY_TITLE = "観察するときのお願い"
SAFETY_TEXT = (
    "奄美の生き物の多くは、国の天然記念物や国内希少野生動植物種に指定されており、"
    "捕獲・採集は法律で禁止されています。写真に収めて、そっと観察を楽しんでください。"
)
LIST_LABEL = "MEET THE ICONS"
LIST_TITLE = "奄美を象徴する生き物たち"
LIST_LEAD = "写真や名前をクリックすると、それぞれの詳しいページを見ることができます。"


def load_creature(category, creature_id):
    md_path = CREATURE_CONTENT_DIR / category / f"{creature_id}.md"
    metadata, body = parse_markdown(md_path)
    resolved_id = metadata.get("id", creature_id)
    return {
        "id": resolved_id,
        "name": metadata.get("name", resolved_id),
        "danger": metadata.get("danger", ""),
        "body": body,
        "photos": photo_files(category, resolved_id),
        "category": category,
    }


def highlight_card_html(creature, generated_creature_keys):
    """category.html用card_htmlのルート階層版（../を付けない）。"""
    category = creature["category"]
    name = html.escape(creature["name"])
    if creature["photos"]:
        photos = html.escape(json.dumps(creature["photos"]), quote=True)
        image = (
            f'<div class="creature-image" data-photos="{photos}">'
            f'<img src="{creature["photos"][0]}" alt="{name}"></div>'
        )
    else:
        image = '<div class="creature-image"><div class="photo-placeholder">写真準備中</div></div>'

    key = (category, creature["id"])
    if key in generated_creature_keys:
        opening = f'<a href="generated-creatures/{category}/{creature["id"]}.html">'
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


def category_buttons_for_highlights(available_categories):
    """category.htmlの category_buttons() のルート階層版。"""
    categories = json.loads(CATEGORY_NAMES.read_text(encoding="utf-8"))
    buttons = []
    for category_id, name in categories.items():
        escaped_name = html.escape(name)
        if category_id in available_categories:
            buttons.append(
                f'<a class="category-button" href="generated-categories/{category_id}.html">{escaped_name} →</a>'
            )
        else:
            buttons.append(
                f'<span class="category-button is-pending">{escaped_name}'
                '<small>準備中</small></span>'
            )
    return "".join(buttons)


def header_navigation_for_highlights(available_categories):
    """category.htmlの header_category_navigation() のルート階層版。"""
    categories = json.loads(CATEGORY_NAMES.read_text(encoding="utf-8"))
    links = []
    for category_id, name in categories.items():
        if category_id not in available_categories:
            continue
        escaped_name = html.escape(name)
        links.append(f'<a href="generated-categories/{category_id}.html">{escaped_name}一覧</a>')
    return "".join(links)


def main():
    generated_creature_keys = {
        (path.parent.name, path.stem)
        for path in (ROOT / "generated-creatures").glob("*/*.html")
    }
    available_categories = {
        parse_markdown(content_path)[0].get("id", content_path.stem)
        for content_path in CATEGORY_CONTENT_DIR.glob("*.md")
    }

    cards = "".join(
        highlight_card_html(load_creature(category, creature_id), generated_creature_keys)
        for category, creature_id in HIGHLIGHT_CREATURES
    )

    template = TEMPLATE.read_text(encoding="utf-8")
    page = template.format(
        name=html.escape(HERO_TITLE),
        eyebrow=html.escape(EYEBROW),
        hero_title=html.escape(HERO_TITLE),
        hero_lead=html.escape(HERO_LEAD),
        intro_title=html.escape(INTRO_TITLE),
        intro_body="".join(f"<p>{html.escape(item)}</p>" for item in INTRO_PARAGRAPHS),
        safety_title=html.escape(SAFETY_TITLE),
        safety_text=html.escape(SAFETY_TEXT),
        list_label=html.escape(LIST_LABEL),
        list_title=html.escape(LIST_TITLE),
        list_lead=html.escape(LIST_LEAD),
        cards=cards,
        category_buttons=category_buttons_for_highlights(available_categories),
        header_category_navigation=header_navigation_for_highlights(available_categories),
    )
    OUTPUT.write_text(page, encoding="utf-8")
    print(OUTPUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
