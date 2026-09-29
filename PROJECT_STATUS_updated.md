# Nature Experience Amami - Project Status

最終更新: 2026-09-28（日本時間）

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
- （2026-09-28追記）写真フォルダは`images/creatures/カテゴリー/生き物ID/`の直下になければ、`images/creatures/カテゴリー/グループ名/生き物ID/`（例: `aquatic-insects/sonota/ashibutome-mizumushi/`）も自動で探す。`generate_creature_pages.py`・`generate_category_pages.py`・`generate_zukan_page.py`の`photo_files()`は同じ探し方に揃えてある。グループフォルダに種を追加するときは対応表への追記は不要（IDとフォルダ名が違う場合だけ追記する）。
- 処理済みJPEGの透かしを二重表示しない。個別ページにHTML/CSSの透かしを追加しない。
- 危険度メーター・観察時期タイムラインは、カテゴリーをまたいで使い回せる共通パーツとして設計している（ただし危険度の見せ方はヘビとそれ以外で分岐）。
- （2026-09-28追記、オーナー決定）図鑑ページ・カテゴリーページ・個別ページの関連カードは「奄美で見られる生き物」を紹介する場所なので、昼行性（`activity: diurnal`）や`night_observable: false`の種も表示してよい。ナイトツアーで出会える種に絞るのは、トップページの大きな写真とThreadsのツアー案内だけ

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
- ~~（2026-09-24追加）トップページの大きな写真から昼行性の種を除外する~~ → 2026-09-24に対応済み（`activity` / `night_observable` をMarkdownに追加し、トップの写真選びに反映。変更履歴参照）
- ~~オキナワキノボリトカゲ・アマミヒメトカゲなど、写真フォルダだけあってMarkdownがない種は、Markdownを作るときに`activity`（キノボリトカゲは`diurnal`＋`night_observable: true`、ヤモリの仲間は`nocturnal`）も書く~~ → 2026-09-29にオキナワキノボリトカゲ・アマミヒメトカゲのMarkdownを作成済み（変更履歴参照）
- ~~（2026-09-28追加）個別ページの「この生き物に興味がある方へ」（関連カード）が、種の多いカテゴリーではどのページでも同じ顔ぶれになる。`generate_creature_pages.py`の`related_cards()`が同じカテゴリーの種をID順に先頭から並べて8件で打ち切るため。水生昆虫では25ページすべてに同じ8種が出て、15種は一度も出ない。鳥・甲虫・昆虫その他も同じ可能性あり（未確認）。直し方の案（オーナー未決定）: A「今のページの次の種から順に選ぶ」、B「同じカテゴリーは4〜5件にして残りを他カテゴリーにする」。あわせて`night_observable: false`の種を関連カードでどう扱うかも決める~~ → 2026-09-28に案Bで対応済み（変更履歴参照）。昼行性・`night_observable: false`の種も関連カードに出してよい（オーナー決定、変更履歴参照）

## 現在のGit状態

（この節は書かれた時点のスナップショット。最新の状況は必ず`git status`で再確認すること。以下は2026-09-12総点検時点）

- ブランチ`main`はリモート`origin/main`と同期済み（ahead/behind無し）。
- 直近のコミット: `69207ee photos` → `b95a0d3 content` → `7f45dbd suisei-kontyu` → `a74409f Merge` → `a6526f9 categories`。
- ワーキングツリーに**未commitの変更**あり（詳細は変更履歴「2026-09-12 全体棚卸し」参照）:
  - 変更: `content/creatures/tori/ootora-tsugumi.md`, `index.html`
  - 削除: `content/creatures/tori/oo-tora-tsugumi.md`, `images/creatures/tori/sasiba/sasiba_000005_20250123_10.jpg`
  - 未追跡（新規）: `content/creatures/tori/amami-yamashigi.md`

2026-09-04時点の記録（参考・履歴として残す）:

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
11. （2026-09-28追記）ホーム画面に追加したアプリ（予約管理など）は、アイコンを削除するとアプリの中のデータも消える。アイコンや名前を変えるために追加し直すときは、①古いアプリの中でバックアップを取り件数を確認 → ②古いアプリは残したまま新しく追加 → ③新しいアプリで復元して件数を確認 → ④最後に古いアプリを削除、の順で進める。中身の更新だけなら「🔄 更新を確認」で足り、追加し直す必要はない

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

### 2026-09-06〜07 図鑑・導線・問い合わせページの更新

#### 生き物図鑑と写真

- ヘビ・カエル・クワガタのカテゴリ一覧ページを整備し、各カードの写真はページを開くたびにランダム表示されるようにした。
- 個別の生き物ページは、複数の写真がある場合にヒーロー写真をランダム表示する。画像の暗いオーバーレイを外し、写真を見やすくした。
- トップページの「○月、森はこんな顔をしている」では、最大6種類を表示する。個別ページがある生き物は、すべて対応する個別ページへリンクする。
- 画像を長辺1920px・JPEG品質82・`Photo by Nature Experience`の透かし付きで最適化し、`data/creatures.json`と生成ページを更新した。

#### ナビゲーションとスマホ表示

- トップページとカテゴリ一覧ページに、ヘビ・カエル・クワガタ一覧へのナビゲーションを追加した。
- 個別ページの上部ナビゲーションには、現在表示中のカテゴリを含む全カテゴリ一覧を表示する。
- スマホの個別ページ・カテゴリ一覧ページは、サイト名とお問い合わせを上段、横スクロールできるカテゴリ一覧を下段に分けた。
- スマホ縦画面のトップ写真は4:3の大きさを維持し、カテゴリーナビの下から始まるよう位置を調整した。写真の下端は小見出しとメイン見出しの間に置き、文字が読みやすい構成にした。横向き画面とPC表示は従来どおり全面表示とする。

#### AIチャット

- 季節の回答は写真の撮影時期ではなく、生き物データの観察時期をもとに案内する。
- 天候・気温・年ごとの状況によって観察できない場合があること、および回答に時間がかかる場合があることを画面上に明記した。

#### お問い合わせページ

- 電話、公式LINE、フォームの3つから問い合わせ方法を選べるようにした。
- フォームには、名前、メールアドレス、参加人数、希望日（第1〜第3希望）、宿泊先、見たい生き物、メッセージを追加した。
- Formspreeによるメール送信を設定済み。電話リンク、公式LINEリンク、フォーム送信メールの到達を確認済み。
- 迷惑送信対策のハニーポットを追加し、送信中表示、送信成功・失敗時の案内を実装した。
- 送信成功時のメッセージがフォーム非表示とともに消える不具合を修正した。
- 「通常2日以内に返信」「送信時点では予約確定ではない」「入力情報の利用目的」をフォームに明記し、大人の人数は1人以上とした。

#### 今後の作業

- Google Search Consoleへ公開URLを登録し、インデックス登録をリクエストする。
- `sitemap.xml`、`robots.txt`、構造化データ、プライバシー案内を整備して検索流入の基礎を作る。隠しキーワードやキーワードの詰め込みは行わない。
- 内容が十分整ったら、旧サイト上部に新サイトへの案内を置き、XとInstagramのプロフィール・投稿へ新サイトURLを掲載する。旧サイトは当面残して並行運用する。
- 公開内容が固まった段階で、GA4またはCloudflareを使ったアクセス解析を導入する。日別・月別・参照元・閲覧ページ・端末・おおよその地域傾向を確認できるようにし、専用管理画面が必要な場合はサーバー側で認証する。

#### 関連コミット

- `26fe3d4 Refresh pages with optimized photos`
- `5bf8308 Clarify creature guide and AI responses`
- `819df6a Improve mobile creature navigation`
- `694d4b5 Add category navigation sitewide`
- `82ce5d4 Improve mobile hero photo framing`
- `922914b Move mobile hero photo lower`
- `ab5cb39 Lower mobile hero below category navigation`
- `5d6b284 Show all categories on creature pages`
- `b55bea0 Add contact form and inquiry options`

（担当: Copilot）

### 2026-09-12 全体棚卸し（フォルダ総点検・現状確認のみ、コード変更なし）

今回はコードの変更は行わず、リポジトリ全体（`content/` `images/` `data/` `creatures/` `generated-*/` `scripts/` `templates/`）を確認し、どこまで進んでいるかを整理した。

#### 09-07以降に起きていたこと

前回の記録（09-06〜07）以降、`a6526f9`〜`69207ee`の5コミットで、ヘビ・カエル・クワガタ以外のカテゴリー（哺乳類・鳥・トカゲ・昆虫・水生昆虫・貝・甲殻類その他）向けの**生写真（未処理）の大量投入**が進んでいた。あわせて`content/creatures/honyu/watase-jinezumi.md`、`content/creatures/tori/oo-tora-tsugumi.md`など数件のcontent mdも追加されている。これは「サイトの対象カテゴリーを大きく広げる準備段階」であり、今回のような全体確認をしないと進捗が見えにくい状態だった。

