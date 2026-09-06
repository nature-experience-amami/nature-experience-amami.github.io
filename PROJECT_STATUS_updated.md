# Nature Experience Amami - Project Status

最終更新: 2026-09-06（日本時間）

このファイルは、Nature Experience Amami の作業状況と判断事項を、ChatGPT（ちゃっぴー）、Claude（くろちゃん）、Copilotなど、誰でも引き継げるように記録するためのメモです。

## プロジェクト概要

- 奄美大島の夜の森で見られる生き物を紹介する静的Webサイト。
- HTML、JSON、Markdown、画像、GitHub ActionsをGitHubリポジトリで管理。
- GitHub Pagesで公開する構成。公開URL: `https://nature-experience-amami.github.io/`
- 写真はPCから `images/creatures/カテゴリ/生き物ID/` へ追加する。

## 現在の構成

```text
.
├─ .github/workflows/process-creature-photos.yml
├─ content/
│  ├─ categories.json
│  └─ creatures/カテゴリ/生き物ID.md
├─ data/creatures.json
├─ images/creatures/カテゴリ/生き物ID/
├─ scripts/
│  ├─ process_creature_photos.py
│  ├─ generate_creatures_json.py
│  └─ generate_creature_pages.py      ← 2026-09-06 全面書き換え（後述）
├─ templates/
│  └─ creature.html                   ← 2026-09-06 新規（個別ページの汎用テンプレート）
├─ generated-creatures/               ← 自動生成の試作出力先（本番のcreatures/とは別）
├─ index.html
├─ hebi.html
├─ kaeru.html / kuwagata.html         ← まだ未作成（今後hebi.html基準で作る予定）
├─ contact.html
├─ tour.html
└─ Worker · JS
```

## 写真処理

### 実行スクリプト

```text
scripts/process_creature_photos.py
```

実行方法:

```bash
python scripts/process_creature_photos.py
```

主な処理:

- EXIF撮影日時を取得
- 生き物IDと6桁連番でリネーム
- 撮影日時をファイル名へ追加
- 長辺を最大2000pxへリサイズ
- `Photo by Nature Experience` を画像へ焼き込み
- 処理済みファイルをスキップ
- EXIF日時がない写真を各生き物フォルダの `failed/` へ移動
- 必要な `failed/` フォルダを自動作成

重要: 処理済みJPEGには透かしが画像データとして焼き込まれています。HTMLで同じ文字を重ねると二重表示になるため、個別ページではHTML/CSSの追加透かしを使用しません。

注意（2026-09-06 判明）: 写真フォルダ名をリネームした後（例: `takachiho-hebi` → `amami-takachiho-hebi`）、処理済み写真のファイル名の頭がフォルダ名と一致しないと、このスクリプトが「未処理」と誤判定し、EXIF情報のない状態（透かし処理済みのため）として `failed/` に移動してしまう。フォルダ名をリネームしたら、中の写真ファイル名の頭も同じ名前に揃えること。

### GitHub Actions

```text
.github/workflows/process-creature-photos.yml
```

現在の動作:

- `images/creatures/**` へのpush、または手動実行で起動
- Ubuntu上でPython 3.11をセットアップ
- `fonts-liberation` をインストール
- `find` で実在する `LiberationSans-Regular.ttf` を探す
- スクリプトが探す `C:/Windows/Fonts/arial.ttf` へコピー
- Pillowをインストール
- 写真処理スクリプトを実行
- `images/creatures` に変更がある場合だけ自動commit・push
- `github-actions[bot]` による再実行を防止

注意: JSON生成ステップは現在のワークフローには含めていません。HTMLやJSONを変更する作業では、対象範囲を明確にしてから別途判断してください。

2026-09-06追記: `process-photos`ワークフロー実行時に「Node.js 20は非推奨、Node.js 24で強制実行される」という警告が出るようになった。GitHub側のランナー仕様変更によるもので、今回の変更とは無関係。ワークフロー自体は成功しており、対応不要。

