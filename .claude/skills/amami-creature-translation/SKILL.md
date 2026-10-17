---
name: amami-creature-translation
description: Nature Experience Amami(奄美大島のナイトツアーサイト)の生き物Markdownの翻訳版(英語 .en.md・スペイン語 .es.md・中国語(繁体字。台湾・香港向け) .zh.md)を作る・直すときに必ず使う。「翻訳ページもよろしく」「英語版も作って」「翻訳して」「中国語のページに出てない」のような依頼のほか、日本語の生き物md(content/creatures/カテゴリー/ID.md)を新しく作った・内容を直した直後に、翻訳版を合わせる必要があるときにも使う(source だけの追記では翻訳は直さない)。サイトのメニューやトップページなど、生き物md以外の翻訳には使わない。
---

# Amami Creature Translation

サイトは日本語の生き物md(`content/creatures/カテゴリー/ID.md`)を正本にして、同じフォルダの
`ID.en.md`・`ID.es.md`・`ID.zh.md` から英語・スペイン語・中国語のページ(`en/`・`es/`・`zh/`)を作る。
翻訳mdが無い種は翻訳版のページに出ず、日本語ページの言語切り替え(EN/ES/中文)も押せない。

中国語版は**台湾・香港向けの繁体字**(2026-10-15 オーナー決定。ページは `<html lang="zh-Hant">`・`og:locale` は `zh_TW`)。
それより前に書かれた古い記録や、他のサイト・資料にある簡体字の名前は、そのまま写さず繁体字に直して使う。

日本語mdを作ったり直したりしたら、翻訳の3ファイルも同じ内容に揃える。日本語版を先にオーナーに確認してもらい、
「コミットして」と言われたときに翻訳もまとめて作るのがいつもの流れ。

## このスキルの読み方

- **決まり**(必ず守る): frontmatter の項目と値、中国語は繁体字で書くこと、`activity`・`night_observable` を書かないこと、内容を足したり省いたりしないこと、学名・文献名の扱い、仮名を残さないこと、作ったあとの作り直しとチェック
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
---
1行目: 科名・属名 *学名*

