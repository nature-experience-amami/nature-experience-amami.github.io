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
    "lizards": 2, "aquatic-insects": 0.5,
}
# 同じ種を避ける期間(直近の投稿件数)。重み3のカテゴリーは種数が少ないので短め
AVOID_RECENT = 30
AVOID_RECENT_MAIN = 14

# 天気の判定の目安(仮の数値。現場の感覚に合わせて変えてよい)。「今夜」は19〜23時
HEAVY_RAIN_MM = 5      # 大雨: 今夜の1時間雨量の最大がこれ以上(mm)
STRONG_WIND_MS = 8     # 強風: 今夜の風速の最大がこれ以上(m/s)
LIGHT_RAIN_MM = 0.1    # 小雨: 今夜の1時間雨量の最大がこれ以上で、大雨ではない(=雨が降る予報)
AFTER_RAIN_MM = 1      # 雨上がり: 昨日の降水量がこれ以上(mm)で、
AFTER_RAIN_POP = 30    #           今夜の降水確率の最大がこれ以下(%)
CLEAR_POP = 20         # 晴れ: 今夜の降水確率の最大がこれ以下(%)で、雨上がり・小雨ではない
WARM_C = 20            # 暖かい: 今夜の平均気温がこれ以上(℃)
CALM_BREAKERS = {"大雨", "強風"}   # この日は、天気条件付きのコツ(大雨・強風が条件のものを除く)を選ばない

# ガイドの経験則(オーナーの現場の感覚)。当てはまる天気の日にプロンプトへ渡す
WEATHER_WISDOM = {
    "大雨": "大雨や風が強すぎる日は、生き物はほとんど動かない",
    "強風": "大雨や風が強すぎる日は、生き物はほとんど動かない",
    "小雨": "小雨や雨上がりは、カエルやヘビがよく活動する",
    "雨上がり": "小雨や雨上がりは、カエルやヘビがよく活動する",
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
  - 天気は渡したデータ(今夜の気温・湿度・降水確率・1時間雨量・風速、昨日の降水量)と天気の判定にあることだけを書く。
    「雨の降らない日が続いている」「週末は晴れ」など、データにないことを推測で補わない
  - 資料に天気との関係が書いてある場合だけ、今夜の天気がその生き物の見つけやすさにどう関係するかを書く
    (例: 資料に「雨の日に活発」→「雨上がりの今夜は出てきてくれそうです」)
  - 【ガイドの経験則】が渡されたときは、それも資料の根拠とみなしてよい
  - 天気の判定に「大雨」か「強風」があるときは、「今夜は生き物があまり動かない夜になりそう」という趣旨を書く
  - 天気の判定に「小雨」か「雨上がり」があるときは、カエルやヘビが活動しやすい夜であることに触れてよい
  - 資料にも経験則にも根拠がなければ、天気そのものを伝えるだけにする(例: 「今夜の奄美は雨の心配もなく、夜の散策日和です」)
  - 注意を書くのは、理由と注意が自然につながるときだけ。何に注意するかを具体的に書く
    (例: 「雨上がりで道がぬかるみやすいので、歩きやすい靴で」)。「足元にお気をつけて」のような曖昧な注意は書かない
  - 上の例文は書き方の参考。そのまま使わず、今夜の実際の天気に合わせて毎回言い回しを変える
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
        meta["name_en"] = english_name(md)
        items.append(meta)
    return items


def english_name(md):
    # サイトの英語版(id.en.md)の name を英名として使う。なければ空
    en = md.with_name(md.stem + ".en.md")
    if not en.exists():
        return ""
    m = re.match(r"^---\s*\n(.*?)\n---", en.read_text(encoding="utf-8"), re.S)
    return str(parse_front_matter(m.group(1)).get("name") or "") if m else ""


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
            "hourly": "temperature_2m,relative_humidity_2m,precipitation_probability,precipitation,wind_speed_10m",
            "daily": "precipitation_sum", "past_days": 1, "forecast_days": 1,
            "wind_speed_unit": "ms", "timezone": "Asia/Tokyo"}, timeout=20).json()
        h, today = d["hourly"], NOW.date().isoformat()
        idx = [i for i, t in enumerate(h["time"]) if t.startswith(today) and 19 <= int(t[11:13]) <= 23]
        return {
            "今夜の気温(平均℃)": round(sum(h["temperature_2m"][i] for i in idx) / len(idx), 1),
            "今夜の湿度(平均%)": round(sum(h["relative_humidity_2m"][i] for i in idx) / len(idx)),
            "今夜の降水確率(最大%)": max(h["precipitation_probability"][i] for i in idx),
            "今夜の1時間雨量(最大mm)": max(h["precipitation"][i] for i in idx),
            "今夜の風速(最大m/s)": round(max(h["wind_speed_10m"][i] for i in idx), 1),
            "昨日の降水量(mm)": d["daily"]["precipitation_sum"][0],
        }
    except Exception as e:
        print("天気の取得に失敗(天気なしで続行):", e)
        return None


