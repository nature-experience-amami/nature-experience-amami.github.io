"""
SUZURI の自分の商品から、公開中のTシャツを取得して data/suzuri-products.json に保存する。
GitHub Actions（.github/workflows/fetch-suzuri-goods.yml）が1日1回動かす。

- APIキーは環境変数 SUZURI_API_KEY から読む（GitHub Secrets）。キーはログに出さない
- APIキーで取ると非公開の商品も返ってくるので、published が true のものだけを残す
- Actions のログは誰でも見られるので、非公開の商品は件数だけを出し、名前は出さない
- 取得に失敗した・0件だったときは、ファイルを書き換えずにエラーで終わる（ページが空になるのを防ぐ）
- 毎日 commit が増えないよう、取得日時はファイルに入れず、並び順も id で固定する
"""
import json
import re
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT / "data" / "suzuri-products.json"
API_BASE = "https://suzuri.jp/api/v1"
PAGE_LIMIT = 50
MAX_PAGES = 40  # 50件×40ページ＝2000件。ここを超えたら止める（無限ループよけ）
# URLに入っていたら外す文字（\ はブラウザが / と読むので、ホストの確認をすり抜けられる）
BAD_URL_CHARS = re.compile(r'[\\\s"\'<>`\x00-\x1f\x7f]')


class NoRedirect(urllib.request.HTTPRedirectHandler):
    """リダイレクトについて行かない（APIキーが別のホストへ送られないように）。"""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise urllib.error.HTTPError(req.full_url, code, "リダイレクトは受け付けません", headers, fp)


OPENER = urllib.request.build_opener(NoRedirect)
# 商品画像の置き場所（2026-10-28 の試し運転で、45件すべてがこのホストだった）
IMAGE_HOST = "lens.suzuri.jp"


def is_tshirt(item):
    name = (item.get("name") or "").lower()
    humanize = item.get("humanizeName") or ""
    return "t-shirt" in name or "Tシャツ" in humanize


def api_get(path, key, params=None):
    url = f"{API_BASE}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {key}",
        "Accept": "application/json",
        "User-Agent": "nature-experience-amami-goods/1.0",
    })
    for attempt in range(3):
        try:
            with OPENER.open(request, timeout=30) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            # 5xx だけ少し待ってやり直す。401 などはすぐ止める
            if error.code >= 500 and attempt < 2:
                time.sleep(5 * (attempt + 1))
                continue
            raise SystemExit(f"SUZURI API エラー: {path} が HTTP {error.code} を返しました")
        except urllib.error.URLError as error:
            if attempt < 2:
                time.sleep(5 * (attempt + 1))
                continue
            raise SystemExit(f"SUZURI API に接続できませんでした: {path}（{error.reason}）")


def https_url(value, allowed_host, subdomains=False):
    """https で、決まったホストのURLだけを通す（ページに出すときの安全のため）。
    subdomains が True なら、そのホストの下のホスト（例: xxx.suzuri.jp）も通す。"""
    if not isinstance(value, str) or BAD_URL_CHARS.search(value):
        return ""
    parsed = urllib.parse.urlparse(value)
    host = parsed.hostname or ""
    if parsed.scheme != "https" or not host or parsed.username or parsed.password or parsed.port:
        return ""
    if host != allowed_host and not (subdomains and host.endswith("." + allowed_host)):
        return ""
    return value


def main():
    key = os.environ.get("SUZURI_API_KEY", "").strip()
    if not key:
        raise SystemExit("SUZURI_API_KEY が設定されていません（GitHub Secrets を確認してください）")

    user_data = api_get("/user", key)
    user = user_data.get("user") or user_data
    user_id = user.get("id")
    if not user_id:
        raise SystemExit("/user から自分のユーザーIDを取れませんでした")
    print(f"SUZURI ユーザー名: {user.get('name')}")

    products = []
    for page in range(MAX_PAGES):
        data = api_get("/products", key, {"userId": user_id, "limit": PAGE_LIMIT, "offset": page * PAGE_LIMIT})
        products.extend(data.get("products") or [])
        if not (data.get("meta") or {}).get("hasNext"):
            break
    else:
        raise SystemExit(f"{MAX_PAGES}ページを超えたので止めました")

    published = [p for p in products if p.get("published") is True]
    unpublished_count = len(products) - len(published)

    tshirts = []
    other_items = Counter()
    image_hosts = Counter()
    url_hosts = Counter()
    for product in published:
        if not isinstance(product.get("id"), int):
            continue
        item = product.get("item") or {}
        if not is_tshirt(item):
            other_items[f'{item.get("humanizeName")}（{item.get("name")}）'] += 1
            continue
        sample_url = https_url(product.get("sampleUrl"), "suzuri.jp", subdomains=True)
        image_url = https_url(product.get("sampleImageUrl"), IMAGE_HOST)
        if not sample_url or not image_url:
            print(f"※ URLがおかしいので外しました: 商品ID {product.get('id')}")
            continue
        image_hosts[urllib.parse.urlparse(image_url).hostname] += 1
        url_hosts[urllib.parse.urlparse(sample_url).hostname] += 1
        material = product.get("material") or {}
        tshirts.append({
            "id": product.get("id"),
            "title": product.get("title") or "",
            "material_id": material.get("id"),
            "material_title": material.get("title") or "",
            "item_name": item.get("name") or "",
            "item_label": item.get("humanizeName") or "",
            "price_with_tax": product.get("priceWithTax"),
            "url": sample_url,
            "image": image_url,
            "published_at": product.get("publishedAt") or "",
        })

    print(f"商品の数: 全部 {len(products)} / 公開中 {len(published)} / 非公開 {unpublished_count}（非公開は名前を出しません）")
    print(f"公開中のTシャツ: {len(tshirts)} 件")
    tshirt_items = Counter(f'{t["item_label"]}（{t["item_name"]}）' for t in tshirts)
    for label, count in tshirt_items.most_common():
        print(f"  Tシャツの種類 {label}: {count} 件")
    for label, count in other_items.most_common():
        print(f"  Tシャツ以外（保存しない） {label}: {count} 件")
    for host, count in image_hosts.most_common():
        print(f"  画像のホスト {host}: {count} 件")
    for host, count in url_hosts.most_common():
        print(f"  商品ページのホスト {host}: {count} 件")
    print("--- 公開中のTシャツの一覧（id / 素材名 / 商品名 / アイテム / 税込価格 / 公開日）---")
    for t in sorted(tshirts, key=lambda t: t["id"]):
        print(f'{t["id"]} / {t["material_title"]} / {t["title"]} / {t["item_label"]} / {t["price_with_tax"]} / {t["published_at"][:10]}')

    if not tshirts:
        raise SystemExit("公開中のTシャツが0件だったので、ファイルは書き換えません")

    tshirts.sort(key=lambda t: t["id"])
    OUTPUT_PATH.write_text(json.dumps({"products": tshirts}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"保存しました: {OUTPUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    sys.exit(main())
