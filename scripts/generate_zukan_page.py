"""
軽量な「図鑑ページ」を自動生成する。
ヘビ・カエル・クワガタのような個別ページは作らず、1カテゴリー1ページに
カード一覧としてまとめる方式(危険度メーター・SAFETY文などは無し)。

対象カテゴリーは ZUKAN_CATEGORIES に列挙する。
content/creatures/カテゴリー/*.md を読み、写真があればカードに使う。
グループ分け(見出し区切り)をしたい場合は、Markdownのfrontmatterに
group: gengoro のような行を追加し、CATEGORY_GROUPS に定義する。
定義が無いカテゴリーは、見出し無しで1つのグリッドにまとめて表示する。

実行方法: python scripts/generate_zukan_page.py
"""
import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from category_header import render_category_strip  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CONTENT_DIR = ROOT / "content" / "creatures"
IMAGES_DIR = ROOT / "images" / "creatures"
CATEGORIES_FILE = ROOT / "content" / "categories.json"
CATEGORY_PAGES_DIR = ROOT / "content" / "category-pages"
TEMPLATE = ROOT / "templates" / "zukan.html"
OUTPUT_DIR = ROOT / "categories"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}

# 図鑑形式で作るカテゴリー(ヘビ・カエル・クワガタのようなフルページ形式のものは含めない)
ZUKAN_CATEGORIES = ["suisei-konntyuu", "koucyu", "konchu", "kani", "tori"]

# 翻訳版(generate_zukan_page_i18n.py)が実際に生成しているカテゴリー
TRANSLATED_ZUKAN_CATEGORIES = {"suisei-konntyuu", "tori"}

# 写真フォルダ名がMarkdownのidと違う場合の対応表。(カテゴリ, Markdownのid): 実際の写真フォルダ名
PHOTO_DIR_ALIASES = {}

# カテゴリーごとの英語表記(ヒーローのラベル用)。無ければカテゴリーIDをそのまま大文字にする。
ENGLISH_LABELS = {
    "suisei-konntyuu": "AQUATIC INSECTS",
    "koucyu": "BEETLES",
    "konchu": "INSECTS",
    "kani": "CRABS",
    "tori": "BIRDS",
}

