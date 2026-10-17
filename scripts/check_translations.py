"""
翻訳(EN/ES/ZH)まわりの「構造的な壊れ」を機械的にチェックする。

判定できるのはあくまで機械的な壊れ方のみで、翻訳の正確さ・自然さまでは
判定できない(学名や生態の記述が正しいかは、人が原文と読み比べる必要がある)。

チェック内容:
  1. リンク切れ: 全HTMLページのhref/src(相対パスのみ)が実在するファイルを
     指しているか
  2. 翻訳ファイル抜け: 翻訳対応済みカテゴリー(AVAILABLE_CATEGORY_PAGES)の
     生き物なのに、content/creatures/配下に.en.md/.es.md/.zh.mdが無い
  3. 日本語の残存: en/es/zh配下のページで、<style>/<script>/HTMLコメントの外側に
     ひらがな・カタカナ(全角中点「・」は除く。区切り文字として正当な
     使い方をされるため)が出てきていないか
  4. danger: 日本語版の danger が content/i18n/translation_rules.json の対応表に
     あるか、翻訳mdの danger が対応表の訳と同じか
  5. 中国語で使わない言葉(translation_rules.json の zh_avoid)
  6. 簡体字の簡易チェック(translation_rules.json の zh_simplified_chars。よく出る字だけ)
     5・6は .zh.md・content/i18n/zh.json・zh/ のHTML(<style>/<script>/コメントの外側)を見る
  7. frontmatter: id・category が日本語版と同じか。months・group は翻訳に書いてあれば
     日本語版と同じか(生成スクリプトは日本語版の値を使うので、無くてもよい)。
     activity・night_observable を翻訳に書いていないか
  8. 1行目の学名(最初の *…*)が日本語版と同じか
  9. 本文の数値: 単位つきの数(mm・cm・kg など)と年(1500〜2099)が日本語版と同じか。
     書き方の違いで誤検知しやすいので「要確認」として知らせるだけ。
     書き方の違いだけと確認済みの箇所は translation_rules.json の
     number_check_exceptions に1件ずつ登録する(登録した文が翻訳に無くなったら知らせる)

結果は「エラー(必ず直す)」と「要確認(人が見る)」に分けて出す。
エラーが1件でもあれば終了コード1、要確認だけなら0。

実行方法: python scripts/check_translations.py
"""
import collections
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT / "content" / "creatures"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_creature_pages_i18n import AVAILABLE_CATEGORY_PAGES  # noqa: E402
from generate_creature_pages import parse_markdown  # noqa: E402

RULES = json.loads((ROOT / "content" / "i18n" / "translation_rules.json").read_text(encoding="utf-8"))

LANGS = ["en", "es", "zh"]

LINK_RE = re.compile(r'(?:href|src)="([^"]+)"')
STYLE_RE = re.compile(r'<style.*?</style>', re.DOTALL)
SCRIPT_RE = re.compile(r'<script.*?</script>', re.DOTALL)
# HTMLコメントは画面に出ないので、日本語の残存チェックでは数えない
COMMENT_RE = re.compile(r'<!--.*?-->', re.DOTALL)
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
            clean = COMMENT_RE.sub("", clean)
            count = len(KANA_RE.findall(clean))
            if count:
                leaks.append((f.relative_to(ROOT), count))
    return leaks


def iter_translation_pairs():
    """(日本語版mdのパス, 言語, 翻訳mdのパス) を、翻訳mdがあるものだけ返す。"""
    for ja_md in sorted(CONTENT_DIR.glob("*/*.md")):
        if "." in ja_md.stem:
            continue
        for lang in LANGS:
            translated = ja_md.with_name(f"{ja_md.stem}.{lang}.md")
            if translated.exists():
                yield ja_md, lang, translated


def rel(path):
    return path.relative_to(ROOT)