#### カテゴリー別パイプライン進捗（写真→自動処理→content md→data/creatures.json→個別ページ→一覧ページ→トップ導線）

| カテゴリー | 写真処理 | content md | data/creatures.json | 個別ページ(本番`creatures/`) | 一覧ページ | トップ導線 |
|---|---|---|---|---|---|---|
| ヘビ | ほぼ完了（未処理1枚） | 7種 | 8件 | 7/7 | `generated-categories/hebi.html`（本番導線化済み） | ○ |
| カエル・イモリ | ほぼ完了（未処理1枚） | 10種 | 11件 | **8/10**（イボイモリ・シリケンイモリの2種のみ本番未反映） | `generated-categories/kaeru.html` | ○ |
| クワガタ | ほぼ完了（未処理2枚） | 9種 | 9件 | 9/9 | `generated-categories/kuwagata.html` | ○ |
| 哺乳類 | 途中（未処理5枚、`toge-nezumi`は写真フォルダ自体が無い） | 4種 | 3件 | **0/4**（`generated-creatures/honyu/`に試作のみ、本番`creatures/honyu/`は未作成） | なし | なし |
| 鳥 | 途中（未処理4枚） | 5種（うち重複・整理待ち2件、下記参照） | 10件（content未整備の7種も写真フォルダだけでJSONに機械的に列挙されている） | **0/5**（本番`creatures/tori/`は未作成） | なし | なし |
| トカゲ | 初期（未処理3枚） | 0種（contentディレクトリ自体まだ無い） | 2件（フォルダのみ、名前・解説なし） | 0 | なし | なし |
| 昆虫その他 | 初期（未処理56枚） | 0種 | 10件（同上） | 0 | なし | なし |
| 水生昆虫・貝・甲殻類（kani/sonota/suisei-konntyuu） | 初期（未処理合計70枚、水生昆虫だけで65枚） | 0種 | 0件（未処理のため写真自体がまだ集計対象外） | 0 | なし | なし |

「ほぼ完了」の3カテゴリー（ヘビ・カエル・クワガタ）は写真→公開ページまで一気通貫で回っている。哺乳類・鳥は「content mdと写真はあるが本番個別ページが無い」段階、それ以外（トカゲ・昆虫・水生昆虫・貝・甲殻類）は「生写真を集めている最中で、まだ名前も解説も無い」段階、という3段階の進み方になっている。

#### 発見した要修正事項（今回は記録のみ、修正は未実施）

1. **鳥カテゴリーに重複content mdが2組見つかった。**
   - `content/creatures/tori/oo-tora-tsugumi.md`（id: oo-tora-tsugumi）と`content/creatures/tori/ootora-tsugumi.md`（id: ootora-tsugumi）が同じ「オオトラツグミ」を指す重複ファイルだった。**この統合作業は既に着手済み・未commit**（ワーキングツリーで`oo-tora-tsugumi.md`を削除し、`ootora-tsugumi.md`側に本文・`danger`・`months`を統合する形で修正中）。
   - `content/creatures/tori/yama-shigi.md`（id: yama-shigi, name: アマミヤマシギ）と、今回新規追加された未追跡ファイル`content/creatures/tori/amami-yamashigi.md`（id: amami-yamashigi, name: アマミヤマシギ）も同種の重複。`yama-shigi.md`には対応する写真フォルダが無く（`images/creatures/tori/yama-shigi/`は存在しない）、`amami-yamashigi.md`側には写真が1枚ある。**こちらは未着手**。オオトラツグミと同じ要領で、`yama-shigi.md`を削除して`amami-yamashigi.md`に一本化するのが妥当と思われる。
2. **オオトラツグミの写真フォルダ名がidと一致していない。** 統合後のid案は`oo-tora-tsugumi`（ハイフンあり）だが、実際の写真フォルダは`images/creatures/tori/oo-toratsugumi/`（`tora`の前にハイフンなし）。かつフォルダ内の写真`_8091848.JPG`は未処理（連番リネーム前）のため、現状は`data/creatures.json`にオオトラツグミが**一件も載っていない**。写真処理の実行に加え、`generate_creatures_json.py`の`MARKDOWN_ID_ALIASES`へのtori用エイリアス追加、またはフォルダ名の統一が必要。
3. **`images/creatures/honyuurui/`というフォルダ名と、`content/categories.json`の哺乳類キー`honyu`が食い違っている。** そのため`data/creatures.json`内の哺乳類エントリの`category_name`が「哺乳類」ではなく生の値`honyuurui`のまま出力されている（`categories.json`にちゃんとした表示名を引けていない）。同様に、写真投入が始まっている`kani`（甲殻類）・`suisei-konntyuu`（水生昆虫）という画像フォルダ名は`content/categories.json`に対応するキーが無い（`categories.json`には`sonota`はあるが`kani`・`suisei-konntyuu`は無い）。写真処理が進んで反映され始める前に、`categories.json`側のキーをフォルダ名と合わせるか、フォルダ名を`categories.json`に合わせて統一しておく必要がある。
4. **`index.html`の未commit変更が、まだ存在しないページへリンクしている。** ワーキングツリー上の`index.html`に、上部ナビと「CREATURE GUIDE」セクションへ「代表的な生き物」→`highlights.html`のリンクが追加されているが、`highlights.html`はリポジトリ内に存在しない（作成前にリンクだけ先に追加した状態）。commit・pushする前に`highlights.html`本体を用意するか、リンク追加を一旦保留する必要がある。
5. **`generated-creatures/tokage/iboimori.html`・`generated-creatures/tokage/shiriken-imori.html`は古いカテゴリー分類の残骸。** イボイモリ・シリケンイモリは現在`content/creatures/kaeru/`配下（両生類カテゴリー）にcontentがあるが、`generated-creatures/`にはカテゴリー変更前の`tokage`（トカゲ）フォルダ配下にも生成物が残っている。実害は無いが紛らわしいので、次回`generate_creature_pages.py`を再実行する際に古い出力を掃除したほうがよい。
6. **直近の生写真投入コミット（`7f45dbd` `69207ee`）以降、`chore: process creature photos`という自動処理コミットがまだ発生していない**（直近のbotコミットは`07342c2`でこれより古い）。GitHub Actionsのワークフロー自体は`images/creatures/**`へのpushで自動起動する設定なので、起動しているか・失敗していないかをGitHub側のActionsタブで確認したほうがよい（ローカルからは実行状況を確認できなかった）。

#### 現在ワーキングツリーにある未commitの変更（今回の点検で発見・中身を確認したのみ）

```text
変更: content/creatures/tori/ootora-tsugumi.md
変更: index.html
削除: content/creatures/tori/oo-tora-tsugumi.md
削除: images/creatures/tori/sasiba/sasiba_000005_20250123_10.jpg
未追跡: content/creatures/tori/amami-yamashigi.md
```

上記1・4に対応する内容。まだ誰もcommitしていない状態なので、次にこのファイルを触るAI/担当者は、ユーザーの意図（オオトラツグミ統合は完了しているか、highlights.htmlは別途用意する予定か）を確認してからcommitすること。

#### 今回は行わなかったこと（確認のみ）

- ブラウザでの表示確認は行っていない（ローカルファイルの中身とGit状態の確認のみ）。
- 上記5件の要修正事項の実際の修正（コード変更・写真処理・commit）は一切行っていない。

（担当: Claude／Sonnet 5）

### 2026-09-13 「generated-」下書きフォルダを公開向けの名前にリネーム

#### 発見の経緯

ユーザーから「`hebi.html`等は今どのフォルダにあるか」「個別ページへのリンクが`creatures/`ではなく`generated-creatures/`を直接指しているのは意図的な変更か」という質問を受け、`git log`で調査。`scripts/generate_category_pages.py`の該当行(個別生き物ページへのリンクを`../generated-creatures/{category}/{id}.html`として組み立てている箇所)が、サイト立ち上げ当初の初回コミット(`77cb332`、2026-09-06)から存在する既存の仕様であり、最近何者かが変更したものではないと判明した。

#### 原因

このファイルの2026-09-12時点の記録(「現在の構成」「カテゴリー別パイプライン進捗」表)にもある通り、`generated-categories/` `generated-creatures/` は元々「自動生成の試作出力先(本番の`creatures/`とは別)」という位置づけで付けられた名前だった。しかし翻訳版(`en/es/zh/creatures/`)には正式名`creatures/`が採用された一方、日本語版だけは「試作」の名前のままGitHub Pagesで公開され続けてしまっていた。つまり「下書き」を示すはずの接頭辞`generated-`が、そのまま外部公開URLの一部になっていた。

#### 対応

