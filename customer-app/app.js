const KEY="nea_customer_app_v1";
let records=JSON.parse(localStorage.getItem(KEY)||"[]");
let currentId=null;
let parsedParticipants=[];

const $=id=>document.getElementById(id);
const today=()=>new Date().toISOString().slice(0,10);
const save=()=>localStorage.setItem(KEY,JSON.stringify(records));

// --- AI連携(サイト本体と同じCloudflare Worker + Geminiを共用) ---
const WORKER_URL="https://nature-experience-ai.aegusaegus.workers.dev/";

// 料金・持ち物など、返信文に正確に反映させたい固定の業務情報。変わったらここを直す。
const GUIDE_FACTS=`
- ツアー料金は2時間6,000円(小学生以下3,000円)。延長は1グループにつき1時間2,000円。
- 保険に加入するため、参加者全員のフルネームと年齢、代表者の連絡先(電話またはメール)が必要。
- 長靴を用意するので、参加者の靴のサイズを聞く。
- 集合場所の相談や、夜間の送迎の相談にも対応可能。
- 予約が確定したら、集合の日時・場所を伝え、長靴を履くので靴下を持参してもらうよう伝える。
- 帰りが遅くなるので、夕食は事前に済ませておいてもらうよう伝える。
- 懐中電灯・カメラ・飲み物・汗拭きタオルがあると楽しめる、と伝えるとよい。
`.trim();

// 返信文の見本(過去の実際の返信)。AIにはこの言い回し・構成をできるだけ真似てもらう。
// 見本を差し替えたい時は、このまま書き換えればすぐ反映される。
const REPLY_EXAMPLES=[
`○○さま

お問合せありがとうございます。ガイドの東田と申します。宜しくお願いします。
お問合せ頂きました日程は両日共に空いておりますのでご案内可能です。2日間でも大丈夫ですよ。
奄美大島の生き物を出来るだけ沢山観察できる様にご案内出来ればと思います。
ツアーは2時間6000円で延長がひとグループで1時間2000円となります。生き物を探したり撮影しているとあっという間に時間が過ぎてしまいますので、延長もご検討ください。3時間から4時間程あれば色々と観察出来ると思います。生き物はそれぞれ生息環境が違いますので、日にちを分けても楽しめると思います。
集合場所は龍郷町にあるビッグ2の駐車場にしたいと思いますが、夜間の運転に不安なら送迎も可能ですのでご連絡ください。

それで宜しければ
ツアー参加希望日
保険に加入しますので、ツアーに参加される方のフルネームと年齢、代表者の連絡先
長靴を準備しますので、靴のサイズを教えてください。

ご検討よろしくお願いします。
東田`,
`○○さま
お問合せありがとうございます。
9月11日、12日は空いているのでご案内可能ですよ

⑤ですが、その時の発生状況や天候によってかなり左右されます。
時期的にアマミマルバネクワガタがシーズンに入る頃で、アマミミヤマクワガタもまだ観れる可能性もありますが、それぞれ環境が違うので一度に両方ご案内するとかなりの長時間コースになってしまいます。

コロギスはマルモンコロギスが発生時期からだいぶ経ってしまっているのであまり観ることが出来ません。
コバネコロギスやハネナシコロギスは観れる可能性はあります。

マルバネを探しに行くのであれば、名瀬からですとポイントまで1時間程かかるので18時頃出発して3時間から4時間程の所用時間がかかります。林道沿いからすぐ見つかる場合もありますが、居なければ林内を歩いて探します。（タイミングによっては見つからない可能性もあります）
アマミミヤマクワガタを観察するには、他のクロウサギガイドの方の迷惑にならない様に少し遅めの時間帯になります。こちらも名瀬から少し離れています。
20時半頃から3時間程度かかる見込みです。
マルバネクワガタを早めに観察する事が出来れば、切り上げてアマミミヤマクワガタを探しに行く事も可能です。
料金は2時間大人6000円、小学生以下3000円で延長がひとグループで1時間2000円になります。

ご検討宜しくお願いします
東田`,
`こんにちは　お問合せありがとうございます。ガイドの東田と申します。宜しくお願いします。
お問合せ頂きました日程だと9月13日も14日も埋まっていて

9月12日が空いております。

料金は2時間6000円で延長がひとグループで1時間2000円となっております。生き物を探したり撮影しているとあっという間に時間が過ぎてしまいますので、延長も併せてご検討ください。
それでも宜しければ、保険に加入しますので、ツアーに参加される方のフルネームと年齢、代表者の連絡先
宿泊予定ホテルを教えてください。
それと長靴を準備しますので、靴のサイズも教えてください。

ご検討宜しくお願いします。
東田`,
`ご予約ありがとうございます。
それでは明日8月20日、19時30分にウエストコートwaテラスまでお迎えに伺いますね。
長靴を履くので靴下を履いてきてください。
帰りは遅くなりますので夕食は済ませておいてください。
飲み物や汗拭きタオルなどあると楽しめると思います。
奄美の生き物を出来るだけ沢山紹介出来る様にコースを組み立てたいと思います。
それではお会い出来るのを楽しみにしております。
東田`,
`いよいよ奄美旅行ですね！
8月17日月曜日19時40分に山羊島ホテル前までお迎えに伺いますので宜しくお願いします。
帰りは遅くなりますので夕食は済ませておいてください。`,
`○○さま
お問合せありがとうございます。ガイドの東田と申します。
お問合せ頂きました7月29日、30日は両日とも予定が入っております。
今のところ27、28日なら空いております。
日程の調整が出来るのであれば、ご案内したいと思います。
何か聞きたい事などあれば気軽に質問してくださいね。
宜しくお願いします。

東田

もうすでに予約が入っているかもしれませんが
フィールドワークの西さんやアマミノダイボウケンの高川さんへも問い合わせてみてください`,
`ご予約ありがとうございます。
7月18日のナイトツアーで予定を組んでおきますね
長靴も準備しておきます。
当日は靴下を履いて来てください。
懐中電灯とカメラがあると楽しめると思います。特にお子さんと一緒に見た生き物の記録をとって後で種類を自分で調べたりするととても勉強になりますよ。
それでは当日お会い出来るのを楽しみにしております！`,
];

