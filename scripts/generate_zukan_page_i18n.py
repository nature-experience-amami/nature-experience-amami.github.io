"""
軽量な「図鑑ページ」(zukan)の翻訳版を生成する。対象は TRANSLATED_ZUKAN_CATEGORIES。
生き物の説明文は content/creatures/カテゴリ/生き物ID.<lang>.md があればそれを、
無ければ日本語版をそのまま使う。カテゴリー紹介文(hero_lead等)は
CATEGORY_CONTENT_I18N にこのスクリプト内で直接持たせている(日本語版と同じ方式)。

出力先: <lang>/generated-categories/カテゴリID.html
実行方法: python scripts/generate_zukan_page_i18n.py
"""
import html
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_zukan_page import (  # noqa: E402
    ROOT, CONTENT_DIR, TRANSLATED_ZUKAN_CATEGORIES, CATEGORY_GROUPS,
    ENGLISH_LABELS, parse_markdown, split_paragraphs, render_latin_inline,
    photo_files, load_categories,
)
from generate_creature_pages_i18n import load_lang, LANGS, AVAILABLE_CATEGORY_PAGES  # noqa: E402

TEMPLATE = ROOT / "templates" / "zukan.i18n.html"
OUTPUT_DIR_NAME = "generated-categories"

CATEGORY_CONTENT_I18N = {
    "suisei-konntyuu": {
        "en": {
            "hero_lead": (
                "Small creatures living quietly at the water's edge — rice paddies, ponds, "
                "riverbanks. Diving beetles, riffle beetles, water striders: look closely and "
                "you'll find them."
            ),
            "about_paragraphs": [
                "Unlike snakes or frogs, aquatic insects don't get a full page per species here. "
                "Instead, this page gathers them all in one field-guide format.",
                "There are a great many species, many of them highly specialized groups, so we "
                "add photos and information gradually as they come together.",
            ],
            "note": (
                "Aquatic insects are delicate, and some species are quite scarce. Please observe "
                "gently from the water's edge, and if you do collect any, keep the number you "
                "take home to a minimum."
            ),
        },
        "es": {
            "hero_lead": (
                "Pequeñas criaturas que viven discretamente junto al agua: arrozales, estanques, "
                "orillas de ríos. Escarabajos buceadores, escarabajos de rabión, zapateros de "
                "agua: mire con atención y los encontrará."
            ),
            "about_paragraphs": [
                "A diferencia de las serpientes o las ranas, los insectos acuáticos no tienen "
                "aquí una página completa por especie. En su lugar, esta página los reúne a "
                "todos en formato de guía de campo.",
                "Hay muchísimas especies, y muchas pertenecen a grupos muy especializados, así "
                "que añadimos fotos e información poco a poco conforme las vamos reuniendo.",
            ],
            "note": (
                "Los insectos acuáticos son delicados, y algunas especies son bastante escasas. "
                "Obsérvelos con cuidado desde la orilla del agua, y si recolecta alguno, lleve a "
                "casa el menor número posible."
            ),
        },
        "zh": {
            "hero_lead": (
                "静静生活在奄美水边的小生物——水田、池塘、河边。龙虱、长角泥甲、宽肩蝽——"
                "仔细寻找就能与它们相遇。"
            ),
            "about_paragraphs": [
                "与蛇类、蛙类不同，水生昆虫不会在本站为每个物种单独制作详细页面，"
                "而是采用图鉴形式集中介绍。",
                "水生昆虫种类繁多，其中不少还是专业性很强的类群，我们会随着照片和资料"
                "的积累逐步补充完善。",
            ],
            "note": (
                "水生昆虫较为纤弱，部分种类数量稀少。请在水边轻柔地观察，如需采集，"
                "也请将带走的数量控制在最低限度。"
            ),
        },
    },
}

FIELD_GUIDE_TITLE_KEY = {
    "suisei-konntyuu": "categories",  # 実際のタイトルは categories[category] をそのまま使う
}


def escape(value):
    return html.escape(str(value), quote=True)


def load_creatures_lang(category, lang):
    category_dir = CONTENT_DIR / category
    if not category_dir.is_dir():
        return []
    creatures = []
    for md in sorted(category_dir.glob("*.md")):
        if md.name.endswith((".en.md", ".es.md", ".zh.md")):
            continue
        ja_data, _ = parse_markdown(md)
        creature_id = ja_data.get("id", md.stem)
        translated_path = category_dir / f"{creature_id}.{lang}.md"
        if translated_path.exists():
            data, body = parse_markdown(translated_path)
        else:
            data, body = ja_data, md.read_text(encoding="utf-8").split("---", 2)[-1].strip()

        photos = photo_files(category, creature_id)
        paragraphs = split_paragraphs(body)
        if paragraphs and "*" in paragraphs[0]:
            latin_line = render_latin_inline(paragraphs[0])
            desc_paragraphs = paragraphs[1:]
        else:
            latin_line = ""
            desc_paragraphs = paragraphs
        description = " ".join(desc_paragraphs)
        creatures.append({
            "id": creature_id,
            "name": data.get("name", creature_id),
            "group": ja_data.get("group", "other"),
            "danger": data.get("danger", ""),
            "danger_ja": ja_data.get("danger", ""),
            "latin": latin_line,
            "description": description,
            "photos": photos,
        })
    return creatures


def zukan_tag(ja_danger, display_danger):
    text = (display_danger or "").strip()
    if not text:
        return ""
    tone = "rare" if any(word in ja_danger for word in ("レッドリスト", "絶滅危惧", "禁止")) else ""
    css_class = f"zukan-tag {tone}".strip()
    return f'<span class="{css_class}">{escape(text)}</span>'