影響範囲が広いため、オートモードを使わず、①棚卸し→②リネーム計画をユーザーに提示→ユーザーの明示的な承認を得てから③④実行、という段階を踏んで進めた。

1. **①棚卸し**: `generated-categories/`(4ファイル)、`generated-creatures/`(7カテゴリー53ファイル)、`en/es/zh/generated-categories/`(各4ファイル)の存在と中身を確認。`en/es/zh/creatures/`は既に正しい名前になっており対象外であることも確認。
2. **リネーム**: `git mv`で `generated-categories/`→`categories/`、`generated-creatures/`→`creatures/`、`en(es,zh)/generated-categories/`→`en(es,zh)/categories/`。
3. **③参照箇所の洗い出しと修正**: リポジトリ全体を`generated-categories`/`generated-creatures`の文字列でgrepし、生成スクリプト8本(`generate_category_pages.py` `generate_category_pages_i18n.py` `generate_creature_pages.py` `generate_creature_pages_i18n.py` `generate_creatures_json.py` `generate_highlights_page.py` `generate_zukan_page.py` `generate_zukan_page_i18n.py`)、手打ちHTML5本(`index.html` `highlights.html` `en/es/zh/index.html`)、`data/creatures.json`、`.github/workflows/process-creature-photos.yml`を新しい名前に書き換え。
4. **④再生成と検証**: 修正後のスクリプトで全ページ(JA/EN/ES/ZH計約230ファイル)を再生成。独自のリンクチェッカーで233ファイル・4297個のローカルhrefを検証し、破損リンク0件を確認(検出された4件はJS内の文字列連結コードへの誤検出で実リンクではないことを確認済み)。

#### AIチャット機能への影響確認

`./Worker · JS`(Cloudflare Worker)のコードには`generated-categories`/`generated-creatures`の文字列はハードコードされておらず、リンクURLの生成自体はフロントエンド(`index.html`のJS、`showPhotos()`関数)が`data/creatures.json`の`page_path`を直接参照して行っていることを確認した。そのため`data/creatures.json`の`page_path`を新しい`creatures/...`形式に更新するだけでチャット経由のリンクも問題なく動作し、Worker側のコード変更は不要だった。

#### 今回は対応しなかったこと(別タスク)

`Worker · JS`内の`CREATURES_URL`定数が、GitHubユーザー名移行前の旧ドメイン(`https://tetsu5686.github.io/...`)を指したままになっている問題を調査中に発見したが、これは今回のリネーム作業とは無関係のため、ユーザーの指示により今回は修正せず、後日別タスクとして対応予定。

#### 結果

- commit `a4d3dbc`としてmainにpush済み(246ファイル変更)。
- 公開URLが `.../categories/hebi.html` `.../creatures/hebi/akamata.html` のように、JA/EN/ES/ZH全言語で一貫した命名になった。
- 上記「現在の構成」および2026-09-12時点の「カテゴリー別パイプライン進捗」表にある`generated-categories/` `generated-creatures/`という表記は、本エントリの内容によって古い情報になっている(フォルダ名自体は変わったが、パイプラインの進捗段階そのものに変更はない)。

（担当: Claude／Sonnet 5）

### 2026-09-13 哺乳類・鳥のカテゴリー一覧ページを公開、水生昆虫図鑑カードをリンク化

#### 背景

前回の「意図せず公開状態になっているページ」調査(本ファイル参照)で、哺乳類(honyuurui)・鳥(tori)は個別ページ(`creatures/honyuurui/*.html` `creatures/tori/*.html`)がすでに生成済みで、トップページのローテーション・AIチャット・関連生き物カード経由で実質公開されているのに、正式な一覧ページが無い状態だと判明していた。ユーザーが個別ページの中身をファクトチェック済みと確認したうえで、正式に一覧ページを作る判断をした。

#### 対応

1. `content/category-pages/honyuurui.md` `tori.md` を新規作成(hebi.md/kaeru.mdと同じフォーマット。天然記念物・国内希少野生動植物種であることを踏まえた安全文言)。
2. `generate_category_pages.py`は「`content/category-pages/*.md`の存在」から公開可能カテゴリーを自動判定する設計だったため、上記ファイルを置いて再実行するだけで`categories/honyuurui.html` `categories/tori.html`が生成され、既存の`hebi.html` `kaeru.html` `kuwagata.html`側のナビ・カテゴリーボタンにも自動的に哺乳類一覧・鳥一覧へのリンクが追加された(スクリプト自体の改修は不要だった)。
3. `generate_creature_pages.py`(個別ページのカテゴリーナビ)・`generate_zukan_page.py`(水生昆虫図鑑ページの他カテゴリーボタン)・`generate_highlights_page.py`を再実行し、サイト全体のナビを同期。
4. `index.html`・`en/es/zh/index.html`のトップナビ・ガイドリンクに「哺乳類/Mammals/Mamíferos/哺乳类」「鳥/Birds/Aves/鸟类」を追加。英語・スペイン語・中国語版には翻訳ページが無いため、`../categories/honyuurui.html`のように**日本語版ページへ直接リンク**する形にした(未対応事項として下記参照)。
5. 副次効果として、これまで写真フォルダが無いため一覧・ローテーションに出ていなかった「アマミトゲネズミ」(`toge-nezumi`)も、`creatures_in_category()`がcontent mdを直接走査する設計のため、哺乳類一覧に正式カードとして表示されるようになった(プレースホルダー画像付き)。

#### トカゲは保留

トカゲ(tokage)はバーバートカゲ1種類しか個別ページが無いため、`content/category-pages/tokage.md`は作成せず、`categories/tokage.html`も生成していない。各所のカテゴリーナビ・ボタンでは引き続き「準備中」表示のまま。アマミヒメトカゲ・オキナワキノボリトカゲの個別ページができてから改めて対応する。

#### 水生昆虫図鑑カードのリンク化

`generate_zukan_page.py`(JA)と`generate_zukan_page_i18n.py`(EN/ES/ZH)の`render_card()`が、これまでリンクの無い`<div class="zukan-card">`のままだった問題を修正。`hebi.html`のカードと同じ「個別ページが実在すればリンク化、無ければdivのまま」というパターンに統一し、水生昆虫17種×JA/EN/ES/ZH計68カードすべてを個別ページへのリンクに変更した。

#### 検証

独自リンクチェッカーで全235ページ・7182件のhref/srcを再検証し、破損0件を確認(検出された8件は`index.html`系JS内の文字列連結コードへの誤検出)。

#### 今回は対応しなかったこと(別タスク)

英語・スペイン語・中国語版ナビの「Mammals」「Mamíferos」「哺乳类」(および鳥/Birds/Aves/鸟类)のリンクは日本語版ページへ直接飛ぶが、ラベル上は翻訳ページかのように見えてしまう。ユーザーから「ラベルに小さく『(JA)』を添えるなど分かりやすくする工夫を今後検討してほしい」との指摘があったが、今回のcommitには含めず後日対応とした。

#### 結果

commit `feef758`としてmainにpush済み(71ファイル変更、うち新規4ファイル)。

（担当: Claude／Sonnet 5）

### 2026-09-14 amami-tool.html(iPhoneから写真をアップロードする専用ツール)の不具合修正

#### 背景

くろちゃんが「iPhoneからGitHubに写真を送れるアプリ」として`amami-tool.html`(リポジトリ直下、GitHub Pagesで公開)を作成していた。ヘビカテゴリーを選んだあと、既存の写真フォルダ名を選んで入力できる「候補チップ」機能が動かないとユーザーから報告があり、原因調査から着手した。

#### 症状①: フォルダ名の候補が出ない

- くろちゃんの直前のコミット(`a415cdc`)で、変数(`categorySelect`等)の定義順序に起因する初期化エラー(保存済み設定がある状態でアプリを開くと、`showApp()`→`loadSpeciesOptions()`が未定義の変数を参照してエラーになり、以降の全処理が止まる)は既に修正済みだったが、症状は解消していなかった。
- まず`loadSpeciesOptions()`のエラーハンドラを直し、失敗時に実際のHTTPステータス・エラーメッセージを画面に表示するようにした(commit `e7d72c7`)。
- 表示されたのは`Load failed`(fetch自体が失敗する分かりやすい系エラー)。ユーザーへの確認で、「リポジトリ (owner/repo)」欄に**サイトの公開URL**(`https://nature-experience-amami.github.io/`)をそのまま入力していたことが判明。正しくは`nature-experience-amami/nature-experience-amami.github.io`という`所有者名/リポジトリ名`形式が必要で、これがAPIリクエストURLの組み立てを壊していた。
- 修正後は`HTTP 401: Bad credentials`に変化。トークン自体の問題と判明。iOSでは`type="password"`の入力欄に対して🔑マークの「保存済みパスワードの自動入力」が提案されるため、ペーストのつもりが誤って別の認証情報を自動入力していた可能性が高いと判断。
- 対策として、①いつでも設定画面(トークン再入力)に戻れる⚙ボタンをヘッダーに追加、②トークン欄の中身を目で確認できる👁表示切り替えボタンを追加(commit `a884dfa`)。

