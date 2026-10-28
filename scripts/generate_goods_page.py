"""
グッズページ（goods.html）と、トップページ（index.html）のおすすめ欄を作る。日本語版だけ。

- 商品は data/suzuri-products.json（scripts/fetch_suzuri_goods.py が毎日 SUZURI から取る）
- 生き物とのひも付け・セット柄・ロゴ・おすすめは content/goods-creatures.json
- 生き物の名前は content/creatures/カテゴリー/ID.md の name: を使う
- index.html は、目印 <!-- GOODS-PICKS:START --> と <!-- GOODS-PICKS:END --> のあいだだけを書き換える
- 商品のファイルが無い・0件のときは、goods.html を作らず、トップのおすすめ欄も空にする

実行方法: python scripts/generate_goods_page.py
"""
import html
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from category_header import render_category_strip, MASTER_CATEGORY_ORDER  # noqa: E402
from fetch_suzuri_goods import https_url, IMAGE_HOST  # noqa: E402
from seo_head import insert_ogp  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
PRODUCTS_PATH = ROOT / "data" / "suzuri-products.json"
SETTINGS_PATH = ROOT / "content" / "goods-creatures.json"
CREATURE_CONTENT_DIR = ROOT / "content" / "creatures"
CATEGORY_NAMES = ROOT / "content" / "categories.json"
TEMPLATE = ROOT / "templates" / "goods.html"
OUTPUT = ROOT / "goods.html"
INDEX = ROOT / "index.html"
PICKS_START = "<!-- GOODS-PICKS:START -->"
PICKS_END = "<!-- GOODS-PICKS:END -->"
OTHER = "other"


def escape(value):
    return html.escape(str(value), quote=True)


def katakana(text):
    return "".join(chr(ord(c) + 0x60) if "ぁ" <= c <= "ゖ" else c for c in text)


def creature_names():
    """{カタカナの名前: (カテゴリー, ID, 名前)} と {(カテゴリー, ID): 名前}"""
    by_name, by_key = {}, {}
    for path in sorted(CREATURE_CONTENT_DIR.glob("*/*.md")):
        if path.name.count(".") > 1:  # 翻訳版（.en.md など）は使わない
            continue
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---"):
            continue
        meta = {}
        for line in text.split("---", 2)[1].splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                meta[key.strip()] = value.strip()
        name = meta.get("name")
        if not name:
            continue
        key = (path.parent.name, meta.get("id") or path.stem)
        by_key[key] = name
        by_name[katakana(name)] = (key[0], key[1], name)
    return by_name, by_key


def load_products():
    if not PRODUCTS_PATH.exists():
        return []
    products = json.loads(PRODUCTS_PATH.read_text(encoding="utf-8")).get("products") or []
    clean = []
    for p in products:
        # 念のため、ページに出す前にもう一度URLを確かめる
        url = https_url(p.get("url"), "suzuri.jp", subdomains=True)
        image = https_url(p.get("image"), IMAGE_HOST)
        if isinstance(p.get("id"), int) and url and image:
            clean.append({**p, "url": url, "image": image})
    return clean


def classify(products, settings, by_name, by_key):
    """商品ごとに、どの種類（カテゴリー）・どの生き物かを決める。"""
    logo_ids = set(settings.get("logo_product_ids", []))
    hidden = set(settings.get("hidden_product_ids", []))
    sets = settings.get("sets", {})
    aliases = settings.get("aliases", {})
    entries, unmatched = [], []
    for p in products:
        if p["id"] in hidden:
            continue
        title = p.get("material_title", "")
        entry = {**p, "category": OTHER, "creature_id": "", "name": title, "is_set": False,
                 "is_logo": p["id"] in logo_ids}
        if entry["is_logo"]:
            entry["name"] = "Nature-Experience ロゴ"
        elif title in sets:
            entry.update(category=sets[title], is_set=True)
        elif title in aliases:
            category, creature_id = aliases[title].split("/", 1)
            entry.update(category=category, creature_id=creature_id,
                         name=by_key.get((category, creature_id), title))
        elif katakana(title) in by_name:
            category, creature_id, name = by_name[katakana(title)]
            entry.update(category=category, creature_id=creature_id, name=name)
        else:
            unmatched.append(title)
        entries.append(entry)
    return entries, unmatched


def yen(value):
    return f"¥{value:,}" if isinstance(value, int) else ""


def card_html(entry, anchor=False, css_class="goods-card"):
    id_attr = f' id="{escape(entry["creature_id"])}"' if anchor and entry["creature_id"] else ""
    badge = '<span class="goods-badge">セット柄</span>' if entry["is_set"] else ""
    return (
        f'<a class="{css_class}"{id_attr} href="{escape(entry["url"])}" target="_blank" rel="noopener">'
        f'<span class="goods-photo"><img src="{escape(entry["image"])}" alt="{escape(entry["name"])}のTシャツ" '
        f'loading="lazy" decoding="async" referrerpolicy="no-referrer" width="400" height="400"></span>'
        f'<span class="goods-name">{escape(entry["name"])}{badge}</span>'
        f'<span class="goods-meta">{escape(entry.get("item_label") or "Tシャツ")}　{yen(entry.get("price_with_tax"))}</span>'
        f'<span class="goods-go">SUZURIで見る ↗</span></a>'
    )