## data/creatures.json の生成

```text
scripts/generate_creatures_json.py
```

`images/creatures/` の実際の写真と `content/creatures/**/*.md` から `data/creatures.json` を自動生成する。表示名(name)はMarkdownのfrontmatterから読むため、生き物が増えてもスクリプト自体は触らなくてよい設計。

### 写真フォルダ名とMarkdownのidが一致しない生き物（重要・2026-09-06に総点検）

正式名称に「アマミ」が付く生き物が多く、写真フォルダ名を後から`amami-`付きにリネームしたため、Markdownのid（まだリネーム前の名前）とズレているケースが複数ある。`MARKDOWN_ID_ALIASES`で対応済み。

```python
MARKDOWN_ID_ALIASES = {
    ("hebi", "ryuukyuu-aohebi"): "ryukyu-ao-hebi",
    ("hebi", "amami-takachiho-hebi"): "takachiho-hebi",
    ("kaeru", "amami-hanasaki-gaeru"): "hanasaki-gaeru",
    ("kaeru", "amami-ishikawa-gaeru"): "ishikawa-gaeru",
    ("kuwagata", "amami-marubane-kuwagata"): "marubane-kuwagata",
    ("kuwagata", "amami-nebuto-kuwagata"): "nebuto-kuwagata",
    ("kuwagata", "amami-nokogiri-kuwagata"): "nokogiri-kuwagata",
    ("kuwagata", "amami-shika-kuwagata"): "shika-kuwagata",
    ("kuwagata", "amami-miyama-kuwagata"): "miyama-kuwagata",
    ("kuwagata", "amami-ko-kuwagata"): "ko-kuwagata",
}
```

未使用の古いフォルダ（カエルの無印`ishikawa-gaeru`）は`IGNORED_SPECIES_DIRS`で除外済み。

2026-09-06時点で写真フォルダが空（未撮影）のため`data/creatures.json`にまだ載っていない種: `haroweru-amagaeru`（カエル）、`ruisu-tsuno-hyotan-kuwagata`（クワガタ）、`amami-marubane-kuwagata`（クワガタ）。写真が入り次第、スクリプト再実行で自動反映される。

将来的な課題: Markdownのid自体を「amami-」付きの正式名称に統一したいという要望があるが、影響範囲が広い（ファイル名・frontmatterのid・生成スクリプトのalias表・related参照・一覧ページのリンク）ため、今回は着手せず後日まとめて専用作業とする方針。

## ヘビ一覧ページ（hebi.html）

ヘビ7種類を表示する一覧ページ。表示順:

1. リュウキュウアオヘビ
2. アカマタ
3. ガラスヒバァ
4. ヒメハブ
5. ハブ
6. ヒャン
7. アマミタカチホヘビ

2026-09-06更新:

- 各生き物カードの`<img>`に`data-id`属性（写真フォルダ名）を追加し、ページ読み込み時に`data/creatures.json`から**ランダムな写真を1枚選んで表示する**JavaScriptを追加した（以前は固定写真1枚だった）。写真を増やしても自動で反映される。
- アマミタカチホヘビのリンク切れ（`href`が`amami-takachiho-hebi.html`になっていたが、実際の個別ページは`takachiho-hebi.html`）を修正。
- アマミタカチホヘビの画像パス切れ（フォルダ名リネーム前の古いパスのままだった）を修正。

未着手: `kaeru.html`・`kuwagata.html`はまだ存在しない。`hebi.html`を基準に作成する予定（写真ランダム表示の仕組みも組み込む）。

## 個別ページの自動生成（2026-09-06 くろちゃんが本格実装、方針を大きく更新）

**重要: 「個別HTMLを自動生成するスクリプトは存在しない」という09-03/09-04時点の記述は古くなりました。2026-09-06に本格実装が完了しています。**

### テンプレート: `templates/creature.html`