#### 症状②: アップロードはできるがサイトに反映されない

- トークンを直してアップロードは成功したが、GitHub Actionsの自動処理後の中身を確認すると、写真が`images/creatures/hebi/akamata/failed/`に入ってしまい、公開ページには反映されていなかった。
- 原因: `amami-tool.html`はGitHubの容量制限に収まるよう、アップロード前にブラウザの`<canvas>`で写真を縮小・圧縮している。この処理は仕組み上、**EXIF(撮影日時などのメタデータ)を完全に消してしまう**。一方`process_creature_photos.py`はEXIFの撮影日時が読み取れない写真を「日時不明」として自動的に`failed/`へ避難させる仕様だった。つまりこのツールでアップロードした写真は、直すまで**必ず**failed行きになる状態だった。
- 修正: `piexifjs`ライブラリを追加し、縮小処理の**前**に元写真からEXIFの撮影日時を読み取っておき、縮小・圧縮した後の写真にその日時を書き戻してからアップロードするようにした(commit `b5198b2`)。Node.js+Pillowで実際に「日時を書き込んだ画像を`process_creature_photos.py`と同じロジックで読み取れるか」を検証してから反映した。
- 同じcommitで、ついでに「リポジトリ (owner/repo)」欄も廃止して`nature-experience-amami/nature-experience-amami.github.io`固定にした(このツールは他のリポジトリで使う予定がなく、今回の誤入力の原因にもなったため)。トークンだけ都度入力すればよい。

#### 検証

修正後、ユーザーが実際にアカマタの写真を再アップロードし、`images/creatures/hebi/akamata/`直下に(`failed/`ではなく)正しく処理された状態で反映され、`creatures/hebi/akamata.html`・`data/creatures.json`・`categories/hebi.html`まで自動更新されることを確認した(アップロードcommit`a89ade8` → 自動処理commit`69f58b7`)。

#### 副次的なQ&A

「パソコンを起動しておかないと写真をアップロードできないか」という質問があったため、amami-tool.htmlの処理(縮小・EXIF書き戻し・GitHubへの送信)はすべてiPhoneのブラウザ内で完結し、その後のGitHub Actions(透かし・リサイズ・ページ再生成)もGitHub側のサーバーで動く仕組みであることを説明した。パソコンが必要なのはコードそのものを変更する作業のときだけで、日常の写真アップロード運用にはパソコンは不要。

（担当: Claude／Sonnet 5）

### 2026-09-24 生き物Markdownの観察月（months）を、オーナーの現場の感覚に合わせて更新

#### 背景

Threads投稿の仕組み（`threads/`、詳細は`threads/THREADS_STATUS.md`）を作る中で、オーナーが現場の感覚で「ナイトツアーで観察しやすい時期」を種ごとに決め、`threads/overrides.yml`に記録していた。これをサイト側のMarkdownにも反映する作業を3段階に分けて進めることになり、今回はその1段階目（観察月の反映）を行った。

調査で分かったこと（計画時に報告済み）:

- Markdownに`months`がない種は、サイトでは本文の「○月から○月」や写真ファイル名の撮影月から自動で月を推定して表示していた（例: アマミタカチホヘビは写真の撮影月から「4月」）。
- 翻訳版（`.en.md` `.es.md` `.zh.md`）の`months`は日本語版より優先される（`generate_creature_pages_i18n.py`）。日本語版に`months`がなく、翻訳版だけにある種が多数あった。

#### 対応

- `content/creatures/`の45種について、`months`の行だけを`threads/overrides.yml`の月に揃えた（commit `eb9b456`、129ファイル）。
  - 日本語版45ファイル: `months`行があるものは書き換え（12件）、ないものはfrontmatterの末尾に追加（33件）。
  - 翻訳版84ファイル（英・西・中 各28）: `months`行があるものだけ書き換え。行がない翻訳版は、生成時に日本語版の値が使われるため触っていない。
  - アマミアオガエルは既に同じ月だったため変更なし。
- **本文は変更していない。** 本文の「繁殖時期」「発生時期」は生き物としての情報、`months`は「ナイトツアーで観察しやすい時期」として、両方を残す方針（オーナー決定）。そのため、カエル8種・クワガタ5種などで、ページ上の「見られる時期」と本文の時期が一致しない種がある（意図どおり）。
- 一年中と確定した14種（ケナガネズミ・ワタセジネズミ・マルダイコクコガネ・水生昆虫11種）は`[1, 2, …, 12]`を明記した。
- 検証: 差分が`months`行だけであること（追加129行・削除96行、すべて`months: [...]`の行）、`content/creatures/`以外のファイルに変更がないこと、生成スクリプトの読み取り関数（`generate_creature_pages.parse_markdown`・`generate_creatures_json.read_creature_content`）で129ファイルすべてが新しい月として読めることを確認。

#### 今回は行わなかったこと

- `data/creatures*.json`・個別ページ・カテゴリー/図鑑ページの再生成（オーナーがActionsの「process-creature-photos」を手動実行する予定。写真のpush以外では自動で動かないため）。
- 昼行性・夜行性（`activity`）のMarkdownへの追加、`threads/make_draft.py`・`threads/overrides.yml`の変更（2・3段階目で対応予定）。

#### 再生成後にサイトの表示が変わる部分

- 個別ページの観察時期の12か月の帯と「観察しやすい時期」の月表示（JA/EN/ES/ZH）
- 図鑑ページの時期表示（例: 「11〜2月」）
- 個別ページの関連生き物カード（同じ観察月の種を優先して選ぶため）
- トップページの「○月、森はこんな顔をしている」（一年中の14種が毎月候補に入るため、水生昆虫が出やすくなる）

#### 結果

- Commit SHA: `eb9b456`（months変更）。この記録は別commit。
- Push: 済み（main）
- 未完了事項: Actionsの手動実行による再生成と表示確認（オーナー）。2段階目（`activity`の追加）・3段階目（`overrides.yml`の整理）。

（担当: Claude／くろちゃん）

### 2026-09-24 トップページの大きな写真に「奄美で見られる生き物」のラベルを追加

#### 背景

トップページで生き物の写真が出るのは、①ページ最上部の大きな写真（8秒ごとに切り替わるスライドショー）、②FIELD NOTE（今月の生き物）、③AIチャットの回答写真の3か所。①は季節に関係なく写真のある全種からランダムに選んでいるが、写真自体の見出しがなく、上に重なる見出しは「奄美の夜の森を、ガイドと歩く。」（ツアーの見出し）だけだった。そのため、昼行性の鳥や蝶の写真も「夜の森」の見出しと一緒に表示されていた。②（今月の生き物）は変更しない方針。

#### 対応（案A）

- 写真の右下の名前ラベルの上に、小さな文字で1行追加（commit `9a33369`、4ファイル・12行追加）
  - 日本語: 奄美で見られる生き物 ／ 英語: Wildlife of Amami ／ スペイン語: Fauna de Amami ／ 中国語: 在奄美能见到的生物
- 変更は`index.html` `en/index.html` `es/index.html` `zh/index.html`の各ファイルで、JavaScript 1行（名前の前にラベルを入れる）とCSS 2行（ラベル枠を2段の配置にし、ラベルを小さく表示）のみ

#### 検証

ローカルでページを開き、ブラウザ（Chromium）で4言語 × 5種類の画面幅（スマホ縦390px・スマホ横844px・タブレット縦820px・PC 1024px・PC 1440px）を確認。すべてでラベルが名前の上に表示され、写真の枠内に収まり、横スクロールも発生しないことを確認した。

変更前から存在していた表示（今回の変更とは無関係、未対応）:
- スマホ横向き（高さ390px）では、名前ラベルが最初の画面の少し下（スクロールすると見える位置）にある
- 幅761〜900pxの縦向き（タブレット縦など）では、名前ラベルが写真の右下ではなく左上に表示される（この幅向けの位置指定がない）

#### 結果

- Commit SHA: `9a33369`（この記録は別commit）
- Push: 済み（main）
- 未完了事項: 上記「あとでやることリスト」に、昼行性の種を大きな写真から除外するTODOを追加（2段階目の`activity`追加後に実施）

（担当: Claude／くろちゃん）

### 2026-09-24 Markdownに活動時間帯（activity）を追加し、トップの大きな写真を「ナイトツアーで出会える生き物」に限定

#### 背景

前回トップの大きな写真に付けたラベル「奄美で見られる生き物」は、全部奄美の生き物なので意味が薄いとオーナーが判断し、方針を変更。写真を「ナイトツアーで出会える生き物」だけから選ぶことにした（3段階の2段階目）。

