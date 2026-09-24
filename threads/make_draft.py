"""
Threads投稿の下書きを作ってGitHub Issueに置くスクリプト
- 曜日ごとに投稿タイプを切り替え(ROTATION)
- サイトのリポジトリ内 threads/ フォルダに置く。サイトのファイルは読むだけで一切変更しない
- 生き物情報はcontent/creatures/**/*.md、写真はサイトの公開URLを使う
- 投稿履歴は過去のIssue(ラベル threads-draft)から読み取り、同じ生き物・ネタの連続を避ける
- Geminiの呼び出しは1日1回(ツアー案内の日は0回)
"""
import ast
import datetime
import json
import os
import random
import re
import sys
import time
from pathlib import Path
from urllib.parse import quote

import requests
import yaml

# ===== 設定 =====
SITE_URL = "https://nature-experience-amami.github.io"
SITE_DIR = Path(".")                         # サイトのリポジトリ直下で実行する(threads/フォルダ以外は読むだけ)
CONTENT_DIR = SITE_DIR / "content" / "creatures"
PHOTO_ROOT = SITE_DIR / "images" / "creatures"   # 処理済み(透かし入り)写真のフォルダ
PAGE_DIR = SITE_DIR / "creatures"            # 個別ページ creatures/カテゴリー/id.html
ALIAS_SOURCE = SITE_DIR / "scripts" / "generate_creatures_json.py"  # 写真フォルダ名とidの対応表(読むだけ)
LANG_MD = re.compile(r"\.(en|es|zh)\.md$")   # 翻訳ファイルは読まない
LINE_URL = "https://line.me/R/ti/p/@701eehfz" # 公式LINE(友だち追加)
TIPS_FILE = Path("threads/tips.yml")
TOPIC_TAG = "#奄美大島"
DRAFT_LABEL = "threads-draft"
AMAMI_LATLON = (28.38, 129.49)
IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp"}
# 上から順に試し、404(モデルが見つからない)なら次へ。GEMINI_MODEL(リポジトリ変数)があれば最優先
GEMINI_MODELS = list(dict.fromkeys(
    m for m in (os.environ.get("GEMINI_MODEL"), "gemini-3.1-flash-lite", "gemini-flash-latest") if m))

# 生き物を選ぶときのカテゴリーの重み(夜に出会える主役級を多めに)。表にないカテゴリーは1
CATEGORY_WEIGHT = {
    "snakes": 3, "amphibians": 3, "stag-beetles": 3, "mammals": 3, "birds": 3,
    "lizards": 2,
}

# 0=月 … 6=日
ROTATION = {0: "creature", 1: "tip", 2: "quiz", 3: "creature", 4: "tip", 5: "creature", 6: "tour"}
TYPE_LABEL = {"creature": "生き物紹介", "tip": "観察のコツ", "quiz": "クイズ", "tour": "ツアー案内"}

JST = datetime.timezone(datetime.timedelta(hours=9))
NOW = datetime.datetime.now(JST)

RULES = """
- 奄美大島のナイトツアーガイド「Nature Experience Amami」の公式アカウントとして書く
- 親しみやすく、でも誇張しない。事実は与えた資料の範囲だけで書き、資料にないことを付け足さない
- 「夜に見られる」「ツアーで会える」など、資料にない活動時間帯・出会いやすさ・見られる場所は書かない
- 学名は資料に書いてあるときだけ使う
- 具体的な観察場所(地名・林道名・集落名など)は絶対に書かない。「奄美大島」までにとどめる
- 採集や持ち帰り、生き物に触る・追い回すことを勧める表現は使わない
- 本文(post)は日本語で250字以内。絵文字は2つまで。ハッシュタグとURLは付けない
- weather_line: 天気情報があれば、今夜の天気についての一言(40字以内)。天気情報がなければ空文字
  - 資料に天気との関係が書いてある場合だけ、今夜の天気がその生き物の見つけやすさにどう関係するかを書く
    (例: 資料に「雨の日に活発」→「雨上がりの今夜は出てきてくれそうです」)
  - 資料に根拠がなければ、天気そのものを伝えるだけにする(例: 「今夜の奄美は雨の心配もなく、夜の散策日和です」)
  - 注意を書くのは、理由と注意が自然につながるときだけ。何に注意するかを具体的に書く
    (例: 「雨上がりで道がぬかるみやすいので、歩きやすい靴で」)。「足元にお気をつけて」のような曖昧な注意は書かない
- english: 本文の要点を短い英語1文で
"""