// Geminiが混雑していると応答がとても遅くなる/固まることがあるため、
// 一定時間で自動的にあきらめて、呼び出し元のフォールバック処理に切り替える。
async function callWorker(action,payload,timeoutMs=20000){
  const controller=new AbortController();
  const timer=setTimeout(()=>controller.abort(),timeoutMs);
  try{
    const res=await fetch(WORKER_URL,{
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify({action,...payload}),
      signal:controller.signal,
    });
    const data=await res.json().catch(()=>null);
    if(!res.ok){
      // Worker側が返してきた具体的なエラー内容(クォータ超過など)をそのまま伝える。
      throw new Error((data&&data.error)?data.error:("worker error "+res.status));
    }
    return data;
  }finally{
    clearTimeout(timer);
  }
}
// AIが使えなかった時、利用上限(クォータ超過)が原因かどうかを見分けて、
// 呼び出し元がわかりやすいメッセージを出せるようにする。
function isQuotaError(err){
  const msg=String((err&&err.message)||err||"").toLowerCase();
  return msg.includes("429")||msg.includes("quota")||msg.includes("resource_exhausted");
}
function aiFallbackMessage(err){
  return isQuotaError(err)
    ? "⚠ AIの利用上限(1日20回)に達したため、簡易版で処理しました。日本時間の夕方ごろに回復します。"
    : "⚠ AIに接続できなかったため、簡易版で処理しました。";
}
function setAiStatus(el,msg){
  if(!el) return;
  el.textContent=msg;
  el.hidden=!msg;
  el.classList.toggle("warn",!!msg);
}

function esc(s){return String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]))}