#### 対応（4つのcommitに分けた）

1. **Markdown（commit `7da3285`、日本語版44ファイル）**: frontmatterの末尾に`activity`（値は`nocturnal` / `diurnal` / `crepuscular`）を追加。分からない種は書かない（推測しない）。翻訳版・本文は変更なし
   - `diurnal`（25種）: オーナーの指示。カワセミ・タゲリ・アカヒゲ・リュウキュウアカショウビン・リュウキュウサンコウチョウ・イソヒヨドリ・セイタカシギ・オーストンオオアカゲラ・クロツラヘラサギ・サシバ・リュウキュウズアカアオバト・ルリナカボソタマムシ・ミドリナカボソタマムシ・オオミドリサルハムシ・フェリエベニボシカミキリ・アオスジアゲハ・イシガケチョウ・オキナワチョウトンボ・ハネナガチョウトンボ・バーバートカゲ・ルリカケス・アカハラダカ・リュウキュウアサギマダラ・リュウキュウアオヘビ・オオトラツグミ
   - `nocturnal`（19種）: 本文に「夜行性」等とはっきり書いてある14種（ハブ・アカマタ・ヒャン・アマミタカチホヘビ・アマミノクロウサギ・ケナガネズミ・アマミトゲネズミ・ワタセジネズミ・リュウキュウコノハズク・アマミコカブト・ベーツヒラタカミキリ・アマミミヤマクワガタ・マルモンコロギス・アシブトメミズムシ）と、オーナーが現場の感覚で確定した5種（アマミヤマシギ・マルダイコクコガネ・ハロウェルアマガエル・クチキコオロギ・マダラコオロギ）
   - `night_observable: true`（5種、新設）: 昼行性だがナイトツアーで観察できる種。ルリカケス・アカハラダカ・オオトラツグミ（夜に寝ている姿を観察できる）、リュウキュウアサギマダラ（越冬集団を夜に観察できる）、リュウキュウアオヘビ（夜間も活動する個体が多い）。すべてオーナーの説明による
   - 上記以外（約55種）は空欄。オキナワキノボリトカゲはMarkdownがまだないため未設定
2. **生成スクリプト（commit `779ffb8`）**: `generate_creatures_json.py`・`generate_creatures_json_i18n.py`が`activity`・`night_observable`を`data/creatures*.json`に出力するようにした（翻訳版の値は日本語版Markdownから読む）。作業用コピーで実行し、追加した2項目以外の出力が現在の`data/`と完全に同じことを確認
3. **トップページ（commit `c3fc70a`、`index.html` `en/es/zh/index.html`）**: 大きな写真の候補から、個別ページのない種（写真フォルダだけの16種）と、`activity: diurnal`の種（`night_observable`の種は除く）を外す。ラベルを変更（日本語: ナイトツアーで出会える生き物／英語: Wildlife on our night tours／スペイン語: Fauna de nuestros tours nocturnos／中国語: 夜间导览中可遇见的生物）
4. **Threads（commit `fa18f1b`）**: `threads/make_draft.py`が昼行性をMarkdownの`activity`・`night_observable`から判定するように変更し、`threads/overrides.yml`の昼行性の印（20種とトカゲのカテゴリー既定値）を削除。`tour_exclude`・月の上書きはThreads専用として残した。昼行性と判定される種は変更前と同じ20種（動作は変わらない）

#### 検証

- Markdown: 差分が`activity`・`night_observable`の行の追加（49行）だけであることを確認。サイトの生成スクリプトの読み取り処理で44ファイルとも正しく読めることを確認
- トップページ: 再生成後のデータ（作業用コピー）でブラウザ表示を確認。4言語×スマホ・PCで、除外対象の種が一度も表示されないこと、ラベルが名前の上に写真枠内で表示され横スクロールも出ないことを確認。候補数は日本語版112→76種、英・西・中96→76種
- 再生成前（今の`data/creatures*.json`には新しい項目がない）でも、個別ページのない16種は外れ、それ以外は今まで通り表示される（表示が崩れることはない）

#### 記録の訂正

リュウキュウアサギマダラに`night_observable`を付けた根拠は「越冬集団を夜に観察できる」（オーナーの説明）。計画の報告時に「夜見られない」と書いたのは誤り。

#### 結果

- Commit SHA: `7da3285`（Markdown）、`779ffb8`（スクリプト）、`c3fc70a`（トップページ）、`fa18f1b`（Threads）。この記録は別commit
- Push: 済み（main）
- 未完了事項: Actionsの「process-creature-photos」を手動実行して`data/creatures*.json`を再生成（オーナーが実施）。再生成後にトップの大きな写真から昼行性の種が外れる

（担当: Claude／くろちゃん）

### 2026-09-24 ナイトツアーから外す種の追加と、トップの大きな写真の切り替え表示の不具合修正

#### ナイトツアーから外す種（オーナーの判断）

- オーナーから8種をナイトツアーから外すよう依頼があった。そのうちフェリエベニボシカミキリ・ミドリナカボソタマムシ・オーストンオオアカゲラ・アオスジアゲハの4種は既に`activity: diurnal`で、再生成済みの`data/creatures.json`でもトップの大きな写真・Threadsのツアー案内から外れていた（変更なし）
- 残る4種（エグリタマミズムシ・フタキボシケシゲンゴロウ・オオシマセンチコガネ・アマミヨコミゾドロムシ）は`activity`が空欄だったため、日本語版Markdownに`night_observable: false`（ナイトツアーでは出会えない）を追加（commit `8a17a0b`）。`night_observable`は true＝昼行性でも夜に観察できる／false＝ナイトツアーでは出会えない／未記入、の3通りになった
- `generate_creatures_json.py`・`generate_creatures_json_i18n.py`：未記入を`null`として出力し、`false`と区別できるようにした（commit `15e2554`）。作業用コピーで実行し、`night_observable`以外の出力は変わらないことを確認
- `index.html`×4言語：トップの大きな写真の候補から`night_observable: false`の種も外す（commit `99d95a8`）。再生成後のデータで確認し、候補は76→72種。4言語×スマホ・PCで、外した種が表示されないことを確認
- `threads/make_draft.py`：`night_observable: false`の種はツアー案内に使わない（`tour_exclude`と同じ扱い、commit `99fdff6`）

#### トップの大きな写真の8秒ごとの切り替えが不自然だった件

- 原因: 写真を暗くするフェード（CSSで1秒）の途中、0.5秒の時点で次の写真に差し替えていた。計測すると、差し替えの瞬間に前の写真がまだ約40%の明るさで見えており、写真がパッと入れ替わって見えていた。名前のラベルもフェードせず一瞬で切り替わっていた
- 修正（commit `c06317f`、4言語の`index.html`）: 写真と名前ラベルを完全に消してから（1秒）差し替え、また1秒かけて表示する。「視差効果を減らす」設定の端末ではフェードなしで切り替える
- 検証: ブラウザで透明度を50msごとに計測し、差し替えが写真・名前とも透明度0の時点で起きることを確認

#### 結果

- Commit SHA: `c06317f`（スライドショー修正）、`8a17a0b`（Markdown）、`15e2554`（スクリプト）、`99d95a8`（トップページ）、`99fdff6`（Threads）。この記録は別commit
- Push: 済み（main）
- 未完了事項: Actionsの「process-creature-photos」を手動実行して`data/creatures*.json`を再生成（4種がトップの写真から外れるのは再生成後）

（担当: Claude／くろちゃん）

### 2026-09-24 トップの大きな写真が5種しか出ない不具合の修正と、カテゴリーの重み付け

#### 不具合（カエル・ヘビ・クワガタが出なくなっていた）

- オーナーから「カエルやヘビ、クワガタがあまりトップページに表示されない」と指摘があった
- 原因: 公開中の`data/creatures*.json`は、`night_observable`の未記入を`false`として出力していた修正前のスクリプトで生成されていた。そこに「`night_observable: false`の種を外す」トップページの処理（commit `99d95a8`）が加わったため、107種が候補から外れ、候補が5種（鳥3種・リュウキュウアサギマダラ・リュウキュウアオヘビ）だけになっていた。検証を再生成後のデータでしか行っておらず、公開中のデータとの組み合わせを見落とした（Claudeのミス）
- 修正: 現在のスクリプトで`data/creatures*.json`（4言語）を再生成してcommit（commit `3b9d8dd`）。変化は未記入の種の`night_observable`が`false`→`null`になった点だけで、それ以外は同一であることを確認。候補は72種に戻った

#### カテゴリーの重み付け（オーナー承認）