# ===== データ読み込み =====
def load_photo_aliases():
    # サイト側の MARKDOWN_ID_ALIASES をテキストとして解析するだけ(importしないので処理は走らない)
    # {(カテゴリー, 写真フォルダ名): id} → {(カテゴリー, id): 写真フォルダ名}
    try:
        tree = ast.parse(ALIAS_SOURCE.read_text(encoding="utf-8"))
        for node in tree.body:
            if (isinstance(node, ast.Assign)
                    and any(isinstance(t, ast.Name) and t.id == "MARKDOWN_ID_ALIASES" for t in node.targets)):
                return {(cat, cid): folder for (cat, folder), cid in ast.literal_eval(node.value).items()}
    except Exception as e:
        print("写真フォルダの対応表を読めませんでした(対応表なしで続行):", e)
    return {}


PHOTO_ALIASES = load_photo_aliases()


def parse_front_matter(text):
    try:
        return yaml.safe_load(text) or {}
    except yaml.YAMLError:
        # YAMLとして読めない行(「: 」を含むsourceなど)がある場合は、必要な項目だけ1行ずつ読む
        meta = dict(re.findall(r"^(id|name|category|danger):\s*(.+?)\s*$", text, re.M))
        m = re.search(r"^months:\s*\[(.*?)\]", text, re.M)
        if m:
            meta["months"] = [int(x) for x in m.group(1).split(",") if x.strip().isdigit()]
        return meta


def load_creatures():
    items = []
    for md in CONTENT_DIR.rglob("*.md"):
        if LANG_MD.search(md.name):
            continue
        m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", md.read_text(encoding="utf-8"), re.S)
        if not m:
            continue
        meta = parse_front_matter(m.group(1))
        if not meta.get("id"):
            continue
        meta["body"] = m.group(2).strip()
        meta["photos"] = find_photos(meta["id"], meta.get("category"))
        items.append(meta)
    return items


def find_photos(cid, category=None):
    # Markdownのidと写真フォルダ名がズレている種(サイト側の対応表・amami-付き)にも対応
    names = [PHOTO_ALIASES.get((category, cid)), cid, f"amami-{cid}"]
    for name in filter(None, names):
        photos = sorted(
            p for d in PHOTO_ROOT.rglob(name) if d.is_dir()
            for p in d.iterdir() if p.suffix.lower() in IMAGE_EXT
        )
        if photos:
            return photos
    return []


def to_url(path):
    return f"{SITE_URL}/{quote(path.relative_to(SITE_DIR).as_posix())}"


def page_url(c):
    page = PAGE_DIR / str(c.get("category", "")) / f"{c['id']}.html"
    return to_url(page) if page.exists() else SITE_URL + "/"


def is_season(c):
    months = c.get("months")
    return not months or NOW.month in months


# ===== 過去の下書き(Issue)から履歴を読む =====
def gh_headers():
    return {"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
            "Accept": "application/vnd.github+json"}


def recent_history(n=30):
    r = requests.get(
        f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/issues",
        params={"labels": DRAFT_LABEL, "state": "all", "per_page": n},
        headers=gh_headers(), timeout=30)
    r.raise_for_status()
    hist = []
    for issue in r.json():
        m = re.search(r"<!-- meta: (.*?) -->", issue.get("body") or "")
        if m:
            hist.append(json.loads(m.group(1)))
    return hist