# カテゴリーごとの紹介文・注意書き。無ければ汎用の文章を使う。
CATEGORY_CONTENT = {
    "koucyu": {
        "hero_lead": (
            "夜の森で出会う、姿も暮らしぶりもさまざまな甲虫たち。"
            "アマミノクロウサギの糞を利用する糞虫から、灯火に飛んでくるカブトムシまで、"
            "奄美で見られる甲虫の一部を紹介します。"
        ),
        "about_paragraphs": [
            "甲虫は奄美大島だけでも非常に種類が多く、専門的なグループも多いジャンルのため、"
            "このページでは写真や情報が集まった種類から少しずつ図鑑形式で紹介しています。"
            "写真や名前をクリックすると、それぞれの詳しいページを見ることができます。",
        ],
        "note": (
            "ここで紹介する甲虫の多くは奄美大島・徳之島にしか分布しない固有種や希少種で、"
            "種によっては法律や条例により採集が禁止されています。観察は生き物にも環境にも"
            "負担をかけないよう、そっと行いましょう。なお、人の活動にともなって島外から"
            "持ち込まれた外来種も含めて紹介しており、これらは在来の生き物と区別して掲載しています。"
        ),
    },
    "suisei-konntyuu": {
        "hero_lead": (
            "田んぼや池、川のふちなど、奄美の水辺にひっそりと暮らす小さな生き物たち。"
            "ゲンゴロウ、ドロムシ、アメンボ――じっくり探すと出会える種類を紹介します。"
        ),
        "about_paragraphs": [
            "種類がとても多く、専門的なグループも多いジャンルのため、"
            "このページでは写真や情報が集まった種類から少しずつ図鑑形式で紹介しています。"
            "写真や名前をクリックすると、それぞれの詳しいページを見ることができます。",
        ],
        "note": (
            "水生昆虫は繊細で、種類によっては生息数が少ないものもいます。観察は水辺からそっと行い、"
            "採集する場合も持ち帰る数は最小限にとどめましょう。"
        ),
    },
    "tori": {
        "hero_lead": (
            "奄美大島の照葉樹林には、瑠璃色のルリカケスや幻の鳥オオトラツグミなど、"
            "この島や周辺の島々だけに暮らす固有の鳥たちがいます。渡り鳥や冬鳥も多く、"
            "季節によって出会える顔ぶれが変わります。"
        ),
        "about_paragraphs": [
            "奄美大島には、ルリカケスやオオトラツグミのようにこの島でしか見られない固有種から、"
            "アカショウビンやサシバのように決まった季節にだけ訪れる渡り鳥まで、多様な鳥が暮らしています。"
            "分類の近い仲間ごとにグループ分けして紹介しています。",
            "鳥は種類が多く、これからも記録が増えていくジャンルのため、"
            "写真や情報が集まった種類から少しずつ図鑑形式で追加しています。"
            "写真や名前をクリックすると、それぞれの詳しいページを見ることができます。",
        ],
        "note": (
            "ここで紹介する鳥の多くは、国の天然記念物や国内希少野生動植物種に指定されており、"
            "法律により捕獲・採集・譲渡が禁止されています。野鳥は捕まえて持ち帰るものではなく、"
            "驚かせずに観察・撮影を楽しむ生き物です。十分な距離を保ち、鳴き声の再生(プレイバック)や"
            "餌で呼び寄せることは避けてください。特に営巣中や繁殖期は親鳥やヒナが敏感になっており、"
            "近づいたり物音を立てたりすると抱卵放棄や巣立ちの失敗につながるおそれがあります。"
            "夜間の撮影ではストロボや強い照明を使わず、営巣場所が特定できる情報をSNS等で"
            "公開しないようにしましょう。"
        ),
    },
}

DEFAULT_CONTENT = {
    "hero_lead": "奄美大島で出会える生き物たちを紹介します。",
    "about_paragraphs": [
        "このページは、写真や情報が集まった種類から少しずつ追加していく図鑑形式のページです。"
    ],
    "note": "観察は生き物にも環境にも負担をかけないよう、そっと行いましょう。",
}