- 候補72種を均等に選ぶと、種数の多い水生昆虫（21種）が29%を占め、両生類14%・ヘビ10%・クワガタ12%にとどまっていた
- `index.html`×4言語の写真選びに、Threads投稿の下書きと同じカテゴリーの重み（ヘビ・両生類4、クワガタ・哺乳類・鳥3、トカゲ2、水生昆虫0.5、その他1）を入れた（commit `74b27bd`）
- 検証: 各`index.html`から実際の選択処理を取り出して20万回実行。4言語とも 両生類27%・ヘビ19%・クワガタ18%・鳥12%・水生昆虫7%・哺乳類6%・甲虫6%・その他昆虫5%。ブラウザで日本語・中国語版がエラーなく切り替わることも確認

#### 結果

- Commit SHA: `3b9d8dd`（データ再生成）、`74b27bd`（重み付け）。この記録は別commit
- Push: 済み（main）
- 注意: 今後`night_observable`や`activity`の扱いを変えるときは、公開中の`data/creatures*.json`がどのスクリプトで作られたかを確認し、必要ならページ側の変更と同時にデータも再生成すること

（担当: Claude／くろちゃん）

### 2026-09-28 水生昆虫の個別ページで写真が「写真準備中」になる不具合の修正と、アシナガミゾドロムシのトップ写真からの除外

#### 不具合（水生昆虫8種の個別ページに写真が出ていなかった）

- オーナーから「水生昆虫のカテゴリーページと個別ページの写真が『写真準備中』になっている」と指摘があった
- 調査で分かったこと:
  - `data/creatures.json`の水生昆虫24種はすべて写真の情報が入っており、9/22以降変化なし。写真ファイルもすべて実在した
  - 写真フォルダ名（`images/creatures/aquatic-insects/`）・`content/categories.json`のキー・Markdownの`category`は、すべて`aquatic-insects`で一致していた
  - カテゴリーページ（図鑑形式、`generate_zukan_page.py`で生成）は正常で、「写真準備中」は写真フォルダのないトビイロゲンゴロウだけ
  - ここ数日の変更（トップ写真・`night_observable`関係）とは無関係。`generate_creature_pages.py`は9/17以降変更されておらず、以前から写真が出ていなかったと考えられる
- 原因: 水生昆虫の写真はグループフォルダ（`amenbo/` `gamushi/` `gengoro/` `himedoromushi/` `katabiro-amennbo/` `sonota/`）の下に1段深く置かれている。`generate_creature_pages.py`の`photo_files()`はカテゴリー直下か`PHOTO_DIR_ALIASES`の対応表でしか写真フォルダを探さず、対応表に載っていない8種（コセアカアメンボ・アマミセスジダルマガムシ・アマミシジミガムシ・フタキボシケシゲンゴロウ・アマミオヨギカタビロアメンボ・アマミコチビミズムシ・アシブトメミズムシ・エグリタマミズムシ）が写真0枚と判定されていた。同じ関数を使う翻訳版（en/es/zh）の個別ページと、関連カード（この生き物に興味がある方へ）の写真も同じ症状だった
- 修正: `generate_creature_pages.py`の`photo_files()`を、`generate_zukan_page.py`と同じく「直下になければグループフォルダの下も探す」形に変更。`generate_category_pages.py`の`photo_files()`も同じ探し方に揃えた（こちらは水生昆虫の対応表が1件もなかったが、出力は図鑑ページで上書きされていたため表には出ていなかった）。水生昆虫の個別ページ（ja/en/es/zh 各25件）を再生成

#### アシナガミゾドロムシをトップ写真の候補から外す（オーナーの判断）

- `content/creatures/aquatic-insects/akahara-ashinaga-mizodoromushi.md`に`night_observable: false`を追加し、`data/creatures*.json`（4言語）を再生成。JSONの変化は本種の`null`→`false`の1行だけ
- これで`night_observable: false`の種は5種（アカハラアシナガミゾドロムシ・アマミヨコミゾドロムシ・エグリタマミズムシ・フタキボシケシゲンゴロウ・オオシマセンチコガネ）

#### 検証

- ブラウザ（Chromium）で水生昆虫の個別ページ100件（4言語×25種）を開き、大きな写真・ギャラリー・関連カードの画像がすべて読み込まれることを確認（読み込めない画像0件）。「写真準備中」はトビイロゲンゴロウのみ。PC幅・スマホ幅（390px）でも表示を確認
- Actionsと同じ手順（`creatures/`を消してから再生成）でも同じ結果。カテゴリー・図鑑・ハイライトページ、他カテゴリーの出力には変化なし
- トップ写真の候補の条件を`data/creatures*.json`に当てはめ、アシナガミゾドロムシが外れることを確認（トップページのブラウザ表示は未確認）
- マージ後の`main`で、関連カードに「写真準備中」がないことを確認

#### 調査中に見つけた別の問題（未対応）

- 関連カード（この生き物に興味がある方へ）が、水生昆虫ではどのページでも同じ8種になり、15種は一度も出ない。詳細と直し方の案は「あとでやることリスト」に記載

#### 結果

- Commit SHA: `5c3af92`（写真表示の修正、102ファイル）、`95ea59f`（アシナガミゾドロムシ、5ファイル）。プルリクエスト #18 でmainにマージ（マージcommit `7e1c608`）。この記録は別commit
- Push: 済み（main）
- 未完了事項: 関連カードの選び方の見直し（案の決定待ち）。トビイロゲンゴロウの写真追加

（担当: Claude／くろちゃん）

### 2026-09-28 ワタセジネズミをナイトツアーで出会える生き物から外す

- オーナーの判断で、ワタセジネズミ（`content/creatures/mammals/watase-jinezumi.md`）に`night_observable: false`を追加し、`data/creatures*.json`（4言語）を再生成。JSONの変化は本種の`null`→`false`の1行だけで、個別ページなどの出力は変化なし
- トップページの大きな写真の候補から外れる。`night_observable: false`の種は6種になった（アカハラアシナガミゾドロムシ・アマミヨコミゾドロムシ・エグリタマミズムシ・フタキボシケシゲンゴロウ・オオシマセンチコガネ・ワタセジネズミ）
- Threadsは`threads/overrides.yml`で既に`tour_exclude: true`になっていたため、動作は変わらない
- `activity: nocturnal`（夜行性）はそのまま残した（生き物としての情報のため）
- Commit SHA: `1ebfab7`。この記録は別commit
- Push: 作業用ブランチ`claude/exciting-brown-j33kwg`にpush済み。mainへのマージ待ち

（担当: Claude／くろちゃん）

### 2026-09-28 個別ページの関連カード（この生き物に興味がある方へ）の選び方を見直し（案B）

#### 調べたこと（全カテゴリー、変更前）

| カテゴリー | 種数 | 1ページの同じカテゴリー／他カテゴリー | 関連カードに一度も出ない同じカテゴリーの種 |
|---|---|---|---|
| 両生類 | 10 | 8／0 | 1 |
| 水生昆虫 | 25 | 8／0 | 16 |
| 甲虫 | 14 | 8／0 | 5 |
| 鳥 | 17 | 8／0 | 8 |
| 昆虫その他 | 11 | 8／0 | 2 |
| クワガタ | 9 | 8／0 | 0 |
| ヘビ | 7 | 6／2 | 0 |
| 哺乳類 | 4 | 3／5 | 0 |
| トカゲ | 1 | 0／8 | — |

- 原因: `generate_creature_pages.py`の`related_cards()`が同じカテゴリーの種をID順に先頭から並べて8件で打ち切っていた。種の多いカテゴリーではどのページでも同じ顔ぶれ（ID順で先頭の種）になり、他のカテゴリーへのリンクも出なかった。サイト全体で98種中33種が、どのページの関連カードにも一度も出ていなかった
- 翻訳版（`generate_creature_pages_i18n.py`）も同じ関数を使っているため同じ状態だった

#### 対応（案B、オーナー承認）

- 関連カード8件の選び方を次の順に変更（commit `649af3b`）
  1. Markdownの`related:`の指定（従来どおり優先。現在指定している種はない）
  2. 同じカテゴリーから最大4件。今のページの次の種から順に選ぶ（ページごとに違う種が出る）
  3. 残りは他のカテゴリーの写真のある種から、観察時期が重なる種を優先して選ぶ。各カテゴリーの種を均等な間隔で並べた一覧から、ページごとに4種ずつずらして取り出す
  4. 他のカテゴリーで埋まらない分は、同じカテゴリーの残りで埋める
- 乱数は使わないので、再生成しても結果は変わらない（Actionsのたびに全ページが変わることはない）
- 最初はカテゴリーを1つずつ順番に回る方式で試したが、1種しかないトカゲ（バーバートカゲ）が98ページ中45ページに出てしまったため、種ごとに均等になる方式に変えた

#### 検証（変更後）

