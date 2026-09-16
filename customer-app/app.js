const KEY="nea_customer_app_v1";
let records=JSON.parse(localStorage.getItem(KEY)||"[]");
let currentId=null;
let parsedParticipants=[];

const $=id=>document.getElementById(id);
const today=()=>new Date().toISOString().slice(0,10);
const save=()=>localStorage.setItem(KEY,JSON.stringify(records));

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
    <article class="card" data-id="${r.id}">
      <div class="card-top"><div><div class="name">${esc(r.name||"氏名未入力")}</div><div class="date">${fmt(r.desiredDate)}</div></div>
      <span class="tag ${r.status}">${r.status==="confirmed"?"予約確定":"未確定"}</span></div>
      <div class="meta">${esc(r.people||"人数未入力")}名　${esc(r.creatures||"生き物未入力")}　${esc(r.hotel||"ホテル未入力")}</div>
    </article>`;
}
function render(){
  updateStats();
  const q=$("search").value.trim().toLowerCase(), f=$("statusFilter").value;
  const rows=records.filter(r=>{
    const text=[r.name,r.hotel,r.creatures,r.phone,r.email,r.notes].join(" ").toLowerCase();
    return (!q||text.includes(q))&&(f==="all"||r.status===f);
  }).sort((a,b)=>(a.desiredDate||"").localeCompare(b.desiredDate||""));
  $("list").innerHTML=rows.length?rows.map(cardHtml).join(""):"<div class='card'>まだ問い合わせはありません。「＋ 新規問い合わせ」から試せます。</div>";
  document.querySelectorAll(".card[data-id]").forEach(el=>el.onclick=()=>showDetail(el.dataset.id));
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
function applyFollowupText(r,text){
  const p=parseText(text);
  ["name","phone","email","desiredDate","people","hotel"].forEach(key=>{
    if(!r[key]&&p[key]) r[key]=p[key];
  });
  if(p.creatures){
    const existing=(r.creatures||"").split(/[、,]/).map(s=>s.trim()).filter(Boolean);
    const added=p.creatures.split(/[、,]/).map(s=>s.trim()).filter(Boolean);
    r.creatures=Array.from(new Set([...existing,...added])).join("、");
  }
  const extracted=parseParticipants(text);
  if(extracted.length){
    if(!Array.isArray(r.participants)) r.participants=[];
    extracted.forEach((ep,i)=>{
      const cur=r.participants[i];
      if(!cur||!cur.confirmed) r.participants[i]={name:ep.name,age:ep.age,shoeSize:ep.shoeSize,confirmed:false};
    });
  }
  if(!Array.isArray(r.followups)) r.followups=[];
  r.followups.push({date:today(),text});
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
const CONTACT_METHODS=["公式LINE","メール","電話","SNSのDM","SIMDEF"];
// 予約確定にすると基本情報は編集できないようにし、「未確定に戻す」で編集を解禁する。
// 確定後に間違いに気づいた時は、一度未確定へ戻してから直せる、という運用に合わせている。
function detailInfoHtml(r){
  if(r.status!=="pending"){
    return `
    <div class="detail-grid">
      <div class="detail-item"><b>状態</b>${r.status==="confirmed"?"予約確定":"未確定"}</div>
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
  const history=[{date:r.createdAt,text:r.raw}].concat(Array.isArray(r.followups)?r.followups:[]);
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
      <button class="primary" id="toggleStatus">${r.status==="confirmed"?"未確定に戻す":"予約確定にする"}</button>
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
    <h3>返信案</h3><textarea id="detailReply" rows="8">${esc(r.reply||"")}</textarea>
    <div class="actions"><button class="ghost" id="copyDetail">返信をコピー</button></div>`;
  $("detailModal").classList.remove("hidden");
  $("toggleStatus").onclick=()=>{r.status=r.status==="confirmed"?"pending":"confirmed";save();render();showDetail(id)};
  $("deleteRecord").onclick=()=>{if(confirm("この問い合わせを削除しますか？")){records=records.filter(x=>x.id!==id);save();render();$("detailModal").classList.add("hidden")}};
  $("detailNotes").onchange=()=>{r.notes=$("detailNotes").value;save();};
  if(r.status==="pending"){
    ["name","phone","email","desiredDate","people","hotel","creatures","contactMethod"].forEach(field=>{
      const el=$(`d-${field}`);
      if(el) el.onchange=()=>{r[field]=el.value;save();render();showDetail(id);};
    });
  }
  $("applyFollowup").onclick=()=>{
    const text=$("followupText").value.trim();
    if(!text){alert("貼り付ける内容がありません。");return;}
    applyFollowupText(r,text);
    save();
    showDetail(id);
  };
  $("copyDetail").onclick=async()=>{await navigator.clipboard.writeText($("detailReply").value);$("copyDetail").textContent="コピーしました"};
}
$("closeModal").onclick=()=>$("detailModal").classList.add("hidden");
$("detailModal").onclick=e=>{if(e.target===$("detailModal"))$("detailModal").classList.add("hidden")};

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

render();
