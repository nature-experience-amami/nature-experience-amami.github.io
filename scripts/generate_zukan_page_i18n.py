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
from seo_head import HTML_LANGS, insert_ogp  # noqa: E402

TEMPLATE = ROOT / "templates" / "zukan.i18n.html"
OUTPUT_DIR_NAME = "categories"

CATEGORY_CONTENT_I18N = {
    "other-arthropods": {
        "en": {
            "hero_lead": (
                "Whip scorpions, giant centipedes, pseudoscorpions and more — the arthropods "
                "of Amami Oshima that are not insects."
            ),
            "about_paragraphs": [
                "This page adds species gradually, in field-guide format, as photos and "
                "information come together.",
            ],
            "note": (
                "When it feels threatened, the Amami whip scorpion defends itself by spraying "
                "a liquid that smells like vinegar. If you find one, please don't touch it, and "
                "observe gently without disturbing the animals or their habitat."
            ),
        },
        "es": {
            "hero_lead": (
                "Escorpiones látigo, ciempiés gigantes, pseudoescorpiones y más: los artrópodos de "
                "Amami Oshima que no son insectos."
            ),
            "about_paragraphs": [
                "Esta página se va completando poco a poco, especie por especie, en formato de "
                "guía de campo, conforme reunimos fotos e información.",
            ],
            "note": (
                "Cuando se siente amenazado, el escorpión látigo de Amami se defiende rociando un "
                "líquido con olor a vinagre. Si encuentra uno, no lo toque y obsérvelo con "
                "cuidado, sin perturbar a los animales ni su hábitat."
            ),
        },
        "zh": {
            "hero_lead": "鞭蠍、蚰蜒、偽蠍等——奄美大島上昆蟲以外的節肢動物。",
            "about_paragraphs": [
                "本頁面會隨著照片與資料的積累，逐步以圖鑑形式增加物種。",
            ],
            "note": (
                "奄美鞭蠍在感到危險時，會噴出帶有醋味的液體保護自己。發現時請不要用手觸碰，"
                "並輕聲觀察，避免打擾生物及其棲息環境。"
            ),
        },
    },
    "other-insects": {
        "en": {
            "hero_lead": (
                "From butterflies and dragonflies to moths, crickets, and katydids — the "
                "insects of Amami Oshima beyond beetles and aquatic insects."
            ),
            "about_paragraphs": [
                "This page adds species gradually, in field-guide format, as photos and "
                "information come together. Click a photo or name to see that species' "
                "full page.",
            ],
            "note": (
                "Some species shown here — including a dragonfly found almost nowhere else "
                "in Japan — are protected under Japan's Act on Conservation of Endangered "
                "Species and may not be collected. Please observe gently, without disturbing "
                "the animals or their habitat."
            ),
        },
        "es": {
            "hero_lead": (
                "De mariposas y libélulas a polillas, grillos y saltamontes: los insectos de "
                "Amami Oshima más allá de los escarabajos y los insectos acuáticos."
            ),
            "about_paragraphs": [
                "Esta página se va completando poco a poco, especie por especie, en formato "
                "de guía de campo, conforme reunimos fotos e información. Haga clic en una "
                "foto o un nombre para ver la página completa de esa especie.",
            ],
            "note": (
                "Algunas especies presentadas aquí — entre ellas una libélula que apenas se "
                "encuentra en otro lugar de Japón — están protegidas por la Ley de "
                "Conservación de Especies en Peligro de Japón y no pueden recolectarse. "
                "Obsérvelas con cuidado, sin perturbar a los animales ni su hábitat."
            ),
        },
        "zh": {
            "hero_lead": (
                "從蝴蝶、蜻蜓到蛾類、蟋蟀與螽斯——甲蟲和水生昆蟲之外，奄美大島的昆蟲們。"
            ),
            "about_paragraphs": [
                "本頁面會隨著照片與資料的積累，逐步以圖鑑形式增加物種。點擊照片或名稱即可"
                "查看該物種的詳細頁面。",
            ],
            "note": (
                "本頁介紹的部分物種——包括一種在日本其他地方幾乎難覓蹤跡的蜻蜓——受日本"
                "《瀕危物種保護法》保護，禁止採集。請輕聲觀察，避免打擾生物及其棲息環境。"
            ),
        },
    },
    "beetles": {
        "en": {
            "hero_lead": (
                "Beetles you'll meet in the night forest, each with its own look and way of "
                "life. From dung beetles that rely on the Amami rabbit's droppings to "
                "rhinoceros beetles drawn to lights, here's a glimpse of the beetles found on "
                "Amami Oshima."
            ),
            "about_paragraphs": [
                "Amami Oshima alone is home to an enormous variety of beetles, many belonging "
                "to highly specialized groups, so this page adds species gradually, in "
                "field-guide format, as photos and information come together. Click a photo "
                "or name to see that species' full page.",
            ],
            "note": (
                "Many of the beetles introduced here are endemic or rare species found only "
                "on Amami Oshima and Tokunoshima, and collecting some of them is prohibited "
                "by law or ordinance. Please observe gently, without placing a burden on the "
                "creatures or their environment. This page also includes invasive species "
                "brought in from outside the island through human activity, which are marked "
                "separately from native species."
            ),
        },
        "es": {
            "hero_lead": (
                "Escarabajos que se encuentran en el bosque nocturno, cada uno con su propio "
                "aspecto y forma de vida. Desde los escarabajos peloteros que dependen de los "
                "excrementos del conejo de Amami hasta los escarabajos rinoceronte atraídos "
                "por la luz, aquí se presenta una muestra de los escarabajos de Amami Oshima."
            ),
            "about_paragraphs": [
                "Amami Oshima alberga una enorme variedad de escarabajos, muchos de ellos "
                "pertenecientes a grupos muy especializados, así que esta página los añade "
                "poco a poco, en formato de guía de campo, conforme reunimos fotos e "
                "información. Haga clic en una foto o un nombre para ver la página completa "
                "de esa especie.",
            ],
            "note": (
                "Muchos de los escarabajos presentados aquí son especies endémicas o raras "
                "que solo se encuentran en Amami Oshima y Tokunoshima, y la recolección de "
                "algunas está prohibida por ley u ordenanza. Obsérvelos con cuidado, sin "
                "suponer una carga para los animales ni para el entorno. Esta página también "
                "incluye especies invasoras introducidas desde fuera de la isla por la "
                "actividad humana, que se indican por separado de las especies nativas."
            ),
        },
        "zh": {
            "hero_lead": (
                "在夜晚的森林中邂逅的甲蟲們，姿態與生活方式各不相同。從依靠奄美黑兔糞便生活的"
                "糞金龜，到飛向燈光的犀金龜，這裡介紹的是奄美島上的部分甲蟲。"
            ),
            "about_paragraphs": [
                "僅奄美大島的甲蟲種類就極為豐富，其中不少還是專業性很強的類群，本頁會隨著"
                "照片和資料的積累逐步以圖鑑形式補充完善。點擊照片或名稱，即可查看該物種的"
                "詳細頁面。",
            ],
            "note": (
                "這裡介紹的甲蟲中，許多是只分布於奄美大島、德之島的固有種或稀有種，其中一些"
                "物種根據法律或條例禁止採集。請在不給生物和環境造成負擔的前提下輕柔地進行"
                "觀察。此外，本頁也收錄了因人類活動而從島外帶入的外來種，並將其與本土生物"
                "區分標注。"
            ),
        },
    },
    "aquatic-insects": {
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
                "靜靜生活在奄美水邊的小生物——水田、池塘、河邊。龍蝨、長角泥甲、寬肩蝽——"
                "仔細尋找就能與它們相遇。"
            ),
            "about_paragraphs": [
                "水生昆蟲種類繁多，其中不少還是專業性很強的類群，本頁會隨著照片和資料的積累"
                "逐步以圖鑑形式補充完善。點擊照片或名稱，即可查看該物種的詳細頁面。",
            ],
            "note": (
                "水生昆蟲較為纖弱，部分種類數量稀少。請在水邊輕柔地觀察，如需採集，"
                "也請將帶走的數量控制在最低限度。"
            ),
        },
    },
    "birds": {
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
                "奄美大島的照葉樹林中，棲息著只分布於這座島嶼及周邊島嶼的固有鳥類——從藍紫色的"
                "琉球松鴉，到曾被稱為「幻之鳥」的奄美地鶇。此外還有許多候鳥與冬候鳥經過或停留，"
                "因此不同季節能遇見的鳥類也會隨之變化。"
            ),
            "about_paragraphs": [
                "奄美大島既有琉球松鴉、奄美地鶇這樣只分布於本島的固有種，也有琉球赤翡翠、"
                "灰臉鵟鷹這樣只在特定季節到訪的候鳥，鳥類種類十分多樣。這裡按照親緣關係相近的"
                "類群進行分組介紹。",
                "鳥類種類繁多，觀察記錄也在不斷增加，因此本頁會隨著照片和資料的積累逐步以"
                "圖鑑形式補充新的種類。點擊照片或名稱，即可查看該物種的詳細頁面。",
            ],
            "note": (
                "這裡介紹的鳥類中，有不少被指定為國家天然紀念物或國內稀有野生動植物種，根據法律"
                "禁止對其進行捕獲、採集及轉讓。野鳥並非應該捕捉帶回家的對象，最好的享受方式是在"
                "不打擾它們的前提下進行觀察與拍攝。請保持足夠的距離，避免使用鳴聲回放或食物來"
                "引誘它們靠近。親鳥和雛鳥在營巢或育雛期間格外敏感，過度靠近或發出聲響可能導致"
                "棄巢或雛鳥無法順利離巢。夜間拍攝時請避免使用閃光燈或強光，也不要在網絡上公開"
                "可能暴露鳥巢具體位置的信息。"
            ),
        },
    },
}

