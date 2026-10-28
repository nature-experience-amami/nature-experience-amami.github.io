# SUZURI API v1 詳細リファレンス

このファイルはSUZURI APIの各リソースのフィールド定義とエンドポイントの詳細パラメータをまとめたものである。

> **注意**: APIの仕様は変更される可能性がある。最新の正確な情報は公式ドキュメント https://suzuri.jp/developer/documentation/v1 を直接参照すること。

## リソース定義

### User

| フィールド | 型 | 説明 |
|-----------|-----|------|
| id | integer | ユーザーID |
| name | string | ユーザー名（一意な識別子） |
| displayName | nullable string | 表示名 |
| avatarUrl | nullable string | アバター画像URL |
| profile | Profile | プロフィール情報 |
| identities | array of Identity | 外部サービス連携情報 |
| official | boolean | 認証バッジの有無 |
| email | string | メールアドレス（`/user` エンドポイントのみ） |

### Profile

| フィールド | 型 | 説明 |
|-----------|-----|------|
| url | nullable string | ホームページURL |
| body | nullable string | プロフィール本文 |
| headerUrl | nullable string | ヘッダ画像URL |

### Identity（外部サービス連携）

| フィールド | 型 | 説明 |
|-----------|-----|------|
| id | integer | ID |
| provider | string | プロバイダ名（"twitter"など） |
| uid | nullable string | 外部サービスのUID |
| nickname | nullable string | ニックネーム |
| url | nullable string | プロフィールURL |

### Material（素材）

| フィールド | 型 | 説明 |
|-----------|-----|------|
| id | integer | 素材ID |
| title | string | タイトル |
| description | nullable string | 説明 |
| price | integer | トリブン（クリエイターの取り分） |
| priceWithTax | integer | 税込トリブン |
| violation | boolean | 規約違反フラグ |
| published | boolean | 公開状態 |
| publishedAt | nullable datetime | 公開日時 |
| uploadedAt | datetime | アップロード日時 |
| dominantRgb | nullable string | 画像の支配的な色 |
| originalWidth | integer | 元画像の幅 |
| originalHeight | integer | 元画像の高さ |
| user | User | 作成者 |

### Item（アイテム: 商品種類）

| フィールド | 型 | 説明 |
|-----------|-----|------|
| id | integer | アイテムID |
| name | string | 一意な識別子 |
| humanizeName | string | 表示名（日本語） |
| angles | array of integer | 利用可能な角度 |
| availablePrintPlaces | array of string | プリント可能な箇所（"front", "back"など） |
| defaultPrintPlace | string | デフォルトのプリント箇所 |
| displayOrder | integer | 表示順 |
| iconUrls | object | アイコンURL（`{"png": "/path"}`） |
| wearingImageUrls | object | 着用イメージURL |
| isMultiPrintable | boolean | 複数箇所プリント対応 |
| printPlaceDisplayNames | object | プリント箇所の日本語表示名 |
| imageDescriptions | array of string | 画像説明 |
| productImageUrlTemplates | object | 動的URL生成用テンプレート |
| isEmbroidery | boolean | 刺繍対応 |
| category | object | カテゴリ |
| minPriceWithTax | integer | 最低税込価格 |
| colorsCount | integer | カラー数 |
| variants | array of ItemVariant | バリエーション一覧 |

### ItemVariant（色・サイズの組み合わせ）

| フィールド | 型 | 説明 |
|-----------|-----|------|
| id | integer | バリエーションID |
| price | integer | 税抜価格 |
| priceWithTax | integer | 税込価格 |
| exemplary | boolean | 代表バリエーションフラグ |
| enabled | boolean | 有効フラグ |
| isLightColor | boolean | 明るい色か |
| isDarkColor | boolean | 暗い色か |
| color | ItemColor | 色情報 |
| size | ItemSize | サイズ情報 |
| printPlaces | array of PrintPlace | プリント箇所情報 |

### ItemColor

| フィールド | 型 | 説明 |
|-----------|-----|------|
| id | integer | 色ID |
| name | string | 色名（"white"など） |
| displayName | string | 表示名（"ホワイト"など） |
| rgb | string | RGBカラーコード（"#ffffff"） |

### ItemSize

| フィールド | 型 | 説明 |
|-----------|-----|------|
| id | integer | サイズID |
| name | string | サイズ名（"s", "m", "l"など） |
| displayName | string | 表示名（"S", "M", "L"） |

### PrintPlace（プリント箇所）