`habu.html`の新デザインを基準に、汎用テンプレート化した。含まれる要素:

- ヒーロー（写真＋情報パネルの分割レイアウト。PC/タブレットは横並び、幅800px以下は縦積み）
- 学名表示（Markdown本文の1段落目、`*学名*`を含む行を自動抽出）
- **危険度表示**（カテゴリで自動切り替え）
  - ヘビ: 危険度メーター（`danger:`の文言から自動判定。無毒15%・毒あり60%・猛毒90%）
  - ヘビ以外: 保護・採集バッジ（「禁止」を含む→警告、「無毒」→安全、「採集可」→中立的に「観察できる生き物」と表示。採集を勧める書き方はしない）
- 観察時期タイムライン（12ヶ月の帯、frontmatterの`months`優先、なければ本文/写真の日付から自動集計）
- ギャラリー＋ライトボックス（写真0枚/1枚/2〜3枚/4枚以上で表示分岐。スマホでは縦一列表示）
- ABOUT本文（Markdown本文をそのまま表示）
- **SAFETYセクション**（全ページ共通メッセージ＋「禁止」に該当する種への個別警告文を自動追加。下記参照）
- 関連生き物カード（related明記→同カテゴリ→同観察月の優先順位、写真の有無に関わらず表示）
- ナイトツアーCTA

今回見送った項目（あとでMarkdownに情報を追記してから対応する「やることリスト」）:

- バッジ列の「夜行性」「全長◯cm」相当の表示
- ECOLOGY／OBSERVATIONの独立セクション（今はABOUT1本にまとめている）
- hero-teaser（一言紹介文）
- クワガタの観察時期（`months:`）の精査（写真EXIFだけでなく本文記載との照合）
- 生き物ごとの詳しい注意事項（特別保護区内でよく見られる、等）

### 全ページ共通のSAFETYメッセージ（確定文言）

> 奄美の生き物は、写真におさめて楽しみましょう。生き物によっては、法律や条例で捕獲・採集・持ち出しが禁止されています。国立公園内の特別保護区では、採集そのものが禁止されているエリアもあります。それぞれの生き物のページで注意事項を確認し、訪れる場所のルールも事前に確認してから観察してください。

決定の背景: 奄美島内で「生き物を持ち出さないで」という声明が出ており、採集を勧めるトーンにしたくない。ただし「希少＝禁止」ではない（天然記念物でなくても採集禁止の種がいる一方、天然記念物でなくても採集可能な希少種もいる）ため、`danger:`に「禁止」の文字列が含まれるかどうかで機械的に判定する方式にした。

### 生成スクリプト: `scripts/generate_creature_pages.py`（全面書き換え）

- 生成対象を「TARGETS固定の3種類（habu, akamata, amami-aka-gaeru）」から**「`content/creatures/`で見つかった生き物すべて」**に変更。結果として、今回のヘビ・カエル・クワガタ以外に、既存Markdownがあった`honyu`（哺乳類）・`tori`（鳥）・`tokage-imori`（トカゲ・イモリ）分も一緒に生成される（今回のミッション外なので本番へは反映しない）。
- 写真フォルダのalias表を`generate_creatures_json.py`と統一。
- 出力先は引き続き`generated-creatures/`。本番`creatures/`への反映は別途手動コピーで行う。

### 動作確認済み

テスト用データで実行し、次のパターンが正しく動作することを確認済み:

- 写真なし（プレースホルダー「写真準備中」表示）
- 毒あり（ヘビの危険度メーター）
- 禁止種（警告バッジ＋SAFETYへの追加警告文）

## 個別ページに関する重要な設計判断（2026-09-06版・上書き更新）

