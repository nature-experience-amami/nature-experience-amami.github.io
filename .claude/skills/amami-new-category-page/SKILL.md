---
name: amami-new-category-page
description: Nature Experience Amami(奄美大島のナイトツアーサイト)で、新しい生き物カテゴリー(哺乳類・鳥・トカゲ・昆虫・水生昆虫・カニなど)のページを新規に作る、または既存カテゴリーのページ形式を見直すときに必ず使う。「〇〇カテゴリーのページ作って」「一覧ページ作って」「一覧ページと図鑑ページどっちがいい?」といった依頼のほか、新しい写真フォルダのカテゴリーが増えて「このカテゴリーどう扱う?」という判断が必要になった場面でも使う。
---

# Amami 新カテゴリー追加スキル

## このスキルの読み方

- **決まり**(必ず守る): IDをそろえる場所(ステップ1)、登録するリスト(ステップ3)、生成スクリプトで作ること、commit・push・マージはオーナーの指示を待つこと
- **目安**(状況に合わせてよい): ページ形式の選び方(ステップ0)、ナビに出すタイミング(ステップ6)

このサイトの一覧ページには2つの形式があり、カテゴリーの性質によって使い分けている。まず形式を決め、
それから手順を踏む。生き物ごとの個別ページ(`creatures/カテゴリー/ID.html`)は、どちらの形式でも作られる。

## ステップ0: ページ形式を決める(最初に必ず判断する)

| 判断材料 | カテゴリーページ方式(説明文つきの一覧ページ) | 図鑑方式(カードを並べた1ページ) |
|---|---|---|
| ツアーでの案内頻度 | 高い(お客さんに詳しく説明する主役級) | 低い(趣味寄り・マニアック) |
| 危険度・保護状況の重要性 | 高い(毒・天然記念物など個別に伝える必要) | 低い、または種類が多すぎて個別に書ききれない |
| 想定種数 | 数種類〜10種類程度 | 10種類を超えることが多い |
| 情報の入手しやすさ | 種ごとにある程度の情報が見つかる | 専門的すぎて情報が薄い種が混ざる |

- 今のカテゴリーページ方式: `snakes` `amphibians` `stag-beetles` `mammals`
- 今の図鑑方式: `birds` `aquatic-insects` `beetles` `other-insects`(`ZUKAN_CATEGORIES` には、まだページのない `crustaceans` `other-arthropods` も入っている)
- `lizards` は生き物ごとのページだけで、一覧ページはまだない

迷ったら、`amami-creature-md`スキルで実際にMarkdownを2〜3種類試作してみて、
「1種類ずつ丁寧に書けそうか」「量が多すぎて図鑑向きか」を確認してから決めてもよい。

## ステップ1: カテゴリーIDを決めて、すべての場所でそろえる(決まり)

カテゴリーIDは英語の小文字とハイフン(例: `aquatic-insects`)。**次の場所で1文字も違わないIDを使う。**

- 写真フォルダ: `images/creatures/カテゴリーID/`(写真のファイル名は生き物IDで始まるので、カテゴリーIDは入らない)
- Markdownのフォルダ: `content/creatures/カテゴリーID/`
- `content/categories.json`(日本語の表示名)
- `content/i18n/en.json` `es.json` `zh.json` の `categories`(翻訳版の表示名)
- ステップ3のリスト

写真フォルダ名は、実際のフォルダを確認してから使う。過去に `honyu`(categories.json)と `honyuurui`(写真フォルダ)、
`shellfish`・`crustaceans`(categories.json)と `kani`(写真フォルダ)のようなズレが起き、表示名が出なかった(カニは2026-09-30に写真フォルダを `crustaceans` にそろえた)。

## ステップ2: danger(危険度・保護状況)フィールドの意味を決める

新しいカテゴリーで`danger`フィールドが何を表すか、最初に決めておく(`amami-creature-md`スキル参照)。
- 毒や攻撃性の強さを表すのか(ヘビのような動物)
- 法的な保護状況・採集可否を表すのか(カエル・クワガタ・鳥・昆虫)
- あるいは今回のカテゴリーには天然記念物指定などが無く、シンプルな注意書き程度でよいのか

## ステップ3: 形式ごとのファイルとリストに登録する(決まり)

### 共通

- `scripts/category_header.py` の `MASTER_CATEGORY_ORDER` にIDを入れる。**ここに無いカテゴリーは、ヘッダーのカテゴリー帯に出ない。** 並び順もここで決まる。

### カテゴリーページ方式

