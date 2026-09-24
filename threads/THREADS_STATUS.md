# Threads投稿システム 状況記録（THREADS_STATUS.md）

ナイトツアー集客のためのThreads投稿の仕組み。複数のAIで引き継げるよう、現在の構成・方針・TODO・変更履歴をここにまとめる。
「変更履歴」は過去の記録を消さずに末尾へ追加する。それ以外のセクションは最新の状態に書き換えてよい。

---

## 現在の構成

- 置き場所：ホームページのリポジトリ内 `threads/` フォルダ（ホームページと干渉しないよう分離）
  - `threads/make_draft.py` … 下書き生成スクリプト
  - `threads/tips.yml` … ガイドの観察のコツ（ネタ帳）
  - `threads/requirements.txt` … requests, pyyaml
  - `threads/THREADS_STATUS.md` … このファイル
  - `.github/workflows/threads-draft.yml` … GitHubのルール上ここにしか置けないため、この1ファイルだけ既存フォルダに追加
- 動き：毎朝 6:17 JST にGitHub Actionsが起動 → 下書きをGitHub Issue（ラベル `threads-draft`）に作成 → 内容を確認してThreadsアプリに手動でコピペ投稿
- 手動実行：Actionsタブの「Threads draft」から、投稿タイプ（auto / creature / tip / quiz / tour）を選んで実行できる
- 投稿履歴：過去30件のIssueに埋め込んだ記録から読み取る（自動commitなし、外部データベースなし）
- Gemini呼び出し：1日1回（ツアー案内の日は0回）。モデル名はリポジトリ変数 `GEMINI_MODEL` で指定、未設定なら `gemini-2.5-flash`
- 天気：Open-Meteo（APIキー不要）で奄美の今夜（19〜23時）の気温・湿度・降水確率と昨日の雨量を取得

## ホームページと干渉しないためのルール

- サイトのファイル（content/creatures の Markdown・写真）は**読むだけ**。ワークフローの権限は `contents: read` と `issues: write` のみ
- ワークフローからのcommit・pushは一切しない（サイトの再公開は発生しない）
- 既存のワークフロー・index.html・生成スクリプトなどには触れない
- 注意：公開リポジトリのため `threads/` の中身もURL直打ちで見える。秘密情報（APIキー等）は絶対にファイルに書かず、Secretsに登録する

## 投稿の方針

### 曜日ローテーション

| 曜日 | タイプ | 内容 |
|---|---|---|
| 月・木・土 | 生き物紹介 | 今の時期（months）に見られる生き物を1種。写真＋Markdown要約＋個別ページへのリンク |
| 火・金 | 観察のコツ | tips.yml のネタをGeminiが投稿向けに整える（意味は変えない・知識を足さない） |
| 水 | クイズ | 写真と「この生き物の名前は？」。名前は伏せてヒントのみ。答えは数時間後に自分でコメント |
| 日 | ツアー案内 | 定型文（Geminiなし）。季節の生き物名＋公式LINE＋ホームページ |

### 全投稿共通のルール（プロンプトに組み込み済み）

- 具体的な観察場所（地名・林道名・集落名）は書かない。「奄美大島」まで
- 採集・持ち帰り・触る・追い回すことを勧めない
- 資料（Markdown・ネタ帳）にないことを付け足さない
- 本文250字以内、絵文字2つまで。天気の一言と英語1文を添える（500字を超えそうなら英語を省略）
- トピックタグは `#奄美大島` に固定（Threadsは1投稿1タグ）

### 載せるリンク

- ホームページ：https://nature-experience-amami.github.io
- 公式LINE（ガイド問い合わせ用、ID @701eehfz）：https://line.me/R/ti/p/@701eehfz
- 生き物紹介・コツの日は個別ページのリンクのみ。LINEはツアー案内の日だけ（宣伝っぽくしすぎない）

## Meta（Threads API）について

- 自動投稿にはMeta開発者登録が必要。過去にFacebookの電話番号認証がループして断念した（Meta側で調査中の既知の不具合）
- そのため、当面は「下書きをIssueに作る → 手動コピペ投稿」で運用する
- 登録が通ったら「Issueに『投稿OK』ラベルを付けると自動投稿」の仕組みを後から追加する予定
- 再挑戦のコツ：先にFacebookのアカウントセンターで電話番号を確認済みにする／認証後にループしたら一度ログアウトしてアプリ一覧ページに直接アクセス／Cookie削除かシークレットウィンドウ／ダメなら数日あける