// --- バックアップ(パスワード暗号化) ---
// PBKDF2でパスワードから鍵を作り、AES-GCMで暗号化する。塩(salt)とIVは
// ファイルに一緒に保存するが、パスワードそのものはどこにも保存しない。
function bufToBase64(buf){
  let binary="";
  const bytes=new Uint8Array(buf);
  for(let i=0;i<bytes.byteLength;i++) binary+=String.fromCharCode(bytes[i]);
  return btoa(binary);
}
function base64ToBuf(b64){
  const binary=atob(b64);
  const bytes=new Uint8Array(binary.length);
  for(let i=0;i<binary.length;i++) bytes[i]=binary.charCodeAt(i);
  return bytes;
}
async function deriveKey(password,salt){
  const keyMaterial=await crypto.subtle.importKey("raw",new TextEncoder().encode(password),"PBKDF2",false,["deriveKey"]);
  return crypto.subtle.deriveKey(
    {name:"PBKDF2",salt,iterations:100000,hash:"SHA-256"},
    keyMaterial,
    {name:"AES-GCM",length:256},
    false,
    ["encrypt","decrypt"]
  );
}
async function encryptBackup(password,data){
  const salt=crypto.getRandomValues(new Uint8Array(16));
  const iv=crypto.getRandomValues(new Uint8Array(12));
  const key=await deriveKey(password,salt);
  const plain=new TextEncoder().encode(JSON.stringify(data));
  const ciphertext=await crypto.subtle.encrypt({name:"AES-GCM",iv},key,plain);
  return {v:1,salt:bufToBase64(salt),iv:bufToBase64(iv),data:bufToBase64(ciphertext)};
}
async function decryptBackup(obj,password){
  const key=await deriveKey(password,base64ToBuf(obj.salt));
  const plain=await crypto.subtle.decrypt({name:"AES-GCM",iv:base64ToBuf(obj.iv)},key,base64ToBuf(obj.data));
  return JSON.parse(new TextDecoder().decode(plain));
}
function fmt(d){if(!d)return "未入力"; const [y,m,day]=d.split("-"); return `${y}/${m}/${day}`}
const WEEKDAYS=["日","月","火","水","木","金","土"];
function fmtWithWeekday(d){return `${fmt(d)}(${WEEKDAYS[new Date(d+"T00:00:00").getDay()]})`}
function statusLabel(status){return {pending:"未確定",confirmed:"予約確定",completed:"終了",cancelled:"キャンセル",personal:"予定あり"}[status]||status}
function updateStats(){
  // 「自分の予定」は問い合わせではないので、集計には含めない
  const customerRecords=records.filter(r=>r.status!=="personal");
  $("allCount").textContent=customerRecords.length;
  $("pendingCount").textContent=customerRecords.filter(r=>r.status==="pending").length;
  $("confirmedCount").textContent=customerRecords.filter(r=>r.status==="confirmed").length;
}
function cardHtml(r){
  if(r.status==="personal"){
    return `
    <article class="card personal" data-id="${r.id}">
      <div class="card-top"><div><div class="name">自分の予定</div><div class="date">${fmt(r.desiredDate)}</div></div>
      <span class="tag personal">予定あり</span></div>
      <div class="meta">${esc(r.notes||"内容未入力")}</div>
    </article>`;
  }
  return `
    <article class="card${r.status==="completed"?" completed":""}${r.status==="cancelled"?" cancelled":""}" data-id="${r.id}">
      <div class="card-top"><div><div class="name">${esc(r.name||"氏名未入力")}</div><div class="date">${fmt(r.desiredDate)}</div></div>
      <span class="tag ${r.status}">${statusLabel(r.status)}</span></div>
      <div class="meta">${esc(r.people||"人数未入力")}名　${esc(r.creatures||"生き物未入力")}　${esc(r.hotel||"ホテル未入力")}</div>
      ${r.status==="cancelled"?`<div class="meta">理由: ${esc(r.cancelReason||"未記入")}</div>`:""}
    </article>`;
}
function render(){
  updateStats();
  const q=$("search").value.trim().toLowerCase(), f=$("statusFilter").value;
  // 終了・キャンセル済みは、通常の一覧からは消えて「履歴」の専用画面でだけ管理する
  const rows=records.filter(r=>{
    if(r.status==="completed"||r.status==="cancelled") return false;
    const text=[r.name,r.hotel,r.creatures,r.phone,r.email,r.notes].join(" ").toLowerCase();
    return (!q||text.includes(q))&&(f==="all"||r.status===f);
  }).sort((a,b)=>(a.desiredDate||"").localeCompare(b.desiredDate||""));
  $("list").innerHTML=rows.length?rows.map(cardHtml).join(""):"<div class='card'>まだ問い合わせはありません。「＋ 新規問い合わせ」から試せます。</div>";
  document.querySelectorAll("#list .card[data-id]").forEach(el=>el.onclick=()=>showDetail(el.dataset.id));
}
function renderHistory(){
  const q=$("historySearch").value.trim().toLowerCase(), d=$("historyDate").value;
  // 終了・キャンセルになった問い合わせだけを、氏名・日付で絞り込んで表示する
  const rows=records.filter(r=>{
    if(r.status!=="completed"&&r.status!=="cancelled") return false;
    const text=[r.name,r.hotel,r.creatures,r.cancelReason].join(" ").toLowerCase();
    return (!q||text.includes(q))&&(!d||r.desiredDate===d);
  }).sort((a,b)=>(b.desiredDate||"").localeCompare(a.desiredDate||""));
  $("historyList").innerHTML=rows.length?rows.map(cardHtml).join(""):"<div class='card'>該当する履歴はありません。</div>";
  document.querySelectorAll("#historyList .card[data-id]").forEach(el=>el.onclick=()=>showDetail(el.dataset.id));
}
function refreshAll(){
  render();
  if(!$("historyView").classList.contains("hidden")) renderHistory();
}
function openEditor(){
  currentId=null;$("editor").classList.remove("hidden");$("parsedArea").classList.add("hidden");$("rawText").focus();
}
function openScheduleEditor(){
  $("scheduleEditor").classList.remove("hidden");$("scheduleDate").focus();
}
function closeScheduleEditor(){
  $("scheduleEditor").classList.add("hidden");
  $("scheduleDate").value="";$("scheduleNotes").value="";
}
$("newScheduleBtn").onclick=openScheduleEditor;
$("closeScheduleEditor").onclick=closeScheduleEditor;
$("saveScheduleBtn").onclick=()=>{
  if(!$("scheduleDate").value){alert("日付を入力してください。");return;}
  const r={id:Date.now().toString(),createdAt:today(),desiredDate:$("scheduleDate").value,notes:$("scheduleNotes").value,status:"personal"};
  records.push(r);save();render();closeScheduleEditor();
};
function resetEditor(){
  ["rawText","name","phone","email","desiredDate","people","hotel","creatures","notes","alt1","alt2","reply"].forEach(id=>$(id).value="");
  $("parsedArea").classList.add("hidden"); $("missing").innerHTML="";
  parsedParticipants=[]; $("participantFieldsEditor").innerHTML="";
  setAiStatus($("parseStatus"),""); setAiStatus($("replyStatus"),"");
}
function parseText(t){
  const date=t.match(/(20\d{2})[\/\-年](\d{1,2})[\/\-月](\d{1,2})日?/);
  const monthDay=t.match(/(\d{1,2})月(\d{1,2})日/);
  const phone=t.match(/0\d{1,4}[-ー]?\d{2,4}[-ー]?\d{3,4}/);
  const email=t.match(/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/i);
  const people=t.match(/(\d+)\s*(?:名|人)/);
  // 「宿泊予定ホテルは何処ですか？」のような質問文自体を宿泊先と誤認しないよう、
  // まず「宿泊先：◯◯」「宿泊予定ホテル　◯◯」のようなラベル＋区切り記号の形を優先的に探す。
  // 見つからない場合だけ、「◯◯ホテル」のように名前自体にホテル系の語が付く形にフォールバックする。
  let hotel="";
  const hotelLabelRe=/(?:宿泊(?:予定)?(?:ホテル|先)?|ホテル(?:名)?)(?:[：:\s　]+|は|が)([^\n。、]{1,30})/g;
  let hm;
  while((hm=hotelLabelRe.exec(t))){
    const val=hm[1].trim();
    // 「宿泊予定ホテルは何処ですか？」のような質問文自体を拾わないよう、
    // 疑問符や疑問詞で始まる場合はスキップして次の候補を探す
    if(/[？?]/.test(val)||/^(?:何|いつ|どこ|どちら|どの|どんな)/.test(val)) continue;
    hotel=val.replace(/(?:です|でした|となります|になります)$/,"").trim();
    break;
  }
  if(!hotel){
    const hotelSuffixRe=/([^\n。、]{1,30}(?:ホテル|旅館|民宿|ゲストハウス))/g;
    let sm;
    while((sm=hotelSuffixRe.exec(t))){
      const val=sm[1].trim();
      // 「宿泊予定ホテル」のようなラベル文言そのものは、固有名詞が付いていないので除外
      if(/^(?:宿泊|予定|ご宿泊)*(?:ホテル|旅館|民宿|ゲストハウス)$/.test(val)) continue;
      hotel=val;
      break;
    }
  }
  const creatures=["ヘビ","ハブ","アカマタ","カエル","アマミアカガエル","オットンガエル","クワガタ","アマミノクロウサギ","カエル類"].filter(x=>t.includes(x));
  let name="";
  const nm=t.match(/(?:代表者|名前|氏名)[：:\s]+([^\n。、]+)/);
  if(nm) name=nm[1].trim();
  else {
    const first=t.split(/\n/).map(x=>x.trim()).find(x=>/^[一-龥ぁ-んァ-ヶ]{2,8}\s*(?:です|と申します|といいます)?[。！!]?$/.test(x));
    if(first) name=first.replace(/[。！!].*$/,"").trim();
  }
  let desired="";
  if(date) desired=`${date[1]}-${String(date[2]).padStart(2,"0")}-${String(date[3]).padStart(2,"0")}`;
  else if(monthDay){
    const y=new Date().getFullYear(); desired=`${y}-${String(monthDay[1]).padStart(2,"0")}-${String(monthDay[2]).padStart(2,"0")}`;
  }
  return {name,phone:phone?.[0]||"",email:email?.[0]||"",desiredDate:desired,people:people?.[1]||"",hotel,creatures:creatures.join("、")};
}
function parseParticipants(t){
  const results=[];
  const nameChar="[一-龥ぁ-んァ-ヶA-Za-z]";
  // 氏名の直後に来る区切り文字(空白・全角記号など)。ここに別の氏名らしき漢字が
  // 挟まると誤検出になるため、区切りは記号・空白だけに絞る。
  const sep="[\\s、,，・/／:：()（）]{0,3}";
  // 「名前 32歳 26.5cm」のように、氏名→年齢→靴サイズの順で書かれている行を拾う
  const ageThenShoe=new RegExp(`(${nameChar}{2,10})${sep}(\\d{1,3})\\s*(?:歳|才)${sep}(\\d{2}(?:\\.\\d)?)\\s*(?:cm|㎝|センチ)`,"g");
  let m;
  while((m=ageThenShoe.exec(t))) results.push({name:m[1],age:m[2],shoeSize:m[3]+"cm"});
  if(results.length===0){
    // 靴サイズ→年齢の順のパターンにも対応
    const shoeThenAge=new RegExp(`(${nameChar}{2,10})${sep}(\\d{2}(?:\\.\\d)?)\\s*(?:cm|㎝|センチ)${sep}(\\d{1,3})\\s*(?:歳|才)`,"g");
    while((m=shoeThenAge.exec(t))) results.push({name:m[1],age:m[3],shoeSize:m[2]+"cm"});
  }
  if(results.length===0){
    // 年齢・靴サイズが書かれていなくても、参加者の名前の列挙だけは拾っておく
    const listMatch=t.match(/(?:参加者|お連れ様|同行者)[：:\s]*([^\n]+)/);
    if(listMatch){
      listMatch[1].split(/[、,，・\/／]/).map(s=>s.trim()).filter(Boolean)
        .forEach(n=>results.push({name:n,age:"",shoeSize:""}));
    }
  }
  return results;
}
function getMissing(){
  const miss=[];
  if(!$("name").value)miss.push("代表者氏名");
  if(!$("desiredDate").value)miss.push("希望日");
  if(!$("people").value)miss.push("参加人数");
  if(!$("creatures").value)miss.push("観察したい生き物");
  if(!$("phone").value&&!$("email").value)miss.push("電話またはメール");
  return miss;
}
function renderMissing(){
  const miss=getMissing();$("missing").innerHTML=miss.length?miss.map(x=>`<span>${esc(x)}</span>`).join(""):"<span style='background:#dcecdf'>基本情報はそろっています</span>";
}
// AI(Gemini)が使えない/失敗した時の、ローカルだけで組み立てるフォールバック用の返信文。
function buildTemplateReply(){
  const n=$("name").value||"お客様",d=$("desiredDate").value, st=$("dateStatus").value;
  const alts=[$("alt1").value,$("alt2").value].filter(Boolean).map(fmt);
  const miss=getMissing();
  let s=`${n}様\n\nお問い合わせありがとうございます。\n`;
  if(d){
    if(st==="available") s+=`${fmt(d)}のナイトツアーは空いております。\n`;
    else if(st==="booked") s+=`${fmt(d)}はすでに他のお客様のガイドが入っております。`;
    else if(st==="personal") s+=`${fmt(d)}は予定が入っております。`;
    else s+=`${fmt(d)}は休業となっております。`;
    if(st!=="available"&&alts.length) s+=`近い日程ですと${alts.join("、または")}でしたら空いておりますが、いかがでしょうか？\n`;
    else if(st!=="available") s+="\n";
  }
  if($("creatures").value)s+=`観察をご希望の生き物は${$("creatures").value}とのこと、承知しました。\n`;
  if(miss.length){
    s+=`\nご予約・日程調整のため、以下についてお知らせください。\n`;
    miss.forEach(x=>s+=`・${x}\n`);
  } else s+=`\n内容を確認のうえ、予約についてご案内いたします。\n`;
  s+="\nよろしくお願いいたします。";
  return s;
}
async function makeReply(){
  const btn=$("makeReply");
  const original=btn?btn.textContent:null;
  if(btn){btn.disabled=true;btn.textContent="作成中…";}
  const context={
    name:$("name").value||"お客様",
    desiredDate:$("desiredDate").value?fmt($("desiredDate").value):"",
    dateStatus:$("dateStatus").value,
    alt1:$("alt1").value?fmt($("alt1").value):"",
    alt2:$("alt2").value?fmt($("alt2").value):"",
    creatures:$("creatures").value,
    people:$("people").value,
    hotel:$("hotel").value,
    missing:getMissing(),
  };
  try{
    const ai=await callWorker("draftReply",{context,examples:REPLY_EXAMPLES,facts:GUIDE_FACTS});
    if(!ai.reply) throw new Error("empty reply");
    $("reply").value=ai.reply;
    setAiStatus($("replyStatus"),"");
  }catch(err){
    console.error("AI返信作成に失敗、テンプレートにフォールバックします",err);
    $("reply").value=buildTemplateReply();
    setAiStatus($("replyStatus"),aiFallbackMessage(err));
  }
  if(btn){btn.disabled=false;btn.textContent=original;}
}
$("newBtn").onclick=openEditor;
$("closeEditor").onclick=()=>{$("editor").classList.add("hidden")};
$("clearBtn").onclick=resetEditor;
$("search").oninput=render;$("statusFilter").onchange=render;
$("historyBtn").onclick=()=>{$("mainView").classList.add("hidden");$("historyView").classList.remove("hidden");renderHistory();};
$("closeHistory").onclick=()=>{$("historyView").classList.add("hidden");$("mainView").classList.remove("hidden");};
$("historySearch").oninput=renderHistory;$("historyDate").onchange=renderHistory;
$("clearHistoryDate").onclick=()=>{$("historyDate").value="";renderHistory();};
$("parseBtn").onclick=async()=>{
  const raw=$("rawText").value;
  if(!raw.trim()){alert("問い合わせ内容を貼り付けてください。");return;}
  const btn=$("parseBtn");
  const original=btn.textContent;
  btn.disabled=true;btn.textContent="読み取り中…";
  let p,participants;
  try{
    const ai=await callWorker("parseInquiry",{text:raw});
    p={name:ai.name||"",phone:ai.phone||"",email:ai.email||"",desiredDate:ai.desiredDate||"",people:ai.people||"",hotel:ai.hotel||"",creatures:ai.creatures||""};
    participants=Array.isArray(ai.participants)?ai.participants:[];
    setAiStatus($("parseStatus"),"");
  }catch(err){
    console.error("AI読み取りに失敗、簡易抽出にフォールバックします",err);
    p=parseText(raw);
    participants=parseParticipants(raw);
    setAiStatus($("parseStatus"),aiFallbackMessage(err));
  }
  btn.disabled=false;btn.textContent=original;
  Object.entries(p).forEach(([k,v])=>{if($(k))$(k).value=v});
  $("parsedArea").classList.remove("hidden"); renderMissing();
  parsedParticipants=participants;
  renderParticipantEditor();
  $("desiredDate").oninput=renderMissing;$("name").oninput=renderMissing;$("creatures").oninput=renderMissing;$("phone").oninput=renderMissing;$("email").oninput=renderMissing;
  $("people").oninput=()=>{syncParticipantEditorToState();renderMissing();renderParticipantEditor()};
  await makeReply();
};
// 希望日の状態や候補日を変えるたびに自動でAIを呼ぶと、無駄にクォータを消費するため、
// 「返信案を作る」ボタンを押した時だけ作成する(自動作成はしない)。
$("makeReply").onclick=makeReply;
$("copyReply").onclick=async()=>{await navigator.clipboard.writeText($("reply").value);$("copyReply").textContent="コピーしました";setTimeout(()=>$("copyReply").textContent="返信をコピー",1200)};
$("saveBtn").onclick=()=>{
  syncParticipantEditorToState();
  const r={id:Date.now().toString(),createdAt:today(),name:$("name").value,phone:$("phone").value,email:$("email").value,desiredDate:$("desiredDate").value,people:$("people").value,hotel:$("hotel").value,creatures:$("creatures").value,contactMethod:$("contactMethod").value,notes:$("notes").value,status:"pending",raw:$("rawText").value,reply:$("reply").value,participants:parsedParticipants};
  records.push(r);save();render();$("editor").classList.add("hidden");alert("保存しました。現在は未確定として登録されています。");
};
function participantFormHtml(prefix,p,i){
  return `
    <div class="ptab-fields">
      <label>氏名<input class="p-name-input" id="${prefix}-name-${i}" value="${esc(p.name)}"></label>
      <label>年齢<input class="p-age-input" id="${prefix}-age-${i}" type="number" min="0" value="${esc(p.age)}"></label>
      <label>靴のサイズ<input class="p-shoe-input" id="${prefix}-shoe-${i}" placeholder="例: 26.0cm" value="${esc(p.shoeSize)}"></label>
    </div>
    <div class="actions">${i>0?'<button type="button" class="ghost ptab-prev">← 戻る</button>':""}<button type="button" class="primary ptab-confirm">確定</button></div>`;
}
function participantSummaryHtml(p,i){
  return `
    <div class="participant-summary">
      <div class="ps-row"><b>氏名</b><span>${esc(p.name||"未入力")}</span></div>
      <div class="ps-row"><b>年齢</b><span>${p.age?esc(p.age)+"歳":"未入力"}</span></div>
      <div class="ps-row"><b>靴のサイズ</b><span>${esc(p.shoeSize||"未入力")}</span></div>
    </div>
    <div class="actions">${i>0?'<button type="button" class="ghost ptab-prev">← 戻る</button>':""}<button type="button" class="ghost ptab-edit">編集</button></div>`;
}
function participantTabsHtml(prefix,count,participants){
  participants=Array.isArray(participants)?participants:[];
  let nav="",panels="";
  for(let i=0;i<count;i++){
    const p=participants[i]||{};
    const isConfirmed=!!p.confirmed;
    const active=i===0?" active":"";
    nav+=`<button type="button" class="ptab-btn${active}${isConfirmed?" confirmed":""}" data-idx="${i}">参加者${i+1}${isConfirmed?" ✓":""}</button>`;
    panels+=`<div class="ptab-panel${active}" data-idx="${i}">${isConfirmed?participantSummaryHtml(p,i):participantFormHtml(prefix,p,i)}</div>`;
  }
  return `<div class="participant-tabs"><div class="ptab-nav">${nav}</div><div class="ptab-panels">${panels}</div></div>`;
}
// タブ切り替え・確定・編集を、コンテナへのイベント委譲でまとめて処理する。
// (人数変更のたびにHTMLごと作り直すため、要素ごとにonclickを付け直す必要がない)
function bindParticipantTabs(container,prefix,getParticipants,setParticipants,onConfirmOrEdit){
  container.addEventListener("click",e=>{
    const tabBtn=e.target.closest(".ptab-btn");
    if(tabBtn){
      const idx=tabBtn.dataset.idx;
      container.querySelectorAll(".ptab-btn").forEach(b=>b.classList.toggle("active",b.dataset.idx===idx));
      container.querySelectorAll(".ptab-panel").forEach(p=>p.classList.toggle("active",p.dataset.idx===idx));
      return;
    }
    const prevBtn=e.target.closest(".ptab-prev");
    if(prevBtn){
      const i=parseInt(prevBtn.closest(".ptab-panel").dataset.idx,10);
      const target=container.querySelector(`.ptab-btn[data-idx="${i-1}"]`);
      if(target) target.click();
      return;
    }
    const confirmBtn=e.target.closest(".ptab-confirm");
    if(confirmBtn){
      const panel=confirmBtn.closest(".ptab-panel");
      const i=parseInt(panel.dataset.idx,10);
      const p={
        name:panel.querySelector(".p-name-input").value,
        age:panel.querySelector(".p-age-input").value,
        shoeSize:panel.querySelector(".p-shoe-input").value,
        confirmed:true,
      };
      const participants=getParticipants();
      participants[i]=p;
      setParticipants(participants);
      panel.innerHTML=participantSummaryHtml(p,i);
      const btn=container.querySelector(`.ptab-btn[data-idx="${i}"]`);
      if(btn){btn.classList.add("confirmed");btn.textContent=`参加者${i+1} ✓`;}
      onConfirmOrEdit&&onConfirmOrEdit();
      const nextBtn=container.querySelector(`.ptab-btn[data-idx="${i+1}"]`);
      if(nextBtn) nextBtn.click();
      return;
    }
    const editBtn=e.target.closest(".ptab-edit");
    if(editBtn){
      const panel=editBtn.closest(".ptab-panel");
      const i=parseInt(panel.dataset.idx,10);
      const participants=getParticipants();
      const p=participants[i]||{};
      p.confirmed=false;
      setParticipants(participants);
      panel.innerHTML=participantFormHtml(prefix,p,i);
      const btn=container.querySelector(`.ptab-btn[data-idx="${i}"]`);
      if(btn){btn.classList.remove("confirmed");btn.textContent=`参加者${i+1}`;}
      onConfirmOrEdit&&onConfirmOrEdit();
    }
  });
}
function renderParticipantEditor(){
  const count=parseInt($("people").value,10)||1;
  $("participantFieldsEditor").innerHTML=participantTabsHtml("np",count,parsedParticipants);
}
function syncParticipantEditorToState(){
  const panels=$("participantFieldsEditor").querySelectorAll(".ptab-panel");
  const updated=[];
  panels.forEach((panel,i)=>{
    const nameEl=panel.querySelector(".p-name-input");
    if(nameEl){
      updated[i]={name:nameEl.value,age:panel.querySelector(".p-age-input").value,shoeSize:panel.querySelector(".p-shoe-input").value,confirmed:false};
    }else{
      updated[i]=parsedParticipants[i]||{};
    }
  });
  parsedParticipants=updated;
}
bindParticipantTabs($("participantFieldsEditor"),"np",()=>parsedParticipants,v=>{parsedParticipants=v;});
// 返信メールなど、後から届いた文章を読み取って既存の問い合わせに反映する。
// 「代表者氏名」のような基本項目は、すでに入力済みなら上書きしない(誤読で消さないため)。
// 参加者情報は、まだ確定していないタブだけを新しい内容で置き換える(確定済みは保護する)。
async function applyFollowupText(r,text){
  let p,extracted,aiErr=null;
  try{
    const ai=await callWorker("parseInquiry",{text});
    p={name:ai.name||"",phone:ai.phone||"",email:ai.email||"",desiredDate:ai.desiredDate||"",people:ai.people||"",hotel:ai.hotel||"",creatures:ai.creatures||""};
    extracted=Array.isArray(ai.participants)?ai.participants:[];
  }catch(err){
    console.error("AI読み取りに失敗、簡易抽出にフォールバックします",err);
    aiErr=err;
    p=parseText(text);
    extracted=parseParticipants(text);
  }
  ["name","phone","email","desiredDate","people","hotel"].forEach(key=>{
    if(!r[key]&&p[key]) r[key]=p[key];
  });
  if(p.creatures){
    const existing=(r.creatures||"").split(/[、,]/).map(s=>s.trim()).filter(Boolean);
    const added=p.creatures.split(/[、,]/).map(s=>s.trim()).filter(Boolean);
    r.creatures=Array.from(new Set([...existing,...added])).join("、");
  }
  if(extracted.length){
    if(!Array.isArray(r.participants)) r.participants=[];
    extracted.forEach((ep,i)=>{
      const cur=r.participants[i];
      if(!cur||!cur.confirmed) r.participants[i]={name:ep.name,age:ep.age,shoeSize:ep.shoeSize,confirmed:false};
    });
  }
  if(!Array.isArray(r.followups)) r.followups=[];
  r.followups.push({date:today(),text});
  return aiErr;
}
let currentDetailId=null;
bindParticipantTabs($("detail"),"p",
  ()=>{
    const rec=records.find(x=>x.id===currentDetailId);
    if(!rec) return [];
    if(!Array.isArray(rec.participants)) rec.participants=[];
    return rec.participants;
  },
  participants=>{
    const rec=records.find(x=>x.id===currentDetailId);
    if(rec){rec.participants=participants;save();}
  }
);
function showScheduleDetail(r,id){
  $("detailTitle").textContent="自分の予定";
  $("detail").innerHTML=`
    <div class="detail-grid">
      <div class="detail-item"><b>日付</b>${fmt(r.desiredDate)}</div>
    </div>
    <h3>内容</h3>
    <textarea id="scheduleDetailNotes" rows="4">${esc(r.notes||"")}</textarea>
    <h3>操作</h3>
    <div class="actions"><button class="ghost" id="deleteRecord">削除</button></div>`;
  $("detailModal").classList.remove("hidden");
  $("scheduleDetailNotes").onchange=()=>{r.notes=$("scheduleDetailNotes").value;save();render();};
  $("deleteRecord").onclick=()=>{if(confirm("この予定を削除しますか？")){records=records.filter(x=>x.id!==id);save();render();$("detailModal").classList.add("hidden")}};
}
const CONTACT_METHODS=["公式LINE","メール","電話","SNSのDM","SIMDEF","その他"];
// 予約確定にすると基本情報は編集できないようにし、「未確定に戻す」で編集を解禁する。
// 確定後に間違いに気づいた時は、一度未確定へ戻してから直せる、という運用に合わせている。
function detailInfoHtml(r){
  if(r.status!=="pending"){
    const cancelNote=r.status==="cancelled"
      ?`<div class="detail-item" style="grid-column:1/-1;background:#fdeaea"><b>キャンセル理由</b>${esc(r.cancelReason||"理由未記入")}</div>`
      :"";
    return `
    <div class="detail-grid">
      <div class="detail-item"><b>状態</b>${statusLabel(r.status)}</div>
      ${cancelNote}
      <div class="detail-item"><b>希望日</b>${fmt(r.desiredDate)}</div>
      <div class="detail-item"><b>人数</b>${esc(r.people||"未入力")}名</div>
      <div class="detail-item"><b>観察希望</b>${esc(r.creatures||"未入力")}</div>
      <div class="detail-item"><b>電話</b>${esc(r.phone||"未入力")}</div>
      <div class="detail-item"><b>メール</b>${esc(r.email||"未入力")}</div>
      <div class="detail-item"><b>ホテル</b>${esc(r.hotel||"未入力")}</div>
      <div class="detail-item"><b>問い合わせ方法</b>${esc(r.contactMethod)}</div>
    </div>`;
  }
  return `
    <p class="hint">未確定の間は、下の項目を直接編集できます。予約確定にすると編集できなくなります。</p>
    <div class="grid">
      <label>代表者氏名<input id="d-name" value="${esc(r.name)}"></label>
      <label>電話<input id="d-phone" value="${esc(r.phone)}"></label>
      <label>メール<input id="d-email" value="${esc(r.email)}"></label>
      <label>希望日<input id="d-desiredDate" type="date" value="${esc(r.desiredDate)}"></label>
      <label>人数<input id="d-people" type="number" min="1" value="${esc(r.people)}"></label>
      <label>ホテル<input id="d-hotel" value="${esc(r.hotel)}"></label>
      <label>観察したい生き物<input id="d-creatures" value="${esc(r.creatures)}"></label>
      <label>問い合わせ方法
        <select id="d-contactMethod">
          ${CONTACT_METHODS.map(m=>`<option${r.contactMethod===m?" selected":""}>${m}</option>`).join("")}
        </select>
      </label>
    </div>`;
}
function showDetail(id){
  const r=records.find(x=>x.id===id);if(!r)return;
  currentDetailId=id;
  if(r.status==="personal"){showScheduleDetail(r,id);return;}
  $("detailTitle").textContent=r.name||"問い合わせ詳細";
  // 新しい返信ほど上に来るように、最新のものから順に並べる
  const history=[{date:r.createdAt,text:r.raw}].concat(Array.isArray(r.followups)?r.followups:[]).reverse();
  const historyHtml=history.map(h=>`
    <div style="margin-bottom:10px">
      <div class="hint" style="margin-bottom:4px">${fmt(h.date)}</div>
      <pre style="white-space:pre-wrap;background:#f5f7f5;padding:12px;border-radius:10px;margin:0">${esc(h.text)}</pre>
    </div>`).join("");
  $("detail").innerHTML=`
    ${detailInfoHtml(r)}
    <h3>備考</h3>
    <textarea id="detailNotes" rows="3" placeholder="アレルギー、特別なご要望、その他メモなど">${esc(r.notes||"")}</textarea>
    <h3>操作</h3>
    <div class="actions">
      ${r.status==="pending"?'<button class="primary" id="toggleStatus">予約確定にする</button>':""}
      ${r.status==="confirmed"?'<button class="ghost" id="toggleStatus">未確定に戻す</button><button class="primary" id="completeBtn">ガイド終了にする</button>':""}
      ${r.status==="completed"?'<button class="ghost" id="uncompleteBtn">確定に戻す</button>':""}
      ${(r.status==="pending"||r.status==="confirmed")?'<button class="ghost" id="cancelBtn">キャンセル</button>':""}
      ${r.status==="cancelled"?'<button class="ghost" id="uncancelBtn">キャンセルを取り消す</button>':""}
      <button class="ghost" id="deleteRecord">削除</button>
    </div>
    <h3>参加者情報</h3>
    <p class="hint">タブで参加者を切り替えながら入力し、「確定」を押すと見やすい表示になります(自動保存されます)。</p>
    ${participantTabsHtml("p",parseInt(r.people,10)||1,r.participants)}
    <h3>返信メール・追加のやり取りを読み取る</h3>
    <p class="hint">お客様からの返信メールなどをそのまま貼り付けて読み取ると、まだ空欄の項目や、未確定の参加者タブを埋められます。すでに入力・確定済みの項目は上書きしません。</p>
    <textarea id="followupText" rows="6" placeholder="返信メールの内容をそのまま貼り付けてください"></textarea>
    <div class="actions"><button class="primary" id="applyFollowup">読み取って反映</button></div>
    <h3>やり取りの履歴</h3>
    ${historyHtml}
    <h3>返信案</h3>
    <p class="hint">やり取りを重ねて返信内容を書き直した時は、「変更を保存」を押すとここに残ります。</p>
    <textarea id="detailReply" rows="8">${esc(r.reply||"")}</textarea>
    <div class="actions">
      <button class="primary" id="saveReply">変更を保存</button>
      <button class="ghost" id="copyDetail">返信をコピー</button>
    </div>`;
  $("detailModal").classList.remove("hidden");
  if($("toggleStatus")) $("toggleStatus").onclick=()=>{r.status=r.status==="confirmed"?"pending":"confirmed";save();render();showDetail(id)};
  if($("completeBtn")) $("completeBtn").onclick=()=>{r.status="completed";save();refreshAll();showDetail(id)};
  if($("uncompleteBtn")) $("uncompleteBtn").onclick=()=>{r.status="confirmed";save();refreshAll();showDetail(id)};
  if($("cancelBtn")) $("cancelBtn").onclick=()=>{
    const reason=prompt("キャンセルの理由を入力してください(台風接近、お客様都合など)");
    if(reason===null) return;
    r.previousStatus=r.status;
    r.status="cancelled";
    r.cancelReason=reason;
    r.cancelledAt=today();
    save();refreshAll();showDetail(id);
  };
  if($("uncancelBtn")) $("uncancelBtn").onclick=()=>{r.status=r.previousStatus||"pending";save();refreshAll();showDetail(id)};
  $("deleteRecord").onclick=()=>{if(confirm("この問い合わせを削除しますか？")){records=records.filter(x=>x.id!==id);save();refreshAll();$("detailModal").classList.add("hidden")}};
  $("detailNotes").onchange=()=>{r.notes=$("detailNotes").value;save();};
  if(r.status==="pending"){
    ["name","phone","email","desiredDate","people","hotel","creatures","contactMethod"].forEach(field=>{
      const el=$(`d-${field}`);
      if(el) el.onchange=()=>{r[field]=el.value;save();render();showDetail(id);};
    });
  }
  $("applyFollowup").onclick=async()=>{
    const text=$("followupText").value.trim();
    if(!text){alert("貼り付ける内容がありません。");return;}
    const btn=$("applyFollowup");
    btn.disabled=true;btn.textContent="読み取り中…";
    const aiErr=await applyFollowupText(r,text);
    save();
    showDetail(id);
    if(aiErr) alert(aiFallbackMessage(aiErr));
  };
  $("saveReply").onclick=()=>{
    r.reply=$("detailReply").value;
    save();
    $("saveReply").textContent="保存しました";
    setTimeout(()=>{$("saveReply").textContent="変更を保存";},1200);
  };
  $("copyDetail").onclick=async()=>{await navigator.clipboard.writeText($("detailReply").value);$("copyDetail").textContent="コピーしました"};
}
$("closeModal").onclick=()=>$("detailModal").classList.add("hidden");
$("detailModal").onclick=e=>{if(e.target===$("detailModal"))$("detailModal").classList.add("hidden")};

