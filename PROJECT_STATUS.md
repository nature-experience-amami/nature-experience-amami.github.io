# Nature Experience Amami - Project Status

最終更新: 2026-09-04（日本時間）

このファイルは、Nature Experience Amami の作業状況と判断事項を、ChatGPT（ちゃっぴー）、Claude（くろちゃん）、Copilotなど、誰でも引き継げるように記録するためのメモです。

## プロジェクト概要

- 奄美大島の夜の森で見られる生き物を紹介する静的Webサイト。
- HTML、JSON、Markdown、画像、GitHub ActionsをGitHubリポジトリで管理。
- GitHub Pagesで公開する構成。
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
│  └─ generate_creatures_json.py
├─ index.html
├─ hebi.html
├─ test-creature-v2.html
├─ contact.html
├─ tour.html.html
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

## ヘビ一覧ページ

```text
hebi.html
```

ヘビ7種類を表示する一覧ページです。現在の表示順:

1. リュウキュウアオヘビ
2. アカマタ
3. ガラスヒバァ
4. ヒメハブ
5. ハブ
6. ヒャン
7. アマミタカチホヘビ

一覧ページの写真参照は、実際の写真フォルダ・ファイル名に合わせて更新済みです。リュウキュウアオヘビは次の写真フォルダ名を使用します。

```text
images/creatures/hebi/ryuukyuu-aohebi/
```

## 個別ページのデザイン方針（2026-09-03 くろちゃんと再検討・確定）

個別ページは `test-creature-v2.html` をベースにした旧デザイン（写真1枚を横幅いっぱいの固定アスペクト比で表示）から、以下の新デザインへ刷新することを決定。ハブのページ（`creatures/hebi/habu.html`）をこの新デザインで実装済み（コードはくろちゃんが作成し、ユーザーが手動で貼り付ける運用）。

### ハブページ（新デザイン）に反映している内容

- ヒーローを「写真（左58%）＋情報パネル（右）」の分割レイアウトに変更。高さの上限を `min(70vh, 600px)` に固定し、写真の縦横比に左右されて大きすぎ／小さすぎになる問題を解消。
- ヒーロー写真にトップページの「懐中電灯で照らす」世界観を意識した控えめなビネット（周辺減光）を追加。
- 名前・分類（クサリヘビ科ハブ属）・学名（*Protobothrops flavoviridis*）・全長・夜行性などのバッジ表示。
- 「危険度メーター」（視覚的なバー表示）を追加。ヘビ以外のカテゴリーにも使い回せる共通パーツとして設計。
- 「観察時期タイムライン」（12ヶ月の帯でアクティブな月だけ光らせる表示）を追加。ヘビの観察時期・カエルの繁殖時期・クワガタの発生時期など、カテゴリーが変わっても使い回せる共通パーツとして設計。
- ギャラリー写真クリックで拡大表示するライトボックスを追加。
- 紹介文（ABOUT）を複数段落に拡張し、新たに「ECOLOGY（生態と特徴）」セクションを追加。旧simdifサイトのカエル・クワガタページ程度のボリューム（生息場所・食性・行動の詳しさ）を目安にする方針。
- ページ末尾にナイトツアーへのCTA（`../../contact.html` へのリンク）を追加。
- ナビ・お問い合わせ・ツアーへのリンクは、ページの設置場所（`creatures/hebi/` 以下）に合わせて `../../` から書く。

### 写真のランダム表示（既存の仕組みを維持）

5枚の写真配列をシャッフルし、先頭1枚をヒーロー、続く3枚をギャラリーへ重複なく割り当てる（1枚は毎回未使用になる）。この仕組みは旧habu.htmlから維持。

写真:

- `habu_000001_20241218_22.jpg`
- `habu_000002_20250228_00.jpg`
- `habu_000003_20250228_00.jpg`
- `habu_000004_20260214_22.jpg`
- `habu_000005_20260221_22.jpg`

処理済み写真には透かしが焼き込まれているため、ヒーロー側にもHTML/CSSの透かし（`.photo-credit`など）は追加しない。ギャラリーの大きい写真（1枚目）のみ、右下の焼き込み透かしが切れないよう `object-fit:contain` を指定する。

## 個別ページに関する重要な設計判断