---

## TODO

### 設置前（要確認）

- [ ] 処理済み（透かし入り）写真のフォルダのパスを確認し、`make_draft.py` の `PHOTO_ROOT`（現在は仮に `photos`）を修正
- [ ] 公式LINEのリンク（https://line.me/R/ti/p/@701eehfz）をタップして友だち追加画面が開くか確認

### 設置

- [ ] GitHub Desktopで `threads/` フォルダと `.github/workflows/threads-draft.yml` を追加し、1回だけcommit・push
- [x] リポジトリの Settings → Secrets に `THREADS_GEMINI_API_KEY` を登録（株式レポート用の `GEMINI_API_KEY` と名前が重なるため別名。ワークフローで環境変数 `GEMINI_API_KEY` として `make_draft.py` に渡す）
- [ ] （任意）Settings → Variables に `GEMINI_MODEL` を登録（株式レポートと同じモデル名）
- [ ] Actionsタブから手動実行し、creature / tip / quiz / tour の4タイプを1回ずつテスト
- [ ] 下書きの文章・写真・リンクが正しいか確認し、必要ならプロンプトを調整

### Threadsアカウントの準備

- [ ] プロフィール整備（アイコン・紹介文・ホームページと公式LINEのリンク）
- [ ] 最初のうちは手動投稿（ツアーの様子など）やコメント返信も並行する

### ネタ帳（tips.yml）

- [ ] 各ネタに関連する生き物のID（`creature:`）を追記（現在はハブのみ設定）
- [ ] 思いついたネタを随時追加

### 今後の拡張（後回し）

- [ ] Meta開発者登録に再挑戦 → 通ったら「投稿OK」ラベルで自動投稿する仕組みを追加
- [ ] アクセストークン（60日期限）の自動更新
- [ ] 下書き完成を公式LINEに通知（任意）
- [ ] 慣れてきたら確認なしの全自動運用に切り替えるか検討

---

## 変更履歴

### 2026-09-24 Threads投稿の下書きシステムを新規作成

- ナイトツアー集客のため、Threadsの投稿下書きを毎朝GitHub Issueに作る仕組みを作成（make_draft.py / tips.yml / requirements.txt / threads-draft.yml）
- Meta開発者登録が認証ループで通らないため、自動投稿は後回しにし、まず下書き＋手動コピペ投稿で始める方針に決定
- 最初は投稿前に内容を確認する運用にする
- 投稿内容は「写真＋Markdown要約＋ホームページ誘導」を土台に、曜日ローテーション（生き物紹介・観察のコツ・クイズ・ツアー案内）と天気連動の一言を追加
- 観察のコツはGeminiに作らせると誤情報の恐れがあるため、ガイド自身が書いたネタ帳（tips.yml、初期10件）を元にする方針
- 当初は別リポジトリ案だったが、ホームページのリポジトリ内に `threads/` フォルダを作って置く形に変更。サイトのファイルは読むだけにして干渉しないようにした
- ツアー案内の日に公式LINE（@701eehfz）とホームページのURLを載せるよう反映
- 未完了事項：写真フォルダのパス（PHOTO_ROOT）の確認、設置とテスト実行
- Commit SHA：なし（未commit）
- Push：未実施

（担当: Claude／くろちゃん）

### 2026-09-24 リポジトリへの設置と写真フォルダの確認

- `threads/` の4ファイルと `.github/workflows/threads-draft.yml` をリポジトリに作成（既存ファイル・既存ワークフローは変更なし）
- 処理済み（透かし入り）写真は `images/creatures/カテゴリー/生き物ID/` にあることを確認（`scripts/process_creature_photos.py` がその場で透かしを入れ、元写真は削除する）。`make_draft.py` の `PHOTO_ROOT` を `SITE_DIR / "images" / "creatures"` に修正
  - 写真862枚はすべて処理済みの名前（`ID_連番_日付_時.jpg`）で、未処理の元写真は0枚。`failed/` の1枚（akamata）は生き物フォルダ直下ではないため対象外