def check_danger():
    errors = []
    table = RULES["danger"]
    for ja_md in sorted(CONTENT_DIR.glob("*/*.md")):
        if "." in ja_md.stem:
            continue
        ja_danger = (parse_markdown(ja_md)[0].get("danger") or "").strip()
        if ja_danger and ja_danger not in table:
            errors.append(f"{rel(ja_md)}: 日本語の danger「{ja_danger}」が対応表(translation_rules.json)にありません")
    for ja_md, lang, translated in iter_translation_pairs():
        ja_danger = (parse_markdown(ja_md)[0].get("danger") or "").strip()
        tr_danger = (parse_markdown(translated)[0].get("danger") or "").strip()
        if not ja_danger:
            if tr_danger:
                errors.append(f"{rel(translated)}: 日本語版に danger が無いのに、翻訳に「{tr_danger}」があります")
            continue
        expected = table.get(ja_danger, {}).get(lang)
        if expected is not None and tr_danger != expected:
            errors.append(f"{rel(translated)}: danger「{tr_danger}」→ 対応表では「{expected}」")
    return errors


def zh_texts():
    """中国語の文(画面に出る部分)を (パス, 本文) で返す。"""
    files = sorted(CONTENT_DIR.glob("*/*.zh.md")) + sorted((ROOT / "content").glob("category-pages/*.zh.md"))
    for f in files:
        yield f, f.read_text(encoding="utf-8")
    zh_json = ROOT / "content" / "i18n" / "zh.json"
    # \uXXXX で書かれているので、読み込んでから文字列に戻す
    yield zh_json, json.dumps(json.loads(zh_json.read_text(encoding="utf-8")), ensure_ascii=False)
    for f in sorted((ROOT / "zh").rglob("*.html")):
        text = f.read_text(encoding="utf-8", errors="ignore")
        text = STYLE_RE.sub("", text)
        text = SCRIPT_RE.sub("", text)
        text = COMMENT_RE.sub("", text)
        yield f, text


def snippet(text, start, end):
    return text[max(0, start - 12):end + 8].replace("\n", " ")


def check_zh_words():
    errors = []
    for path, text in zh_texts():
        for rule in RULES["zh_avoid"]:
            word = rule["word"]
            for m in re.finditer(re.escape(word), text):
                if any(text.startswith(exc, m.start()) for exc in rule.get("except", [])):
                    continue
                errors.append(f"{rel(path)}: 「{word}」→「{rule['use']}」 …{snippet(text, m.start(), m.end())}…")
    return errors


def check_zh_simplified():
    errors = []
    chars_re = re.compile("[" + re.escape(RULES["zh_simplified_chars"]) + "]")
    for path, text in zh_texts():
        for m in chars_re.finditer(text):
            errors.append(f"{rel(path)}: 簡体字「{m.group()}」 …{snippet(text, m.start(), m.end())}…")
    return errors


def check_frontmatter():
    errors = []
    for ja_md, lang, translated in iter_translation_pairs():
        ja, tr = parse_markdown(ja_md)[0], parse_markdown(translated)[0]
        for key in ("id", "category"):
            if ja.get(key) != tr.get(key):
                errors.append(f"{rel(translated)}: {key} が日本語版と違います(日本語版 {ja.get(key)} / 翻訳 {tr.get(key)})")
        for key in ("months", "group"):
            if key in tr and tr.get(key) != ja.get(key):
                errors.append(f"{rel(translated)}: {key} が日本語版と違います(日本語版 {ja.get(key)} / 翻訳 {tr.get(key)})。合わせるか、翻訳から消す")
        for key in ("activity", "night_observable"):
            if key in tr:
                errors.append(f"{rel(translated)}: {key} は翻訳に書きません(日本語版だけに書く)")
    return errors


def first_scientific_name(body):
    first_paragraph = re.split(r"\n\s*\n", body.strip())[0]
    m = re.search(r"\*([^*]+)\*", first_paragraph)
    return " ".join(m.group(1).split()) if m else None


def check_scientific_name():
    errors = []
    for ja_md, lang, translated in iter_translation_pairs():
        ja_name = first_scientific_name(parse_markdown(ja_md)[1])
        tr_name = first_scientific_name(parse_markdown(translated)[1])
        if ja_name != tr_name:
            errors.append(f"{rel(translated)}: 1行目の学名が日本語版と違います(日本語版 {ja_name} / 翻訳 {tr_name})")
    return errors


UNIT = (r"(?:mm|cm|km|kg|g|m|%|％|毫米|公分|公尺|公里|公斤|千克|公克|克|米"
        r"|metros?|meters?|metres?|kilogramos?|gramos?)(?![a-zA-Z])")