# グループ分けの定義。(カテゴリー): {"order": [...], "labels": {...}}
CATEGORY_GROUPS = {
    "koucyu": {
        "order": ["funchu", "kabuto", "hanamuguri", "manmaru", "tamamushi", "kamikiri", "hamushi", "other"],
        "labels": {
            "funchu": "糞虫の仲間",
            "kabuto": "カブトムシの仲間",
            "hanamuguri": "ハナムグリの仲間",
            "manmaru": "マンマルコガネの仲間",
            "tamamushi": "タマムシの仲間",
            "kamikiri": "カミキリムシの仲間",
            "hamushi": "ハムシの仲間",
            "other": "その他",
        },
    },
    "suisei-konntyuu": {
        "order": ["gengoro", "doromushi", "amenbo", "mizumushi", "other"],
        "labels": {
            "gengoro": "ゲンゴロウの仲間",
            "doromushi": "ヒメドロムシの仲間",
            "amenbo": "アメンボの仲間",
            "mizumushi": "ミズムシの仲間",
            "other": "その他",
        },
    },
    "tori": {
        "order": ["suzume", "buppousou", "fukurou", "taka", "kitsutsuki", "hato", "chidori", "other"],
        "labels": {
            "suzume": "スズメ目(ヒタキ・カラス・サンコウチョウの仲間)",
            "buppousou": "ブッポウソウ目(カワセミの仲間)",
            "fukurou": "フクロウ目",
            "taka": "タカ目",
            "kitsutsuki": "キツツキ目",
            "hato": "ハト目",
            "chidori": "チドリ目(シギ・チドリの仲間)",
            "other": "その他",
        },
    },
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
                frontmatter[key.strip()] = [
                    item.strip().strip("\"'") for item in value[1:-1].split(",") if item.strip()
                ]
            else:
                frontmatter[key.strip()] = value
    return frontmatter, body.strip()


def split_paragraphs(body):
    return [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]


def render_latin_inline(paragraph):
    parts = re.split(r"\*(.+?)\*", paragraph)
    rendered = []
    for i, part in enumerate(parts):
        if i % 2 == 1:
            rendered.append(f"<em>{escape(part)}</em>")
        else:
            rendered.append(escape(part))
    return "".join(rendered)


def load_categories():
    return json.loads(CATEGORIES_FILE.read_text(encoding="utf-8")) if CATEGORIES_FILE.exists() else {}


def photo_files(category, creature_id):
    directory_name = PHOTO_DIR_ALIASES.get((category, creature_id), creature_id)
    category_dir = IMAGES_DIR / category
    if not category_dir.is_dir():
        return []

    # 1階層: images/creatures/カテゴリー/生き物ID/
    directory = category_dir / directory_name
    if not directory.is_dir():
        # 2階層: images/creatures/カテゴリー/グループ名/生き物ID/
        directory = None
        for sub in category_dir.iterdir():
            if sub.is_dir() and (sub / directory_name).is_dir():
                directory = sub / directory_name
                break
        if directory is None:
            return []

    return sorted(
        str(path.relative_to(ROOT)).replace("\\", "/")
        for path in directory.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_EXTS
    )


def format_months(months):
    """観察しやすい時期を「4〜9月」のような短い表記にする(年をまたぐ範囲にも対応)。"""
    months = sorted({int(m) for m in months})
    if not months:
        return ""
    if len(months) == 1:
        return f"{months[0]}月"
    doubled = months + [m + 12 for m in months]
    n = len(months)
    for start_idx in range(n):
        window = doubled[start_idx:start_idx + n]
        if window == list(range(window[0], window[0] + n)):
            start_m = window[0] if window[0] <= 12 else window[0] - 12
            end_m = window[-1] if window[-1] <= 12 else window[-1] - 12
            return f"{start_m}〜{end_m}月"
    return "・".join(f"{m}月" for m in months)


def zukan_tag(danger_text):
    text = (danger_text or "").strip()
    if not text:
        return ""
    if "外来種" in text:
        tone = "invasive"
    elif any(word in text for word in ("レッドリスト", "絶滅危惧", "禁止")):
        tone = "rare"
    else:
        tone = ""
    css_class = f"zukan-tag {tone}".strip()
    return f'<span class="{css_class}">{escape(text)}</span>'


def load_creatures(category):
    category_dir = CONTENT_DIR / category
    if not category_dir.is_dir():
        return []
    creatures = []
    for md in sorted(category_dir.glob("*.md")):
        if md.name.endswith((".en.md", ".es.md", ".zh.md")):
            continue
        data, body = parse_markdown(md)
        creature_id = data.get("id", md.stem)
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
            "group": data.get("group", "other"),
            "danger": data.get("danger", ""),
            "months": data.get("months") or [],
            "latin": latin_line,
            "description": description,
            "photos": photos,
        })
    return creatures


def render_card(creature):
    photos = creature["photos"]
    if photos:
        if len(photos) > 1:
            photo_urls = json.dumps([f"../{p}" for p in photos], ensure_ascii=False)
            image = (
                f'<img src="../{photos[0]}" data-photos=\'{escape(photo_urls)}\' '
                f'alt="{escape(creature["name"])}">'
            )
        else:
            image = f'<img src="../{photos[0]}" alt="{escape(creature["name"])}">'
    else:
        image = '<div class="zukan-placeholder">写真準備中</div>'
    latin_html = f'<div class="zukan-latin">{creature["latin"]}</div>' if creature["latin"] else ""
    season_text = format_months(creature.get("months", []))
    season_html = f'<div class="zukan-season">観察期 {escape(season_text)}</div>' if season_text else ""
    tag_html = zukan_tag(creature["danger"])
    page_path = ROOT / "creatures" / creature["category"] / f'{creature["id"]}.html'
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
        f'{season_html}'
        f'{tag_html}'
        f'</div>{closing}'
    )