本文(日本語版の内容をそのまま訳す)
```

- **`activity` と `night_observable` は翻訳mdに書かない。** 生成スクリプトが日本語版から読むため(書くと食い違いのもと)
- **`source` は翻訳mdに書かなくてよい。記録は日本語版にだけ置く。** 生成スクリプトはどの言語の `source` も読まず、ページにもデータにも出ない(人が見るための記録)。すでに翻訳にある `source` は消さなくてよい(2026-10-17 オーナー決定)
- 内容を足したり省いたりしない。日本語版にない情報を足さない
- 学名・著者名・年・文献名(論文タイトル)は訳さずそのまま。日本語の論文タイトルは各言語に訳し「(in Japanese)/(en japonés)/(日文)」を添える

## 中国語は繁体字(決まり)

- `.zh.md` は frontmatter(`name`・`danger`、書いてあれば `source`)も本文も、すべて繁体字で書く。簡体字を1字も混ぜない
- 字形は台湾の標準に合わせる(例: 裡・著・為・眾・線・溫・棲・臺/台は既存に合わせて「台」)
- 1つの簡体字が複数の繁体字に分かれる字は、意味で選ぶ。2026-10-15 の繁体字化で決めた例:
  - 发 → 發(発生・発見)/髮(毛髪)
  - 只 → 隻(数のあと。「一隻」)/只(「只有」)
  - 后 → 後(前後)
  - 复 → 復(回復)・覆(覆う)・複(複数)
  - 干 → 乾(乾燥)・幹(幹)/干潟の「干」はそのまま
  - 里 → 裡(中)、着 → 著(〜している)、系 → 係・繫・系(意味で選ぶ)
  - 松鴉・游蛇・划蝽・台灣の「游」「划」「台」はそのまま
- 言葉は台湾の言い方にする(2026-10-17 オーナー決定)。使わない言葉と言い換えの一覧は `content/i18n/translation_rules.json` の `zh_avoid` にまとめてあり、`check_translations.py` がエラーとして見つける。言葉を足すときは、このファイルに足す(スキルに一覧を書き写さない)
- 「毫米」は台湾でも使うのでそのままでよい。情報不足(DD)の「數據缺乏(DD)」は、ランク名を台湾の紅皮書の言い方に合わせるための例外(`zh_avoid` の `except`)
- 日本の固有名詞・サイト名で日本の漢字のまま残すもの(例: 「虫屋(kuromushiya)」)は、簡体字に見えても変えない

## 1行目(科名・属名)の書き方(目安)

学名を `*斜体*` で最後に置くことだけは決まり。前の部分の言い回しは既存ファイルの例を参考に:

| 言語 | 例 |
|---|---|
| en | `Skink family (Scincidae), genus Plestiodon. *Plestiodon barbouri*` / `Raspy cricket family (Gryllacrididae), Short-winged Raspy Cricket *Metriogryllacris magna*` |
| es | `Familia de los eslizones (Scincidae), género Plestiodon. *Plestiodon barbouri*` |
| zh | `石龍子科石龍子屬 *Plestiodon barbouri*` / `蟋螽科 短翅蟋螽 *Metriogryllacris magna*` |

図鑑形式のカテゴリー(beetles・aquatic-insects・other-insects・birds・other-arthropods)は、日本語版が「科名 和名 *学名*」なら翻訳も「科名, 名前 *学名*」にする。

## 名前の付け方(目安)

定まった通称があればそれが最優先。無いときの付け方の例:

- 英語の通称があればそれを使う(例: Brahminy Blind Snake、Plains Cupid、Okinawa Tree Lizard)
- 通称が無い奄美の固有種・亜種は、既存に合わせて「Amami + 特徴 + 仲間の名前」(例: Amami Blue Soldier Beetle、Amami Spotted Camel Cricket)
- 人名由来は所有格(例: Kawamura's Rice Frog、Zimmermann's Diving Beetle)
- スペイン語は英語名を自然に訳す(例: Rana de Arroz de Kawamura、Escarabajo Buceador de Zimmermann)
- 中国語は、台湾・香港で使われている名前を優先する(台湾の生き物の名前は TaiCOL 臺灣物種名錄 `taicol.tw` で学名から引ける)。台湾にいない種で、中国などで使われている名前があれば、それを繁体字に直して使う(例: 澤蛙、鉤盲蛇、蘇鐵綺灰蝶)。無ければ属の中国名 + 特徴(例: 奄美斑灶馬)
- GBIF の vernacularNames や中国語版ウィキペディアの記事名は簡体字のことが多い。繁体字に直して使い、台湾・香港の名前と違うときは台湾・香港の名前を優先する(どちらも学名で同じ種かを確かめる。AGENTS.md の決まり)
- 2026-10-15 より前に付けた中国語名は、簡体字の名前を字だけ繁体字に直したもので、台湾での通称かは確かめていない。翻訳を直すついでに台湾・香港の名前が見つかったら、変える前にオーナーに伝える
- 付けた名前は報告で一覧にする(定まった名前が無く付けたものはそう伝える)

## danger の訳し方(決まり。同じ日本語には同じ訳を使い、ページ間で表記を揃える)

日本語版の書き方: レッドリストは「〇〇レッドリスト:ランク(略号)」(コロンあり・略号あり)。中国語は「日本環境省紅色名錄」(台湾の「環境部」と紛れないよう「日本」を付ける)、英語・スペイン語は「of Japan」「de Japón」を付けない(2026-10-17 オーナー決定)。

訳の対応表は `content/i18n/translation_rules.json` の `danger` にある(日本語版の danger の文字そのまま → en・es・zh の訳)。翻訳mdの danger は、この表の訳をそのまま使う。`check_translations.py` が、表と違う訳と、表に無い日本語の danger をエラーとして見つける。

- 日本語版に新しい danger が出てきたら、表に4言語を足してから翻訳mdを書く。新しい訳はオーナーに見せて決める(表は1か所だけ。スキルに表を書き写さない)
- ランクは略号と同じ意味の語にする(VU＝易危、EN＝瀕危、NT＝近危)。「絶滅危惧II類」を「瀕危II類」と直訳しない(2026-10-17 に誤訳があった)
- 中国語の中黒は「・」に揃える(「·」を使わない)

## 気をつけること(決まり)

- **植物などの言葉は、`content/i18n/translation_rules.json` の `glossary`(用語集)の訳を使う。** 例: シイ → chinquapin / shii (*Castanopsis*) / 椎樹。用語集に無い言葉で訳が決まったら、オーナーに確認して用語集に足す(2026-10-17、スペイン語でシイを「castaño de Japón」(クリ)と訳していた)
- スペイン語で使わない言葉は `es_avoid`、中国語は `zh_avoid` にあり、`check_translations.py` がエラーとして見つける
- **中国語・英語・スペイン語の文中に、ひらがな・カタカナを残さない。** `scripts/check_translations.py` が「日本語の残存」として引っかける。日本語の旧名などを書くときはローマ字にする(例: 「以前的日文名為“Heriguro-hime-tokage”」)
- 地名はローマ字(Amami Oshima、Tokunoshima、Minamidaito-jima など)。中国語は繁体字の漢字(奄美大島、德之島、鹿兒島縣)
- 数値・単位は日本語版と同じ値(mm/cm、〜 は en/es では "-")

## 作ったあと(決まり)

順番は ①機械のチェック → ②翻訳の監修 → ③反映。機械＝決まりで判定できること、監修＝意味と名前、と役割を分けている(2026-10-17 オーナー決定)。

### ① ページの作り直しと機械のチェック

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
python scripts/generate_highlights_page_i18n.py
python scripts/generate_sitemap.py
python scripts/check_translations.py
```