- 個別ページの自動生成は**実装済み**（`scripts/generate_creature_pages.py` + `templates/creature.html`）。今後は「見つかったMarkdownすべてを自動生成する」方式に一本化し、手動でコピーして個別に作り込むことはしない。
- `generate_creatures_json.py`は`data/creatures.json`の生成専用（AIチャットが参照するデータ）。`generate_creature_pages.py`は個別ページHTML生成専用。役割が違うので混同しないこと（似た名前だが別物）。
- `content/creatures/**/*.md`は個別ページの内容の基礎資料。写真が0枚でもMarkdownがあればページを生成する。
- 個別ページは`creatures/カテゴリ/`以下に置くため、画像・共通ページへのリンクは`../../`から始める。
- 写真フォルダ名はMarkdownのIDと必ずしも一致しない。実際のフォルダを確認する（アリアス対応表を参照）。
- 処理済みJPEGの透かしを二重表示しない。個別ページにHTML/CSSの透かしを追加しない。
- 危険度メーター・観察時期タイムラインは、カテゴリーをまたいで使い回せる共通パーツとして設計している（ただし危険度の見せ方はヘビとそれ以外で分岐）。

## 未完了の作業（2026-09-06時点）

### 本番creatures/への反映（最優先）

`generated-creatures/hebi` `generated-creatures/kaeru` `generated-creatures/kuwagata` の中身をブラウザで最終確認した上で、本番の`creatures/`へコピーする必要がある。

```powershell
Copy-Item generated-creatures\hebi\* creatures\hebi\ -Force
Copy-Item generated-creatures\kaeru\* creatures\kaeru\ -Force
Copy-Item generated-creatures\kuwagata\* creatures\kuwagata\ -Force
```

現状（本番`creatures/`）:

- `habu.html`・`akamata.html`は**まだ旧デザイン**（ECOLOGY/OBSERVATIONのある2026-09-03版）のまま
- ガラスヒバァ・ヒメハブ・ヒャン・リュウキュウアオヘビ・アマミタカチホヘビの個別ページは**まだ本番に存在しない**（`hebi.html`からリンクすると404になる）
- カエル・クワガタの個別ページは9種類とも本番に一度も存在したことがない

この反映がまだ**commit・push前**なので、本番サイトの見た目は変わっていない。

### 一覧ページ

`kaeru.html`・`kuwagata.html`をまだ作成していない。`hebi.html`を基準に、写真ランダム表示の仕組みも含めて作る予定。

### トップページの生き物ローテーション表示

トップページで「8秒ごとに生き物が切り替わる」表示機能が、ヘビ以外のカテゴリーにも対応しているか未確認（`index.html`とその関連JSをまだ確認していない）。

### data/creatures.jsonへのクワガタ等の反映（2026-09-04にCopilotが発見、2026-09-06に対応完了）

以前は`data/creatures.json`にヘビ7種類分しか入っておらずAIチャットがクワガタに回答できない問題があったが、2026-09-06にカエル・クワガタ分も反映済み。あわせてフォルダ名のズレも解消済み（上記「写真フォルダ名とMarkdownのidが一致しない生き物」参照）。

## あとでやることリスト（今回は見送った項目）

- Markdownのid（ファイル名・frontmatterのid）を、正式名称に合わせて「amami-」付きに統一する（影響範囲が広いため、まとめて専用作業として後日実施）
- OBSERVATIONセクション（季節・時間帯・場所・観察のポイントの4項目）用の情報をMarkdownに追記
- hero-teaser（生き物ページ冒頭の一言紹介文）用の情報をMarkdownに追記
- クワガタの観察時期（`months:`）を、写真のEXIF日付だけでなく本文の記載と照らし合わせて精査
- 生き物ごとの詳しい注意事項（特別保護区内でよく見られる、等）をMarkdownに追記

## 現在のGit状態

2026-09-04時点の記録では、以下がローカルに未push状態だった（この記録作成時点で最新のGit状態は要確認）。

```text
main...origin/main [ahead 3]
```

```text
d5b4c4a Merge branch 'main' of https://github.com/tetsu5686/nature-experience-amami
04b3088 fix: update ryukyu aohebi image
bef5f4d feat: update snake overview page
73f36d3 (origin/main) chore: process creature photos
```

