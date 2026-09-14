"""
軽量な「図鑑ページ」(zukan)の翻訳版を生成する。対象は TRANSLATED_ZUKAN_CATEGORIES。
生き物の説明文は content/creatures/カテゴリ/生き物ID.<lang>.md があればそれを、
無ければ日本語版をそのまま使う。カテゴリー紹介文(hero_lead等)は
CATEGORY_CONTENT_I18N にこのスクリプト内で直接持たせている(日本語版と同じ方式)。

出力先: <lang>/categories/カテゴリID.html
実行方法: python scripts/generate_zukan_page_i18n.py
"""
import html
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_zukan_page import (  # noqa: E402
    ROOT, CONTENT_DIR, TRANSLATED_ZUKAN_CATEGORIES, CATEGORY_GROUPS,
    ENGLISH_LABELS, parse_markdown, split_paragraphs,
    render_latin_inline, photo_files, load_categories,
)
from generate_creature_pages_i18n import load_lang, LANGS, AVAILABLE_CATEGORY_PAGES  # noqa: E402
from category_header import render_category_strip  # noqa: E402

TEMPLATE = ROOT / "templates" / "zukan.i18n.html"
OUTPUT_DIR_NAME = "categories"

CATEGORY_CONTENT_I18N = {
    "suisei-konntyuu": {
        "en": {
            "hero_lead": (
                "Small creatures living quietly at the water's edge — rice paddies, ponds, "
                "riverbanks. Diving beetles, riffle beetles, water striders: look closely and "
                "you'll find them."
            ),
            "about_paragraphs": [
                "There are a great many species, many of them highly specialized groups, so this "
                "page adds them gradually, in field-guide format, as photos and information come "
                "together. Click a photo or name to see that species' full page.",
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
                "Hay muchísimas especies, y muchas pertenecen a grupos muy especializados, así "
                "que esta página las añade poco a poco, en formato de guía de campo, conforme "
                "reunimos fotos e información. Haga clic en una foto o un nombre para ver la "
                "página completa de esa especie.",
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
                "水生昆虫种类繁多，其中不少还是专业性很强的类群，本页会随着照片和资料的积累"
                "逐步以图鉴形式补充完善。点击照片或名称，即可查看该物种的详细页面。",
            ],
            "note": (
                "水生昆虫较为纤弱，部分种类数量稀少。请在水边轻柔地观察，如需采集，"
                "也请将带走的数量控制在最低限度。"
            ),
        },
    },
    "tori": {
        "en": {
            "hero_lead": (
                "Amami Oshima's laurel forests are home to birds found only on this island and "
                "its neighbors — from the deep blue Lidth's Jay to the once-legendary Amami "
                "Thrush. Many migrants and winter visitors pass through too, so the birds you "
                "meet change with the season."
            ),
            "about_paragraphs": [
                "Amami Oshima is home to everything from endemic species like Lidth's Jay and "
                "the Amami Thrush, found nowhere else, to migratory birds like the Ruddy "
                "Kingfisher and the Grey-faced Buzzard that visit only in certain seasons. Birds "
                "are grouped here by their closest relatives.",
                "There are many kinds of birds, and new records keep being added, so species are "
                "added to this field guide gradually as photos and information come together. "
                "Click a photo or name to see that species' full page.",
            ],
            "note": (
                "Many of the birds introduced here are protected as national Natural Monuments "
                "or Nationally Rare Wild Species, and their capture, collection, or transfer is "
                "prohibited by law. Wild birds aren't something to catch and take home — they're "
                "best enjoyed by observing and photographing them without disturbing them. Keep "
                "a good distance, and avoid using playback calls or food to lure them in. Parent "
                "birds and chicks are especially sensitive while nesting or breeding, and "
                "approaching too closely or making noise can cause the nest to be abandoned or "
                "the chicks to fail to fledge successfully. Avoid flash or strong lights when "
                "photographing at night, and don't share information online that could reveal a "
                "nest's exact location."
            ),
        },
        "es": {
            "hero_lead": (
                "Los bosques laurifolios de Amami Oshima albergan aves que solo existen en esta "
                "isla y las vecinas, desde el azul intenso del arrendajo de Lidth hasta el otrora "
                "legendario zorzal de Amami. También pasan muchas aves migratorias y visitantes "
                "invernales, así que las especies que se encuentran cambian con la estación."
            ),
            "about_paragraphs": [
                "En Amami Oshima conviven especies endémicas como el arrendajo de Lidth y el "
                "zorzal de Amami, que no se encuentran en ningún otro lugar, junto con aves "
                "migratorias como el martín pescador rojizo y el busardo cariblanco, que solo "
                "visitan en ciertas estaciones. Aquí se agrupan por parentesco taxonómico.",
                "Hay muchas especies de aves y los registros siguen aumentando, así que vamos "
                "añadiendo especies a esta guía de campo poco a poco, conforme reunimos fotos e "
                "información. Haga clic en una foto o un nombre para ver la página completa de "
                "esa especie.",
            ],
            "note": (
                "Muchas de las aves presentadas aquí están protegidas como Monumentos Naturales "
                "nacionales o Especies Silvestres Nacionales Raras, y su captura, recolección o "
                "traslado está prohibido por ley. Las aves silvestres no son algo que se capture "
                "y se lleve a casa: lo mejor es disfrutarlas observándolas y fotografiándolas sin "
                "molestarlas. Mantenga una buena distancia y evite usar reproducciones de cantos "
                "o comida para atraerlas. Los progenitores y los polluelos son especialmente "
                "sensibles durante la nidificación o la cría, y acercarse demasiado o hacer "
                "ruido puede provocar que abandonen el nido o que las crías no lleguen a volar "
                "con éxito. Evite el flash o las luces intensas al fotografiar de noche, y no "
                "comparta en línea información que pueda revelar la ubicación exacta de un nido."
            ),
        },
        "zh": {
            "hero_lead": (
                "奄美大岛的照叶树林中，栖息着只分布于这座岛屿及周边岛屿的固有鸟类——从蓝紫色的"
                "琉球松鸦，到曾被称为「幻之鸟」的奄美地鸫。此外还有许多候鸟与冬候鸟经过或停留，"
                "因此不同季节能遇见的鸟类也会随之变化。"
            ),
            "about_paragraphs": [
                "奄美大岛既有琉球松鸦、奄美地鸫这样只分布于本岛的固有种，也有琉球赤翡翠、"
                "灰脸鵟鹰这样只在特定季节到访的候鸟，鸟类种类十分多样。这里按照亲缘关系相近的"
                "类群进行分组介绍。",
                "鸟类种类繁多，观察记录也在不断增加，因此本页会随着照片和资料的积累逐步以"
                "图鉴形式补充新的种类。点击照片或名称，即可查看该物种的详细页面。",
            ],
            "note": (
                "这里介绍的鸟类中，有不少被指定为国家天然纪念物或国内稀有野生动植物种，根据法律"
                "禁止对其进行捕获、采集及转让。野鸟并非应该捕捉带回家的对象，最好的享受方式是在"
                "不打扰它们的前提下进行观察与拍摄。请保持足够的距离，避免使用鸣声回放或食物来"
                "引诱它们靠近。亲鸟和雏鸟在营巢或育雏期间格外敏感，过度靠近或发出声响可能导致"
                "弃巢或雏鸟无法顺利离巢。夜间拍摄时请避免使用闪光灯或强光，也不要在网络上公开"
                "可能暴露鸟巢具体位置的信息。"
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
            "category": category,
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


def render_card(creature, strings, lang):
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
    page_path = ROOT / lang / "creatures" / creature["category"] / f'{creature["id"]}.html'
    if page_path.is_file():
        opening = f'<a class="zukan-card" href="../creatures/{creature["category"]}/{creature["id"]}.html">'
        closing = "</a>"
    else:
        opening = '<div class="zukan-card">'
        closing = "</div>"
    return (
        f'{opening}'
        f'<div class="zukan-image">{image}</div>'
        '<div class="zukan-info">'
        f'<div class="zukan-name">{escape(creature["name"])}</div>'
        f'{latin_html}'
        f'<p class="zukan-desc">{escape(creature["description"])}</p>'
        f'{tag_html}'
        f'</div>{closing}'
    )


def render_groups(category, creatures, strings, lang):
    group_def = CATEGORY_GROUPS.get(category)
    if not group_def:
        cards = "".join(render_card(c, strings, lang) for c in creatures)
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
        cards = "".join(render_card(c, strings, lang) for c in members)
        sections.append(
            f'<div class="group"><p class="group-title">{escape(label)}</p>'
            f'<div class="zukan-grid">{cards}</div></div>'
        )
    return "\n".join(sections)


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
            parts.append(f'<a href="../../categories/{category}.html">{escape(label)}</a>')
        else:
            parts.append(f'<a href="../../{code}/categories/{category}.html">{escape(label)}</a>')
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
        category_strip=render_category_strip(strings["categories"], category, AVAILABLE_CATEGORY_PAGES, pending_label=s["pending_label"]),
        groups_html=render_groups(category, creatures, strings, lang),
        other_buttons=render_other_buttons(strings, category),
        night_tour_title=escape(s["night_tour_title"]),
        night_tour_lead=escape(s["night_tour_lead"]),
        night_tour_cta=escape(s["night_tour_cta"]),
        explore_more_title=escape(s["explore_more_title"]),
        footer_copy=escape(s["footer_text"]),
        t_home=escape(s["home"]),
        t_highlights=escape(s["highlights_nav"]),
        t_tour=escape(s["tour"]),
        t_contact=escape(s["contact"]),
        t_category_nav_aria=escape(s["creature_category_nav_aria"]),
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
