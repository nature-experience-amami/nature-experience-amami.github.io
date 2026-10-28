---
name: suzuri-api
description: SUZURI REST APIを使ったアプリケーション構築のガイド。SUZURI APIでグッズを作成・検索・表示するアプリや、SUZURIと連携するサービスを開発する際に使用する。「SUZURIのAPIで」「SUZURIで商品を」「SUZURIと連携」「スズリAPI」「suzuri.jpのAPI」などSUZURIに関連するアプリケーション開発の話題が出たら、このスキルを参照すること。
---

# SUZURI API リファレンス

SUZURI（suzuri.jp）はGMOペパボが運営するプリントオンデマンドサービス。公開REST APIでオリジナルグッズの作成・検索・表示が可能。

最新のAPI仕様: https://suzuri.jp/developer/documentation/v1
アイテム別の推奨入稿画像サイズ: https://suzuri.jp/item_templates

このスキルはベースライン情報。実装時は上記の最新情報を優先する。

## API概要

| 項目 | 値 |
|------|-----|
| ベースURL | `https://suzuri.jp/api/v1` |
| プロトコル | HTTPS必須 |
| リクエスト形式 | GET: クエリストリング、POST/PUT/DELETE: `application/json` |
| レスポンス形式 | JSON |
| JSONスキーマ | `GET https://suzuri.jp/api/v1/schema` |

## 認証

### APIキー

自分のアカウントに紐づくアプリ向け。https://suzuri.jp/developer/apps で発行。

```
Authorization: Bearer {api_key}
```

スコープ: `read`（読み取り）/ `write`（作成・更新・削除）

注意: キー発行者自身の非公開商品も取得される。公開商品のみ扱う場合は `published` フィールドでフィルタする。

### OAuth 2.0

複数ユーザーがそれぞれ自分のアカウントで操作するアプリ向け。

1. `GET https://suzuri.jp/oauth/authorize` に `client_id`, `scope`, `redirect_uri`, `response_type=code` を指定
2. ユーザー認可後、`redirect_uri` に `code` が返る
3. `POST https://suzuri.jp/oauth/token` で `grant_type=authorization_code`, `code`, `redirect_uri`, `client_id`, `client_secret` を送信（Content-Type: `application/x-www-form-urlencoded`）

アプリ登録は https://suzuri.jp/developer/apps で行う。コールバックURLはアプリに1つしか設定できないため、環境ごとに別のアプリ登録が必要。`redirect_uri` はHTTPS必須。

### 認証方式の選び方

| 観点 | APIキー | OAuth |
|------|--------|-------|
| グッズ作成先 | キー発行者のショップ | アプリユーザーのショップ |
| 非公開グッズへのアクセス | 発行者のもののみ | ユーザーのもの |
| 用途 | 自分のショップ管理、個人ツール | マルチユーザーアプリ |

## リソース構造

```
Item（アイテム: Tシャツ、マグカップなど商品種類）
  └── ItemVariant（色・サイズの組み合わせ）

Material（素材: ユーザーがアップロードしたデザイン画像）
  └── Product（商品: Material × Item の組み合わせ）

Choice（オモイデ: 商品のコレクション）
  └── Product（商品を追加）

Favorite（ズッキュン: 商品へのいいね）
```

素材（Material）を作成すると、指定したアイテムに対して商品（Product）が自動生成される。素材を削除すると紐づく商品もすべて削除される。

## エンドポイント一覧

詳細なパラメータやレスポンス形式は [references/api-reference.md](references/api-reference.md) を参照。

