const KEY="nea_customer_app_v1";
let records=JSON.parse(localStorage.getItem(KEY)||"[]");
let currentId=null;
let parsedParticipants=[];

const $=id=>document.getElementById(id);
const today=()=>new Date().toISOString().slice(0,10);
const save=()=>localStorage.setItem(KEY,JSON.stringify(records));

function esc(s){return String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]))}
function fmt(d){if(!d)return "未入力"; const [y,m,day]=d.split("-"); return `${y}/${m}/${day}`}
function updateStats(){
  $("allCount").textContent=records.length;
  $("pendingCount").textContent=records.filter(r=>r.status==="pending").length;
  $("confirmedCount").textContent=records.filter(r=>r.status==="confirmed").length;
}
function render(){
  updateStats();
  const q=$("search").value.trim().toLowerCase(), f=$("statusFilter").value;
  const rows=records.filter(r=>{
    const text=[r.name,r.hotel,r.creatures,r.phone,r.email].join(" ").toLowerCase();
    return (!q||text.includes(q))&&(f==="all"||r.status===f);
  }).sort((a,b)=>(a.desiredDate||"").localeCompare(b.desiredDate||""));
  $("list").innerHTML=rows.length?rows.map(r=>`
    <article class="card" data-id="${r.id}">
      <div class="card-top"><div><div class="name">${esc(r.name||"氏名未入力")}</div><div class="date">${fmt(r.desiredDate)}</div></div>
      <span class="tag ${r.status}">${r.status==="confirmed"?"予約確定":"未確定"}</span></div>
      <div class="meta">${esc(r.people||"人数未入力")}名　${esc(r.creatures||"生き物未入力")}　${esc(r.hotel||"ホテル未入力")}</div>
    </article>`).join(""):"<div class='card'>まだ問い合わせはありません。「＋ 新規問い合わせ」から試せます。</div>";
  document.querySelectorAll(".card[data-id]").forEach(el=>el.onclick=()=>showDetail(el.dataset.id));
}
function openEditor(){
  currentId=null;$("editor").classList.remove("hidden");$("parsedArea").classList.add("hidden");$("rawText").focus();
}
function resetEditor(){
  ["rawText","name","phone","email","desiredDate","people","hotel","creatures","alt1","alt2","reply"].forEach(id=>$(id).value="");
  $("parsedArea").classList.add("hidden"); $("missing").innerHTML="";
  parsedParticipants=[]; $("participantFieldsEditor").innerHTML="";
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
function makeReply(){
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
  $("reply").value=s;
}
$("newBtn").onclick=openEditor;
$("closeEditor").onclick=()=>{$("editor").classList.add("hidden")};
$("clearBtn").onclick=resetEditor;
$("search").oninput=render;$("statusFilter").onchange=render;
$("parseBtn").onclick=()=>{
  const raw=$("rawText").value;
  const p=parseText(raw);
  Object.entries(p).forEach(([k,v])=>{if($(k))$(k).value=v});
  $("parsedArea").classList.remove("hidden"); renderMissing();
  parsedParticipants=parseParticipants(raw);
  renderParticipantEditor();
  $("desiredDate").oninput=renderMissing;$("name").oninput=renderMissing;$("creatures").oninput=renderMissing;$("phone").oninput=renderMissing;$("email").oninput=renderMissing;
  $("people").oninput=()=>{syncParticipantEditorToState();renderMissing();renderParticipantEditor()};
  makeReply();
};
$("dateStatus").onchange=makeReply;$("alt1").onchange=makeReply;$("alt2").onchange=makeReply;
$("makeReply").onclick=makeReply;
$("copyReply").onclick=async()=>{await navigator.clipboard.writeText($("reply").value);$("copyReply").textContent="コピーしました";setTimeout(()=>$("copyReply").textContent="返信をコピー",1200)};
$("saveBtn").onclick=()=>{
  syncParticipantEditorToState();
  const r={id:Date.now().toString(),createdAt:today(),name:$("name").value,phone:$("phone").value,email:$("email").value,desiredDate:$("desiredDate").value,people:$("people").value,hotel:$("hotel").value,creatures:$("creatures").value,contactMethod:$("contactMethod").value,status:"pending",raw:$("rawText").value,reply:$("reply").value,participants:parsedParticipants};
  records.push(r);save();render();$("editor").classList.add("hidden");alert("保存しました。現在は未確定として登録されています。");
};
function participantFieldsHtml(prefix,count,participants){
  participants=Array.isArray(participants)?participants:[];
  let html="";
  for(let i=0;i<count;i++){
    const p=participants[i]||{};
    html+=`
      <div class="participant-block">
        <div class="p-title">参加者${i+1}</div>
        <div class="participant-fields">
          <label>氏名<input id="${prefix}-name-${i}" value="${esc(p.name)}"></label>
          <label>年齢<input id="${prefix}-age-${i}" type="number" min="0" value="${esc(p.age)}"></label>
          <label>靴のサイズ<input id="${prefix}-shoe-${i}" placeholder="例: 26.0cm" value="${esc(p.shoeSize)}"></label>
        </div>
      </div>`;
  }
  return html;
}
function renderParticipantEditor(){
  const count=parseInt($("people").value,10)||1;
  $("participantFieldsEditor").innerHTML=participantFieldsHtml("np",count,parsedParticipants);
}
function syncParticipantEditorToState(){
  const rows=$("participantFieldsEditor").querySelectorAll(".participant-block").length;
  const updated=[];
  for(let i=0;i<rows;i++){
    const nameEl=$(`np-name-${i}`);
    if(!nameEl) break;
    updated.push({name:nameEl.value,age:$(`np-age-${i}`).value,shoeSize:$(`np-shoe-${i}`).value});
  }
  parsedParticipants=updated;
}
function showDetail(id){
  const r=records.find(x=>x.id===id);if(!r)return;
  $("detailTitle").textContent=r.name||"問い合わせ詳細";
  $("detail").innerHTML=`
    <div class="detail-grid">
      <div class="detail-item"><b>状態</b>${r.status==="confirmed"?"予約確定":"未確定"}</div>
      <div class="detail-item"><b>希望日</b>${fmt(r.desiredDate)}</div>
      <div class="detail-item"><b>人数</b>${esc(r.people||"未入力")}名</div>
      <div class="detail-item"><b>観察希望</b>${esc(r.creatures||"未入力")}</div>
      <div class="detail-item"><b>電話</b>${esc(r.phone||"未入力")}</div>
      <div class="detail-item"><b>メール</b>${esc(r.email||"未入力")}</div>
      <div class="detail-item"><b>ホテル</b>${esc(r.hotel||"未入力")}</div>
      <div class="detail-item"><b>問い合わせ方法</b>${esc(r.contactMethod)}</div>
    </div>
    <h3>操作</h3>
    <div class="actions">
      <button class="primary" id="toggleStatus">${r.status==="confirmed"?"未確定に戻す":"予約確定にする"}</button>
      <button class="ghost" id="deleteRecord">削除</button>
    </div>
    <h3>参加者情報</h3>
    <div id="participantFields">${participantFieldsHtml("p",parseInt(r.people,10)||1,r.participants)}</div>
    <div class="actions"><button class="secondary" id="saveParticipants">参加者情報を保存</button></div>
    <h3>元の問い合わせ</h3><pre style="white-space:pre-wrap;background:#f5f7f5;padding:12px;border-radius:10px">${esc(r.raw)}</pre>
    <h3>返信案</h3><textarea id="detailReply" rows="8">${esc(r.reply||"")}</textarea>
    <div class="actions"><button class="ghost" id="copyDetail">返信をコピー</button></div>`;
  $("detailModal").classList.remove("hidden");
  $("toggleStatus").onclick=()=>{r.status=r.status==="confirmed"?"pending":"confirmed";save();render();showDetail(id)};
  $("deleteRecord").onclick=()=>{if(confirm("この問い合わせを削除しますか？")){records=records.filter(x=>x.id!==id);save();render();$("detailModal").classList.add("hidden")}};
  $("saveParticipants").onclick=()=>{
    const count=parseInt(r.people,10)||1;
    const participants=[];
    for(let i=0;i<count;i++){
      participants.push({name:$(`p-name-${i}`).value,age:$(`p-age-${i}`).value,shoeSize:$(`p-shoe-${i}`).value});
    }
    r.participants=participants;save();
    $("saveParticipants").textContent="保存しました";setTimeout(()=>{$("saveParticipants").textContent="参加者情報を保存"},1200);
  };
  $("copyDetail").onclick=async()=>{await navigator.clipboard.writeText($("detailReply").value);$("copyDetail").textContent="コピーしました"};
}
$("closeModal").onclick=()=>$("detailModal").classList.add("hidden");
$("detailModal").onclick=e=>{if(e.target===$("detailModal"))$("detailModal").classList.add("hidden")};
render();