- `content/category-pages/カテゴリーID.md` を作る(`id` `name` `eyebrow` `hero_title` `hero_lead` `list_title` `safety_text` などの項目は、既存の `mammals.md` を見本にする)。**このmdがあるカテゴリーだけ一覧ページが作られる。**
- 翻訳版 `カテゴリーID.en.md` `.es.md` `.zh.md` も作る
- `scripts/generate_category_pages_i18n.py` の `FULL_PAGE_CATEGORIES` にIDを追加する
- テンプレートは `templates/category.html` と `category.i18n.html`、生成は `generate_category_pages.py` と `generate_category_pages_i18n.py`

### 図鑑方式

- `scripts/generate_zukan_page.py` の `ZUKAN_CATEGORIES` にIDを追加する
- 同じファイルの `ENGLISH_LABELS`(見出しの英字)と `CATEGORY_CONTENT`(ページの説明文)に追加する。`CATEGORY_CONTENT` が無いと、どのカテゴリーにも使える `DEFAULT_CONTENT` の説明文になる
- 翻訳版も作るなら、同じファイルの `TRANSLATED_ZUKAN_CATEGORIES` に追加し、`generate_zukan_page_i18n.py` の `CATEGORY_CONTENT_I18N` に説明文を書く
- グループ見出し(例:「ゲンゴロウの仲間」)を使うなら、`CATEGORY_GROUPS` にそのカテゴリー用の`order`と`labels`を追加し、
  各mdに `group:` を書く。翻訳版の見出しは `content/i18n/*.json` の `group_キー`
- テンプレートは `templates/zukan.html` と `zukan.i18n.html`、生成は `generate_zukan_page.py` と `generate_zukan_page_i18n.py`

## ステップ4: Markdownを用意する

`amami-creature-md`スキルで生き物ごとのMarkdownを作り、`amami-creature-translation`スキルで翻訳版を作る。

## ステップ5: 生成・確認

GitHub Actionsが自動で動くのは写真をpushしたときだけ。Markdownやスクリプトを変えたら、
自分で生成スクリプトを実行する(またはActionsの「process-creature-photos」を手動で実行する)。
順番は `.github/workflows/process-creature-photos.yml` と同じにする。

```text
python scripts/generate_creatures_json.py        # AIチャット用の data/creatures.json
rm -rf creatures
python scripts/generate_creature_pages.py
python scripts/generate_category_pages.py
python scripts/generate_zukan_page.py
python scripts/generate_highlights_page.py
rm -rf en/creatures es/creatures zh/creatures
python scripts/generate_creature_pages_i18n.py
python scripts/generate_creatures_json_i18n.py
python scripts/generate_category_pages_i18n.py
python scripts/generate_zukan_page_i18n.py
python scripts/generate_highlights_page_i18n.py
python scripts/generate_sitemap.py
python scripts/check_translations.py             # 翻訳の抜けの確認
```

1. `categories/カテゴリーID.html`(と翻訳版の `en/categories/` など)ができているか確認する
2. ほかのカテゴリーページのカテゴリー帯に、新しいカテゴリーが出ているか確認する
3. ブラウザでPC幅・スマホ幅の両方を確認する(写真あり/なしの表示分岐、グループ見出しの有無なども)

## ステップ6: ナビに出るタイミングと、トップページのリンク(目安)

- **カテゴリー帯(各カテゴリーページのヘッダー)は、スクリプトが自動で作る。** ページのあるカテゴリーだけが出る。
  カテゴリーページ方式は `content/category-pages/` のmdを置いた時点、図鑑方式は `content/creatures/カテゴリーID/` に
  日本語のmdが1つでもある時点でページができ、ナビにも出る。
- そのため、中身が薄いうちに出したくないときは、ステップ3のリストへの追加やmdのcommitを、種類が揃うまで待つ。
  出す目安は、図鑑方式なら各グループに1種類ずつくらい、カテゴリーページ方式なら主要な種類が一通り揃った状態。
- **トップページのリンクは手で追加する。** `index.html` と `en/` `es/` `zh/` の `index.html` の4つで、それぞれ
  カテゴリーの並び(`cat-item`)と「奄美の生き物を知る」の一覧(`guide-link`)の2か所。4言語とも忘れずに。

## ステップ7: 記録する

終わったら `PROJECT_STATUS.md` の「現在の構成」を直し、「今月の変更履歴」に記録する(`amami-project-status-log`スキル)。

## よくある落とし穴(過去に実際に起きた問題)

- 写真フォルダ名とcategories.jsonのキーがズレていて表示名が出ない(ステップ1)
- 同じ生き物のcontent Markdownが重複して存在する(統合を忘れる)
- Markdownを変えただけではActionsが動かず、ページやAIチャットのデータが古いままになる(ステップ5)
- commit・pushは、ユーザーから明示的な確認が無い限り実行しない(`AGENTS.md`の作業ルール)
