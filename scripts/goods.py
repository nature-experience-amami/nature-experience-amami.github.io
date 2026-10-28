"""
グッズ（SUZURI のヘビTシャツ）の案内を作る。設定は content/goods.json。

- 対象の言語は goods.json の text にある言語だけ（今は日本語と中国語）。それ以外の言語では何も出さない
- リンク先はグッズページ（goods.html。scripts/generate_goods_page.py が作る日本語のページ）の、その生き物の欄
- goods.html がまだ無いあいだは何も出さない（飛び先が無いリンクを出さないため）
- css/goods.css も、案内を出すページだけで読み込む
- 画像ファイルがまだ無いときは、画像の枠を出さずに文字だけにする
- root は「そのページからサイトのルートへの相対パス」（例: categories/snakes.html なら "../"）
"""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "content" / "goods.json"
CREATURE_CONTENT_DIR = ROOT / "content" / "creatures"

GOODS_PAGE = "goods.html"

_config = None


def config():
    global _config
    if _config is None:
        _config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    return _config


def _escape(value):
    return html.escape(str(value), quote=True)


def _text(lang):
    if not (ROOT / GOODS_PAGE).exists():
        return None
    return config()["text"].get(lang)


def _lang_root(lang, root):
    return root if lang == "ja" else f"{root}{lang}/"


def _creature_name(creature_id, lang):
    category = config()["category"]
    suffix = "" if lang == "ja" else f".{lang}"
    path = CREATURE_CONTENT_DIR / category / f"{creature_id}{suffix}.md"
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8")
    if text.startswith("---"):
        for line in text.split("---", 2)[1].splitlines():
            if line.startswith("name:"):
                return line.split(":", 1)[1].strip()
    return None


def _image_html(t, root, css_class):
    image = config().get("image")
    if not image or not (ROOT / image).exists():
        return ""
    return (
        f'<div class="{css_class}"><img src="{_escape(root + image)}" '
        f'alt="{_escape(t["image_alt"])}" loading="lazy"></div>'
    )


def _goods_attrs(root, anchor):
    """グッズページ（日本語版はサイトのルートにある）の、その欄へのリンク。"""
    return f'href="{_escape(f"{root}{GOODS_PAGE}#{anchor}")}"'


def _notice_html(t):
    return f'<p class="goods-notice">{_escape(t["notice"])}</p>' if t.get("notice") else ""


def banner_html(lang, category, root):
    """カテゴリー一覧ページ（ヘビ）のバナー。"""
    t = _text(lang)
    if not t or category != config()["category"]:
        return ""
    chips = []
    for creature_id in config()["creatures"]:
        name = _creature_name(creature_id, lang)
        page = f"creatures/{category}/{creature_id}.html"
        if not name or not (ROOT / _lang_root(lang, "") / page).exists():
            continue
        chips.append(f'<a href="{_escape(_lang_root(lang, root) + page)}">{_escape(name)}</a>')
    image = _image_html(t, root, "goods-image")
    return (
        f'<section class="goods-section" id="goods"><div class="goods-banner{"" if image else " no-image"}">'
        f"{image}<div class=\"goods-body\">"
        f'<p class="goods-label">GOODS</p>'
        f'<h2 class="goods-title">{_escape(t["banner_title"])}</h2>'
        f'<p class="goods-lead">{_escape(t["banner_lead"])}</p>'
        f'<div class="goods-chips">{"".join(chips)}</div>'
        f'<a class="goods-button" {_goods_attrs(root, category)}>{_escape(t["button"])}</a>'
        f"{_notice_html(t)}</div></div></section>"
    )


def note_html(lang, category, creature_id, name, root):
    """個別ページの小さな案内。Tシャツに載っている種だけ。name はエスケープ前の名前。"""
    t = _text(lang)
    if not t or category != config()["category"] or creature_id not in config()["creatures"]:
        return ""
    image = _image_html(t, root, "goods-note-image")
    return (
        f'<aside class="goods-note">{image}<div class="goods-note-text">'
        f'<strong>{_escape(t["note_title"].format(name=name))}</strong>'
        f'<span>{_escape(t["note_sub"])}</span>{_notice_html(t)}</div>'
        f'<a class="goods-note-link" {_goods_attrs(root, creature_id)}>{_escape(t["note_link"])}</a></aside>'
    )


def footer_html(lang, root):
    """フッターのリンク。footer_to_banner が true の言語は、注意書きのあるヘビ一覧のバナーへ飛ばす。"""
    t = _text(lang)
    if not t:
        return ""
    if t.get("footer_to_banner"):
        href = _escape(f'{_lang_root(lang, root)}categories/{config()["category"]}.html#goods')
        attrs = f'href="{href}"'
    else:
        attrs = f'href="{_escape(root + GOODS_PAGE)}"'
    return f'<p class="footer-goods"><a {attrs}>{_escape(t["footer_link"])}</a></p>'


def css_link(lang, root):
    """案内を出す言語のページだけで css/goods.css を読み込む。"""
    if not _text(lang):
        return ""
    return f'<link rel="stylesheet" href="{_escape(root)}css/goods.css">\n'