- `load_creatures()` を実行（Gemini・GitHub APIは呼ばない）したところ、**そのままでは2つの問題があり、エラーで止まる**ことが判明（未修正・要相談）
  1. `content/creatures/**/*.md` をすべて読むため、翻訳ファイル（`.en.md` / `.es.md` / `.zh.md`）まで生き物として読み込まれてしまう（日本語98件＋翻訳で合計392件、IDが重複する）
  2. 一部のMarkdownの `source:` 行に「: 」を含む文があり、YAMLとして読めずに停止する（日本語では `nomura-himedoromushi.md` と `ryuukyuu-munabiro-tuyadoromushi.md` の2件、翻訳ファイルでは35件）。サイト側の生成スクリプトはYAMLを使わず行ごとに読んでいるため、サイトには影響なし
- 仮に「日本語の.mdだけ」「読めない行は飛ばす」という条件で確認した結果：日本語98種のうち94種で写真が見つかり（計754枚、透かしなしの写真・failed内の写真は0枚）、見つからなかったのは4種
  - 見つからなかった4種：iboimori（写真フォルダは amami-ibo-imori）、ryukyu-ao-hebi（写真フォルダは ryuukyuu-aohebi）、tobiiro-gengoro・toge-nezumi（写真フォルダなし）
  - 最初の2種は、サイト側の `MARKDOWN_ID_ALIASES` にある対応表が `make_draft.py` の「amami-付き」の対応だけでは拾えないため
- 未完了事項：上記2つの問題の修正方針の決定、写真が見つからない2種の対応の決定
- Commit SHA：（このcommit）
- Push：`claude/connection-check-f9140f` ブランチへ（mainへのマージは未実施）

（担当: Claude Code）

### 2026-09-24 load_creatures() の読み込み不具合を修正

- `make_draft.py` の読み込み部分を修正（サイト側のファイルは変更なし）
  1. 翻訳ファイル（`.en.md` / `.es.md` / `.zh.md`）を読み込み対象から除外
  2. YAMLとして読めないMarkdownは、`id` / `name` / `category` / `danger` / `months` だけを1行ずつ読むように変更（エラーで止まらない）
  3. 写真フォルダ名とidの対応表として、サイト側 `scripts/generate_creatures_json.py` の `MARKDOWN_ID_ALIASES` を使用。`ast` でファイルの文字列を解析するだけで、importや実行はしない（読めない場合は対応表なしで続行）。従来の「amami-付き」の対応も残した
- 修正後に `load_creatures()` を実行（Gemini・GitHub APIは呼ばない）：日本語98種のうち96種で写真が見つかった（計798枚）。ID重複なし、透かしなし・failed内の写真の混入なし、全種に個別ページあり
  - iboimori（24枚）と ryukyu-ao-hebi（20枚）は対応表で見つかるようになった
  - 写真が見つからないのは tobiiro-gengoro（トビイロゲンゴロウ）と toge-nezumi（アマミトゲネズミ）の2種のみ。写真フォルダがないためで、この2種は投稿の対象外になる（写真を追加すれば自動で対象になる）
  - `danger` は57種に設定あり。YAMLで読めなかった2種（nomura-himedoromushi・ryuukyuu-munabiro-tuyadoromushi）は元々 `danger` の行がない
- 未完了事項：mainへのマージ、Secrets登録、Actionsでのテスト実行
- Commit SHA：（このcommit）
- Push：`claude/connection-check-f9140f` ブランチへ（mainへのマージは未実施）

（担当: Claude Code）

### 2026-09-24 GeminiのSecret名を THREADS_GEMINI_API_KEY に変更

- 既存のSecret `GEMINI_API_KEY`（株式レポート用）と名前が重なるため、Threads用のキーは `THREADS_GEMINI_API_KEY` という名前で登録された（登録済み）
- `.github/workflows/threads-draft.yml` の `GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}` を `GEMINI_API_KEY: ${{ secrets.THREADS_GEMINI_API_KEY }}` に変更
  - 左側の `GEMINI_API_KEY` は `make_draft.py` が読む環境変数名なのでそのまま。`make_draft.py` は変更なし
- TODOの「Secrets登録」を完了に更新
- 未完了事項：mainへのマージ、Actionsでのテスト実行
- Push：`claude/connection-check-f9140f` ブランチへ（mainへのマージは未実施）

（担当: Claude Code）
