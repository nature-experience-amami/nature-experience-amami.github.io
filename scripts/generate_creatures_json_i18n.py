"""
images/creatures/... の写真から、data/creatures.json と同じ形式の
data/creatures.<lang>.json (en/es/zh) を作る。

生き物ごとに content/creatures/カテゴリ/生き物ID.<lang>.md があれば使い、
無ければ(まだ翻訳が無い生き物)トップページには載せない。

実行方法: python scripts/generate_creatures_json_i18n.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_creatures_json import (  # noqa: E402
    IMAGES_DIR, CONTENT_DIR, DATE_RE, IMAGE_EXTS, IGNORED_SPECIES_DIRS,
    MARKDOWN_ID_ALIASES, read_creature_content, months_from_text, species_dirs,
)
from generate_creature_pages_i18n import load_lang, LANGS  # noqa: E402

OUTPUT_DIR = Path("data")


def scan(lang):
    category_names = load_lang(lang)["categories"]
    creatures = []
    for category_dir in sorted(p for p in IMAGES_DIR.iterdir() if p.is_dir()):
        for species_dir in sorted(
            (p for p in species_dirs(category_dir)
             if (category_dir.name, p.name) not in IGNORED_SPECIES_DIRS),
            key=lambda p: p.name,
        ):
            months, photos = set(), []
            for photo in sorted(species_dir.iterdir()):
                if photo.suffix.lower() not in IMAGE_EXTS:
                    continue
                m = DATE_RE.match(photo.stem)
                if m:
                    months.add(int(m.group(2)))
                # <lang>/index.html から直接使えるよう、リポジトリルートから見た
                # パスに "../" を付けて <lang>/ 配下からの相対パスにしておく。
                photos.append("../" + str(photo.relative_to(".")).replace("\\", "/"))
            if not photos:
                continue

            markdown_id = MARKDOWN_ID_ALIASES.get(
                (category_dir.name, species_dir.name), species_dir.name
            )
            translated_path = CONTENT_DIR / category_dir.name / f"{markdown_id}.{lang}.md"
            if not translated_path.exists():
                continue  # まだ翻訳が無い生き物は、この言語のトップページには出さない
            generated_path = Path(lang) / "creatures" / category_dir.name / f"{markdown_id}.html"
            if not generated_path.exists():
                continue  # 翻訳ページが未生成なら出さない
            # こちらも <lang>/ 配下からの相対パス(lang自体のプレフィックスは付けない)
            page_path = f"creatures/{category_dir.name}/{markdown_id}.html"

            frontmatter, description = read_creature_content(translated_path)
            # activity / night_observable は日本語版Markdownにだけ書くので、そちらから読む
            ja_frontmatter, _ = read_creature_content(CONTENT_DIR / category_dir.name / f"{markdown_id}.md")
            name = frontmatter.get("name") or markdown_id
            category_name = category_names.get(category_dir.name, category_dir.name)
            creatures.append({
                "id": markdown_id,
                "name": name,
                "category": category_dir.name,
                "category_name": category_name,
                "months": frontmatter.get("months") or months_from_text(description) or sorted(months),
                "activity": ja_frontmatter.get("activity", ""),
                "night_observable": ja_frontmatter.get("night_observable", False),
                "description": description,
                "photos": photos,
                "page_path": page_path,
            })
    return creatures


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for lang in LANGS:
        data = scan(lang)
        output = OUTPUT_DIR / f"creatures.{lang}.json"
        output.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"{lang}: {len(data)}種のデータを {output} に書き出しました")


if __name__ == "__main__":
    main()
