"""
全ページ共通のOGPタグ(ThreadsやLINEでリンクを貼ったときの写真・説明)を作る。

- テンプレートの description の次の行に置いた目印 <!-- OGP --> を、タグに置き換える。
- og:title / og:description は、できあがったページの <title> と meta description を
  そのまま使う(文言を二重に書かないため。テンプレートを直せば自動でそろう)。
- og:image は、生き物の個別ページはそのページのメイン写真(photos[0])、
  それ以外と写真のない種はサイトの代表写真(DEFAULT_IMAGE)。
"""
import re
from urllib.parse import quote

BASE_URL = "https://nature-experience-amami.github.io"
SITE_NAME = "Nature Experience Amami"
# サイトの代表写真(2026-10-12 オーナーが選定)
DEFAULT_IMAGE = "images/creatures/mammals/amami-kuro-usagi/amami-kuro-usagi_000002_20250301_20.jpg"
OG_LOCALES = {"ja": "ja_JP", "en": "en_US", "es": "es_ES", "zh": "zh_CN"}
MARKER = "<!-- OGP -->"

TITLE_RE = re.compile(r"<title>(.*?)</title>", re.S)
DESCRIPTION_RE = re.compile(r'<meta name="description" content="([^"]*)">')


def absolute_url(rel_path):
    """リポジトリのルートからのパスを公開URLにする。トップ(index.html)はフォルダのURLにする。"""
    if rel_path == "index.html" or rel_path.endswith("/index.html"):
        rel_path = rel_path[: -len("index.html")]
    return f"{BASE_URL}/{quote(rel_path)}"


def ogp_tags(page, rel_path, lang, image=None):
    # ページ内の title と description はすでにHTMLエスケープ済みなので、そのまま使う
    title = TITLE_RE.search(page).group(1).strip()
    description = DESCRIPTION_RE.search(page).group(1)
    return "\n".join([
        f'<meta property="og:title" content="{title}">',
        f'<meta property="og:description" content="{description}">',
        f'<meta property="og:url" content="{absolute_url(rel_path)}">',
        f'<meta property="og:image" content="{absolute_url(image or DEFAULT_IMAGE)}">',
        '<meta property="og:type" content="website">',
        f'<meta property="og:site_name" content="{SITE_NAME}">',
        f'<meta property="og:locale" content="{OG_LOCALES[lang]}">',
        '<meta name="twitter:card" content="summary_large_image">',
    ])


def insert_ogp(page, rel_path, lang, image=None):
    """ページの目印 <!-- OGP --> をOGPタグに置き換える。目印がなければ止める(付け忘れに気づくため)。"""
    if MARKER not in page:
        raise ValueError(f"OGPの目印 {MARKER} がテンプレートにありません: {rel_path}")
    return page.replace(MARKER, ogp_tags(page, rel_path, lang, image), 1)