2026-09-06のセッションでは、次のファイルの変更をユーザーが手動でリポジトリへ反映済み（写真処理・データ再生成分）:

- `scripts/generate_creatures_json.py`（MARKDOWN_ID_ALIASES追加・IGNORED_SPECIES_DIRS追加）
- `data/creatures.json`（再生成）
- `images/creatures/`配下（`process_creature_photos.py`実行による写真処理、`amami-takachiho-hebi`フォルダ内のファイル名修正）

次のファイルはユーザーが受け取り済みだが、**commit・push状況は本記録作成時点で未確認**:

- `templates/creature.html`（新規）
- `scripts/generate_creature_pages.py`（全面書き換え）
- `hebi.html`（写真ランダム表示・リンク修正版）
- `generated-creatures/hebi・kaeru・kuwagata`配下の生成済みHTML（本番`creatures/`へはまだ未反映）

Pushする前にGitHub側の履歴と、未追跡ファイルを必ず確認すること。

## 作業ルール

1. 作業前に変更対象ファイルを明記する。
2. 指定されていないHTML、JSON、Worker、Python、写真は変更しない。
3. 既存デザインを再利用し、大幅な作り直しを避ける。
4. 写真フォルダとファイル名を実際に確認してから参照する。
5. 処理済み写真の焼き込み透かしとHTML透かしを二重にしない。
6. Commit / Pushは、明示的な依頼がある場合だけ実行する。
7. Commitする場合は、対象ファイルだけを明示的にstageする。
8. 他のAIが作業を続けるときは、このファイルの「未完了の作業」「現在のGit状態」「作業ルール」を先に読む。
9. （2026-09-06追記）Windows環境はPowerShellを使用。`dir /b`のようなcmd専用オプションは使えないため`Get-ChildItem`を使う。
10. （2026-09-06追記）同じファイルを何度も渡す場合はダウンロードフォルダに重複が溜まりやすいので、「今回で◯回目」と明記し、古い版は削除してから最新版に置き換えるよう案内する。

## 更新方法

作業を行ったAIは、必要に応じて次の項目を追記する。

- 日付
- 担当AIまたは作業者
- 変更ファイル
- 変更理由
- 確認したこと
- 未完了事項
- Commit SHA（commitした場合のみ）
- Push済みかどうか

既存の記録を削除せず、時系列の変更履歴を末尾へ追加する。

## 変更履歴

### 2026-09-03

- GitHub Actionsで写真処理を自動化するワークフローを整備。
- Ubuntu上でLiberation Sansを探してArial互換フォントとして配置する処理を追加。
- `generate_creatures_json.py`はワークフローから外し、写真処理対象を`images/creatures`に限定。
- `hebi.html`の7種類の写真参照を実在する写真へ合わせた。
- `hebi.html`を`bef5f4d`と`04b3088`でcommitした。Pushはこの記録作成時点で未確認。
- `creatures/hebi/habu.html`をハブ個別ページの試作として作成。
- ハブページにランダム写真表示を追加。
- 処理済み写真の焼き込み透かしとHTML/CSS透かしの二重表示を調査し、HTML/CSS側の透かしを削除。
- 左側の大きいギャラリー写真に`object-fit: contain`を追加。
- Habu試作ページは未commit・未push。
- 今後はHabu試作をブラウザ確認してから、残り6ページを作成する。

（担当: Claude／くろちゃん）

