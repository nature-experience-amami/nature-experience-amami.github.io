---
name: amami-photo-fix
description: Nature Experience Amami(奄美大島のナイトツアーサイト)の生き物写真(images/creatures/)を直す・消す・調べるときに必ず使う。「写真の日付が間違ってた、直して」「間違えてアップした写真を消して」「failedに入ってる写真は何？」「写真はあるけどmdがないやつは？」「写真準備中になってる」「同じ写真が入ってた」のような依頼や、amami-tool.htmlでアップした写真がページに出ない・月がおかしいといった相談で使う。生き物の紹介文(md)を書くこと自体は amami-creature-md スキル、写真アップロードツールのコードの修正には使わない。
---

# Amami Photo Fix

## このスキルの読み方

- **決まり**(必ず守る): 処理済み写真の撮影日はファイル名だけにあること、ファイル名の形(`ID_連番6桁_YYYYMMDD_HH.jpg`)、消す前にオーナーに確認すること、main を取り込んでから作業すること、ページの作り直し、マージはオーナーの指示を待つこと
- **目安**(状況に合わせてよい): 調べ方や一覧の見せ方、報告の書き方

## ハルシネーション禁止(決まり)

確かめていないことを本当らしく言わない。写真の作業では特に:

- 「消えている」「直っている」は、main の中身を実際に確認してから言う
- どの写真が何の写真か、撮影日がいつかを推測で決めない。分からなければオーナーに聞く

## 写真の流れ(知っておくこと)

1. オーナーはiPhoneの `amami-tool.html`(GitHub Pagesで公開、パソコン不要)から写真を送る。写真は
   `images/creatures/カテゴリー/生き物ID/` か、`images/creatures/カテゴリー/グループ/生き物ID/`(例: `other-insects/tombo/ryuukyuu-haguro-tombo/`)に入る
2. `images/creatures/**` が変わると GitHub Actions の `process-creature-photos.yml` が動き、
   `scripts/process_creature_photos.py` が写真を処理してからページを全部作り直し、自動でコミットする
3. 処理では、EXIFの撮影日時を読んで `生き物ID_連番6桁_撮影日YYYYMMDD_時HH.jpg` に名前を変え、縮小・透かし入れをする。
   **このとき EXIF は消える。処理後の写真の撮影日はファイル名にしか残らない**
4. EXIFの撮影日時が読めない写真(SNSから保存した写真など)は処理されず、その生き物フォルダの `failed/` に移される。`failed/` は生き物ではない

撮影日はサイトで使われている: md に `months` が無い種は、写真ファイル名の撮影月から「観察しやすい月」が自動で決まる。

## よくある依頼と直し方

作業はいつもの流れ(ブランチで作業 → コミット → プルリクエスト → オーナーの「マージして」でマージ)で行う。
始める前に `git fetch origin main` で main を取り込み、オーナーがGitHubの画面やiPhoneで直接変えた分を必ず反映しておく。

### 撮影日の打ち間違い(例: 20260228 → 20250228)

処理済みの写真は EXIF が無いので、**ファイル名を直せばよい**(画像の中身は触らない)。

```bash
git mv 生き物フォルダ/ID_000001_20260228_12.jpg 生き物フォルダ/ID_000001_20250228_12.jpg
```

- 連番(`000001`)と時(`_12`)はそのまま、日付の部分だけ直す
- 同じ連番の写真が他にないか確認する
- `data/creatures.json` などに古いファイル名が残るので、ページを作り直す(下記)。md がまだ無い種でも `data/creatures.json` には載っている
- オーナーが複数枚送ったと言っていても、日付が違っているのは一部だけのことがある。フォルダの中身を一覧にして、どれを直すか確かめる

### 処理済みの写真が、撮影日でなく処理した日時の名前になった(実際にあった例)