def render_groups(category, creatures):
    group_def = CATEGORY_GROUPS.get(category)
    if not group_def:
        cards = "".join(render_card(c) for c in creatures)
        return f'<div class="group"><div class="zukan-grid">{cards}</div></div>'

    by_group = {}
    for creature in creatures:
        by_group.setdefault(creature["group"], []).append(creature)

    sections = []
    for key in group_def["order"]:
        members = by_group.get(key)
        if not members:
            continue
        label = group_def["labels"].get(key, key)
        cards = "".join(render_card(c) for c in members)
        sections.append(
            f'<div class="group"><p class="group-title">{escape(label)}</p>'
            f'<div class="zukan-grid">{cards}</div></div>'
        )
    return "\n".join(sections)


def render_other_buttons(categories, current, available_categories):
    buttons = ['<a href="../highlights.html" class="category-button">代表的な生き物 →</a>']
    for key, label in categories.items():
        if key == current:
            continue
        if key in available_categories:
            buttons.append(f'<a href="{key}.html" class="category-button">{escape(label)} →</a>')
    return "".join(buttons)


def render_lang_bar(category):
    order = [("en", "EN"), ("es", "ES"), ("zh", "中文")]
    parts = ['<span class="current">JA</span>']
    for code, label in order:
        if category in TRANSLATED_ZUKAN_CATEGORIES:
            parts.append(f'<a href="../{code}/categories/{category}.html">{label}</a>')
        else:
            parts.append(f'<span class="disabled">{label}</span>')
    return "".join(parts)


def render_category(category, categories, available_categories):
    creatures = load_creatures(category)
    if not creatures:
        print(f"スキップ（{category}: Markdownが見つかりません）")
        return

    title = categories.get(category, category)
    content = CATEGORY_CONTENT.get(category, DEFAULT_CONTENT)
    about_html = "".join(f"<p>{escape(p)}</p>" for p in content["about_paragraphs"])
    eyebrow = f"CREATURES / {ENGLISH_LABELS.get(category, category.upper())}"

    html_out = TEMPLATE.read_text(encoding="utf-8").format(
        title=escape(title),
        eyebrow=escape(eyebrow),
        hero_lead=escape(content["hero_lead"]),
        about_paragraphs=about_html,
        note=escape(content["note"]),
        category_strip=render_category_strip(categories, category, available_categories),
        groups_html=render_groups(category, creatures),
        other_buttons=render_other_buttons(categories, category, available_categories),
        lang_links=render_lang_bar(category),
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output = OUTPUT_DIR / f"{category}.html"
    output.write_text(html_out, encoding="utf-8")
    print(output.relative_to(ROOT))


def main():
    categories = load_categories()
    # ヘビ・カエル・クワガタのようなフルページ形式のカテゴリー(content/category-pages/*.md)と、
    # 図鑑形式で実際にページが作られたカテゴリーだけをリンク可能とし、
    # まだページの無いカテゴリーへのリンクで404が起きないようにする。
    available_categories = {
        parse_markdown(path)[0].get("id", path.stem)
        for path in CATEGORY_PAGES_DIR.glob("*.md")
        if not path.name.endswith((".en.md", ".es.md", ".zh.md"))
    } | {category for category in ZUKAN_CATEGORIES if load_creatures(category)}
    for category in ZUKAN_CATEGORIES:
        render_category(category, categories, available_categories)


if __name__ == "__main__":
    main()