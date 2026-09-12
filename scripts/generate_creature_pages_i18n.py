"""
content/creatures/カテゴリー/生き物ID.<lang>.md (例: habu.en.md) を元に、
翻訳版の個別ページを生成する。

- 日本語版(生き物ID.md)が存在しない翻訳ファイルは処理しない(分類判定に日本語版の
  danger記述を使うため)
- 危険度メーター/バッジの強さ判定(何%か、警告色にするか)は、常に日本語版のdanger
  記述をもとに判定する。表示するラベルの文字だけ、翻訳版のdanger記述を使う。
  (英語で書かれた"Highly venomous"のような文字列からは強さを判定できないため)
- サイト共通の文言(ホーム、お問い合わせ、SAFETY定型文など)は content/i18n/<lang>.json
  から読み込む
- 出力先は <lang>/creatures/カテゴリー/生き物ID.html (サイトのルート直下に言語フォルダ)

実行方法: python scripts/generate_creature_pages_i18n.py
"""
import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_creature_pages import (  # noqa: E402
    ROOT, CONTENT_DIR, PHOTO_DIR_ALIASES,
    parse_markdown, photo_files, split_paragraphs, render_latin_inline,
    related_cards,
)

TEMPLATE = ROOT / "templates" / "creature.i18n.html"
I18N_DIR = ROOT / "content" / "i18n"
LANGS = ["en", "es", "zh"]


def escape(value):
    return html.escape(str(value), quote=True)


def load_lang(lang):
    path = I18N_DIR / f"{lang}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def classify_danger(category, danger_ja_text):
    """危険度の強さを、日本語版のdanger記述から判定する(表示ラベルは別途翻訳版を使う)。"""
    text = (danger_ja_text or "").strip()
    prohibited = "禁止" in text
    if category == "hebi":
        if not text or "情報準備中" in text:
            level = 0
        elif "無毒" in text:
            level = 15
        elif "猛毒" in text:
            level = 90
        elif "毒" in text:
            level = 60
        else:
            level = 30
        return {"type": "meter", "level": level, "prohibited": prohibited}
    if prohibited:
        tone = "warning"
    elif "無毒" in text:
        tone = "safe"
    else:
        tone = "neutral"
    return {"type": "badge", "tone": tone, "prohibited": prohibited}


def render_danger_block(category, danger_ja_text, danger_display_text, strings):
    info = classify_danger(category, danger_ja_text)
    label = danger_display_text or strings["strings"].get("months_prep", "")
    if info["type"] == "meter":
        return (
            '<div class="meter-block">'
            f'<div class="meter-label"><span>{escape(strings["strings"]["danger_label"])}</span>'
            f'<strong>{escape(label)}</strong></div>'
            f'<div class="meter-track"><div class="meter-fill" style="width:{info["level"]}%"></div></div>'
            '</div>'
        ), info["prohibited"]
    return f'<span class="status-badge {info["tone"]}">{escape(label)}</span>', info["prohibited"]


def render_safety(danger_display_text, prohibited, strings):
    s = strings["strings"]
    parts = [f"<p>{escape(s['safety_common'])}</p>"]
    if prohibited and danger_display_text:
        warning = s["safety_warning_template"].format(danger=danger_display_text)
        parts.append(f'<p class="warning-line">{escape(warning)}</p>')
    return "".join(parts), (" warning" if prohibited else "")


def load_translated_creatures(lang):
    results = []
    for md in sorted(CONTENT_DIR.glob(f"*/*.{lang}.md")):
        category = md.parent.name
        data, body = parse_markdown(md)
        creature_id = data.get("id", md.name.split(f".{lang}.md")[0])

        ja_md = CONTENT_DIR / category / f"{creature_id}.md"
        if not ja_md.exists():
            print(f"スキップ（{lang}: 日本語版が見つかりません）: {category}/{creature_id}")
            continue
        ja_data, _ = parse_markdown(ja_md)

        photos = photo_files(category, creature_id)
        paragraphs = split_paragraphs(body)
        if paragraphs and "*" in paragraphs[0]:
            latin_line = render_latin_inline(paragraphs[0])
            desc_paragraphs = paragraphs[1:]
        else:
            latin_line = ""
            desc_paragraphs = paragraphs

        results.append({
            "id": creature_id,
            "category": category,
            "name": data.get("name", creature_id),
            "danger": data.get("danger", ""),
            "danger_ja": ja_data.get("danger", ""),
            "months": data.get("months") or ja_data.get("months") or [],
            "latin_line": latin_line,
            "body_paragraphs": desc_paragraphs,
            "photos": photos,
            "related_ja": ja_data.get("related", []) if isinstance(ja_data.get("related", []), list) else [],
        })
    return results


def render_card(candidate, current, all_ja_categories, strings):
    if candidate["photos"]:
        image = f'<img src="../../{candidate["photos"][0]}" alt="{escape(candidate["name"])}">'
    else:
        image = f'<div class="placeholder">{escape(strings["strings"]["photo_prep"])}</div>'
    href = (
        f'{candidate["id"]}.html'
        if candidate["category"] == current["category"]
        else f'../{candidate["category"]}/{candidate["id"]}.html'
    )
    category_label = strings["categories"].get(candidate["category"], candidate["category"])
    return (
        f'<a class="related-card" href="{href}">{image}'
        f'<span class="related-category">{escape(category_label)}</span>'
        f'<strong>{escape(candidate["name"])}</strong></a>'
    )


