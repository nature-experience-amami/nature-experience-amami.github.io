---
name: amami-creature-translation
description: Nature Experience Amami(奄美大島のナイトツアーサイト)の生き物Markdownの翻訳版(英語 .en.md・スペイン語 .es.md・中国語 .zh.md)を作る・直すときに必ず使う。「翻訳ページもよろしく」「英語版も作って」「翻訳して」「中国語のページに出てない」のような依頼のほか、日本語の生き物md(content/creatures/カテゴリー/ID.md)を新しく作った・内容を直した・sourceを追記した直後に、翻訳版を合わせる必要があるときにも使う。サイトのメニューやトップページなど、生き物md以外の翻訳には使わない。
---

# Amami Creature Translation

サイトは日本語の生き物md(`content/creatures/カテゴリー/ID.md`)を正本にして、同じフォルダの
`ID.en.md`・`ID.es.md`・`ID.zh.md` から英語・スペイン語・中国語のページ(`en/`・`es/`・`zh/`)を作る。
翻訳mdが無い種は翻訳版のページに出ず、日本語ページの言語切り替え(EN/ES/中文)も押せない。

日本語mdを作ったり直したりしたら、翻訳の3ファイルも同じ内容に揃える。日本語版を先にオーナーに確認してもらい、
「コミットして」と言われたときに翻訳もまとめて作るのがいつもの流れ。

## このスキルの読み方

- **決まり**(必ず守る): frontmatter の項目と値、`activity`・`night_observable` を書かないこと、内容を足したり省いたりしないこと、学名・文献名の扱い、仮名を残さないこと、作ったあとの作り直しとチェック
- **目安**(状況に合わせて変えてよい): 1行目の言い回し、名前の付け方、訳文の自然さの工夫。下の表や例は見本で、もっと良い訳や通称が見つかればそちらを使う

## ハルシネーション禁止(決まり。いちばん大事)

サイトは実在の生き物を紹介し、訪れた人がそれを信じる。確かめていないことを本当らしく書くのは、どんなに小さくても禁止。

- 翻訳では日本語版にないことを足さない(知っている知識で補わない)。日本語版の内容に疑問があれば、訳す前にオーナーに伝える
- 書くのは、情報源で確かめられたことだけ。記憶や「たぶんこうだろう」で数値・学名・分布・生態・保護の指定を書かない
- 情報源・論文名・著者・年・URLを作らない。実際に見たものだけを source に書く
- 検索結果の要約しか読めなかったものは、そうだと分かるように報告する(要約は取り違えが多い。例: 2026年の論文を奄美の初記録と書いてしまった)
- 分からないことは、書かないか「〜とされる」「詳しいことは分かっていない」と書く。空欄は間違いより良い
- オーナーへの報告でも同じ。確かめていないのに「できた」「消えている」「正しい」と言わない

## 翻訳mdの書式(決まり)

```yaml
---
id: 日本語版と同じ
name: その言語での名前
category: 日本語版と同じ
group: 日本語版と同じ(あるときだけ)
danger: その言語に訳したもの(日本語版にあるときだけ)
months: 日本語版と同じ(あるときだけ)
source: その言語に訳したもの(日本語版にあるときだけ)
---
1行目: 科名・属名 *学名*

本文(日本語版の内容をそのまま訳す)
```

- **`activity` と `night_observable` は翻訳mdに書かない。** 生成スクリプトが日本語版から読むため(書くと食い違いのもと)
- 内容を足したり省いたりしない。日本語版にない情報を足さない
- 学名・著者名・年・文献名(論文タイトル)は訳さずそのまま。日本語の論文タイトルは各言語に訳し「(in Japanese)/(en japonés)/(日文)」を添える

## 1行目(科名・属名)の書き方(目安)

学名を `*斜体*` で最後に置くことだけは決まり。前の部分の言い回しは既存ファイルの例を参考に:

| 言語 | 例 |
|---|---|
| en | `Skink family (Scincidae), genus Plestiodon. *Plestiodon barbouri*` / `Raspy cricket family (Gryllacrididae), Short-winged Raspy Cricket *Metriogryllacris magna*` |
| es | `Familia de los eslizones (Scincidae), género Plestiodon. *Plestiodon barbouri*` |
| zh | `石龙子科石龙子属 *Plestiodon barbouri*` / `蟋螽科 短翅蟋螽 *Metriogryllacris magna*` |

図鑑形式のカテゴリー(beetles・aquatic-insects・other-insects・birds)は、日本語版が「科名 和名 *学名*」なら翻訳も「科名, 名前 *学名*」にする。

## 名前の付け方(目安)

定まった通称があればそれが最優先。無いときの付け方の例:

- 英語の通称があればそれを使う(例: Brahminy Blind Snake、Plains Cupid、Okinawa Tree Lizard)
- 通称が無い奄美の固有種・亜種は、既存に合わせて「Amami + 特徴 + 仲間の名前」(例: Amami Blue Soldier Beetle、Amami Spotted Camel Cricket)
- 人名由来は所有格(例: Kawamura's Rice Frog、Zimmermann's Diving Beetle)
- スペイン語は英語名を自然に訳す(例: Rana de Arroz de Kawamura、Escarabajo Buceador de Zimmermann)
- 中国語は中国で使われている名前があればそれ(例: 泽蛙、钩盲蛇、苏铁绮灰蝶)、無ければ属の中国名 + 特徴(例: 奄美斑灶马)
- 付けた名前は報告で一覧にする(定まった名前が無く付けたものはそう伝える)

## danger の訳し方(決まり。同じ日本語には同じ訳を使い、ページ間で表記を揃える)

| 日本語 | en | es | zh |
|---|---|---|---|
| 無毒 | Non-venomous | No venenosa | 无毒 |
| 無毒・希少 | Non-venomous · Rare | No venenosa · Rara | 无毒・稀有 |
| 捕獲禁止(鹿児島県希少野生動植物) | Collecting prohibited (Kagoshima Prefecture Rare Wildlife) | Recolección prohibida (Vida Silvestre Rara de la Prefectura de Kagoshima) | 禁止捕获(鹿儿岛县稀有野生动植物) |
| 環境省レッドリスト絶滅危惧II類(VU) | Ministry of the Environment Red List: Vulnerable (VU) | Lista Roja del Ministerio de Medio Ambiente: Vulnerable (VU) | 环境省红色名录 易危(VU) |
| 環境省レッドリスト:準絶滅危惧(NT) | Ministry of the Environment Red List: Near Threatened (NT) | Lista Roja del Ministerio de Medio Ambiente: Casi Amenazada (NT) | 环境省红色名录:近危(NT) |

## 気をつけること(決まり)

- **中国語・英語・スペイン語の文中に、ひらがな・カタカナを残さない。** `scripts/check_translations.py` が「日本語の残存」として引っかける。日本語の旧名などを書くときはローマ字にする(例: 「以前的日文名为“Heriguro-hime-tokage”」)
- 地名はローマ字(Amami Oshima、Tokunoshima、Minamidaito-jima など)。中国語は漢字(奄美大岛、德之岛)
- 数値・単位は日本語版と同じ値(mm/cm、〜 は en/es では "-")

## 作ったあと(決まり)

リポジトリのルートでページを作り直して確認する(日本語ページも、言語切り替えのリンクが変わるので作り直しが必要):

```bash
python scripts/generate_creatures_json.py
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
python scripts/check_translations.py
```

- 「リンク切れ」「翻訳ファイル抜け」が0件であること。`en/es/zh/index.html` の日本語残存15箇所は以前からある分
- コミットは「翻訳mdの追加」と「ページの再生成と記録」の2つに分け、`PROJECT_STATUS.md` の変更履歴に記録してプルリクエストを作る。マージはオーナーの「マージして」を待つ
