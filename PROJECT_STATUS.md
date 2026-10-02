# Nature Experience Amami - Project Status

最終更新: 2026-10-02（日本時間）

今の状況とやることだけを書くファイルです。作業前に `AGENTS.md`（共通ルール）を先に読んでください。
2026年9月までの経緯は `docs/history/2026-09.md` にあります（2026-09-30まで使っていた `PROJECT_STATUS_updated.md` を、そのまま名前を変えて移したもの）。

【要確認】の付いた項目は、確かめられなかったものです。確かめたら印を外して直してください。

## プロジェクト概要

- 奄美大島の夜の森で見られる生き物を紹介する静的Webサイト。日本語・英語・スペイン語・中国語の4言語。
- GitHub Pagesで公開。公開URL: `https://nature-experience-amami.github.io/`
- 生き物の情報は `content/creatures/` のMarkdownが正本。ページとデータは生成スクリプトで作る。
- 同じリポジトリに、予約管理アプリ（`customer-app/`）とThreads投稿の仕組み（`threads/`）も置いている。

## 現在の構成

（2026-09-30にリポジトリの実物で確認）

```text
.
├─ AGENTS.md                      共通ルール
├─ CLAUDE.md                      Claude Code が AGENTS.md を読み込むための入口
├─ PROJECT_STATUS.md              このファイル
├─ docs/history/                  月ごとの変更履歴
├─ .claude/skills/                作業ごとの手順書（スキル）
├─ .github/workflows/
│  ├─ process-creature-photos.yml  写真のpushで写真処理とページの作り直し
│  └─ threads-draft.yml            Threads下書き
├─ content/
│  ├─ categories.json             カテゴリーIDと表示名
│  ├─ category-pages/*.md         一覧ページ形式のカテゴリー（snakes・amphibians・stag-beetles・mammals）の説明文。4言語
│  ├─ creatures/カテゴリー/生き物ID.md（翻訳は .en.md .es.md .zh.md）
│  ├─ i18n/                       翻訳版ページの文言
│  └─ notes-hebi-anzen.md notes-kuwagata-saishu.md
├─ data/creatures*.json           AIチャット用のデータ（4言語、生成物）
├─ images/creatures/カテゴリー/(グループ/)生き物ID/
├─ scripts/                       写真処理・生成スクリプト・翻訳チェック
├─ templates/                     ページのひな形（category・creature・highlights・zukan と各 i18n 版）
├─ creatures/ categories/         日本語版のページ（生成物）
├─ en/ es/ zh/                    翻訳版（index・contact・tour・highlights・categories・creatures）
├─ index.html highlights.html tour.html contact.html amami-tool.html
├─ css/ js/ logo/
├─ customer-app/                  予約管理アプリ（使い方と注意は customer-app/README.md）
├─ threads/                       Threads投稿（詳細は threads/THREADS_STATUS.md）
├─ instagram-campaign/
├─ conversation-history-2026-09-*.md  9月の会話の控え
├─ sitemap.xml robots.txt
└─ Worker · JS                    Cloudflare Workerの控え（自動では反映されない）
```

- カテゴリーのフォルダ名は英語名: `snakes` `amphibians` `stag-beetles` `mammals` `birds` `lizards` `aquatic-insects` `beetles` `other-insects` `other-arthropods`（写真だけ `crustaceans`（カニ）もある）。
- 一覧ページの形式: `snakes` `amphibians` `stag-beetles` `mammals` はカテゴリーページ、`birds` `aquatic-insects` `beetles` `other-insects` `other-arthropods` は図鑑ページ（`scripts/generate_zukan_page.py`）。`other-arthropods` の図鑑ページは日本語版だけで、英語・スペイン語・中国語の一覧ページはまだない（生き物ごとのページは4言語ある）。`lizards` は生き物ごとのページだけで、一覧ページはまだない。
- `categories/hebi.html` `kaeru.html` `kuwagata.html` `honyuurui.html` `tori.html` `suisei-konntyuu.html` `koucyu.html` などは、英語名に変える前の古いURLから新しいページへ移動させるための転送ページ。

## 進行中の作業

### AIチャットの安定化（2026-09-30）