- 全カテゴリーで、1ページの同じカテゴリー4件＋他カテゴリー4件（哺乳類は同じカテゴリーが3種しかないため3＋5、トカゲは0＋8）。他カテゴリーの4件は2〜4カテゴリーに分かれる
- ページごとに違う組み合わせになり、関連カードに一度も出ない種は0種。1種が出る回数は3〜14回（変更前は0〜45回）。多いのは一年中観察できる種（観察時期が重なる種を優先するため）
- 個別ページ ja/en/es/zh 計392件を再生成。変わったのは関連カードの行だけ。関連カードのリンク・画像はすべて実在するファイルを指す。ブラウザ（Chromium）で4ページを開き、画像がすべて表示されることを確認
- 「写真準備中」のカードが出るのは、写真のないトビイロゲンゴロウ・アマミトゲネズミが同じカテゴリーの枠に入るときだけ（他カテゴリーの枠には写真のある種だけを使う）

#### 結果

- Commit SHA: `649af3b`。この記録は別commit
- Push: 作業用ブランチ`claude/exciting-brown-j33kwg`にpush済み。mainへのマージ待ち
- 未完了事項: `night_observable: false`の種（6種）や昼行性の種を関連カードでどう扱うか（現在は通常どおり出る）

（担当: Claude／くろちゃん）

### 2026-09-28 図鑑ページ・関連カードに昼行性の種を表示する方針の確認

- オーナーの決定: 図鑑ページや個別ページの関連カードは「奄美で見られる生き物」を紹介する場所なので、昼行性の種（`activity: diurnal`）や`night_observable: false`の種も表示してよい
- ナイトツアーで出会える種だけに絞るのは、これまでどおりトップページの大きな写真とThreadsのツアー案内だけ
- 前のエントリの未完了事項「`night_observable: false`の種や昼行性の種を関連カードでどう扱うか」は、この決定で完了（コードの変更はなし）
- 「個別ページに関する重要な設計判断」にもこの方針を追記した
- Commit SHA: この記録のcommitのみ（コードの変更なし）
- Push: 作業用ブランチ`claude/exciting-brown-j33kwg`にpush済み。mainへのマージ待ち

（担当: Claude／くろちゃん）

### 2026-09-28 予約管理アプリ（customer-app）：自分の予定の終了・キャンセル、自動での履歴移動、履歴の月フォルダ

#### 背景（オーナーの依頼）

- 自分の予定にも、ガイドの予約と同じように「終了」「キャンセル」ボタンを付け、押したら履歴へ移したい
- 履歴は、月が終わったら「2026年9月」のようなフォルダにまとめ、押すと中を確認できるようにしたい。この先の予約・予定は並んで見られるほうがよい
- 履歴では、お客様の予約と自分の予定を日付順に一緒に並べる（見返しやすいため）
- 自分の予定は、日付が過ぎたら自動で履歴へ移す。ガイドの予約は「ガイド終了にする」を押してから移す

#### 対応（`customer-app/app.js`・`style.css`・`index.html`・`README.md`）

- 自分の予定の詳細に「終了にする」「キャンセル」を追加。押すと一覧から消えて履歴へ移る。キャンセル理由は任意。履歴から「終了を取り消す」「キャンセルを取り消す」で一覧に戻せる
- 履歴に移した後も自分の予定と分かるよう、記録に`kind: "personal"`を付ける。既存の予定は`status: "personal"`で判定するので、データの移行は不要
- 自分の予定は、日付が過ぎると翌日から自動で「終了」として履歴へ移す（`autoCompleted`を記録）。日付が過ぎた予定を手で一覧に戻した場合は`keepOpen`を付け、自動では戻さない
- 履歴画面: 今月以降（と日付なし）の分はそのまま日付順に並べ、終わった月は「📁 2026年9月」のような月フォルダにまとめる（新しい月が上、押すと開く）。お客様の予約と自分の予定は同じ列に日付順。検索・日付で絞り込むと、該当する月のフォルダが自動で開く
- 一覧画面（これからの予約・予定を日付順に並べる）は変更なし
- `index.html`の`?v=`を上げた（style.css v9、app.js v15）

#### 検証

- ブラウザ（Chromium、幅390px）にサンプルデータを入れて操作。ページのエラーなし
- 終了・キャンセル・取り消し、月フォルダの開閉、検索でフォルダが自動で開くことを確認
- 今日を9/28として、9/27・8/10の自分の予定は自動で履歴へ移り、9/28・10/2の予定と、日付が過ぎた9/20のガイド予約（予約確定）は一覧に残ることを確認
- 手で戻した過去の予定は、再読み込み後も一覧に残ることを確認

#### 結果

- Commit SHA: `5ceb284`（終了・キャンセルと月フォルダ）、`ce57287`（自動での履歴移動）。プルリクエスト #21 でmainにマージ（マージcommit `b951bd1`）。この記録は別commit
- Push: 済み（main）
- 記録の補足: 本日の「ワタセジネズミ」「関連カードの見直し」「昼行性の種を表示する方針」の各エントリで「mainへのマージ待ち」としていたものは、プルリクエスト #19・#20 でmainにマージ済み
- 注意: データは各端末のブラウザ（localStorage）にだけ保存される。更新前に「⬇ バックアップ」を取っておくと安全
- 株式レポート（別リポジトリ`tetsu-ai-secretar`）の本日の修正は、そちらの`PROJECT_STATUS.md`に記録した

（担当: Claude／くろちゃん）

### 2026-09-28 トップの大きな写真の名前ラベルの位置を修正（大きな画面）

- オーナーから「大きな画面で見ると、『ナイトツアーで出会える生き物』と名前が写真の中央あたりに出る。右下にしたい」と依頼
- 原因: ラベルは写真のリンク（`.hero-photo-link`）の中にあるので写真の枠から位置が決まるが、PC用の設定で下からの距離を画面全体の高さから計算していた（`100svh - 写真の上端 - 写真の高さ + 1rem`）。写真の高さは最大620pxなので、縦に大きい画面ほどラベルが上にずれ、2560×1440では写真の外まで出ていた
- 修正: `bottom: 1rem; right: 1rem;` にして、写真の右下の角から16px内側に固定（`index.html`・`en/es/zh/index.html`）
- 検証: PCの画面サイズ6種類×4言語で、ラベルが写真の下から16px・右から16pxに収まることを確認。スマホ用の設定は変更なし
- Commit SHA: `ac386cf`。プルリクエスト #23 でmainにマージ
- Push: 済み（main）

（担当: Claude／くろちゃん）

### 2026-09-28 iPhoneのホーム画面用アイコン、予約データが消えた件とバックアップの件数表示

#### ホーム画面用のアイコンと名前

- ホーム画面に追加したトップページと予約管理アプリが、どちらも「N」のアイコンで、名前も「NatureExperie...」と切れていた。アイコン画像（`apple-touch-icon`）がなく、iPhoneが題名の頭文字で仮のアイコンを作っていたため
- トップページ（4言語）: ハブの顔の写真（`images/creatures/snakes/habu/habu_000066_20260607_23.jpg`を正方形に切り抜き、オーナーが3案からBを選択）。`images/icons/apple-touch-icon.png`（180px）・`icon-192.png`。名前は「奄美ナイト」（en/es/zhは「Amami Night」）
- 予約管理アプリ: 濃い緑の地にカレンダーと「予約」の文字。`customer-app/apple-touch-icon.png`・`icon-192.png`。名前は「予約管理」
- 各ページに `apple-touch-icon`・`icon`・`apple-mobile-web-app-title` を追加（commit `99a04a9`、プルリクエスト #24）

#### 予約データが消えた件

- アイコンを付け直すため、Claudeの案内で「古いアイコンを削除 → 追加し直す」の順に作業した結果、予約管理アプリの中のデータが消えた。ホーム画面のアプリはアプリごとに別の保存場所を持ち、アイコンの削除でデータも消えるため
- 直前に取ったバックアップ（17:00）には2件しか入っておらず、ほかのバックアップもSafari側にもデータはなかった。消えた予約は戻せなかった（試運転の段階で、オーナーは了承）
- バックアップが2件だった理由は特定できていない。前の版はバックアップのあとファイルが本当に保存されたかを確かめなかったため、以前のバックアップが保存されていなかった可能性がある（オーナーの見立て）
- Claudeの案内の誤り: 「古いアプリを残したまま新しく追加し、復元して件数を確かめてから古いアプリを消す」順で案内すべきだった。作業ルール11に追記した

#### バックアップ・復元で件数を表示（`customer-app/app.js`）

- バックアップ: パスワードを決める前と作成後に、予約・自分の予定の件数（うち履歴の件数）を表示
- 復元: 置き換える前に、バックアップの中身と今のデータの件数を並べて表示
- ファイル名に時刻を追加（`nea-customer-backup-YYYYMMDD-HHMM.json`）
- `customer-app/README.md` に、アイコン削除でデータが消えること、Safariとは保存場所が別なことを追記
- Commit SHA: `7e238ae`（プルリクエスト #25）
- Push: 済み（main）