RANGE_SEP = r"\s*(?:-|〜|～|–|至|到|a|to|y|and)\s*"
NUMBER_WITH_UNIT_RE = re.compile(r"(\d+(?:\.\d+)?(?:" + RANGE_SEP + r"\d+(?:\.\d+)?)*)\s*" + UNIT)
YEAR_RE = re.compile(r"(?<![\d.])(1[5-9]\d\d|20\d\d)(?!\d)(?!\.\d)")


def body_numbers(body, lang):
    # 桁区切り(7,000)をそろえる。スペイン語は 7.000 が桁区切り、3,5 が小数点
    body = re.sub(r"(?<=\d),(?=\d{3}(?!\d))", "", body)
    if lang == "es":
        body = re.sub(r"(?<=\d)\.(?=\d{3}(?!\d))", "", body)
        body = re.sub(r"(?<=\d),(?=\d)", ".", body)
    numbers = []
    for m in NUMBER_WITH_UNIT_RE.finditer(body):
        numbers += re.findall(r"\d+(?:\.\d+)?", m.group(1))
    numbers += YEAR_RE.findall(body)
    return collections.Counter(numbers)


def check_body_numbers():
    warnings = []
    exceptions = collections.defaultdict(list)
    for exc in RULES.get("number_check_exceptions", []):
        exceptions[exc["file"]].append(exc)
    for ja_md, lang, translated in iter_translation_pairs():
        ja_numbers = body_numbers(parse_markdown(ja_md)[1], "ja")
        tr_body = parse_markdown(translated)[1]
        tr_numbers = body_numbers(tr_body, lang)
        for exc in exceptions.get(str(rel(translated)), []):
            if exc["text"] in tr_body:
                # 確認済みの書き方の違い: この文があれば、日本語版の数値は翻訳にもあるものとして扱う
                tr_numbers[exc["ja_number"]] += 1
            else:
                warnings.append(f"{rel(translated)}: 確認済みの例外の文「{exc['text']}」が見つかりません。"
                                "translation_rules.json の number_check_exceptions を見直す")
        missing, extra = ja_numbers - tr_numbers, tr_numbers - ja_numbers
        if missing or extra:
            parts = []
            if missing:
                parts.append("日本語版にあって翻訳に無い: " + ", ".join(sorted(missing.elements())))
            if extra:
                parts.append("翻訳にだけある: " + ", ".join(sorted(extra.elements())))
            warnings.append(f"{rel(translated)}: " + " / ".join(parts))
    return warnings


def print_section(title, items):
    print(f"=== {title} ===")
    for item in items:
        print(f"  {item}")
    print(f"{len(items)}件\n")


def main():
    broken = [f"{f} -> {url}" for f, url in check_broken_links()]
    missing = [f"{c}/{i}.{lang}.md が存在しません" for c, i, lang in check_missing_translation_files()]
    leaks = [f"{f}: {n}箇所" for f, n in sorted(check_leftover_japanese(), key=lambda x: -x[1])]

    errors = [
        ("1. リンク切れ", broken),
        ("2. 翻訳ファイル抜け", missing),
        ("3. 日本語(かな)の残存(EN/ES/ZHページ)", leaks),
        ("4. danger が対応表と違う", check_danger()),
        ("5. 中国語で使わない言葉", check_zh_words()),
        ("6. 簡体字(簡易チェック)", check_zh_simplified()),
        ("7. frontmatter が日本語版と違う", check_frontmatter()),
        ("8. 1行目の学名が日本語版と違う", check_scientific_name()),
    ]
    warnings = [
        ("9. 本文の数値(単位つきの数・年)が日本語版と違う", check_body_numbers()),
    ]

    print("##### エラー(必ず直す) #####\n")
    for title, items in errors:
        print_section(title, items)
    print("##### 要確認(人が見る。書き方の違いで出ることがある) #####\n")
    for title, items in warnings:
        print_section(title, items)

    error_total = sum(len(items) for _, items in errors)
    warning_total = sum(len(items) for _, items in warnings)
    print(f"合計: エラー {error_total}件 / 要確認 {warning_total}件")
    return 1 if error_total else 0


if __name__ == "__main__":
    sys.exit(main())