- 原因はGeminiの返事の遅さによる時間切れ（524）と、Gemini側の混雑（503）。対策の①②LOW③（#40・#43・#44・#45）と、観察月の出どころの言い分け（#46・#47）は反映済み（Cloudflareへのデプロイも済み）。詳しくは `docs/history/2026-09.md` の 2026-09-30 の記録。
- 2026-10-01に確認すること:
  - チャットの答え方（チンメルマンセスジゲンゴロウ＝「撮影記録があります」、ハブ＝「観察しやすい」）
  - ログの `seconds` を数日分見て、打ち切りの25秒（`ASK_TIMEOUT_MS`）を決め直す
  - 予備モデル `gemini-3.1-flash-lite` に切り替わったとき、チャット用のキーで使えるか

### 2026-10-01にオーナーがやること

- claude.ai の設定画面から、アカウント側のスキルを2026-09-30に渡した `.skill` ファイルで差し替える: `amami-creature-md`・`amami-project-status-log`・`amami-new-category-page`（中身はこのリポジトリの `.claude/skills/` と同じ）
- 上の「2026-10-01に確認すること」（AIチャット）
- 株式レポートのLINE（別リポジトリ `tetsu-ai-secretar`）: 区切りの罫線が青くならないか、スパムのようなタイトルが消えているか、予定がそろっているか、長いURLが外れているか

## やることリスト

### AIチャット・Worker

- サイトの `index.html`（4言語）が、Workerに生き物データを丸ごと付けて送っている（約17万字、Workerは使っていない）。送らないようにする。
- Cloudflareの変数 `GEMINI_API_KEY_ADMIN` は使われていない。消すかどうか決める。

### 生き物データ・ページ

- 生き物ページで、写真の撮影日だけで決まった月（`months_source` が `photos`、日本語版18種）も「観察しやすい時期」として表示されている。オーナーが `months:` を書くか、ページでも「撮影記録」と表示を分けるか決める。
  - トップページの「FIELD NOTE（今月に観察しやすい生き物）」も同じで、`index.html` は `months_source` を見ずに月だけで選んでいる（2026-10-01確認。10月はアマミヒラタヒシバッタと ko-iso-kanimushi が対象。ko-iso-kanimushi は2026-10-02にmdができ「コイソカニムシの仲間」と出るが、months は写真の撮影日から）。説明文は「ガイドが入力した観察時期をもとに」なので合わない。
  - 2026-10-01に18種の時期をWeb検索したが、ページを開けず要約だけだった。小さい水生昆虫とアマミヒラタヒシバッタは情報が見つからなかった。ネットワーク設定のあとに調べ直し、オーナーと1種ずつ `months:` を決める（資料の繁殖期などは本文へ）。決めきれない種は `months:` を書かず、フィールドノートには出さないようにする案。
- カニ（`crustaceans`）の2種類と、オオヒラタザトウムシ（`other-arthropods/oohirata-zatoumushi`）は、Markdownがまだない。そのためAIチャットで和名ではなく写真フォルダ名（例: okayadokari）が出る。
  - ザトウムシは、奄美のものは「アマミオオヒラタザトウムシ」と呼ばれるが、和名と学名（*Leiobunum maximum distinctum*、2025年に *Pseudoliobunum* 属へ）の対応を確かめられず保留（2026-10-02）。Suzuki (1973) や『タクサ』49号の総説が読めれば調べ直せる。オーナーの写真は奄美で撮影したもの。
- その他の節足動物の英語・スペイン語・中国語の図鑑ページを作るか決める（`amami-new-category-page` スキル）。
- トビイロゲンゴロウの写真がない（Markdownはある）。
- 確かめきれていない内容: コバネコロギスの奄美大島での分布（写真の種の確認が必要）、アマミマダラカマドウマの体長、オキナワキノボリトカゲの条例による捕獲禁止の有無、チンメルマンセスジゲンゴロウの奄美の個体の亜種の扱い・環境省と鹿児島県のランク。
- Markdownのidを正式名称に合わせて「amami-」付きに統一する（影響が広いので専用の作業として）。
- Markdownに追記したい情報: OBSERVATION（季節・時間帯・場所・観察のポイント）、hero-teaser（一言紹介文）、生き物ごとの詳しい注意事項。

### 表示

- トップの大きな写真の名前ラベル: 幅761〜900pxの縦向きで左上に出る、スマホ横向きで最初の画面の下にはみ出す（2026-09-24時点）。9/28の修正は幅901px以上（`@media (min-width:901px)`）だけに効くもので、この2つは直していない。【要確認】今の見え方（実機で確認）。