- 旧simdifサイト（カエル・クワガタ・代表的な生き物ページ）を確認し、個別ページの項目（分類・学名・サイズ・時期・生息場所・特徴文・注意事項・写真）がカテゴリー間で共通化できることを確認した。
- ヒーロー画像の「大きすぎる/小さすぎる」問題を解決するため、個別ページのデザインを刷新する方針を決定。分割ヒーロー（写真＋情報パネル）、危険度メーター、観察時期タイムラインという、カテゴリーをまたいで使い回せる共通パーツを設計した。
- ハブを例にしたデザインプロトタイプ（`creature-template-preview.html`）を作成し、確認後にABOUTセクションを拡張・ECOLOGYセクションを新設した。
- 上記デザインを反映した新しい`creatures/hebi/habu.html`のコードを作成し、ユーザーに渡した（写真のランダム表示の仕組みは維持、5枚シャッフルしヒーロー1枚＋ギャラリー3枚に割り当て）。ナビ・CTAのリンクは`creatures/hebi/`配下からの相対パス（`../../`）に修正。
- このコードは、ユーザーが手動でリポジトリの`creatures/hebi/habu.html`に貼り付ける予定。この記録作成時点で、実際の反映・commit・pushは未確認。
- 未完了事項: 新デザイン版habu.htmlのブラウザ確認、commit・push、残り6ページへの展開。
- Commit SHA: なし（未commit）。Push: 未確認。

### 2026-09-04

- AIチャットの回答写真を、生き物ごとにランダム1枚だけ表示する仕様へ修正。
- AIが同じ生き物IDを複数返した場合も、フロント側とWorker側で重複排除するように変更。
- 回答写真の下に、生き物の日本語名（種名）を表示するように変更。
- 回答写真と種名をクリックすると、対応する個別生き物紹介ページへ移動するように変更。
- 現在リンクを設定しているページ:
  - `creatures/hebi/habu.html`
  - `generated-creatures/hebi/akamata.html`
  - `generated-creatures/kaeru/amami-aka-gaeru.html`
- 個別ページが未作成の生き物は、写真表示を維持しつつ`#tour`（ナイトツアー案内）へリンクする。
- リュウキュウアオヘビの写真フォルダIDとMarkdown IDの不一致に対応し、日本語名と解説をJSONへ正しく取り込めるようにした。
- `data/creatures.json`を再生成し、リュウキュウアオヘビが`リュウキュウアオヘビ`と表示されることを確認。
- 今回のコミット:
  - `1064d9a Resolve Ryukyu green snake content ID`
  - `b25daf3 Deduplicate AI creature photos`
  - `838895a Link AI creature photos to introductions`
- Push: 未確認（GitHubへ反映するには別途pushが必要）。

（担当: Copilot）

### 2026-09-04 追加確認

- `generated-creatures/`は野良ファイルではなく、Markdownを正本にした個別ページ自動生成の意図的な試作出力先であることを再確認。
- `generated-creatures/hebi/akamata.html`、`generated-creatures/kaeru/amami-aka-gaeru.html`を確認。
- 3ページは、PC・スマートフォン向けのレスポンシブレイアウト、写真あり・写真なしの表示分岐、関連生き物カード、個別ページ間の相対リンクを備えている。
- 写真ありページはヒーロー画像とギャラリーを表示し、写真なしページは「写真準備中」と解説を表示する。
- 個別ページ生成方式は、今後「自動生成方式」に一本化する方針を決定。手動で`creatures/`配下へ同じページを並行作成しない。
- ヘビ全体、続いてカエル・クワガタへ展開する前に、まず自動生成テンプレートを必要に応じて改善し、生成結果を確認する。
- AIチャットから生成済み個別ページへのリンクは、試作中の暫定リンクではなく、自動生成方式の本番導線として維持する。
- 生成済みページがまだない生き物は、従来どおりナイトツアー案内（`#tour`）へリンクする。
- 今後の自動生成で確認する項目:
  - 写真0枚・1枚・2〜3枚・4枚以上のギャラリー表示
  - スマートフォンでのヒーロー、本文、関連カードの表示
  - 写真フォルダIDとMarkdown IDが異なる生き物の名前・解説解決
  - AIチャット、Topページ、一覧ページからのリンク整合性

（担当: Copilot）

### 2026-09-04 ツアーページ正式名称