（担当: Claude／くろちゃん）

### 2026-09-29 予約管理アプリ：未保存の変更のお知らせ、バックアップのパスワードは毎回入力

- データの保存先の方針（オーナー決定）: GitHubの非公開リポジトリへの自動保管も検討したが、当面はiPhoneの「ファイル」アプリ（iCloud Drive）へのバックアップで守る。Webのアプリは本人の操作なしにファイルへ保存できないため、変更のたびに1回タップする運用
- 未保存の変更のお知らせ: データを保存するたびに「バックアップしていない変更」を数え、画面の上に「💾 バックアップしていない変更が◯件あります（最後のバックアップ: 日時）」と「今すぐバックアップ」ボタンを出す。一度もバックアップしていない時も出す。ファイルが保存されたかはアプリから分からないため、最後に「保存まで済んだらOK」と確かめてから保存済みにする（commit `94682dd`、プルリクエスト #29）
- パスワード: #29でアプリに覚えさせる機能を入れたが、オーナーの判断で毎回入力に戻し、機能ごと外した。前の版で覚えさせたパスワードは起動時に消す（commit `8790115`、プルリクエスト #30）
- 検証: ブラウザで、最初のバックアップ、変更後のお知らせ、お知らせからのバックアップ、保存をやめた時（お知らせが残る）、復元（毎回パスワード入力）を確認。オーナーがiPhoneでバックアップと復元ができることを確認
- 注意: バックアップのパスワードは「パスワード」アプリなどに控えておく（忘れると復元できない）
- ~~未完了事項: GitHubの非公開リポジトリへの自動保管（`nea-customer-data`）は見送り。必要になったら、オーナーがiPhoneでGitHubにログインできるようになった（パスキー登録済み）ので、リポジトリとトークンの準備から再開できる~~ → 2026-09-29 オーナー判断で見送りに決定し、やることから外した。予約データはiPhoneの「ファイル」アプリへのバックアップで守る
- Push: 済み（main）
- 関連: 同じ日にThreads下書きの作り直し（3分後・5分後）を追加した。詳細は `threads/THREADS_STATUS.md`（プルリクエスト #28）

（担当: Claude／くろちゃん）

### 2026-09-29 写真だけあった9種類のMarkdownを作成

- 写真フォルダはあるのにMarkdownがなかった種を洗い出し、カテゴリーページのある分類の9種類を作った（オーナーが昼行性・夜行性を指定）
  - 両生類: ヌマガエル（`numa-gaeru`、夜行性）
  - 甲虫: アマミアオジョウカイ（`amami-aojyoukai`、昼行性、グループ「その他」）
  - トカゲ: アマミヒメトカゲ（`amami-hime-tokage`、昼行性）、オキナワキノボリトカゲ（`okinawa-kinobori-tokage`、昼行性＋`night_observable: true`：夜に眠る姿を見られる）
  - ヘビ: ブラーミニメクラヘビ（`mekura-hebi`、夜行性、外来種）
  - 昆虫その他: リュウキュウハグロトンボ（`ryuukyuu-haguro-tombo`、昼行性）、アマミマダラカマドウマ（`amami-madara-kamadouma`、夜行性）、コバネコロギス（`kobane-korogisu`、夜行性）、クロマダラソテツシジミ（`kuromadara-sotetsu-shijimi`、昼行性、外来種）
- idはすべて写真フォルダ名と同じ。昆虫その他の4種はグループのフォルダ（`tombo/`・`tyokushi/`・`tyou/`）の下にあるが、生成スクリプトが2階層目も探すので対応表への追加は不要
- 内容はWeb検索で複数の情報源を突き合わせて作成。ヌマガエルの背中線は、オーナーの確認（WEB両爬図鑑の記述、手元の写真に白い線がない）を受けて「入る個体もいる」に修正した（WEB両爬図鑑の「奄美・沖縄では見られない」は背中の両脇の背側線の話で、背中線とは別）
- 確かめきれていない点: コバネコロギスは奄美大島での分布をはっきり書いた資料が見つからなかった（写真の種の確認が必要）。アマミマダラカマドウマの体長は資料が見つからず未記載。オキナワキノボリトカゲの条例による捕獲禁止の有無は未確認のため、dangerには環境省レッドリストのみ記載
- 生成スクリプトを実行してページを作り直した（新しい9ページ、関連カード、図鑑・カテゴリーページ、`data/creatures.json`）
- 未完了事項: ~~9種類の翻訳（`.en.md`・`.es.md`・`.zh.md`）は未作成のため、翻訳版のページにはまだ出ない。~~ → 同日に作成済み（下記）。カニ（`kani`）とその他の節足動物（`other-arthropods`）の7種類は、Markdownもカテゴリーページもまだない。`images/creatures/snakes/akamata/failed/` に写真処理の残りらしい画像が1枚ある
- Push: 済み（プルリクエスト経由）

（担当: Claude／くろちゃん）

### 2026-09-29 9種類の翻訳（英語・スペイン語・中国語）を作成

- 上の9種類について `.en.md`・`.es.md`・`.zh.md` を作成（計27ファイル）。日本語版の内容をそのまま訳し、`activity`・`night_observable` は日本語版だけに書く決まりに合わせて入れていない
- 名前（英/西/中）: ヌマガエル Kawamura's Rice Frog／Rana de Arroz de Kawamura／泽蛙、アマミアオジョウカイ Amami Blue Soldier Beetle／Escarabajo Soldado Azul de Amami／奄美青花萤、アマミヒメトカゲ Amami Short-legged Skink／Eslizón de Patas Cortas de Amami／奄美光蜥、オキナワキノボリトカゲ Okinawa Tree Lizard／Lagarto Arborícola de Okinawa／冲绳攀蜥、ブラーミニメクラヘビ Brahminy Blind Snake／Serpiente Ciega Brahminy／钩盲蛇、リュウキュウハグロトンボ Ryukyu Black-winged Damselfly／Caballito del Diablo de Alas Negras de Ryukyu／琉球单脉色蟌、アマミマダラカマドウマ Amami Spotted Camel Cricket／Grillo Camello Moteado de Amami／奄美斑灶马、コバネコロギス Short-winged Raspy Cricket／Grillo Áspero de Alas Cortas／短翅蟋螽、クロマダラソテツシジミ Plains Cupid／Cupido de las Llanuras／苏铁绮灰蝶
- 英語名・中国語名の多くは定まった通称がなく、既存の訳し方（Amami ○○ など）に合わせて付けた
- 生成スクリプトで翻訳版のページを作り直し、`scripts/check_translations.py` でリンク切れ0件・翻訳ファイル抜け0件を確認。日本語の残存は `en/es/zh/index.html` の15箇所だけで、今回の変更前からあるもの
- Push: 済み（プルリクエスト経由）

（担当: Claude／くろちゃん）

### 2026-09-29 チンメルマンセスジゲンゴロウの写真の日付修正とMarkdown作成

- 写真: オーナーがX(旧Twitter)から保存した写真に撮影日を入れ直してアップした際の打ち間違いで、`chinmeruman-sesuji-gengoro_000001_20260228_12.jpg` になっていたのを `..._20250228_12.jpg` に直した（処理済みの写真はEXIFが消えているので、日付はファイル名だけ）。間違えてアップした `failed/IMG_9015.jpg` は削除（プルリクエスト #35）
- Markdown: `content/creatures/aquatic-insects/chinmeruman-sesuji-gengoro.md` を作成（グループ `gengoro`）。オーナーの指示で `night_observable: false`（トップのナイトツアーの写真には出さない）
  - 学名は2026年の論文 Watanabe, Kato, Ueda & Shaverdo（European Journal of Taxonomy）に従い、*Copelatus zimmermanni* から *Austrelatus zimmermanni* (Gschwendtner, 1934) に変更。同じ論文で奄美大島から初めて記録され、南大東島・宮古島の個体群が新亜種として記載された
  - 生活史（卵から成虫まで39〜61日、雨水の一時的な水たまりにもすむ）は Watanabe & Ohba (2022) Entomological Science による
  - 論文のページはこの作業環境から開けず、検索で出る要旨で確認した。奄美大島の個体の亜種の扱い（原亜種とみられる）、正確な発表日、奄美での採集環境は未確認。環境省・鹿児島県のランクも未確認のため `danger` は書いていない
- 翻訳（`.en.md`・`.es.md`・`.zh.md`）も作成。名前は Zimmermann's Diving Beetle／Escarabajo Buceador de Zimmermann／齐氏背线龙虱
- ページを作り直し、`scripts/check_translations.py` でリンク切れ0件・翻訳ファイル抜け0件を確認
- Push: 済み（プルリクエスト経由）

（担当: Claude／くろちゃん）