def weather_conditions(w):
    # 天気データ → {"大雨", "強風", "小雨", "雨上がり", "晴れ", "暖かい"} のうち当てはまるもの
    if not w:
        return set()
    conds = set()
    rain, pop = w["今夜の1時間雨量(最大mm)"] or 0, w["今夜の降水確率(最大%)"] or 0
    if rain >= HEAVY_RAIN_MM:
        conds.add("大雨")
    elif rain >= LIGHT_RAIN_MM:
        conds.add("小雨")
    if (w["今夜の風速(最大m/s)"] or 0) >= STRONG_WIND_MS:
        conds.add("強風")
    if (w["昨日の降水量(mm)"] or 0) >= AFTER_RAIN_MM and pop <= AFTER_RAIN_POP:
        conds.add("雨上がり")
    if pop <= CLEAR_POP and not conds & {"雨上がり", "小雨", "大雨"}:
        conds.add("晴れ")
    if (w["今夜の気温(平均℃)"] or 0) >= WARM_C:
        conds.add("暖かい")
    return conds


def weather_block(w):
    # プロンプトに渡す【今夜の天気】の中身
    if not w:
        return "なし"
    conds = weather_conditions(w)
    order = ["大雨", "強風", "小雨", "雨上がり", "晴れ", "暖かい"]
    lines = [json.dumps(w, ensure_ascii=False),
             "天気の判定: " + ("、".join(c for c in order if c in conds) or "特になし")]
    wisdom = list(dict.fromkeys(WEATHER_WISDOM[c] for c in order if c in conds and c in WEATHER_WISDOM))
    if wisdom:
        lines.append("【ガイドの経験則】(オーナーの現場の感覚。資料の根拠とみなしてよい)")
        lines += [f"- {x}" for x in wisdom]
    return "\n".join(lines)


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
    return f"名前: {c.get('name')}\n英名: {c.get('name_en') or '(資料になし)'}\n危険度・保護: {c.get('danger', '')}\n資料:\n{c['body']}"


# ===== 投稿タイプごとの下書き作成 =====
def weighted_choice(pool):
    return random.choices(pool, weights=[CATEGORY_WEIGHT.get(c.get("category"), 1) for c in pool])[0]


def pick(pool, hist):
    # hist は新しい順
    recent = {h.get("creature") for h in hist[:AVOID_RECENT]}
    recent_main = {h.get("creature") for h in hist[:AVOID_RECENT_MAIN]}
    fresh = [c for c in pool
             if c["id"] not in (recent_main if CATEGORY_WEIGHT.get(c.get("category"), 1) >= 3 else recent)]
    return weighted_choice(fresh or pool)


def draft_creature(creatures, hist, weather):
    pool = [c for c in creatures if c["photos"] and is_season(c)] or [c for c in creatures if c["photos"]]
    c = pick(pool, hist)
    out = gemini(f"""以下の生き物を紹介するThreads投稿を作ってください。
{RULES}
出力はJSON: {{"post": "...", "weather_line": "...", "english": "..."}}

【生き物】
{creature_info(c)}

【今夜の天気】
{weather_block(weather)}""")
    return c, out, None