# ===== 天気 =====
def tonight_weather():
    try:
        d = requests.get("https://api.open-meteo.com/v1/forecast", params={
            "latitude": AMAMI_LATLON[0], "longitude": AMAMI_LATLON[1],
            "hourly": "temperature_2m,relative_humidity_2m,precipitation_probability",
            "daily": "precipitation_sum", "past_days": 1, "forecast_days": 1,
            "timezone": "Asia/Tokyo"}, timeout=20).json()
        h, today = d["hourly"], NOW.date().isoformat()
        idx = [i for i, t in enumerate(h["time"]) if t.startswith(today) and 19 <= int(t[11:13]) <= 23]
        return {
            "今夜の気温(平均℃)": round(sum(h["temperature_2m"][i] for i in idx) / len(idx), 1),
            "今夜の湿度(平均%)": round(sum(h["relative_humidity_2m"][i] for i in idx) / len(idx)),
            "今夜の降水確率(最大%)": max(h["precipitation_probability"][i] for i in idx),
            "昨日の降水量(mm)": d["daily"]["precipitation_sum"][0],
        }
    except Exception as e:
        print("天気の取得に失敗(天気なしで続行):", e)
        return None


# ===== Gemini =====
def gemini(prompt):
    body = {"contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseMimeType": "application/json", "temperature": 0.8}}
    for model in GEMINI_MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        for attempt in range(3):
            r = requests.post(url, params={"key": os.environ["GEMINI_API_KEY"]}, json=body, timeout=90)
            if r.ok:
                print(f"Geminiモデル: {model}")
                return json.loads(r.json()["candidates"][0]["content"]["parts"][0]["text"])
            if r.status_code == 404:
                print(f"Geminiモデル {model} が見つからない(404) → 次の候補へ")
                break
            print(f"Gemini失敗({r.status_code}, {model}) 再試行 {attempt + 1}/3")
            time.sleep(15)
        else:
            r.raise_for_status()
    r.raise_for_status()


def creature_info(c):
    return f"名前: {c.get('name')}\n危険度・保護: {c.get('danger', '')}\n資料:\n{c['body']}"


# ===== 投稿タイプごとの下書き作成 =====
def weighted_choice(pool):
    return random.choices(pool, weights=[CATEGORY_WEIGHT.get(c.get("category"), 1) for c in pool])[0]


def pick(pool, used):
    fresh = [c for c in pool if c["id"] not in used]
    return weighted_choice(fresh or pool)


def draft_creature(creatures, hist, weather):
    used = {h.get("creature") for h in hist}
    pool = [c for c in creatures if c["photos"] and is_season(c)] or [c for c in creatures if c["photos"]]
    c = pick(pool, used)
    out = gemini(f"""以下の生き物を紹介するThreads投稿を作ってください。
{RULES}
出力はJSON: {{"post": "...", "weather_line": "...", "english": "..."}}

【生き物】
{creature_info(c)}

【今夜の天気】
{json.dumps(weather, ensure_ascii=False) if weather else "なし"}""")
    return c, out, None


def draft_quiz(creatures, hist, weather):
    used = {h.get("creature") for h in hist}
    pool = [c for c in creatures if c["photos"] and is_season(c)] or [c for c in creatures if c["photos"]]
    c = pick(pool, used)
    out = gemini(f"""以下の生き物の写真を使った「この生き物の名前は？」クイズのThreads投稿を作ってください。
{RULES}
- post には生き物の名前を絶対に出さず、資料から分かるヒントを1〜2個入れる。最後に「答えはコメントで！」のように呼びかける
- answer には正解の名前と、一言解説(100字以内)
出力はJSON: {{"post": "...", "weather_line": "...", "english": "...", "answer": "..."}}

【生き物】
{creature_info(c)}

【今夜の天気】
{json.dumps(weather, ensure_ascii=False) if weather else "なし"}""")
    return c, out, None