def render_category_nav(strings, current_category):
    links = []
    for key, label in strings["categories"].items():
        cls = ' class="active"' if key == current_category else ""
        links.append(f'<a href="../../{key}.html"{cls}>{escape(label)}</a>')
    return "".join(links)


def render_lang_bar(lang, category, creature_id, translated_langs_for_this_creature):
    order = [("ja", "JA")] + [(code, load_lang(code)["lang_label"]) for code in LANGS]
    parts = []
    for code, label in order:
        if code == lang:
            parts.append(f'<span class="current">{escape(label)}</span>')
        elif code == "ja":
            parts.append(f'<a href="../../../generated-creatures/{category}/{creature_id}.html">{escape(label)}</a>')
        elif code in translated_langs_for_this_creature:
            parts.append(f'<a href="../../../{code}/creatures/{category}/{creature_id}.html">{escape(label)}</a>')
        else:
            parts.append(f'<span class="disabled">{escape(label)}</span>')
    return "".join(parts)


def render(creature, lang, strings, same_lang_creatures, translated_langs_by_key):
    s = strings["strings"]
    active = set(creature["months"])
    ticks = "".join(
        f'<span class="season-tick{" active" if month in active else ""}"></span>'
        for month in range(1, 13)
    )

    photos = creature["photos"]
    if photos:
        hero = f'<img src="../../{photos[0]}" alt="{escape(creature["name"])}">'
        gallery_photos = photos[1:4]
        if gallery_photos:
            figures = "".join(
                f'<figure><img class="gallery-photo" src="../../{p}" alt="{escape(creature["name"])}"></figure>'
                for p in gallery_photos
            )
            gallery = f'<div class="gallery">{figures}</div>'
        else:
            gallery = f'<div class="gallery-empty">{escape(s["gallery_more_prep"])}</div>'
    else:
        hero = f'<div class="placeholder">{escape(s["photo_prep"])}</div>'
        gallery = f'<div class="gallery-empty">{escape(s["gallery_empty"])}</div>'

    body_html = "".join(f"<p>{escape(p)}</p>" for p in creature["body_paragraphs"])
    latin_line = f'<p class="latin">{creature["latin_line"]}</p>' if creature["latin_line"] else ""

    danger_block, prohibited = render_danger_block(
        creature["category"], creature["danger_ja"], creature["danger"], strings
    )
    safety_html, safety_class = render_safety(creature["danger"], prohibited, strings)

    related = related_cards(
        {**creature, "months": creature["months"], "related": creature["related_ja"]},
        same_lang_creatures,
    )
    cards = "".join(render_card(c, creature, strings["categories"], strings) for c in related)
    related_html = (
        f'<section class="related"><p class="section-label">DISCOVER MORE</p>'
        f'<h2>{escape(s["discover_heading"])}</h2><div class="related-grid">{cards}</div></section>'
        if cards else ""
    )

    key = (creature["category"], creature["id"])
    lang_links = render_lang_bar(lang, creature["category"], creature["id"], translated_langs_by_key.get(key, set()))

    months_text = "・".join(str(m) for m in creature["months"]) if creature["months"] else s["months_prep"]

    return TEMPLATE.read_text(encoding="utf-8").format(
        html_lang=lang,
        title=escape(creature["name"]),
        meta_description=escape(f'{creature["name"]} — Amami Oshima, Japan. Nature Experience Amami.'),
        category=escape(strings["categories"].get(creature["category"], creature["category"])),
        category_slug=creature["category"].upper(),
        latin_line=latin_line,
        danger_block=danger_block,
        months=escape(months_text),
        ticks=ticks,
        hero=hero,
        gallery=gallery,
        body=body_html,
        safety_html=safety_html,
        safety_class=safety_class,
        related=related_html,
        category_nav=render_category_nav(strings, creature["category"]),
        lang_links=lang_links,
        photo_script="",
        t_home=escape(s["home"]),
        t_contact=escape(s["contact"]),
        t_close=escape(s["close"]),
        t_season_label=escape(s["season_label"]),
        t_safety_heading=escape(s["safety_heading"]),
        about_heading=escape(s["about_heading"].format(name=creature["name"])),
        gallery_heading=escape(s["gallery_heading"].format(name=creature["name"])),
        tour_heading=escape(s["tour_heading"]),
        tour_text=escape(s["tour_text"]),
        tour_cta=escape(s["tour_cta"]),
        footer_text=escape(s["footer_text"]),
    )


def main():
    # どの生き物がどの言語に翻訳済みかを先にすべて調べておく(言語切り替えリンク用)
    translated_langs_by_key = {}
    all_by_lang = {}
    for lang in LANGS:
        creatures = load_translated_creatures(lang)
        all_by_lang[lang] = creatures
        for c in creatures:
            key = (c["category"], c["id"])
            translated_langs_by_key.setdefault(key, set()).add(lang)

    for lang in LANGS:
        strings = load_lang(lang)
        creatures = all_by_lang[lang]
        if not creatures:
            print(f"スキップ（{lang}: 翻訳Markdownが見つかりません）")
            continue
        for creature in creatures:
            output = ROOT / lang / "creatures" / creature["category"] / f'{creature["id"]}.html'
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(
                render(creature, lang, strings, creatures, translated_langs_by_key),
                encoding="utf-8",
            )
            print(output.relative_to(ROOT))


if __name__ == "__main__":
    main()
