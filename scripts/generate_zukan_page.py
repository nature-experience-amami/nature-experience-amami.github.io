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
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT_DIR = ROOT / "content" / "creatures"
IMAGES_DIR = ROOT / "images" / "creatures"
CATEGORIES_FILE = ROOT / "content" / "categories.json"
TEMPLATE = ROOT / "templates" / "zukan.html"
OUTPUT_DIR = ROOT / "generated-categories"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}

# 図鑑形式で作るカテゴリー(ヘビ・カエル・クワガタのようなフルページ形式のものは含めない)
ZUKAN_CATEGORIES = ["suisei-konntyuu", "konchu", "kani"]

# 写真フォルダ名がMarkdownのidと違う場合の対応表。(カテゴリ, Markdownのid): 実際の写真フォルダ名
PHOTO_DIR_ALIASES = {
    ("suisei-konntyuu", "okinawa-suji-gengoro"): "gengoro/okinawa-suji-gengoro",
    ("suisei-konntyuu", "tobiiro-gengoro"): "gengoro/tobiiro-gengoro",
    ("suisei-konntyuu", "usuiro-shima-gengoro"): "gengoro/usuiro-shima-gengoro",
    ("suisei-konntyuu", "akahara-ashinaga-mizodoromushi"): "himedoromushi/akahara-ashinaga-mizodoromushi",
    ("suisei-konntyuu", "amami-hababiro-doromusshi"): "himedoromushi/amami-hababiro-doromusshi",
    ("suisei-konntyuu", "amami-mizo-doromushi"): "himedoromushi/amami-mizo-doromushi",
    ("suisei-konntyuu", "amami-yokomizo-doromushi"): "himedoromushi/amami-yokomizo-doromushi",
    ("suisei-konntyuu", "naga-tsuya-doromushi"): "himedoromushi/naga-tsuya-doromushi",
    ("suisei-konntyuu", "nomura-himedoromushi"): "himedoromushi/nomura-himedoromushi",
    ("suisei-konntyuu", "ryuukyuu-munabiro-tuyadoromushi"): "himedoromushi/ryuukyuu-munabiro-tuyadoromushi",
    ("suisei-konntyuu", "satou-kara-himedoromushi"): "himedoromushi/satou-kara-himedoromushi",
    ("suisei-konntyuu", "ueno-tsuya-doromushi"): "himedoromushi/ueno-tsuya-doromushi",
    ("suisei-konntyuu", "kesi-katabiro-amennbo"): "katabiro-amennbo/kesi-katabiro-amennbo",
    ("suisei-konntyuu", "chairo-kesi-katabiro-amennbo"): "katabiro-amennbo/chairo-kesi-katabiro-amennbo",
    ("suisei-konntyuu", "iriomote-kesi-katabiro-amennbo"): "katabiro-amennbo/iriomote-kesi-katabiro-amennbo",
    ("suisei-konntyuu", "tsutsui-nagare-katabiro-amennbo"): "katabiro-amennbo/tsutsui-nagare-katabiro-amennbo",
}

# カテゴリーごとの英語表記(ヒーローのラベル用)。無ければカテゴリーIDをそのまま大文字にする。
ENGLISH_LABELS = {
    "suisei-konntyuu": "AQUATIC INSECTS",
    "konchu": "INSECTS",
    "kani": "CRABS",
}

# カテゴリーごとの紹介文・注意書き。無ければ汎用の文章を使う。
CATEGORY_CONTENT = {
    "suisei-konntyuu": {
        "hero_lead": (
            "田んぼや池、川のふちなど、奄美の水辺にひっそりと暮らす小さな生き物たち。"
            "ゲンゴロウ、ドロムシ、アメンボ――じっくり探すと出会える種類を紹介します。"
        ),
        "about_paragraphs": [
            "水生昆虫は、ヘビやカエルのように1種類ごとの詳しい紹介ページは作らず、"
            "このページの中でまとめて紹介する「図鑑形式」にしています。",
            "種類がとても多く、専門的なグループも多いジャンルのため、"
            "写真や情報が集まった種類から少しずつ追加していきます。",
        ],
        "note": (
            "水生昆虫は繊細で、種類によっては生息数が少ないものもいます。観察は水辺からそっと行い、"
            "採集する場合も持ち帰る数は最小限にとどめましょう。"
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
    "suisei-konntyuu": {
        "order": ["gengoro", "doromushi", "amenbo", "mizumushi", "other"],
        "labels": {
            "gengoro": "ゲンゴロウの仲間",
            "doromushi": "ドロムシの仲間",
            "amenbo": "アメンボの仲間",
            "mizumushi": "ミズムシの仲間",
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
    directory = IMAGES_DIR / category / directory_name
    if not directory.is_dir():
        return []
    return sorted(
        str(path.relative_to(ROOT)).replace("\\", "/")
        for path in directory.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_EXTS
    )


def zukan_tag(danger_text):
    text = (danger_text or "").strip()
    if not text:
        return ""
    tone = "rare" if any(word in text for word in ("レッドリスト", "絶滅危惧", "禁止")) else ""
    css_class = f"zukan-tag {tone}".strip()
    return f'<span class="{css_class}">{escape(text)}</span>'


def load_creatures(category):
    category_dir = CONTENT_DIR / category
    if not category_dir.is_dir():
        return []
    creatures = []
    for md in sorted(category_dir.glob("*.md")):
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
            "name": data.get("name", creature_id),
            "group": data.get("group", "other"),
            "danger": data.get("danger", ""),
            "latin": latin_line,
            "description": description,
            "photos": photos,
        })
    return creatures


def render_card(creature):
    if creature["photos"]:
        image = f'<img src="../{creature["photos"][0]}" alt="{escape(creature["name"])}">'
    else:
        image = '<div class="zukan-placeholder">写真準備中</div>'
    latin_html = f'<div class="zukan-latin">{creature["latin"]}</div>' if creature["latin"] else ""
    tag_html = zukan_tag(creature["danger"])
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


def render_nav(categories, current):
    links = []
    for key, label in categories.items():
        cls = ' class="active"' if key == current else ""
        links.append(f'<a href="{key}.html"{cls}>{escape(label)}</a>')
    return "".join(links)


def render_other_buttons(categories, current):
    buttons = []
    for key, label in categories.items():
        if key == current:
            continue
        buttons.append(f'<a href="{key}.html" class="category-button">{escape(label)} →</a>')
    return "".join(buttons)


def render_category(category, categories):
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
        nav_links=render_nav(categories, category),
        groups_html=render_groups(category, creatures),
        other_buttons=render_other_buttons(categories, category),
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output = OUTPUT_DIR / f"{category}.html"
    output.write_text(html_out, encoding="utf-8")
    print(output.relative_to(ROOT))


def main():
    categories = load_categories()
    for category in ZUKAN_CATEGORIES:
        render_category(category, categories)


if __name__ == "__main__":
    main()