### 集客・公開の準備

- Google Search Consoleへの登録、`sitemap.xml`・`robots.txt`・構造化データ・プライバシー案内の整備。隠しキーワードやキーワードの詰め込みはしない。
- 内容が整ったら、旧サイトに新サイトへの案内を置き、XとInstagramに新サイトのURLを載せる（旧サイトは当面並行運用）。
- アクセス解析（GA4またはCloudflare）の導入。

## 今月の変更履歴

（2026-10-01以降の記録をここに追加する。書き方は `amami-project-status-log` スキルを参照）

### 2026-10-01 リュウキュウアオヘビの食性の記述と属名の綴りを修正

- オーナーの指摘（主食はミミズで、自然下でカエルを食べる例は少ないのでは）を受けて調べた。カエルはリュウキュウカジカガエルの捕食例が1例ほどで、飼育下ではカエルに興味を示さないとされる（検索結果の要約で確認）。食性の文を「主にミミズを食べる」にして、カエルの記述を外した（4言語）
- 属名の綴り `Cycophuops` を `Cyclophiops` に修正（4言語）
- 監修役 `creature-reviewer` で監修。要修正なし。日本爬虫両棲類学会の標準和名リストは *Cyclophiops semicarinatus* のまま（海外のデータベースは *Ptyas semicarinata*）。どちらも検索結果の要約でのみ確認
- 未完了事項: 学会リストの本文の確認、条例で捕獲禁止の種でないことの公式一覧での確認、id（`ryukyu-ao-hebi`）と写真フォルダ名（`ryuukyuu-aohebi`）の違い（対応表で動いている）。本文の「5月から11月頃」と `months:`（5〜10月）のずれはオーナー判断
- Commit SHA: 77037e3（md）、ページの再生成と記録はこの次のcommit
- Push: 済み

（担当: Claude Code）

### 2026-10-02 その他の節足動物4種のMarkdownを追加

- クラウド環境のネットワーク設定に、生き物の調べ物に使うサイトをオーナーが登録した。開けるのは ja/en.wikipedia・コトバンク・api.gbif.org・環境省・鹿児島県など。J-STAGE・GBIFの通常ページ・IUCN・生物多様性遺産図書館はサイト側で断られる（登録では直らない）。WebFetch では止められるサイトもあり、curl の方が開ける
- 写真はあるがmdが無かった `other-arthropods` の5種を調べ、4種のmdを作った（4言語）: アマミサソリモドキ（*Typopeltis stimpsonii*）、オオゲジ（*Thereuopoda clunifera*）、イソカニムシ（*Anchigarypus japonicus*。2020年に *Garypus* から移った）、コイソカニムシの仲間（*Nipponogarypus* sp.。2024年の論文で薩南・琉球のものが *N. okinoerabensis* に分けられたが、写真の種を決めきれないため「仲間」とした）
- 監修役 `creature-reviewer` で監修し、分布の書き方などを直した。論文3本（Harvey ほか 2020、Jeong ほか 2024、Tan ほか 2025）は検索結果の要約でのみ確認
- オーナーの回答: コイソカニムシの仲間以外の3種は夜行性でナイトツアーで観察できる（`activity: nocturnal`）。コイソカニムシの仲間は昼に石の下から出てくるが夜行性かは確証がない（`activity` は書かず `night_observable: false`）
- danger は4種とも書いていない（奄美市の指定希少種ではない。鹿児島県レッドリストはクモ類・多足類を対象にしていない。環境省レッドリストは名簿の本体を未確認）
- months は4種とも書いていない（写真の撮影日から自動集計）
- 英語・スペイン語・中国語の名前は、定まった通称を確かめられなかったので付けたもの（Amami Whip Scorpion、Giant House Centipede、Japanese Seashore Pseudoscorpion など）
- 未完了事項: オオヒラタザトウムシのmd（保留。リポジトリに下書きは無い。やることリストに記載）、その他の節足動物の翻訳版図鑑ページ
- Commit SHA: fe1f684（md）、ページの再生成と記録はこの次のcommit
- Push: 済み

（担当: Claude Code）

### 2026-10-02 オオゲジの英語名を変更