- `check_translations.py` の前までは `.github/workflows/process-creature-photos.yml` の生成スクリプトと同じ順番。ワークフローに生成スクリプトが増えたら、ここも揃える(2026-10-17、代表的な生き物ページとサイトマップの2つが抜けていた)
- `check_translations.py` の結果は「エラー(必ず直す)」と「要確認(人が見る)」に分かれる。エラーは0件にする(リンク切れ・翻訳ファイル抜け・かなの残存・danger・中国語で使わない言葉・簡体字・frontmatter・1行目の学名)。要確認(本文の単位つきの数・年の食い違い)は、日本語版と読み比べる。書き方の違いだけなら、オーナーに確認してから `translation_rules.json` の `number_check_exceptions` にファイル名と該当の文で1件ずつ登録する(例: kurotusraherasagi.zh.md の「20世紀90年代初」)。比べ方そのものは緩めない
- 簡体字のチェックは、よく出る字(`translation_rules.json` の `zh_simplified_chars`)だけを見る。0件でも新しく書いた文は目で見直す

### ② 翻訳の監修(creature-reviewer)

- **呼ぶ**: 新しい種を翻訳したとき、翻訳の本文や名前を直したとき
- **呼ばない**: 表記を揃えるだけの機械的な変更(danger の表記・言葉の置き換えなど、①で確かめられるもの)
- 1種につき英・西・中をまとめて1回で頼む。渡すのはパスだけで、翻訳したときの考えや経緯は渡さない(新しい目で見てもらうため)。頼み方の見本: 「翻訳の監修: 日本語版 content/creatures/beetles/taiwan-saikabuto.md、翻訳 taiwan-saikabuto.en.md・.es.md・.zh.md」
- 監修役が見るのは、意味のずれ・足し省き・名前・読み手に不自然な言い回しだけ(①で分かることは見ない)

### ③ 反映

- 「🔴 直すべき」を反映する。反映しなかった指摘は、理由と一緒にオーナーに伝える
- 「🟡 好みの範囲」と「⚪ 確かめられなかったこと」は一覧にしてオーナーに見せ、どうするか決めてもらう
- 反映して本文が変わったら、もう一度①の `check_translations.py` を動かす

### コミット

- コミットは「翻訳mdの追加」と「ページの再生成と記録」の2つに分け、`PROJECT_STATUS.md` の変更履歴に記録してプルリクエストを作る。マージはオーナーの「マージして」を待つ
