# Nature Experience Amami - Project Status

最終更新: 2026-09-30（日本時間）

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

- カテゴリーのフォルダ名は英語名: `snakes` `amphibians` `stag-beetles` `mammals` `birds` `lizards` `aquatic-insects` `beetles` `other-insects`（写真だけ `crustaceans`（カニ） `other-arthropods` もある）。
- 一覧ページの形式: `snakes` `amphibians` `stag-beetles` `mammals` はカテゴリーページ、`birds` `aquatic-insects` `beetles` `other-insects` は図鑑ページ（`scripts/generate_zukan_page.py`）。`lizards` は生き物ごとのページだけで、一覧ページはまだない。
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
- Claude Code のクラウド環境のネットワーク設定で、生き物の調べ物に使うサイトを許可する（環境の編集 → Network access）。2026-09-30、`ja.wikipedia.org`・`www.sci.hokudai.ac.jp`・`jpnrdb.com` のページを開こうとして止められた（Web検索はできる）。監修役 `creature-reviewer` も同じ制限を受ける。追加候補: 上の3つ、`en.wikipedia.org`・`www.gbif.org`・`www.env.go.jp`・`www.pref.kagoshima.jp`
- 上の設定のあと、アマミサソリモドキ（`other-arthropods/amami-sasorimodoki`）とオオゲジ（`other-arthropods/oo-geji`）のmdを作り、`creature-reviewer` で監修する（`amami-creature-md` スキル）。9/30は検索結果の要約だけで調べたところで止めた（下書きファイルはまだ無い）

## やることリスト

### AIチャット・Worker

- サイトの `index.html`（4言語）が、Workerに生き物データを丸ごと付けて送っている（約17万字、Workerは使っていない）。送らないようにする。
- Cloudflareの変数 `GEMINI_API_KEY_ADMIN` は使われていない。消すかどうか決める。

### 生き物データ・ページ

- 生き物ページで、写真の撮影日だけで決まった月（`months_source` が `photos`、日本語版18種）も「観察しやすい時期」として表示されている。オーナーが `months:` を書くか、ページでも「撮影記録」と表示を分けるか決める。
  - トップページの「FIELD NOTE（今月に観察しやすい生き物）」も同じで、`index.html` は `months_source` を見ずに月だけで選んでいる（2026-10-01確認。10月はアマミヒラタヒシバッタと、mdが無くフォルダ名で出る ko-iso-kanimushi が対象）。説明文は「ガイドが入力した観察時期をもとに」なので合わない。
  - 2026-10-01に18種の時期をWeb検索したが、ページを開けず要約だけだった。小さい水生昆虫とアマミヒラタヒシバッタは情報が見つからなかった。ネットワーク設定のあとに調べ直し、オーナーと1種ずつ `months:` を決める（資料の繁殖期などは本文へ）。決めきれない種は `months:` を書かず、フィールドノートには出さないようにする案。
- カニ（`crustaceans`）とその他の節足動物（`other-arthropods`）の7種類は、Markdownもカテゴリーページもまだない。そのためAIチャットで和名ではなく写真フォルダ名（例: okayadokari）が出る。
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
