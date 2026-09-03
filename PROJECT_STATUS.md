# Nature Experience Amami - Project Status

最終更新: 2026-09-03（日本時間）

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

## 個別ページの試作

### 試作ページ

```text
creatures/hebi/habu.html
```

このページは `test-creature-v2.html` をベースに作成したハブの個別ページ試作です。

反映している内容:

- ハブの名前
- 分類: クサリヘビ科ハブ属
- 学名: `Protobothrops flavoviridis`
- 全長約226cm
- 観察時期: 5月から11月頃、暖かい冬の日にも活動
- 夜行性
- 生息場所: 森林、草原、水辺、農地、樹上、人家周辺
- 食性
- 攻撃性と安全上の注意
- 2〜3m以上の距離を保つ観察ポイント

写真:

- `habu_000001_20241218_22.jpg`
- `habu_000002_20250228_00.jpg`
- `habu_000003_20250228_00.jpg`
- `habu_000004_20260214_22.jpg`
- `habu_000005_20260221_22.jpg`

ページ読み込み時にJavaScriptで5枚をシャッフルし、ヒーロー1枚とギャラリー3枚へ重複なく割り当てます。現在、左側の大きいギャラリー写真だけは、4:3画像の右下透かしが切れないよう次の指定を追加しています。

```css
.gallery figure:first-child img{object-fit:contain}
```

処理済み写真には透かしが焼き込まれているため、`habu.html` 内の `.photo-credit` 要素とCSSは削除済みです。

## 個別ページに関する重要な設計判断

- 個別HTMLを自動生成するスクリプトは、現時点では存在しません。
- `generate_creatures_json.py` は `data/creatures.json` の生成専用です。
- `content/creatures/**/*.md` は個別ページの内容の基礎資料です。
- 個別ページを増やす場合は、まず `creatures/hebi/habu.html` を基準にする。
- 個別ページは `creatures/hebi/` 以下に置くため、画像・共通ページへのリンクは `../../` から始める。
- 写真フォルダ名はMarkdownのIDと必ずしも一致しません。実際のフォルダを確認する。
- 処理済みJPEGの透かしを二重表示しない。個別ページにHTML/CSSの透かしを追加しない。

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

作成時は、それぞれのMarkdownと実在する処理済み写真を確認し、ハブ試作ページの構造を大きく変えずに内容だけ差し替える。

### 一覧ページとのリンク確認

`hebi.html` は上記7ページへリンクしています。現在はハブ以外のリンク先HTMLが未作成です。

アマミタカチホヘビの一覧リンクは次の名前です。

```text
creatures/hebi/amami-takachiho-hebi.html
```

一方、Markdownと写真フォルダのIDは `takachiho-hebi` です。ページ作成時は一覧リンクを変えないなら、HTMLファイル名を一覧リンクに合わせる必要があります。

### 他カテゴリー

カエル、クワガタなどの一覧ページ・個別ページの実装は、今後構成を確認してから着手する。ヘビの試作を先にブラウザ確認し、問題点を確定する。

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