def draft_tip(creatures, hist, weather):
    tips = yaml.safe_load(TIPS_FILE.read_text(encoding="utf-8"))
    used = {h.get("tip") for h in hist}
    fresh = [i for i in range(len(tips)) if i not in used]
    ti = random.choice(fresh or list(range(len(tips))))
    tip = tips[ti]
    by_id = {c["id"]: c for c in creatures if c["photos"]}
    c = by_id.get(tip.get("creature")) or weighted_choice(
        [c for c in by_id.values() if is_season(c)] or list(by_id.values()))
    out = gemini(f"""ガイドが書いた「観察のコツ」を、Threads投稿に整えてください。
{RULES}
- ガイドの言葉の意味を変えない。ガイドが書いていない知識を足さない(生き物資料は写真の説明に使う程度)
出力はJSON: {{"post": "...", "weather_line": "...", "english": "..."}}

【ガイドのコツ】({tip.get('type', '')})
{tip['text']}

【添える写真の生き物】
{creature_info(c)}

【今夜の天気】
{json.dumps(weather, ensure_ascii=False) if weather else "なし"}""")
    return c, out, ti


def draft_tour(creatures, hist, weather):
    season = [c for c in creatures if c["photos"] and c.get("months") and NOW.month in c["months"]]
    names = "・".join(c["name"] for c in random.sample(season, min(3, len(season))))
    c = random.choice(season or [c for c in creatures if c["photos"]])
    post = ("奄美大島の夜の森を、ガイドと一緒に歩いてみませんか？\n"
            + (f"今の時期は{names}などに出会えるチャンスがあります。\n" if names else "")
            + "その日の天気や季節に合わせて、生き物を探しに行きます。\n\n"
            + f"ご予約・ご質問は公式LINEから気軽にどうぞ\n{LINE_URL}\n\n"
            + f"ホームページ\n{SITE_URL}")
    return c, {"post": post, "weather_line": "", "english": ""}, None


# ===== Issue作成 =====
def build_text(ptype, c, out):
    parts = [out["post"].strip()]
    if out.get("weather_line"):
        parts.append(out["weather_line"].strip())
    if ptype in ("creature", "tip"):
        parts.append(f"詳しくはこちら→ {page_url(c)}")
    if out.get("english"):
        parts.append(out["english"].strip())
    parts.append(TOPIC_TAG)
    text = "\n\n".join(parts)
    if len(text) > 480 and out.get("english"):   # Threadsの500字制限対策
        parts.remove(out["english"].strip())
        text = "\n\n".join(parts)
    return text


def create_issue(ptype, c, out, tip_index):
    text = build_text(ptype, c, out)
    photos = random.sample(c["photos"], min(3, len(c["photos"])))
    lines = [f"## 投稿文（{len(text)}字）", "```text", text, "```"]
    if out.get("answer"):
        lines += ["", "## クイズの答え（数時間後に自分でコメント）", "```text",
                  f"{out['answer'].strip()}\n詳しくはこちら→ {page_url(c)}", "```"]
    lines += ["", "## 写真（長押しで保存 → Threadsに添付）"]
    lines += [f"![{c.get('name')}]({to_url(p)})" for p in photos]
    meta = {"type": ptype, "creature": c["id"], "tip": tip_index, "date": NOW.date().isoformat()}
    lines += ["", f"<!-- meta: {json.dumps(meta, ensure_ascii=False)} -->"]

    title = f"{NOW:%m/%d} {TYPE_LABEL[ptype]}：{c.get('name')}"
    r = requests.post(
        f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/issues",
        json={"title": title, "body": "\n".join(lines), "labels": [DRAFT_LABEL]},
        headers=gh_headers(), timeout=30)
    r.raise_for_status()
    print("下書き作成:", r.json()["html_url"])


def main():
    ptype = os.environ.get("POST_TYPE") or ROTATION[NOW.weekday()]
    creatures = load_creatures()
    if not any(c["photos"] for c in creatures):
        sys.exit(f"写真付きの生き物が見つかりません。PHOTO_ROOT({PHOTO_ROOT})を確認してください")
    hist = recent_history()
    weather = tonight_weather() if ptype != "tour" else None
    maker = {"creature": draft_creature, "quiz": draft_quiz, "tip": draft_tip, "tour": draft_tour}[ptype]
    c, out, tip_index = maker(creatures, hist, weather)
    create_issue(ptype, c, out, tip_index)


if __name__ == "__main__":
    main()