| フィールド | 型 | 説明 |
|-----------|-----|------|
| id | integer | ID |
| place | string | 箇所名（"front", "back"など） |
| price | integer | この箇所の追加価格 |
| itemVariantId | integer | 紐づくバリエーションID |

### Product（商品）

| フィールド | 型 | 説明 |
|-----------|-----|------|
| id | integer | 商品ID |
| title | string | タイトル |
| published | boolean | 公開状態 |
| publishedAt | nullable datetime | 公開日時 |
| createdAt | datetime | 作成日時 |
| updatedAt | datetime | 更新日時 |
| examplaryAngle | nullable string | 代表角度 |
| imageUrl | string | 画像テンプレートURL（要パラメータ置換） |
| sampleImageUrl | string | サンプル画像URL（WebP、そのまま使用可） |
| url | string | ページテンプレートURL |
| sampleUrl | string | 商品ページURL（そのまま使用可） |
| priceWithTax | integer | 税込価格 |
| discountedPriceWithTax | integer | 割引後税込価格 |
| item | Item | アイテム情報 |
| material | Material | 素材情報 |
| itemVariants | array of ItemVariant | バリエーション一覧 |
| sampleItemVariant | ItemVariant | 代表バリエーション |

### Choice（オモイデ）

| フィールド | 型 | 説明 |
|-----------|-----|------|
| id | integer | ID |
| title | string | タイトル |
| description | nullable string | 説明 |
| secret | boolean | 非公開フラグ |
| bannerUrl | nullable uri | バナー画像URL |
| productsCount | integer | 含まれる商品数 |
| user | User | 作成者 |

### Favorite（ズッキュン）

| フィールド | 型 | 説明 |
|-----------|-----|------|
| id | integer | ID |
| count | integer | ズッキュン数 |
| productId | integer | 対象商品ID |
| user | User | ユーザー |

## エンドポイント詳細

### Activity

#### GET /api/v1/activities
アクティビティ一覧を取得する。

**パラメータ:**
| 名前 | 型 | 必須 | デフォルト | 説明 |
|------|-----|------|-----------|------|
| limit | integer | - | 30 | 取得件数（1-30） |

#### GET /api/v1/activities/unreads
未読アクティビティ数を取得する。パラメータなし。

### Material

#### GET /api/v1/materials
素材一覧を取得する。

**パラメータ:**
| 名前 | 型 | 必須 | デフォルト | 説明 |
|------|-----|------|-----------|------|
| limit | integer | - | 20 | 取得件数（1-50） |
| offset | integer | - | 0 | 開始位置 |
| userId | integer | - | - | ユーザーIDでフィルタ |

#### POST /api/v1/materials
素材を作成する。レート制限あり。

**パラメータ:**
| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| texture | string | 必須 | 画像URL またはデータURI |
| title | string | 必須 | 素材のタイトル |
| description | string | - | 説明文 |
| price | integer | - | トリブン（クリエイターの取り分） |
| products | array | - | 作成する商品の設定 |

**products配列の各要素:**
| 名前 | 型 | 説明 |
|------|-----|------|
| itemId | integer | アイテムID |
| published | boolean | 公開するかどうか |
| resizeMode | string | "contain"（フィット）or "cover"（埋め尽くし、一部アイテムのみ） |

#### POST /api/v1/materials/text
テキストから素材を作成する。レート制限あり。

**パラメータ:**
| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| text | string | 必須 | テキスト（255文字以内） |
| itemVariantId | integer | 必須 | アイテムバリエーションID |

#### PUT /api/v1/materials/{material_id}
素材を更新する。レート制限あり。

**パラメータ:**
| 名前 | 型 | 説明 |
|------|-----|------|
| title | string | タイトル |
| description | string | 説明文 |
| price | integer | トリブン |
| products | array | 商品設定の更新 |

#### DELETE /api/v1/materials/{material_id}
素材を削除する。紐づく商品もすべて削除される。

### Product

#### GET /api/v1/products
商品一覧を取得する。

**パラメータ:**
| 名前 | 型 | 必須 | デフォルト | 説明 |
|------|-----|------|-----------|------|
| limit | integer | - | 20 | 取得件数（1-50） |
| offset | integer | - | 0 | 開始位置 |
| itemId | integer | - | - | アイテムIDでフィルタ |
| materialId | integer | - | - | 素材IDでフィルタ |
| userId | integer | - | - | ユーザーIDでフィルタ |
| userName | string | - | - | ユーザー名でフィルタ |

#### GET /api/v1/products/{product_id}
商品詳細を取得する。

#### GET /api/v1/products/search
商品をキーワード検索する。