FIELD_GUIDE_TITLE_KEY = {
    "aquatic-insects": "categories",  # 実際のタイトルは categories[category] をそのまま使う
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
    if "外来種" in ja_danger:
        tone = "invasive"
    elif any(word in ja_danger for word in ("レッドリスト", "絶滅危惧", "禁止")):
        tone = "rare"
    else:
        tone = ""
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
    buttons = [f'<a href="../highlights.html" class="category-button">{escape(s["highlights_nav"])} →</a>']
    for key, label in strings["categories"].items():
        if key == current:
            continue
        if key in AVAILABLE_CATEGORY_PAGES:
            buttons.append(f'<a href="{key}.html" class="category-button">{escape(label)} →</a>')
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
        html_lang=HTML_LANGS.get(lang, lang),
        title=escape(title),
        meta_description=escape(f"{title} of Amami Oshima — Nature Experience Amami."),
        eyebrow=escape(eyebrow),
        hero_lead=escape(content["hero_lead"]),
        zukan_about_title=escape(s["zukan_about_title"]),
        about_paragraphs=about_html,
        note=escape(content["note"]),
        field_guide_title=escape(title),
        category_strip=render_category_strip(strings["categories"], category, AVAILABLE_CATEGORY_PAGES),
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
    page = insert_ogp(page, f"{lang}/{OUTPUT_DIR_NAME}/{category}.html", lang)
    output_path.write_text(page, encoding="utf-8")
    print(output_path.relative_to(ROOT))


def main():
    for category in TRANSLATED_ZUKAN_CATEGORIES:
        for lang in LANGS:
            render_category(category, lang)


if __name__ == "__main__":
    main()
