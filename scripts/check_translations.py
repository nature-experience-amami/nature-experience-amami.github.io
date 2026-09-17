"""
翻訳(EN/ES/ZH)まわりの「構造的な壊れ」を機械的にチェックする。

判定できるのはあくまで機械的な壊れ方のみで、翻訳の正確さ・自然さまでは
判定できない(学名や生態の記述が正しいかは、人が原文と読み比べる必要がある)。

チェック内容:
  1. リンク切れ: 全HTMLページのhref/src(相対パスのみ)が実在するファイルを
     指しているか
  2. 翻訳ファイル抜け: 翻訳対応済みカテゴリー(AVAILABLE_CATEGORY_PAGES)の
     生き物なのに、content/creatures/配下に.en.md/.es.md/.zh.mdが無い
  3. 日本語の残存: en/es/zh配下のページで、<style>/<script>の外側に
     ひらがな・カタカナ(全角中点「・」は除く。区切り文字として正当な
     使い方をされるため)が出てきていないか

実行方法: python scripts/check_translations.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT / "content" / "creatures"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_creature_pages_i18n import AVAILABLE_CATEGORY_PAGES  # noqa: E402

LANGS = ["en", "es", "zh"]

LINK_RE = re.compile(r'(?:href|src)="([^"]+)"')
STYLE_RE = re.compile(r'<style.*?</style>', re.DOTALL)
SCRIPT_RE = re.compile(r'<script.*?</script>', re.DOTALL)
# ひらがな・カタカナ(全角中点U+30FBは除く。月の区切りなどに正当に使われる)
KANA_RE = re.compile(r'[぀-ゟ゠-ヺー-ヿ]')


def html_files():
    files = list(ROOT.glob("*.html"))
    files += list((ROOT / "categories").glob("*.html"))
    files += list((ROOT / "creatures").rglob("*.html"))
    for lang in LANGS:
        files += list((ROOT / lang).rglob("*.html"))
    return files


def check_broken_links():
    broken = []
    for f in html_files():
        text = f.read_text(encoding="utf-8", errors="ignore")
        # JSの文字列連結(' + x + ')などをリンクと誤検出しないよう、
        # <script>内は対象から除外する
        text_no_script = SCRIPT_RE.sub("", text)
        for m in LINK_RE.finditer(text_no_script):
            url = m.group(1)
            if not url or url.startswith(("http://", "https://", "mailto:", "tel:", "#", "data:", "javascript:")):
                continue
            path_part = url.split("#")[0].split("?")[0]
            if not path_part:
                continue
            target = (f.parent / path_part).resolve()
            if not target.exists():
                broken.append((f.relative_to(ROOT), url))
    return broken


def check_missing_translation_files():
    missing = []
    for category_dir in sorted(CONTENT_DIR.iterdir()):
        if not category_dir.is_dir() or category_dir.name not in AVAILABLE_CATEGORY_PAGES:
            continue
        ja_files = sorted(p for p in category_dir.glob("*.md") if "." not in p.stem)
        for ja_md in ja_files:
            creature_id = ja_md.stem
            for lang in LANGS:
                translated = category_dir / f"{creature_id}.{lang}.md"
                if not translated.exists():
                    missing.append((category_dir.name, creature_id, lang))
    return missing


def check_leftover_japanese():
    leaks = []
    for lang in LANGS:
        for f in (ROOT / lang).rglob("*.html"):
            text = f.read_text(encoding="utf-8", errors="ignore")
            clean = STYLE_RE.sub("", text)
            clean = SCRIPT_RE.sub("", clean)
            count = len(KANA_RE.findall(clean))
            if count:
                leaks.append((f.relative_to(ROOT), count))
    return leaks


def main():
    print("=== 1. リンク切れチェック ===")
    broken = check_broken_links()
    if broken:
        for f, url in broken:
            print(f"  {f} -> {url}")
    print(f"{len(broken)}件")

    print("\n=== 2. 翻訳ファイル抜けチェック ===")
    missing = check_missing_translation_files()
    if missing:
        for category, creature_id, lang in missing:
            print(f"  {category}/{creature_id}.{lang}.md が存在しません")
    print(f"{len(missing)}件")

    print("\n=== 3. 日本語の残存チェック(EN/ES/ZHページ) ===")
    leaks = check_leftover_japanese()
    if leaks:
        for f, count in sorted(leaks, key=lambda x: -x[1]):
            print(f"  {f}: {count}箇所")
    print(f"{len(leaks)}ファイル")

    total = len(broken) + len(missing) + len(leaks)
    print(f"\n合計: {total}件の要確認項目")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
