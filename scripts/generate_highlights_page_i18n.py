"""
「奄美を代表する生き物」ページ (highlights.html) の翻訳版を生成する。

掲載する生き物はJA版と同じ HIGHLIGHT_CREATURES (generate_highlights_page.py) を使う。
ページ文言(hero/intro/safety等)はこのファイル内に直接、言語ごとに持たせている
(generate_zukan_page_i18n.py の CATEGORY_CONTENT_I18N と同じ方式)。

出力先: <lang>/highlights.html
実行方法: python scripts/generate_highlights_page_i18n.py
"""
import html
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_category_pages import (  # noqa: E402
    ROOT, CREATURE_CONTENT_DIR, parse_markdown, photo_files,
)
from generate_category_pages_i18n import card_description, card_status  # noqa: E402
from generate_highlights_page import HIGHLIGHT_CREATURES  # noqa: E402
from generate_creature_pages_i18n import load_lang, LANGS, AVAILABLE_CATEGORY_PAGES  # noqa: E402
from category_header import render_category_strip  # noqa: E402

TEMPLATE = ROOT / "templates" / "highlights.i18n.html"
OUTPUT_NAME = "highlights.html"

EYEBROW = "CREATURES / HIGHLIGHTS"
LIST_LABEL = "MEET THE ICONS"

HIGHLIGHTS_CONTENT_I18N = {
    "en": {
        "hero_title": "Signature Wildlife of Amami Oshima",
        "hero_lead": (
            "From the Amami Rabbit to a host of other distinctive creatures found only on "
            "this island — the forests of Amami Oshima at night hold a richer ecosystem than "
            "could ever be fully captured here."
        ),
        "intro_title": "Amami Oshima's Signature Endemic Species",
        "intro_paragraphs": [
            "Having been separated from the continent for a very long time, Amami Oshima has "
            "nurtured creatures found nowhere else in the world. Among them, the Amami Rabbit "
            "and Lidth's Jay are especially well known as symbols of the island.",
            "The Amami City Biodiversity Regional Strategy also names the Amami Rabbit, Amami "
            "Ishikawa's Frog, and Lidth's Jay among the island's representative endemic species.",
            "What's introduced here is only a small part of the whole. Amami Oshima's night "
            "forests are home to many more creatures still — snakes, frogs, stag beetles, and "
            "much more.",
        ],
        "safety_title": "A Request for Observers",
        "safety_text": (
            "Many of Amami's creatures are designated Natural Monuments or Nationally Rare Wild "
            "Species, and their capture or collection is prohibited by law. Please enjoy "
            "observing them quietly, and capture the moment in a photograph instead."
        ),
        "list_title": "Meet the Icons of Amami",
        "list_lead": "Click a photo or name to see that species' full page.",
    },
    "es": {
        "hero_title": "Fauna Emblemática de Amami Oshima",
        "hero_lead": (
            "Desde el Conejo de Amami hasta muchas otras criaturas singulares que solo se "
            "encuentran en esta isla: los bosques nocturnos de Amami Oshima albergan un "
            "ecosistema más rico de lo que aquí se puede mostrar por completo."
        ),
        "intro_title": "Las Especies Endémicas Emblemáticas de Amami Oshima",
        "intro_paragraphs": [
            "Tras llevar separada del continente durante muchísimo tiempo, Amami Oshima ha "
            "dado cobijo a criaturas que no se encuentran en ningún otro lugar del mundo. "
            "Entre ellas, el Conejo de Amami y el arrendajo de Lidth son especialmente "
            "conocidos como símbolos de la isla.",
            "La Estrategia Regional de Biodiversidad de la ciudad de Amami también menciona "
            "al Conejo de Amami, la rana de Ishikawa de Amami y el arrendajo de Lidth entre "
            "las especies endémicas representativas de la isla.",
            "Lo que se presenta aquí es solo una pequeña parte del conjunto. Los bosques "
            "nocturnos de Amami Oshima albergan muchas más criaturas: serpientes, ranas, "
            "ciervos volantes y mucho más.",
        ],
        "safety_title": "Una Petición para los Observadores",
        "safety_text": (
            "Muchas de las criaturas de Amami están designadas Monumentos Naturales o "
            "Especies Silvestres Nacionales Raras, y su captura o recolección está prohibida "
            "por ley. Disfrute observándolas en silencio y capture el momento en una fotografía."
        ),
        "list_title": "Conozca los Iconos de Amami",
        "list_lead": "Haga clic en una foto o un nombre para ver la página completa de esa especie.",
    },
    "zh": {
        "hero_title": "奄美大岛的代表性生物",
        "hero_lead": (
            "从奄美黑兔到许多只有这座岛屿才有的个性生物——奄美大岛的夜间森林中，"
            "蕴藏着一个远比这里所能展示的更为丰富的生态系统。"
        ),
        "intro_title": "奄美大岛的代表性固有种",
        "intro_paragraphs": [
            "奄美大岛自与大陆分离以来经过了漫长的岁月，孕育出许多在世界其他地方都看不到的生物。"
            "其中，奄美黑兔和琉球松鸦作为岛屿的象征而广为人知。",
            "在奄美市的生物多样性地区战略中，也将奄美黑兔、奄美石川蛙、琉球松鸦等列为该岛具有"
            "代表性的固有种。",
            "这里介绍的只是其中很小的一部分。奄美大岛的夜间森林中，还栖息着蛇类、蛙类、"
            "锹形虫等更多种类的生物。",
        ],
        "safety_title": "观察时的注意事项",
        "safety_text": (
            "奄美的许多生物被指定为国家天然纪念物或国内稀有野生动植物种，法律禁止捕获、采集。"
            "请通过拍照留念，静静地享受观察的乐趣。"
        ),
        "list_title": "认识奄美的代表性生物",
        "list_lead": "点击照片或名称即可查看该物种的详细页面。",
    },
}