- `tour.html.html`を`tour.html`へ変更。
- トップページ上段の「ナイトツアーを見る」ボタンを`tour.html`への直接リンクへ変更。
- `hebi.html`など既存の`tour.html`参照と正式ファイル名を統一。
- 今後追加するツアー導線も`tour.html`を使用する。
- Commit・Push: 未実施。

（担当: Copilot）

### 2026-09-04 GitHubユーザー名・公開URLの移行

- 最終的な公開URLを`https://tetsu5686.github.io/nature-experience-amami/`から`https://nature-experience-amami.github.io/`（ルートURL）にするため、以下を実施し完了した。
  1. GitHubユーザー名を`tetsu5686`→`nature-experience-amami`に変更（希望名が一時的に他者使用中に見えたが、結局空いていたためそのまま確定）。
  2. リポジトリ名を`nature-experience-amami`→`nature-experience-amami.github.io`にリネーム。新規リポジトリを作らず既存リポジトリのリネームのみで、写真・GitHub Actions・Pages設定・コミット履歴はすべてそのまま引き継がれた。
  3. Cloudflare Worker（ワーカーズ.txt）内の`CREATURES_URL`を`https://nature-experience-amami.github.io/data/creatures.json`に変更し、デプロイ。
  4. Worker環境変数`ALLOWED_ORIGIN`を`https://nature-experience-amami.github.io`に変更し、デプロイ。
  5. GitHub Desktopのリモート・ログインを新ユーザー名に更新（一度サインインが`x-github-desktop-auth://`のリダイレクトで止まったが、リンクを再クリックして解消）。
- HTML/CSS/JSは全て相対パスで書かれていたため、上記以外のコード修正は不要だった。
- 動作確認済み: 新URLでトップページ・写真・ヘビ一覧・個別ページ・お問い合わせ・AIチャットすべて正常。旧URLは想定通り404（GitHub Pagesはユーザー名/リポジトリ名変更時にリダイレクトされない仕様のため）。
- 移行の過程で、AIチャットにクワガタについて質問しても回答が出ないことに気づき、原因が`data/creatures.json`への未反映であることを特定（詳細は「未完了の作業」参照）。
- Commit・Push: 今回の変更はGitHubのユーザー名・リポジトリ名設定とCloudflare Worker側の変更のみで、リポジトリ内のファイル変更・commitは無し。

（担当: Claude／くろちゃん）

### 2026-09-04 トップページのツアー導線

- FIELD NOTEの直後に、短い「NIGHT FIELD TOUR」案内セクションを追加。
- 「奄美の夜の森へ」と表示し、詳細・料金ページ`tour.html`へリンクするボタンを配置。
- トップページにツアー詳細や料金を重複掲載せず、詳しい内容は`tour.html`に集約する方針を反映。
- 上段の「ナイトツアーを見る」ボタンと、中段のツアー案内ボタンを同じ`tour.html`へ統一。
- ツアー案内セクションをAIチャットの直後から移動し、「ナイトツアーの流れ」の直後に配置。
- セクションの背景色を、ヒーローから順に黒・緑・黒・緑・黒となるよう調整。
- Commit・Push: 未実施。

（担当: Copilot）

### 2026-09-06 個別ページ自動生成の本格実装・データ整合性の総点検