def grouped(entries):
    """種類ごとに並べる。セット柄を先頭に、同じ生き物はまとめて、だいたい登録順に。"""
    categories = json.loads(CATEGORY_NAMES.read_text(encoding="utf-8"))
    order = [c for c in MASTER_CATEGORY_ORDER if c in categories] + [OTHER]
    groups = []
    for category in order:
        items = [e for e in entries if e["category"] == category and not e["is_logo"]]
        if not items:
            continue
        first_id = {}
        for e in sorted(items, key=lambda e: e["id"]):
            first_id.setdefault(e["creature_id"] or e["name"], e["id"])
        items.sort(key=lambda e: (not e["is_set"], first_id[e["creature_id"] or e["name"]], e["id"]))
        label = categories.get(category, "その他")
        groups.append((category, label, items))
    return groups


def render_page(entries):
    groups = grouped(entries)
    categories = json.loads(CATEGORY_NAMES.read_text(encoding="utf-8"))
    chips = "".join(
        f'<a href="#{escape(cat)}">{escape(label)}<small>{len(items)}</small></a>' for cat, label, items in groups
    )
    sections = []
    for category, label, items in groups:
        seen, cards = set(), []
        for e in items:
            first = e["creature_id"] and e["creature_id"] not in seen
            seen.add(e["creature_id"])
            cards.append(card_html(e, anchor=first))
        zukan = (
            f'<a class="goods-zukan" href="categories/{escape(category)}.html">{escape(label)}の図鑑 →</a>'
            if (ROOT / "categories" / f"{category}.html").exists() else ""
        )
        sections.append(
            f'<section class="goods-group" id="{escape(category)}" aria-labelledby="h-{escape(category)}">'
            f'<div class="goods-group-head"><h2 id="h-{escape(category)}">{escape(label)}</h2>'
            f'<span class="goods-count">{len(items)}点</span>{zukan}</div>'
            f'<div class="goods-row">{"".join(cards)}</div></section>'
        )
    logos = [e for e in entries if e["is_logo"]]
    logo_html = "".join(card_html(e, css_class="goods-card goods-logo") for e in logos)
    available = {p.stem for p in (ROOT / "categories").glob("*.html")}
    page = TEMPLATE.read_text(encoding="utf-8").format(
        chips=chips,
        logo=f'<div class="goods-logo-wrap">{logo_html}</div>' if logo_html else "",
        groups="".join(sections),
        count=len(entries),
        category_strip=render_category_strip(categories, None, available, href_prefix="categories/"),
    )
    return insert_ogp(page, "goods.html", "ja")


def render_picks(entries, settings):
    """トップのおすすめ欄。ロゴ → 印を付けた商品の順。印が無ければ新しい順で4点。"""
    by_id = {e["id"]: e for e in entries}
    picks = [by_id[i] for i in settings.get("logo_product_ids", []) if i in by_id]
    featured = [by_id[i] for i in settings.get("featured_product_ids", []) if i in by_id]
    if not featured:
        featured = sorted((e for e in entries if not e["is_logo"]),
                          key=lambda e: e.get("published_at", ""), reverse=True)[:4]
    picks += featured
    if not picks:
        return ""
    cards = "".join(card_html(e, css_class="goods-card") for e in picks)
    return (
        '<link rel="stylesheet" href="css/goods.css">'
        '<section class="goods-top" aria-label="グッズの案内"><div class="goods-top-inner">'
        '<p class="goods-label">GOODS</p><h2>奄美の生き物Tシャツ</h2>'
        '<p class="goods-top-lead">ツアーで出会った生き物を、Tシャツで持ち帰りませんか。SUZURIで販売しています。</p>'
        f'<div class="goods-row goods-picks">{cards}</div>'
        f'<a class="goods-button" href="goods.html">グッズ一覧を見る（{len(entries)}点）→</a>'
        '</div></section>'
    )


def update_index(block):
    text = INDEX.read_text(encoding="utf-8")
    # 目印がそれぞれ1回ずつ、START が先にあるときだけ書き換える（手で動かした・消したときは止める）
    start, end = text.find(PICKS_START), text.find(PICKS_END)
    if text.count(PICKS_START) != 1 or text.count(PICKS_END) != 1 or end < start:
        raise SystemExit(f"index.html の目印 {PICKS_START} / {PICKS_END} が1回ずつありません")
    new = text[: start + len(PICKS_START)] + block + text[end:]
    if new != text:
        INDEX.write_text(new, encoding="utf-8")
        print("index.html（おすすめ欄）")


def main():
    settings = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
    by_name, by_key = creature_names()
    entries, unmatched = classify(load_products(), settings, by_name, by_key)
    for title in unmatched:
        print(f"※ 生き物にひも付けられなかった商品（「その他」に入れました）: {title}")
    if not entries:
        print("商品が無いので、goods.html は作らず、トップのおすすめ欄を空にします")
        update_index("")
        return
    OUTPUT.write_text(render_page(entries), encoding="utf-8")
    print(OUTPUT.relative_to(ROOT))
    update_index(render_picks(entries, settings))


if __name__ == "__main__":
    main()
