"""
サイト内のHTMLページを走査してsitemap.xmlを作る。

- ルート直下 / en/ / es/ / zh/ 配下の公開ページ(index, tour, contact, highlights,
  categories/*, creatures/**/*)のみ対象。
- <meta name="robots" content="noindex...">を含むページ(カテゴリー名変更前の
  リダイレクト用スタブページなど)は除外。
- 管理ツール(amami-tool.html, customer-app/)やInstagram用ランディングページ
  (instagram-campaign/)はそもそも走査対象(index/tour/contact/highlights/
  categories/creatures)に含まれないため対象外。

実行方法: python scripts/generate_sitemap.py
"""
import re
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
BASE_URL = "https://nature-experience-amami.github.io"
OUTPUT = ROOT / "sitemap.xml"

LANG_DIRS = ["", "en", "es", "zh"]
TOP_LEVEL_PAGES = ["index.html", "tour.html", "contact.html", "highlights.html"]

NOINDEX_RE = re.compile(r'<meta\s+name="robots"[^>]*noindex', re.IGNORECASE)


def is_noindex(path):
    text = path.read_text(encoding="utf-8", errors="ignore")
    return bool(NOINDEX_RE.search(text))


def collect_urls():
    urls = []
    for lang in LANG_DIRS:
        base = ROOT / lang if lang else ROOT

        for name in TOP_LEVEL_PAGES:
            path = base / name
            if path.exists() and not is_noindex(path):
                urls.append(url_for(lang, name))

        for section in ["categories", "creatures"]:
            section_dir = base / section
            if not section_dir.exists():
                continue
            for path in sorted(section_dir.rglob("*.html")):
                if is_noindex(path):
                    continue
                rel = path.relative_to(base).as_posix()
                urls.append(url_for(lang, rel))

    return urls


def url_for(lang, rel_path):
    parts = [lang, rel_path] if lang else [rel_path]
    joined = "/".join(p for p in parts if p)
    return f"{BASE_URL}/{quote(joined)}"


def main():
    urls = collect_urls()
    entries = "\n".join(
        f"  <url>\n    <loc>{url}</loc>\n  </url>" for url in urls
    )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{entries}\n"
        "</urlset>\n"
    )
    OUTPUT.write_text(xml, encoding="utf-8")
    print(f"{len(urls)}件のURLを{OUTPUT.relative_to(ROOT)}に書き出しました")


if __name__ == "__main__":
    main()