def draft_quiz(creatures, hist, weather):
    pool = [c for c in creatures if c["photos"] and is_season(c)] or [c for c in creatures if c["photos"]]
    c = pick(pool, hist)
    out = gemini(f"""以下の生き物の写真を使った「この生き物の名前は？」クイズのThreads投稿を作ってください。
{RULES}
- post には生き物の名前を絶対に出さず、資料から分かるヒントを1〜2個入れる。最後に「答えはコメントで！」のように呼びかける
- answer には正解の名前と、一言解説(100字以内)
- answer_en には英語の答えを1文で。形式は「Answer: 英名, 短い解説」。英名は資料にあればそれを使い、なければ一般的な英名にする
出力はJSON: {{"post": "...", "weather_line": "...", "english": "...", "answer": "...", "answer_en": "..."}}

【生き物】
{creature_info(c)}

【今夜の天気】
{weather_block(weather)}""")
    return c, out, None


def tip_creatures(tip):
    # creature は「id」1つ、またはリスト(要素は「id」か「{id, months}」) → [(id, 月のリスト or None)]
    items = tip.get("creature") or []
    if not isinstance(items, list):
        items = [items]
    out = []
    for it in items:
        if isinstance(it, dict):
            out.append((str(it.get("id") or ""), it.get("months")))
        elif it:
            out.append((str(it), None))
    return out


def tip_available(tip, conds):
    # months: その月だけ / weather: どれか1つに当てはまる日だけ(両方あれば両方)
    if tip.get("months") and NOW.month not in tip["months"]:
        return False
    need = set(tip.get("weather") or [])
    if not need:
        return True
    if conds & CALM_BREAKERS and not need & CALM_BREAKERS:
        return False   # 大雨・強風の日は、天気条件付きのコツを選ばない
    return bool(need & conds)


def draft_tip(creatures, hist, weather):
    tips = yaml.safe_load(TIPS_FILE.read_text(encoding="utf-8"))
    used = {h.get("tip") for h in hist}
    # コツ単位の months / weather を満たすものだけ選択肢に入れる
    conds = weather_conditions(weather)
    in_month = [i for i, t in enumerate(tips) if tip_available(t, conds)]
    in_month = in_month or list(range(len(tips)))
    fresh = [i for i in in_month if i not in used]
    ti = random.choice(fresh or in_month)
    tip = tips[ti]
    by_id = {c["id"]: c for c in creatures if c["photos"]}
    related = [by_id[cid] for cid, months in tip_creatures(tip)
               if cid in by_id and (not months or NOW.month in months)
               and (not tip.get("creature_season") or is_season(by_id[cid]))]
    if related:
        c = random.choice(related)
        photo_note = ("【添える写真の生き物】(このコツに関係する生き物)\n"
                      "- コツと結びつけて紹介してよい。ただし資料の範囲で")
    else:
        c = weighted_choice([c for c in by_id.values() if is_season(c)] or list(by_id.values()))
        photo_note = ("【添える写真の生き物】(コツとは関係なく、写真のためにランダムに選んだ生き物)\n"
                      "- コツと写真の生き物を結びつけない。コツの説明にこの生き物を使わない\n"
                      "- 本文の最後に「写真は○○」のように名前を簡単に紹介するだけにする")
    out = gemini(f"""ガイドが書いた「観察のコツ」を、Threads投稿に整えてください。
{RULES}
- ガイドの言葉の意味を変えない。ガイドが書いていない知識を足さない(生き物資料は写真の説明に使う程度)
出力はJSON: {{"post": "...", "weather_line": "...", "english": "..."}}

【ガイドのコツ】({tip.get('type', '')})
{tip['text']}

{photo_note}
{creature_info(c)}

【今夜の天気】
{weather_block(weather)}""")
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
                  "\n".join(filter(None, [out["answer"].strip(), (out.get("answer_en") or "").strip(),
                                          f"詳しくはこちら→ {page_url(c)}"])), "```"]
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