def render_card(creature, strings):
    photos = creature["photos"]
    if photos:
        if len(photos) > 1:
            photo_urls = json.dumps([f"../../{p}" for p in photos], ensure_ascii=False)
            image = (
                f'<img src="../../{photos[0]}" data-photos=\'{escape(photo_urls)}\' '
                f'alt="{escape(creature["name"])}">'
            )
        else:
            image = f'<img src="../../{photos[0]}" alt="{escape(creature["name"])}">'
    else:
        image = f'<div class="zukan-placeholder">{escape(strings["strings"]["photo_prep"])}</div>'
    latin_html = f'<div class="zukan-latin">{creature["latin"]}</div>' if creature["latin"] else ""
    tag_html = zukan_tag(creature["danger_ja"], creature["danger"])
    return (
        '<div class="zukan-card">'
        f'<div class="zukan-image">{image}</div>'
        '<div class="zukan-info">'
        f'<div class="zukan-name">{escape(creature["name"])}</div>'
        f'{latin_html}'
        f'<p class="zukan-desc">{escape(creature["description"])}</p>'
        f'{tag_html}'
        '</div></div>'
    )


def render_groups(category, creatures, strings):
    group_def = CATEGORY_GROUPS.get(category)
    if not group_def:
        cards = "".join(render_card(c, strings) for c in creatures)
        return f'<div class="group"><div class="zukan-grid">{cards}</div></div>'

    by_group = {}
    for creature in creatures:
        by_group.setdefault(creature["group"], []).append(creature)

    sections = []
    for key in group_def["order"]:
        members = by_group.get(key)
        if not members:
            continue
        label_key = f"group_{key}"
        label = strings["strings"].get(label_key, key)
        cards = "".join(render_card(c, strings) for c in members)
        sections.append(
            f'<div class="group"><p class="group-title">{escape(label)}</p>'
            f'<div class="zukan-grid">{cards}</div></div>'
        )
    return "\n".join(sections)


def render_nav(strings, current):
    links = []
    for key, label in strings["categories"].items():
        if key == current:
            links.append(f'<span class="active">{escape(label)}</span>')
        elif key in AVAILABLE_CATEGORY_PAGES:
            links.append(f'<a href="{key}.html">{escape(label)}</a>')
        else:
            links.append(f'<span class="is-pending">{escape(label)}</span>')
    return "".join(links)


def render_other_buttons(strings, current):
    s = strings["strings"]
    buttons = []
    for key, label in strings["categories"].items():
        if key == current:
            continue
        if key in AVAILABLE_CATEGORY_PAGES:
            buttons.append(f'<a href="{key}.html" class="category-button">{escape(label)} →</a>')
        else:
            buttons.append(
                f'<span class="category-button is-pending">{escape(label)}'
                f'<small>{escape(s["pending_label"])}</small></span>'
            )
    return "".join(buttons)


def render_lang_bar(lang, category):
    order = [("ja", "JA")] + [(code, load_lang(code)["lang_label"]) for code in LANGS]
    parts = []
    for code, label in order:
        if code == lang:
            parts.append(f'<span class="current">{escape(label)}</span>')
        elif code == "ja":
            parts.append(f'<a href="../../generated-categories/{category}.html">{escape(label)}</a>')
        else:
            parts.append(f'<a href="../../{code}/generated-categories/{category}.html">{escape(label)}</a>')
    return "".join(parts)


def render_category(category, lang):
    strings = load_lang(lang)
    creatures = load_creatures_lang(category, lang)
    if not creatures:
        print(f"スキップ（{lang}/{category}: Markdownが見つかりません）")
        return

    title = strings["categories"].get(category, category)
    content = CATEGORY_CONTENT_I18N.get(category, {}).get(lang)
    if not content:
        print(f"スキップ（{lang}/{category}: 翻訳された紹介文がありません）")
        return
    about_html = "".join(f"<p>{escape(p)}</p>" for p in content["about_paragraphs"])
    eyebrow = f"CREATURES / {ENGLISH_LABELS.get(category, category.upper())}"
    s = strings["strings"]

    page = TEMPLATE.read_text(encoding="utf-8").format(
        html_lang=lang,
        title=escape(title),
        meta_description=escape(f"{title} of Amami Oshima — Nature Experience Amami."),
        eyebrow=escape(eyebrow),
        hero_lead=escape(content["hero_lead"]),
        zukan_about_title=escape(s["zukan_about_title"]),
        about_paragraphs=about_html,
        note=escape(content["note"]),
        field_guide_title=escape(title),
        nav_links=render_nav(strings, category),
        groups_html=render_groups(category, creatures, strings),
        other_buttons=render_other_buttons(strings, category),
        night_tour_title=escape(s["night_tour_title"]),
        night_tour_lead=escape(s["night_tour_lead"]),
        night_tour_cta=escape(s["night_tour_cta"]),
        explore_more_title=escape(s["explore_more_title"]),
        footer_copy=escape(s["footer_text"]),
        t_home=escape(s["home"]),
        t_tour=escape(s["tour"]),
        t_contact=escape(s["contact"]),
        lang_links=render_lang_bar(lang, category),
    )

    output_dir = ROOT / lang / OUTPUT_DIR_NAME
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{category}.html"
    output_path.write_text(page, encoding="utf-8")
    print(output_path.relative_to(ROOT))


def main():
    for category in TRANSLATED_ZUKAN_CATEGORIES:
        for lang in LANGS:
            render_category(category, lang)


if __name__ == "__main__":
    main()