**パラメータ:**
| 名前 | 型 | 必須 | デフォルト | 説明 |
|------|-----|------|-----------|------|
| q | string | - | - | 検索キーワード（100文字以内） |
| limit | integer | - | 20 | 取得件数（1-50） |
| offset | integer | - | 0 | 開始位置 |
| itemId | integer | - | - | アイテムIDでフィルタ |

#### GET /api/v1/products/on_sale
セール中の商品一覧を取得する。

**パラメータ:**
| 名前 | 型 | 必須 | デフォルト | 説明 |
|------|-----|------|-----------|------|
| limit | integer | - | 20 | 取得件数（1-50） |
| offset | integer | - | 0 | 開始位置 |

### Item

#### GET /api/v1/items
取扱中のアイテム（商品種類）一覧を取得する。パラメータなし。

### Choice

#### GET /api/v1/choices
オモイデ一覧を取得する。

**パラメータ:**
| 名前 | 型 | 必須 | デフォルト | 説明 |
|------|-----|------|-----------|------|
| limit | integer | - | 20 | 取得件数（1-50） |
| offset | integer | - | 0 | 開始位置 |
| userId | integer | - | - | ユーザーIDでフィルタ |
| userName | string | - | - | ユーザー名でフィルタ |

#### GET /api/v1/choices/{choice_id}
オモイデ詳細を取得する。

#### POST /api/v1/choices
オモイデを作成する。

**パラメータ:**
| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| title | string | 必須 | タイトル |
| description | string | - | 説明 |
| bannerUrl | string | - | バナー画像URL |
| choiceProducts | array | - | 含める商品 |

#### PUT /api/v1/choices/{choice_id}
オモイデを更新する。

**パラメータ:**
| 名前 | 型 | 説明 |
|------|-----|------|
| title | string | タイトル |
| description | string | 説明 |
| bannerUrl | string | バナー画像URL |
| choiceProducts | array | 商品設定 |

#### DELETE /api/v1/choices/{choice_id}
オモイデを削除する。

#### GET /api/v1/choices/{choice_id}/products
オモイデ内の商品一覧を取得する。

**パラメータ:**
| 名前 | 型 | 必須 | デフォルト | 説明 |
|------|-----|------|-----------|------|
| limit | integer | - | 20 | 取得件数（1-50） |
| offset | integer | - | 0 | 開始位置 |

#### POST /api/v1/choices/{choice_id}
オモイデに商品を追加する。

**パラメータ:**
| 名前 | 型 | 説明 |
|------|-----|------|
| productId | integer | 商品ID |
| itemVariantId | integer | バリエーションID |

#### POST /api/v1/choices/{choice_id}/remove
オモイデから商品を削除する。

**パラメータ:**
| 名前 | 型 | 説明 |
|------|-----|------|
| productId | integer | 商品ID |
| itemVariantId | integer | バリエーションID |

### Favorite

#### GET /api/v1/products/{product_id}/favorites
商品のズッキュン一覧を取得する。

**パラメータ:**
| 名前 | 型 | 必須 | デフォルト | 説明 |
|------|-----|------|-----------|------|
| itemId | integer | - | - | アイテムIDでフィルタ |
| limit | integer | - | 20 | 取得件数（1-50） |
| offset | integer | - | 0 | 開始位置 |

#### GET /api/v1/users/{user_id}/favorites
ユーザーのズッキュン一覧を取得する。

#### POST /api/v1/products/{product_id}/favorites
ズッキュンを追加する。レート制限あり。

**パラメータ:**
| 名前 | 型 | 説明 |
|------|-----|------|
| anonymouse | boolean | 匿名かどうか（API側のtypoでanonymouseが正しいキー名） |
| count | integer | 数（最大100） |

#### DELETE /api/v1/products/{product_id}/favorites
ズッキュンを削除する。

### User

#### GET /api/v1/users
ユーザー一覧を取得する。

**パラメータ:**
| 名前 | 型 | 必須 | デフォルト | 説明 |
|------|-----|------|-----------|------|
| name | string | - | - | ユーザー名でフィルタ |
| limit | integer | - | 20 | 取得件数（1-50） |
| offset | integer | - | 0 | 開始位置 |

#### GET /api/v1/users/{user_id}
ユーザー詳細を取得する。

#### GET /api/v1/user
認証済みユーザーの情報を取得する。emailフィールドが含まれる。

#### PUT /api/v1/user
認証済みユーザーの情報を更新する。

## JSONスキーマ

APIの完全なJSONスキーマは以下で取得できる：

```
GET https://suzuri.jp/api/v1/schema
```