- 個別HTMLを自動生成するスクリプトは、現時点では存在しない。カテゴリーが増えても、当面は「共通の型を持つコピー用テンプレート」方式で進める（habu.htmlの新デザインを基準にする）。自動生成（JSON駆動）は、型が固まり数が増えてから検討する。
- `generate_creatures_json.py` は `data/creatures.json` の生成専用。
- `content/creatures/**/*.md` は個別ページの内容の基礎資料。
- 個別ページを増やす場合は、まず新デザイン版の `creatures/hebi/habu.html` を基準にする。
- 個別ページは `creatures/hebi/` 以下に置くため、画像・共通ページへのリンクは `../../` から始める。
- 写真フォルダ名はMarkdownのIDと必ずしも一致しない。実際のフォルダを確認する。
- 処理済みJPEGの透かしを二重表示しない。個別ページにHTML/CSSの透かしを追加しない。
- 危険度メーター・観察時期タイムラインは、ヘビ以外のカテゴリー（カエル・クワガタなど）でも使い回せる共通パーツとして設計している。
- 紹介文（ABOUT・ECOLOGY相当のセクション）は、旧simdifサイトのカエル・クワガタページ程度のボリューム感で書く方針。

## 未完了の作業

### ヘビ個別ページ6種類

次の6ページは未作成です。

```text
creatures/hebi/akamata.html
creatures/hebi/garasu-hibaa.html
creatures/hebi/hime-habu.html
creatures/hebi/hyan.html
creatures/hebi/ryukyu-ao-hebi.html
creatures/hebi/amami-takachiho-hebi.html
```

作成時は、それぞれのMarkdownと実在する処理済み写真を確認し、新デザイン版のハブページ（分割ヒーロー・危険度メーター・観察時期タイムライン・ABOUT/ECOLOGY構成）の構造を基準にして、中身だけ差し替える。

### 一覧ページとのリンク確認

`hebi.html` は7ページへリンクしています。現在はハブ以外のリンク先HTMLが未作成です。

アマミタカチホヘビの一覧リンクは次の名前です。

```text
creatures/hebi/amami-takachiho-hebi.html
```

一方、Markdownと写真フォルダのIDは `takachiho-hebi` です。ページ作成時は一覧リンクを変えないなら、HTMLファイル名を一覧リンクに合わせる必要があります。

### ハブページ（新デザイン）のcommit・push

新デザイン版の `creatures/hebi/habu.html` は、くろちゃんがコードを渡した段階で、ユーザーが手動で貼り付ける予定。このメモ作成時点では、実際にファイルへ反映されたか・commit/pushされたかは未確認。

### 他カテゴリー

カエル、クワガタなどの一覧ページ・個別ページの実装は、今後構成を確認してから着手する。ヘビの新デザインをブラウザ確認し、問題点を確定してから他カテゴリーへ展開する。

## 現在のGit状態

このメモ作成前に確認した状態:

```text
main...origin/main [ahead 3]
```

ローカルの主な履歴:

```text
d5b4c4a Merge branch 'main' of https://github.com/tetsu5686/nature-experience-amami
04b3088 fix: update ryukyu aohebi image
bef5f4d feat: update snake overview page
73f36d3 (origin/main) chore: process creature photos
```

現時点で、ローカルには未pushのコミットが3つあります。Pushする前にGitHub側の履歴と、未追跡ファイルを必ず確認してください。

未追跡として確認されているファイル:

```text
contact.html
creatures/hebi/habu.html
test-creature-v2.html
tour.html.html
```

これらには既存作業が含まれる可能性があるため、勝手に削除・まとめてcommitしない。

## 作業ルール

