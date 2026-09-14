"""
カテゴリー帯(ヘッダー内の横スクロールカテゴリーナビ)を、カテゴリー一覧ページ・
図鑑ページで共通の並び順・共通のロジックで生成するための共有モジュール。

表示順序と「現在地/リンク可能/準備中」の判定ロジックをここ1箇所にまとめ、
generate_category_pages.py・generate_zukan_page.py(および将来のi18n版)から
共通で呼び出す。「代表的な生き物」はカテゴリーではなくメインナビ側の項目
なので、このマスターリストには含めない。

実行方法: このファイル単体では実行しない(他スクリプトからimportして使う)
"""
import html

# 表示順のマスターリスト。全カテゴリー/図鑑ページでこの順序に統一する。
MASTER_CATEGORY_ORDER = [
    "hebi", "kaeru", "kuwagata", "tori", "honyuurui",
    "tokage", "suisei-konntyuu", "konchu", "kai", "sonota",
]


def escape(value):
    return html.escape(str(value), quote=True)


def render_category_strip(categories, current, available, href_suffix=".html", href_prefix=""):
    """categories: {カテゴリーID: 表示名} の辞書(content/categories.json相当)。
    current: 現在表示中のカテゴリーID。
    available: リンク可能な(実際にページがある)カテゴリーIDの集合。
    href_prefix/href_suffix: リンク先の組み立てに使う(ページの階層により変える)。

    戻り値はカテゴリー帯の中身のHTML文字列(<a>/<span class="cat-item ...">を並べたもの)。
    実装済み(現在地・リンク可能)のカテゴリーを左側に、準備中のカテゴリーを右側に
    まとめる。各グループ内の並び順はMASTER_CATEGORY_ORDERに従う。
    """
    ready_items = []
    soon_items = []
    for category_id in MASTER_CATEGORY_ORDER:
        name = categories.get(category_id)
        if not name:
            continue
        escaped_name = escape(name)
        if category_id == current:
            ready_items.append(
                f'<span class="cat-item current" id="currentCat">{escaped_name}</span>'
            )
        elif category_id in available:
            ready_items.append(
                f'<a href="{href_prefix}{category_id}{href_suffix}" class="cat-item">{escaped_name}</a>'
            )
        else:
            soon_items.append(
                f'<span class="cat-item soon">{escaped_name}(準備中)</span>'
            )
    return "".join(ready_items) + "".join(soon_items)