| 操作 | メソッド | エンドポイント |
|------|---------|---------------|
| アイテム一覧 | GET | `/items` |
| 素材一覧 | GET | `/materials` |
| 素材作成 | POST | `/materials` |
| テキスト素材作成 | POST | `/materials/text` |
| 素材更新 | PUT | `/materials/{id}` |
| 素材削除 | DELETE | `/materials/{id}` |
| 商品一覧 | GET | `/products` |
| 商品詳細 | GET | `/products/{id}` |
| 商品検索 | GET | `/products/search` |
| セール商品 | GET | `/products/on_sale` |
| オモイデ一覧 | GET | `/choices` |
| オモイデ作成 | POST | `/choices` |
| オモイデ更新 | PUT | `/choices/{id}` |
| オモイデ削除 | DELETE | `/choices/{id}` |
| ズッキュン一覧 | GET | `/products/{id}/favorites` |
| ズッキュン追加 | POST | `/products/{id}/favorites` |
| ズッキュン削除 | DELETE | `/products/{id}/favorites` |
| ユーザー一覧 | GET | `/users` |
| ユーザー詳細 | GET | `/users/{id}` |
| 自分の情報 | GET | `/user` |
| アクティビティ | GET | `/activities` |
| 未読数 | GET | `/activities/unreads` |

## 実装パターン

### 商品一覧を表示する

```
GET /api/v1/products?userName={your_name}
Authorization: Bearer {token}
```

- 商品画像: `sampleImageUrl`（WebP）推奨。`imageUrl` はテンプレートURLでパラメータ置換が必要
- 商品ページリンク: `sampleUrl` を使う

### 画像からグッズを作成する

```
POST /api/v1/materials
Content-Type: application/json
Authorization: Bearer {token}

{
  "texture": "https://example.com/image.png",
  "title": "デザイン名",
  "price": 100,
  "description": "説明文",
  "products": [
    { "itemId": 1, "published": true }
  ]
}
```

- `texture`: 画像URLまたはデータURI
- `price`: トリブン（クリエイターの取り分）。0以上の整数
- `products`: `itemId` は `GET /api/v1/items` で事前に取得する
- `resizeMode`: `contain`（フィット）/ `cover`（埋め尽くし、一部アイテムのみ）
- 刺繍アイテムなど、API経由での商品作成に非対応のItemがある

### プレビュー付きグッズ作成フロー

1. `POST /api/v1/materials` でグッズ作成
2. レスポンスの `sampleImageUrl` でプレビュー表示
3. 購入: `sampleUrl` へ遷移 / 取り消し: `DELETE /api/v1/materials/{id}` で素材ごと削除

### テキストからグッズを作成する

```
POST /api/v1/materials/text
Content-Type: application/json
Authorization: Bearer {token}

{
  "text": "Hello World",
  "itemVariantId": 123
}
```

- `text`: 255文字以内
- `itemVariantId`: 対象のアイテムバリエーションID

### 商品を検索する

```
GET /api/v1/products/search?q={keyword}&limit=20&offset=0
```

## ページネーション

リストAPIは `limit` と `offset` をサポート。

- `limit`: 取得件数（デフォルト20〜30、最大50）
- `offset`: 開始位置（デフォルト0）
- `meta.hasNext` が `true` なら次のページが存在

## レート制限

レスポンスヘッダで確認: `X-Ratelimit-Limit` / `X-Ratelimit-Remaining` / `X-Ratelimit-Reset`

対象エンドポイント: `POST /materials`, `PUT /materials/{id}`, `POST /materials/text`, `POST /products/{id}/favorites`

## エラーハンドリング

HTTPステータスコードで判断する（レスポンスボディの内容は保証されない）。

| コード | 意味 |
|--------|------|
| 200 | 成功 |
| 201 | 作成成功 |
| 204 | 成功（ボディなし） |
| 401 | 認証エラー |
| 40x | クライアントエラー |
| 50x | サーバーエラー |

## 画像URLテンプレート

`sampleImageUrl` を使えば置換不要。カスタムサイズが必要な場合は `imageUrl` の以下を置換:

- `{width}x{height}`: 画像サイズ
- `{size}`: サイズ指定
- `{color}`: 色指定
- `[/angle]`: 表示角度（front, backなど）

## 価格の計算

```
商品価格 = 素材のトリブン + アイテムバリエーション価格 + プリント箇所追加価格
```

APIレスポンスの `priceWithTax` に税込最終価格が含まれる。