1. 作業前に変更対象ファイルを明記する。
2. 指定されていないHTML、JSON、Worker、Python、写真は変更しない。
3. 既存デザインを再利用し、大幅な作り直しを避ける。
4. 写真フォルダとファイル名を実際に確認してから参照する。
5. 処理済み写真の焼き込み透かしとHTML透かしを二重にしない。
6. Commit / Pushは、明示的な依頼がある場合だけ実行する。
7. Commitする場合は、対象ファイルだけを明示的にstageする。
8. 他のAIが作業を続けるときは、このファイルの「未完了の作業」「現在のGit状態」「作業ルール」を先に読む。

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
- `generate_creatures_json.py` はワークフローから外し、写真処理対象を `images/creatures` に限定。
- `hebi.html` の7種類の写真参照を実在する写真へ合わせた。
- `hebi.html` を `bef5f4d` と `04b3088` でcommitした。Pushはこの記録作成時点で未確認。
- `creatures/hebi/habu.html` をハブ個別ページの試作として作成。
- ハブページにランダム写真表示を追加。
- 処理済み写真の焼き込み透かしとHTML/CSS透かしの二重表示を調査し、HTML/CSS側の透かしを削除。
- 左側の大きいギャラリー写真に `object-fit: contain` を追加。
- Habu試作ページは未commit・未push。
- 今後はHabu試作をブラウザ確認してから、残り6ページを作成する。

（担当: Claude／くろちゃん）

- 旧simdifサイト（カエル・クワガタ・代表的な生き物ページ）を確認し、個別ページの項目（分類・学名・サイズ・時期・生息場所・特徴文・注意事項・写真）がカテゴリー間で共通化できることを確認した。
- ヒーロー画像の「大きすぎる/小さすぎる」問題を解決するため、個別ページのデザインを刷新する方針を決定。分割ヒーロー（写真＋情報パネル）、危険度メーター、観察時期タイムラインという、カテゴリーをまたいで使い回せる共通パーツを設計した。
- ハブを例にしたデザインプロトタイプ（`creature-template-preview.html`）を作成し、確認後にABOUTセクションを拡張・ECOLOGYセクションを新設した。
- 上記デザインを反映した新しい `creatures/hebi/habu.html` のコードを作成し、ユーザーに渡した（写真のランダム表示の仕組みは維持、5枚シャッフルしヒーロー1枚＋ギャラリー3枚に割り当て）。ナビ・CTAのリンクは `creatures/hebi/` 配下からの相対パス（`../../`）に修正。
- このコードは、ユーザーが手動でリポジトリの `creatures/hebi/habu.html` に貼り付ける予定。この記録作成時点で、実際の反映・commit・pushは未確認。
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
- 個別ページが未作成の生き物は、写真表示を維持しつつ `#tour`（ナイトツアー案内）へリンクする。
- リュウキュウアオヘビの写真フォルダIDとMarkdown IDの不一致に対応し、日本語名と解説をJSONへ正しく取り込めるようにした。
- `data/creatures.json` を再生成し、リュウキュウアオヘビが `リュウキュウアオヘビ` と表示されることを確認。
- 今回のコミット:
  - `1064d9a Resolve Ryukyu green snake content ID`
  - `b25daf3 Deduplicate AI creature photos`
  - `838895a Link AI creature photos to introductions`
- Push: 未確認（GitHubへ反映するには別途pushが必要）。

（担当: Copilot）

### 2026-09-04 追加確認

- `generated-creatures/` は野良ファイルではなく、Markdownを正本にした個別ページ自動生成の意図的な試作出力先であることを再確認。
- `generated-creatures/hebi/akamata.html`、`generated-creatures/kaeru/amami-aka-gaeru.html` を確認。
- 3ページは、PC・スマートフォン向けのレスポンシブレイアウト、写真あり・写真なしの表示分岐、関連生き物カード、個別ページ間の相対リンクを備えている。
- 写真ありページはヒーロー画像とギャラリーを表示し、写真なしページは「写真準備中」と解説を表示する。
- 個別ページ生成方式は、今後「自動生成方式」に一本化する方針を決定。手動で `creatures/` 配下へ同じページを並行作成しない。
- ヘビ全体、続いてカエル・クワガタへ展開する前に、まず自動生成テンプレートを必要に応じて改善し、生成結果を確認する。
- AIチャットから生成済み個別ページへのリンクは、試作中の暫定リンクではなく、自動生成方式の本番導線として維持する。
- 生成済みページがまだない生き物は、従来どおりナイトツアー案内（`#tour`）へリンクする。
- 今後の自動生成で確認する項目:
  - 写真0枚・1枚・2〜3枚・4枚以上のギャラリー表示
  - スマートフォンでのヒーロー、本文、関連カードの表示
  - 写真フォルダIDとMarkdown IDが異なる生き物の名前・解説解決
  - AIチャット、Topページ、一覧ページからのリンク整合性

（担当: Copilot）