def escape(value):
    return html.escape(str(value), quote=True)


def load_highlight_creature(category, creature_id, lang):
    ja_path = CREATURE_CONTENT_DIR / category / f"{creature_id}.md"
    ja_data, _ = parse_markdown(ja_path)
    translated_path = CREATURE_CONTENT_DIR / category / f"{creature_id}.{lang}.md"
    if translated_path.exists():
        data, body = parse_markdown(translated_path)
    else:
        data, body = ja_data, ja_path.read_text(encoding="utf-8").split("---", 2)[-1].strip()
    return {
        "id": creature_id,
        "category": category,
        "name": data.get("name", creature_id),
        "danger": data.get("danger", ""),
        "danger_ja": ja_data.get("danger", ""),
        "body": body,
        "photos": photo_files(category, creature_id),
    }


def highlight_card_html(creature, generated_keys, lang, strings):
    category = creature["category"]
    name = escape(creature["name"])
    if creature["photos"]:
        photos = escape(json.dumps(creature["photos"]))
        image = (
            f'<div class="creature-image" data-photos="{photos}">'
            f'<img src="{creature["photos"][0]}" alt="{name}"></div>'
        )
    else:
        image = f'<div class="creature-image"><div class="photo-placeholder">{escape(strings["strings"]["photo_prep"])}</div></div>'

    key = (lang, category, creature["id"])
    if key in generated_keys:
        opening = f'<a href="creatures/{category}/{creature["id"]}.html">'
        closing = "</a>"
        link = "VIEW CREATURE →"
        card_class = ""
    else:
        opening = "<div>"
        closing = "</div>"
        link = "PAGE PREPARING"
        card_class = " card-disabled"

    status = card_status(category, creature["danger_ja"], creature["danger"], strings)
    danger_class = (
        " danger"
        if "禁止" in creature["danger_ja"] or ("毒" in creature["danger_ja"] and "無毒" not in creature["danger_ja"])
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


def category_buttons(strings):
    cats = strings["categories"]
    return "".join(
        f'<a class="category-button" href="categories/{category_id}.html">{escape(name)} →</a>'
        for category_id, name in cats.items()
        if category_id in AVAILABLE_CATEGORY_PAGES
    )


def render_lang_bar(lang):
    order = [("ja", "JA")] + [(code, load_lang(code)["lang_label"]) for code in LANGS]
    parts = []
    for code, label in order:
        if code == lang:
            parts.append(f'<span class="current">{escape(label)}</span>')
        elif code == "ja":
            parts.append('<a href="../highlights.html">JA</a>')
        else:
            parts.append(f'<a href="../{code}/highlights.html">{escape(label)}</a>')
    return "".join(parts)


def main():
    generated_keys = set()
    for lang in LANGS:
        for path in (ROOT / lang / "creatures").glob("*/*.html"):
            generated_keys.add((lang, path.parent.name, path.stem))

    template = TEMPLATE.read_text(encoding="utf-8")

    for lang in LANGS:
        content = HIGHLIGHTS_CONTENT_I18N.get(lang)
        if not content:
            print(f"スキップ（{lang}: 翻訳文言がありません）")
            continue
        strings = load_lang(lang)
        s = strings["strings"]

        cards = "".join(
            highlight_card_html(
                load_highlight_creature(category, creature_id, lang),
                generated_keys, lang, strings,
            )
            for category, creature_id in HIGHLIGHT_CREATURES
        )

        page = template.format(
            html_lang=lang,
            name=escape(s["highlights_nav"]),
            meta_description=escape(f'{content["hero_title"]} — Nature Experience Amami.'),
            eyebrow=escape(EYEBROW),
            hero_title=escape(content["hero_title"]),
            hero_lead=escape(content["hero_lead"]),
            intro_title=escape(content["intro_title"]),
            intro_body="".join(f"<p>{escape(item)}</p>" for item in content["intro_paragraphs"]),
            safety_title=escape(content["safety_title"]),
            safety_text=escape(content["safety_text"]),
            list_label=escape(LIST_LABEL),
            list_title=escape(content["list_title"]),
            list_lead=escape(content["list_lead"]),
            cards=cards,
            category_buttons=category_buttons(strings),
            category_strip=render_category_strip(
                strings["categories"], None, AVAILABLE_CATEGORY_PAGES,
                href_prefix="categories/",
            ),
            explore_more_title=escape(s["explore_more_title"]),
            explore_more_lead=escape(s["explore_more_lead"]),
            night_tour_title=escape(s["night_tour_title"]),
            night_tour_lead=escape(s["night_tour_lead"]),
            night_tour_cta=escape(s["night_tour_cta"]),
            footer_text=escape(s["footer_text"]),
            t_home=escape(s["home"]),
            t_tour=escape(s["tour"]),
            t_contact=escape(s["contact"]),
            t_category_nav_aria=escape(s["creature_category_nav_aria"]),
            lang_links=render_lang_bar(lang),
        )

        output_path = ROOT / lang / OUTPUT_NAME
        output_path.write_text(page, encoding="utf-8")
        print(output_path.relative_to(ROOT))


if __name__ == "__main__":
    main()