- 2026-10-14に分かった例: アマミイボイモリの写真24枚が、すべて `amami-ibo-imori_連番_20260907_19.jpg` になっていた(実際は2024年12月〜2026年4月の冬の写真)
- 原因: 2026-09-07 に、正しい撮影日の入った処理済みの写真25枚(`amami-iboimori_…`)がフォルダ `amami-ibo-imori/` に入った。ファイル名の頭(`amami-iboimori`)がフォルダ名(`amami-ibo-imori`)と違うため、ワークフローが「まだ処理していない写真」として処理し直し、撮影日が処理した日時(UTCの9/7 19時)のファイル名で作り直された(元の25枚は消された)
- 決まり: 写真フォルダ名を変えるときは、中の写真ファイル名の頭も同じ名前に揃える(AGENTS.md と同じ)。揃っていないと、処理済みの写真がもう一度処理されてしまう
- 当時のスクリプトは、EXIFの無い写真にファイルの更新日時(=処理した時刻)を撮影日として付けていた。2026-09-12 の変更で、EXIFの無い写真は `failed/` に移すようになった(日付は書き換わらない)
- 2026-10-14 から、`process_creature_photos.py` の `fix_mismatched_prefix()` が、処理済みの形(`名前_連番6桁_日付8桁_時2桁.jpg`)なのに頭だけがフォルダ名と違う写真を、処理の前に頭だけ付け替える(写真の中身・日付・時は変えない。連番がフォルダの中でぶつかるときだけ空いている番号にする)。ワークフローのログに「ファイル名の頭をフォルダ名に付け替えた写真」として出る。付け替えが出たら、フォルダ名を変えたときに揃え忘れたということなので、オーナーに伝える
- 見分け方: 同じフォルダの写真がすべて同じ日・同じ時の名前で、その日時が写真をアップロード・処理した日時と同じ
- 戻し方(撮影日を推測しない): `git log --follow` や GitHub のコミット一覧で、写真が作り直された commit とその直前の commit を探し、直前の commit から元の写真(正しいファイル名)を取り出す。元の写真と今の写真を縮小して画像どうしで比べ、いちばん似ている元の写真の日付・時をファイル名に戻す(`git mv`)。連番はそのまま。続けて撮った同じような写真は1位と2位がほぼ同点になるが、日時も同じなので日付は決められる。「日時が違う元の写真のうち、いちばん似ているもの」の一致度がはっきり低いことも確かめる(イボイモリの例では、同じ写真が0.9995以上、日時が違う写真は0.60以下)
- 浅いクローン(履歴が50件ほど)だと古い commit が無い。`git fetch --unshallow origin main` で全履歴を取る(写真が多いので数分かかる)

### 間違えてアップした写真・failed の写真を消す

- `git rm` で消す。消す前に、それがどの写真か(ファイル名・サイズ・入っている場所)をオーナーに伝え、消してよいか確かめる
- `failed/` の写真は「日付が無くて処理できなかった写真」。要る写真なら、撮影日を入れ直して amami-tool から送り直してもらう。要らなければ消す
- オーナーが自分で消したと言っても、main にまだ残っていることがある(iPhoneの写真アプリで消しただけ、GitHubで「Commit changes」を押していない、など)。main を確認して、残っていればそう伝える

### 写真はあるのに md がない種を探す

写真フォルダ(`failed` を除き、写真が入っている一番下のフォルダ)の名前と、`content/creatures/*/*.md` の `id`
(および `scripts/generate_creature_pages.py` の `PHOTO_DIR_ALIASES`)を突き合わせて一覧にする。
カテゴリーページがある分類と、`crustaceans`(カニ)・`other-arthropods` のようにまだカテゴリーページが無い分類は分けて伝える。
md を作るときは `amami-creature-md` スキルを使う。

### 「写真準備中」と出る

md の `id` と写真フォルダ名がずれている、または写真がグループのフォルダの下にあって探せていないことが多い。
生成スクリプトの `photo_files()` は1階層目と2階層目(グループの下)を探す。ずれているときは、フォルダ名を md の id に合わせるか、`PHOTO_DIR_ALIASES` に対応を足す。

## ページの作り直し(決まり)

写真のファイル名を変えた・消したときは、リポジトリのルートで作り直す(ワークフローと同じ順):

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
```

`scripts/__pycache__/` の `*.cpython-311.pyc` はコミットしない。

## 報告(目安。形式は自由、中身は落とさない)

- 何をどう直したか(元のファイル名 → 新しいファイル名、消したファイル)
- 観察しやすい月などサイトの表示が変わるか
- プルリクエストのURL。マージはオーナーの「マージして」を待つ
- 必要なら `PROJECT_STATUS.md` の変更履歴に記録する(`amami-project-status-log` スキル)