- オーナーの指示で、オオゲジの英語名を Giant House Centipede から Giant Centipede に変えた（`oo-geji.en.md`）。スペイン語・中国語の名前はそのまま
- Commit SHA: a97f2bf（md）、ページの再生成と記録はこの次のcommit
- Push: 済み

（担当: Claude Code）

### 2026-10-02 オオゲジのスペイン語名を変更

- オーナーの指示で、英語名に合わせてスペイン語名を Ciempiés Doméstico Gigante から Ciempiés Gigante に変えた（`oo-geji.es.md`）。中国語の名前（大蚰蜒）はそのまま
- Commit SHA: 6a7f604（md）、ページの再生成と記録はこの次のcommit
- Push: 済み

（担当: Claude Code）

### 2026-10-02 ナイトツアーで出会える生き物の分類（activity・night_observable）を全種そろえた

- 日本語版md 112種を「ナイトツアーで見られる／見られない／未記入」に分けてオーナーに見せ、オーナーの指示で未記入を無くした（51ファイル）
  - `activity: nocturnal` を追加: カエル7種、イモリ2種、クワガタ8種、ヒメハブ、ガラスヒバァ、タイワンクツワムシ、オオトモエ、アマミヒラタヒシバッタ、トカラマンマルコガネ、アマミヒメケブカマグソコガネ、アマミセマダラマグソコガネ、ゲンゴロウ3種（トビイロ・コガタノ・オキナワスジ）
  - `activity: nocturnal` + `night_observable: false`（夜行性だがツアーでは出会えない）: トラフズク、タイワンサイカブト
  - `activity: diurnal`: アオウバタマムシ、オオシマトラフハナムグリ
  - `night_observable: true`: リュウキュウアカショウビン
  - `night_observable: false`: 水生昆虫（夜の沢は危ないのでツアーから外す）。アシブトメミズムシと、未記入だった17種。`activity` は書いていない
- 結果: ナイトツアーで見られる59種、見られない53種、未記入0種。トップの大きな写真の候補は57種（写真のない種は出ない）
- `data/creatures*.json` を生成スクリプトで作り直した（差分は activity・night_observable の行だけ）。生き物ページのHTMLは activity を使わないので作り直していない
- 水生昆虫の扱いを `amami-creature-md` スキルに書き足した
- 未完了事項: ブラウザでのトップページの表示確認
- Commit SHA: 571fa74・8f1005e（最初の反映）、b775d96・b025cb1（ゲンゴロウ3種を戻す）、1827827・c8460be（ゲンゴロウ3種を夜行性に）、スキルと記録はこの次のcommit
- Push: 済み

（担当: Claude Code）

### 2026-10-02 アマミタカチホヘビをナイトツアーで出会える生き物から外した

- オーナーの指示: 夜行性だが、とても珍しく見せられる自信がないため。`takachiho-hebi.md` に `night_observable: false` を追加し、`data/creatures*.json` を作り直した
- 結果: ナイトツアーで見られる58種、見られない54種。トップの大きな写真の候補は56種
- 「珍しくて見せられる自信がない種は外す」を `amami-creature-md` スキルに書き足した
- Commit SHA: このエントリと同じブランチの4つのcommit（md・データ・スキル・記録）
- Push: 済み

（担当: Claude Code）

### 2026-10-02 その他の節足動物4種の観察時期を追加

- オーナーの情報で、アマミサソリモドキに `months: [5〜10]`（一年中見られ、5〜10月頃が活発）、オオゲジに `months: [6〜9]`（3〜12月頃見られ、6〜9月頃が観察しやすい）を書き、本文にも見られる時期を足した（4言語）
- イソカニムシ（撮影2・3月）とコイソカニムシの仲間（撮影3・10月）は、ほかの時期が分からないため `months:` は書かず（写真の撮影日から自動集計のまま）、本文に「〇月と〇月に撮影記録があるが、ほかの時期に見られるかはまだ分かっていない」と足した（4言語）。写真が増えて月が変わったら本文も直す
- ページとデータを作り直した。サソリモドキ・オオゲジの months が変わったため、関連カードが入れ替わり414ファイルが変わった。公開中のページにはカテゴリーの帯に「その他の節足動物」が無かったが、この作り直しで入った
- Commit SHA: 2a437fe・a6ba391（サソリモドキ・オオゲジ）、a9c978d・042273c（カニムシ2種）、記録はこの次のcommit
- Push: 済み

（担当: Claude Code）