// ホーム画面に追加したアプリは、消して登録し直さなくても、ここでキャッシュを
// バイパスして最新のindex.html/app.jsを取りに行けるようにする。
$("refreshBtn").onclick=async()=>{
  if("caches" in window){
    try{
      const keys=await caches.keys();
      await Promise.all(keys.map(k=>caches.delete(k)));
    }catch(e){/* キャッシュAPIが無い/失敗しても、下のURL書き換えだけで基本は更新できる */}
  }
  const url=new URL(location.href);
  url.searchParams.set("_r",Date.now());
  location.href=url.toString();
};

$("backupBtn").onclick=async()=>{
  if(!records.length){alert("バックアップするデータがありません。");return;}
  const password=prompt("バックアップ用のパスワードを決めてください(復元時に同じパスワードが必要です)");
  if(!password) return;
  const backup=await encryptBackup(password,records);
  const blob=new Blob([JSON.stringify(backup)],{type:"application/json"});
  const url=URL.createObjectURL(blob);
  const a=document.createElement("a");
  a.href=url;
  a.download=`nea-customer-backup-${today().replace(/-/g,"")}.json`;
  document.body.appendChild(a);a.click();document.body.removeChild(a);
  URL.revokeObjectURL(url);
};
$("restoreBtn").onclick=()=>$("restoreFile").click();
$("restoreFile").onchange=async(e)=>{
  const file=e.target.files[0];
  if(!file){return;}
  const password=prompt("バックアップ作成時に設定したパスワードを入力してください");
  if(!password){e.target.value="";return;}
  try{
    const obj=JSON.parse(await file.text());
    const restored=await decryptBackup(obj,password);
    if(!Array.isArray(restored)) throw new Error("invalid backup");
    if(!confirm(`${restored.length}件のデータが見つかりました。今のデータをこれで置き換えます。よろしいですか？`)){e.target.value="";return;}
    records=restored;save();render();
    alert("復元しました。");
  }catch(err){
    alert("復元に失敗しました。パスワードが違うか、ファイルが壊れている可能性があります。");
  }
  e.target.value="";
};

$("todayLabel").textContent=`本日 ${fmtWithWeekday(today())}`;
render();
