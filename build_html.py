"""Build a single-file filterable HTML page from races.json."""
import json
from pathlib import Path

races = json.loads(Path("races.json").read_text(encoding="utf-8"))
data_js = json.dumps(races, ensure_ascii=False)

html = r"""<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>路跑賽事篩選器 · Taipei Marathon</title>
<style>
:root{
  --bg:#0e1116;--panel:#161b22;--panel2:#1f2630;--border:#2a3340;
  --fg:#e6edf3;--muted:#8b96a5;--accent:#f97316;--accent2:#22d3ee;
  --open:#22c55e;--upcoming:#eab308;--closed:#6b7280;--star:#fbbf24;
  --shadow:0 1px 2px rgba(0,0,0,.4),0 4px 16px rgba(0,0,0,.3);
  --neon:#ff2bd6;
}
@media (prefers-color-scheme:light){
  :root{--bg:#f7f7f5;--panel:#fff;--panel2:#f0f2f5;--border:#e3e6eb;--fg:#1a1d22;--muted:#5a6271;--shadow:0 1px 2px rgba(0,0,0,.05),0 4px 16px rgba(0,0,0,.06);}
}
*{box-sizing:border-box}
html,body{margin:0;padding:0;background:var(--bg);color:var(--fg);font-family:-apple-system,"PingFang TC","Noto Sans TC","Helvetica Neue",sans-serif;font-size:14px;line-height:1.5}
a{color:var(--accent2);text-decoration:none}
a:hover{text-decoration:underline}
header{position:sticky;top:0;z-index:10;background:color-mix(in srgb,var(--bg) 92%,transparent);backdrop-filter:blur(10px);border-bottom:1px solid var(--border)}
.wrap{max-width:1280px;margin:0 auto;padding:0 16px}
h1{margin:0;font-size:18px;font-weight:600;letter-spacing:.02em}
.title-row{display:flex;align-items:baseline;justify-content:space-between;gap:16px;padding:12px 0 4px}
.subtitle{color:var(--muted);font-size:12px}
.controls{display:flex;flex-direction:column;gap:8px;padding:8px 0 12px}
.row{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.label{color:var(--muted);font-size:12px;min-width:48px}
.chip{display:inline-flex;align-items:center;gap:4px;padding:4px 10px;border-radius:999px;border:1px solid var(--border);background:var(--panel);color:var(--fg);font-size:12px;cursor:pointer;user-select:none;transition:all .12s}
.chip:hover{border-color:var(--accent)}
.chip.on{background:var(--accent);border-color:var(--accent);color:#fff}
.chip.on.state-open{background:var(--open);border-color:var(--open)}
.chip.on.state-upcoming{background:var(--upcoming);border-color:var(--upcoming);color:#1a1d22}
.chip.on.state-closed{background:var(--closed);border-color:var(--closed)}
.search{flex:1;min-width:200px;padding:8px 12px;border-radius:8px;border:1px solid var(--border);background:var(--panel);color:var(--fg);font-size:14px}
.search:focus{outline:none;border-color:var(--accent)}
.toolbar{display:flex;justify-content:space-between;align-items:center;gap:12px;padding:8px 0;border-top:1px dashed var(--border);margin-top:4px}
.count{color:var(--muted);font-size:12px}
.count strong{color:var(--fg);font-weight:600}
.btn{padding:6px 12px;border-radius:8px;border:1px solid var(--border);background:var(--panel);color:var(--fg);font-size:12px;cursor:pointer}
.btn:hover{border-color:var(--accent)}
.btn.primary{background:var(--accent);border-color:var(--accent);color:#fff}
main{padding:16px 0 64px}
.month-section{margin:0 0 28px}
.month-head{position:sticky;top:0;display:flex;align-items:baseline;gap:10px;margin:0 0 12px;padding:8px 0;background:color-mix(in srgb,var(--bg) 92%,transparent);backdrop-filter:blur(8px);border-bottom:2px solid var(--accent);z-index:5}
.month-head h2{margin:0;font-size:22px;font-weight:700;letter-spacing:.04em;color:var(--accent)}
.month-head .month-meta{color:var(--muted);font-size:12px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:12px}
.card{background:var(--panel);border:1px solid var(--border);border-radius:12px;padding:14px;display:flex;flex-direction:column;gap:8px;box-shadow:var(--shadow);transition:transform .1s,border-color .12s}
.card:hover{border-color:var(--accent);transform:translateY(-1px)}
.card.starred{border-color:var(--star);box-shadow:0 0 0 1px var(--star) inset,var(--shadow)}
.card-head{display:flex;justify-content:space-between;align-items:flex-start;gap:8px}
.name{font-size:15px;font-weight:600;line-height:1.35}
.name a{color:var(--fg)}
.star{background:none;border:0;font-size:20px;cursor:pointer;color:var(--muted);padding:0;line-height:1;transition:color .1s,transform .1s}
.star:hover{transform:scale(1.15)}
.star.on{color:var(--star)}
.meta{display:flex;flex-wrap:wrap;gap:6px 10px;color:var(--muted);font-size:12px}
.meta b{color:var(--fg);font-weight:500}
.dists{display:flex;flex-wrap:wrap;gap:4px}
.dist{padding:2px 8px;border-radius:6px;background:var(--panel2);font-size:11px;font-variant-numeric:tabular-nums}
.dist.km42{background:#dc2626;color:#fff}
.dist.km21{background:#ea580c;color:#fff}
.dist.km10{background:#0891b2;color:#fff}
.dist.kmsmall{background:#475569;color:#fff}
.dist .fee{opacity:.85;margin-left:4px}
.dist{cursor:pointer;transition:transform .08s,box-shadow .12s,outline-offset .1s;border:0}
.dist:hover{transform:translateY(-1px)}
.dist.picked{outline:2px solid var(--neon);outline-offset:2px;font-weight:700;box-shadow:0 0 0 1px var(--neon) inset,0 0 8px rgba(255,43,214,.7),0 0 16px rgba(255,43,214,.35)}
.dist.picked::before{content:"✓ ";font-weight:700}
.foot{display:flex;justify-content:space-between;align-items:center;gap:8px;font-size:11px;color:var(--muted);margin-top:4px;padding-top:8px;border-top:1px dashed var(--border)}
.state{display:inline-flex;align-items:center;gap:4px;padding:2px 8px;border-radius:999px;font-size:11px;font-weight:500}
.state.open{background:rgba(34,197,94,.15);color:var(--open)}
.state.upcoming{background:rgba(234,179,8,.15);color:var(--upcoming)}
.state.closed{background:rgba(107,114,128,.2);color:var(--closed)}
.state::before{content:"●";font-size:8px}
.empty{text-align:center;padding:64px 16px;color:var(--muted)}
.badge-new{display:inline-block;background:var(--accent);color:#fff;font-size:10px;padding:1px 6px;border-radius:4px;margin-left:6px;vertical-align:middle}
.region-tag{padding:2px 8px;border-radius:4px;background:var(--panel2);font-size:11px}
@media (max-width:640px){
  .grid{grid-template-columns:1fr}
  .label{min-width:auto;width:100%}
}
.print-head{display:none}
@media print{
  @page{size:A4;margin:12mm}
  /* 強制 light 主題，讓白紙上彩色卡片清楚 */
  :root{--bg:#fff !important;--panel:#fff !important;--panel2:#f0f2f5 !important;--border:#cbd5e1 !important;--fg:#1a1d22 !important;--muted:#5a6271 !important;--shadow:none !important}
  /* 保留瀏覽器列印時的背景色與顏色 */
  *{-webkit-print-color-adjust:exact !important;print-color-adjust:exact !important;color-adjust:exact !important}
  html,body{background:#fff !important}
  /* 隱藏 UI chrome */
  header,.empty,.star{display:none !important}
  main{padding:0}
  .wrap{max-width:none;padding:0}
  /* 列印抬頭 */
  .print-head{display:block;margin:0 0 12px;padding:0 0 8px;border-bottom:2px solid var(--accent)}
  .print-head h1{font-size:20px;margin:0 0 4px;color:var(--accent)}
  .print-head .sub{color:#5a6271;font-size:11px}
  /* 月份標題不要 sticky，避免疊出鬼影 */
  .month-head{position:static !important;backdrop-filter:none !important}
  .month-section{break-inside:avoid-page}
  /* 卡片避免被切半，2 欄較省紙 */
  .card{break-inside:avoid;page-break-inside:avoid;box-shadow:none !important;border:1px solid #cbd5e1 !important}
  .grid{grid-template-columns:1fr 1fr;gap:8px}
  /* 連結用黑色文字、不顯示底線網址 */
  .name a{color:var(--fg) !important}
  a[href]:after{content:""}
}
</style>
</head>
<body>
<header>
  <div class="wrap">
    <div class="title-row">
      <h1>🏃 路跑賽事篩選器 <span class="subtitle">資料來源：taipeimarathon.org.tw · 共 __TOTAL__ 場</span></h1>
    </div>
    <div class="controls">
      <div class="row">
        <input id="q" class="search" placeholder="搜尋賽事名稱、地點、主辦單位…">
      </div>
      <div class="row">
        <span class="label">距離</span>
        <span id="cats"></span>
      </div>
      <div class="row">
        <span class="label">月份</span>
        <span id="months"></span>
      </div>
      <div class="row">
        <span class="label">地區</span>
        <span id="regions"></span>
      </div>
      <div class="row">
        <span class="label">報名</span>
        <span id="states"></span>
      </div>
      <div class="toolbar">
        <span class="count">顯示 <strong id="shown">0</strong> / <span id="total">0</span> 場 · ⭐ 我的清單 <strong id="starCount">0</strong> · ✓ 已選距離 <strong id="pickCount">0</strong></span>
        <div class="row" style="gap:6px">
          <button class="chip" id="onlyStarred">⭐ 只看我的清單</button>
          <button class="btn" id="clearAll">清除篩選</button>
          <button class="btn" id="exportStar">匯出我的清單</button>
          <button class="btn primary" id="printPdf">🖨 列印 PDF</button>
        </div>
      </div>
    </div>
  </div>
</header>
<main class="wrap">
  <div class="print-head">
    <h1>我的賽事清單</h1>
    <div class="sub" id="printSub"></div>
  </div>
  <div id="months-out"></div>
  <div id="empty" class="empty" hidden>沒有符合條件的賽事 — 試試清除篩選</div>
</main>
<script>
const RACES = __DATA__;
const STORE_KEY = "tpemar_starred_v1";
const FILTER_KEY = "tpemar_filters_v1";
const PICKS_KEY = "tpemar_picks_v1";
const starred = new Set(JSON.parse(localStorage.getItem(STORE_KEY) || "[]"));
const picks = new Set(JSON.parse(localStorage.getItem(PICKS_KEY) || "[]"));
const pickKey = (name,label) => name + "::" + label;

const monthNames = ["1月","2月","3月","4月","5月","6月","7月","8月","9月","10月","11月","12月"];
const allCats = ["全馬","半馬","10K+","休閒","特殊"];
const allStates = [
  {key:"open",label:"報名中",cls:"state-open"},
  {key:"upcoming",label:"即將開放",cls:"state-upcoming"},
  {key:"closed",label:"已截止",cls:"state-closed"},
];
const allRegions = [...new Set(RACES.map(r=>r.region))].sort((a,b)=>{
  if(a==="其他")return 1;if(b==="其他")return -1;return a.localeCompare(b,"zh-Hant");
});
const allMonths = [...new Set(RACES.map(r=>r.month).filter(Boolean))].sort((a,b)=>a-b);

const filters = Object.assign(
  {q:"",cats:new Set(),months:new Set(),regions:new Set(),states:new Set(),onlyStarred:false},
  loadFilters()
);

function loadFilters(){
  try{
    const o=JSON.parse(localStorage.getItem(FILTER_KEY)||"{}");
    return {q:o.q||"",cats:new Set(o.cats||[]),months:new Set(o.months||[]),regions:new Set(o.regions||[]),states:new Set(o.states||[]),onlyStarred:!!o.onlyStarred};
  }catch{return{}}
}
function saveFilters(){
  localStorage.setItem(FILTER_KEY,JSON.stringify({q:filters.q,cats:[...filters.cats],months:[...filters.months],regions:[...filters.regions],states:[...filters.states],onlyStarred:filters.onlyStarred}));
}
function saveStars(){localStorage.setItem(STORE_KEY,JSON.stringify([...starred]));}
function savePicks(){localStorage.setItem(PICKS_KEY,JSON.stringify([...picks]));}

function makeChip(label,active,onClick,extraCls=""){
  const b=document.createElement("button");
  b.className="chip"+(active?" on":"")+(extraCls?" "+extraCls:"");
  b.textContent=label;
  b.addEventListener("click",onClick);
  return b;
}

function renderChips(){
  const cats=document.getElementById("cats");cats.innerHTML="";
  allCats.forEach(c=>cats.appendChild(makeChip(c,filters.cats.has(c),()=>{toggle(filters.cats,c);render();})));
  const ms=document.getElementById("months");ms.innerHTML="";
  allMonths.forEach(m=>ms.appendChild(makeChip(monthNames[m-1],filters.months.has(m),()=>{toggle(filters.months,m);render();})));
  const rs=document.getElementById("regions");rs.innerHTML="";
  allRegions.forEach(r=>rs.appendChild(makeChip(r,filters.regions.has(r),()=>{toggle(filters.regions,r);render();})));
  const ss=document.getElementById("states");ss.innerHTML="";
  allStates.forEach(s=>ss.appendChild(makeChip(s.label,filters.states.has(s.key),()=>{toggle(filters.states,s.key);render();},s.cls)));
}
function toggle(set,v){set.has(v)?set.delete(v):set.add(v);saveFilters();}

function distClass(label){
  const m=label.match(/([\d.]+)\s*K/i);
  if(!m)return"";
  const k=parseFloat(m[1]);
  if(k>=42)return"km42";
  if(k>=21)return"km21";
  if(k>=10)return"km10";
  return"kmsmall";
}

function matches(r){
  if(filters.onlyStarred && !starred.has(r.name))return false;
  if(filters.cats.size && !r.categories.some(c=>filters.cats.has(c)))return false;
  if(filters.months.size && !filters.months.has(r.month))return false;
  if(filters.regions.size && !filters.regions.has(r.region))return false;
  if(filters.states.size && !filters.states.has(r.reg_state))return false;
  if(filters.q){
    const q=filters.q.toLowerCase();
    const hay=(r.name+" "+r.location+" "+r.organizer).toLowerCase();
    if(!hay.includes(q))return false;
  }
  return true;
}

function card(r){
  const isStar=starred.has(r.name);
  const stateMeta=allStates.find(s=>s.key===r.reg_state);
  const el=document.createElement("article");
  el.className="card"+(isStar?" starred":"");
  const dists=r.distances.map(d=>{
    const cls=distClass(d.label);
    const isPicked=picks.has(pickKey(r.name,d.label));
    const fee=d.fee?` <span class="fee">$${d.fee}</span>`:"";
    const tip=[d.fee?`費用 $${d.fee}`:"",d.limit?`限額 ${d.limit}`:"","點擊選/取消"].filter(Boolean).join(" · ");
    return `<span class="dist ${cls}${isPicked?' picked':''}" data-label="${escapeHtml(d.label)}" title="${tip}">${d.label}${fee}</span>`;
  }).join("");
  el.innerHTML=`
    <div class="card-head">
      <div class="name">
        <a href="${r.link}" target="_blank" rel="noopener">${escapeHtml(r.name)}</a>
        ${r.is_new?'<span class="badge-new">NEW</span>':""}
      </div>
      <button class="star${isStar?' on':''}" title="${isStar?'從清單移除':'加入我的清單'}">${isStar?"★":"☆"}</button>
    </div>
    <div class="meta">
      <span><b>${r.month}/${String(r.day).padStart(2,"0")}</b> (${r.weekday}) ${r.start_time||""}</span>
      <span class="region-tag">${r.region}</span>
      <span>${escapeHtml(r.location.replace(r.region,""))}</span>
    </div>
    <div class="dists">${dists}</div>
    <div class="foot">
      <span>${escapeHtml(r.organizer||"")}</span>
      <span class="state ${r.reg_state}">${stateMeta?stateMeta.label:r.status} ${r.status_raw && r.reg_state!=='closed' && r.status_raw!==r.status?'· '+escapeHtml(r.status_raw):''}</span>
    </div>`;
  el.querySelector(".star").addEventListener("click",e=>{
    e.preventDefault();e.stopPropagation();
    if(starred.has(r.name))starred.delete(r.name);else starred.add(r.name);
    saveStars();render();
  });
  el.querySelectorAll(".dist").forEach(node=>{
    node.addEventListener("click",e=>{
      e.preventDefault();e.stopPropagation();
      const k=pickKey(r.name,node.dataset.label);
      if(picks.has(k)){picks.delete(k);node.classList.remove("picked");}
      else{picks.add(k);node.classList.add("picked");if(!starred.has(r.name)){starred.add(r.name);saveStars();render();return;}}
      savePicks();
      document.getElementById("pickCount").textContent=picks.size;
    });
  });
  return el;
}

function escapeHtml(s){return (s||"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));}

function render(){
  renderChips();
  document.getElementById("onlyStarred").classList.toggle("on",filters.onlyStarred);
  document.getElementById("starCount").textContent=starred.size;
  document.getElementById("pickCount").textContent=picks.size;
  const list=RACES.filter(matches).sort((a,b)=>(a.month-b.month)||(a.day-b.day));
  const out=document.getElementById("months-out");
  out.innerHTML="";
  const groups=new Map();
  list.forEach(r=>{const k=r.month||0;if(!groups.has(k))groups.set(k,[]);groups.get(k).push(r);});
  for(const [m,items] of groups){
    const sec=document.createElement("section");sec.className="month-section";
    const head=document.createElement("div");head.className="month-head";
    head.innerHTML=`<h2>${m?monthNames[m-1]:"未排定"}</h2><span class="month-meta">${items.length} 場</span>`;
    sec.appendChild(head);
    const grid=document.createElement("div");grid.className="grid";
    items.forEach(r=>grid.appendChild(card(r)));
    sec.appendChild(grid);
    out.appendChild(sec);
  }
  document.getElementById("shown").textContent=list.length;
  document.getElementById("total").textContent=RACES.length;
  document.getElementById("empty").hidden=list.length>0;
}

document.getElementById("q").addEventListener("input",e=>{filters.q=e.target.value.trim();saveFilters();render();});
document.getElementById("q").value=filters.q;
document.getElementById("onlyStarred").addEventListener("click",()=>{filters.onlyStarred=!filters.onlyStarred;saveFilters();render();});
document.getElementById("clearAll").addEventListener("click",()=>{
  filters.q="";filters.cats.clear();filters.months.clear();filters.regions.clear();filters.states.clear();filters.onlyStarred=false;
  document.getElementById("q").value="";saveFilters();render();
});
document.getElementById("printPdf").addEventListener("click",()=>{
  if(!starred.size){alert("尚未加入任何賽事，先按卡片右上角的 ☆");return;}
  if(!filters.onlyStarred){filters.onlyStarred=true;saveFilters();render();}
  const today=new Date();
  const ds=`${today.getFullYear()}-${String(today.getMonth()+1).padStart(2,"0")}-${String(today.getDate()).padStart(2,"0")}`;
  document.getElementById("printSub").textContent=`列印日期 ${ds} · 共 ${starred.size} 場 · 資料：taipeimarathon.org.tw`;
  setTimeout(()=>window.print(),50);
});
document.getElementById("exportStar").addEventListener("click",()=>{
  const list=RACES.filter(r=>starred.has(r.name)).sort((a,b)=>(a.month-b.month)||(a.day-b.day));
  if(!list.length){alert("尚未加入任何賽事，先按卡片右上角的 ☆");return;}
  const lines=list.map(r=>{
    const chosen=r.distances.filter(d=>picks.has(pickKey(r.name,d.label))).map(d=>d.label);
    const distStr=chosen.length?`✓ ${chosen.join("/")}`:r.distances.map(d=>d.label).join("/");
    return `${r.month}/${String(r.day).padStart(2,"0")} (${r.weekday}) ${r.name} · ${r.region} · ${distStr}\n${r.link}`;
  });
  const blob=new Blob([lines.join("\n\n")],{type:"text/plain;charset=utf-8"});
  const a=document.createElement("a");a.href=URL.createObjectURL(blob);a.download="my_races.txt";a.click();
});

render();
</script>
</body>
</html>
"""

out = html.replace("__DATA__", data_js).replace("__TOTAL__", str(len(races)))
Path("index.html").write_text(out, encoding="utf-8")
print(f"Wrote index.html ({len(out):,} bytes, {len(races)} races)")