- `scripts/generate_creatures_json.py`を修正: カエル・クワガタ・ヘビの写真フォルダ名とMarkdownのidのズレ（計10件）を`MARKDOWN_ID_ALIASES`に登録。未使用の古いフォルダ（カエルの無印`ishikawa-gaeru`）を`IGNORED_SPECIES_DIRS`で除外。
- 未処理の生写真（透かし・リサイズ前）が複数種に混ざっていたため`process_creature_photos.py`を実行。あわせて、フォルダ名リネーム後にファイル名の頭が揃っていないと誤って`failed/`へ移動される問題を発見・対処（`amami-takachiho-hebi`で発生）。
- `data/creatures.json`を再生成し、ヘビ8種＋カエル・クワガタ（写真ありのみ）が正しく反映されることを確認。
- `templates/creature.html`を新規作成。habu.htmlの新デザインを基準に、全カテゴリー共通で使える汎用テンプレートとして設計（詳細は「個別ページの自動生成」セクション参照）。
- `scripts/generate_creature_pages.py`を全面書き換え。生成対象をTARGETS固定の3種類から「見つかったMarkdownすべて」に変更。危険度表示のロジック（ヘビ=メーター、それ以外=バッジ）、SAFETYセクションの自動生成、学名の自動分離などを実装。
- 全ページ共通のSAFETYメッセージの文言を確定（「奄美の生き物は、写真におさめて楽しみましょう。生き物によっては、法律や条例で捕獲・採集・持ち出しが禁止されています。国立公園内の特別保護区では、採集そのものが禁止されているエリアもあります。それぞれの生き物のページで注意事項を確認し、訪れる場所のルールも事前に確認してから観察してください。」）。
- `hebi.html`を修正: 各カードに`data-id`属性を追加し、`data/creatures.json`から写真をランダム表示するJavaScriptを追加。アマミタカチホヘビのリンク切れ・画像パス切れを修正。
- スマホ表示時のギャラリーを、2列表示から縦一列表示に修正。
- ヘビ7種・カエル8種・クワガタ9種（あわせて`honyu`・`tori`・`tokage-imori`分も既存Markdownがあるため一緒に）を`generated-creatures/`に生成済み。
- 未完了事項: 生成した`generated-creatures/hebi・kaeru・kuwagata`のブラウザ最終確認と、本番`creatures/`への反映（コピー）。`kaeru.html`・`kuwagata.html`一覧ページの作成。トップページの生き物ローテーション表示がヘビ以外に対応しているかの確認。
- Commit SHA: なし（この記録作成時点で、templates/creature.html・generate_creature_pages.py・hebi.htmlの反映・commit状況は未確認。generate_creatures_json.py・data/creatures.json・写真処理分は反映済みと聞いているが、commit/push状況は要確認）。

（担当: Claude／くろちゃん）

### 2026-09-06 一覧ページ自動生成の試作

- 本番の`hebi.html`は変更せず、一覧ページの試作を`generated-categories/hebi.html`へ生成。
- `content/category-pages/hebi.md`を新設し、ヒーロー・カテゴリ紹介・注意事項・一覧見出しなど、カテゴリ固有の文章を管理する正本とした。
- `templates/category.html`を新設。既存の`hebi.html`のヘッダー、ヒーロー、紹介、2列カード、ツアーCTAの世界観を基準にした共通テンプレートである。
- `scripts/generate_category_pages.py`を新設。カテゴリ文章、`content/creatures/hebi/*.md`、写真フォルダ、生成済み個別ページを読み、一覧カードを自動生成する。
- カードは写真、危険・注意の補助ラベル、種名、短い解説、個別ページリンクを表示する。写真なしの場合は「写真準備中」とし、個別ページ未生成の場合はリンクを無効化して「PAGE PREPARING」と表示する。
- ヘビ7種のカードと、生成済み個別ページへのリンクを生成して確認した。
- 無毒の生き物が警告色にならないよう、補助ラベルの色分けは「猛毒」または「毒あり」の場合だけ警告色にする。
- 本番反映、Commit・Push: 未実施。

（担当: Copilot）

### 2026-09-06 トップページの生き物案内

- `index.html`の「NIGHT FIELD TOUR」案内の直後に、緑背景の「CREATURE GUIDE」セクションを追加。
- 見出しは「奄美の生き物を知る」、ボタンは既存のツアー導線と統一したオレンジ色の「ヘビを見る →」とした。
- ボタンは、現時点で一覧ページが完成している`hebi.html`へリンクする。
- カエル・クワガタなどの一覧ページ完成後、同じセクションへ対応ボタンを追加する。
- Commit・Push: 未実施。

（担当: Copilot）
