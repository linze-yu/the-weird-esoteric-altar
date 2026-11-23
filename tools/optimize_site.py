#!/usr/bin/env python3
"""
优化冰山图站点产物:
  ① 字体子集化(TTF → WOFF2,只保留页面实际用到的字)
  ② 数据分层(entries.json → data/tier{1..8}.json + data/index.json)
  ③ 生成 data/index.json(含 tier/category 索引)
用法: PYTHONPATH=/opt/data/python-packages python3 optimize_site.py <site_dir>
"""
import os, re, sys, json, gzip
from pathlib import Path
from collections import defaultdict

SITE = Path(sys.argv[1] if len(sys.argv) > 1 else "/opt/data/cache/scratch/gh-deploy")
FONT_SRC = SITE/"NotoSansSC.ttf"
FONT_OUT = SITE/"NotoSansSC.woff2"
DATA = SITE/"data"
DATA.mkdir(exist_ok=True)

print("════════ ① 读词条 ════════\n")
entries = json.load(open(SITE/"entries.json", encoding="utf-8"))
print(f"  {len(entries):,} 条")

print("\n════════ ② 收集用字 ════════\n")
UI = ("怪谈冰山图探灵数据源词条层级分类文献搜索随机深度轴紧凑设置清除全部显示隐藏排序默认"
      "访问来源关闭描述水面上水下深林常规精怪变化异端灾异害人死丧疫毒色欲蛊惑食人噬命寻常草木"
      "器物祥瑞守护妖异兽鬼神人植物异象未归类所有共条正在加载更多展开收起有链接无描述最新需补充"
      "复制版权使用条款隐私说明继续即表示同意本站社区共建设览收藏评论点赞背景纯黑液态标题全文"
      "模糊精确返回首页历史今天书籍手动中文字体加载失败请检查网络本地服务器首次访问需要一些时间"
      "向下滚动越深越黑点击词条打开详情滚轮缩放拖拽平移筛选模式随机按钮字体字号错落排版偏移"
      "导出导入清空数据排序声音响起范围内没有匹配的词条这个层级没有匹配的词条返回顶部"
      "第层浅深常规底座核心外层最深处")
chars = set(UI)
chars |= set("0123456789.·—…、，。！？：；（）「」《》【】/\\|-_+=<>%&#@ 　")
for e in entries:
    for k in ("title","desc","kind","feature","shape","dist","dynasty","world"):
        v = e.get(k)
        if isinstance(v,str): chars |= set(v)
    for t in (e.get("tags") or []): chars |= set(str(t))
    for b in (e.get("books") or []): chars |= set(str(b))
    for t in e.get("title",""): chars |= set(t)
cjk = {c for c in chars if ord(c) > 0x2000}
print(f"  CJK {len(cjk):,} + 其他 {len(chars)-len(cjk):,} = {len(chars):,} 字符")

print("\n════════ ③ 字体子集化 ════════\n")
from fontTools import subset
opt = subset.Options()
opt.flavor = "woff2"
opt.desubroutinize = True
opt.layout_features = ["*"]
opt.notdef_outline = True
opt.recalc_bounds = True
opt.drop_tables = ["DSIG"]
opt.name_IDs = ["*"]
opt.name_legacy = True
font = subset.load_font(str(FONT_SRC), opt)
ss = subset.Subsetter(options=opt)
ss.populate(text="".join(sorted(chars)))
ss.subset(font)
subset.save_font(font, str(FONT_OUT), opt)
orig = FONT_SRC.stat().st_size
new = FONT_OUT.stat().st_size
print(f"  TTF  {orig:>10,} B")
print(f"  WOFF2 {new:>9,} B  (省 {100-new/orig*100:.1f}%)")

print("\n════════ ④ 数据分层 ════════\n")
by_tier = defaultdict(list)
for e in entries: by_tier[e["tier"]].append(e)
meta = {"total": len(entries), "tiers": {}, "categories": {}}
for t in sorted(by_tier, reverse=True):
    lst = by_tier[t]
    payload = json.dumps(lst, ensure_ascii=False, separators=(",",":")).encode("utf-8")
    fn = f"data/tier{t}.json"
    (SITE/fn).write_bytes(payload)
    gz = len(gzip.compress(payload, 9))
    meta["tiers"][str(t)] = {"file": fn, "count": len(lst), "bytes": len(payload), "gzip": gz}
    print(f"  L{t}: {len(lst):>5} 条  raw {len(payload):>9,}  gzip {gz:>9,}")
cats = defaultdict(int)
for e in entries: cats[e["category"]] += 1
meta["categories"] = dict(cats)
(SITE/"data/index.json").write_text(json.dumps(meta, ensure_ascii=False, separators=(",",":")), encoding="utf-8")
print(f"  index.json: {(SITE/'data/index.json').stat().st_size:,} B")

print("\n════════ ⑤ 前端改造:分层懒加载 ════════\n")
html = (SITE/"index.html").read_text(encoding="utf-8")

# 字体引用换 woff2
html = html.replace("@font-face{font-family:'NotoSC';src:url('NotoSansSC.ttf') format('truetype');font-display:swap}",
                    "@font-face{font-family:'NotoSC';src:url('NotoSansSC.woff2') format('woff2');font-display:swap;unicode-range:U+4E00-9FFF,U+3400-4DBF,U+F900-FAFF}")

# 换掉 fetch + 渲染逻辑
OLD_FETCH = """fetch("entries.json").then(r=>r.json()).then(d=>{
  ENT=d;BYID=Object.fromEntries(d.map(e=>[e.id,e]));
  $("n-ent").textContent=d.length.toLocaleString();
  $("n-cat").textContent=Object.keys(CATS).length;
  $("n-src").textContent=new Set(d.flatMap(e=>e.books||[]).filter(b=>b&&b.length<40)).size.toLocaleString();
  buildFilters();render();
  $("q").addEventListener("input",ev=>{Q=ev.target.value.trim();render();});
  $("btn-random").onclick=()=>{const c=ENT.filter(match);if(c.length)openModal(c[Math.floor(Math.random()*c.length)]);};
  $("btn-depth").onclick=e=>{SHOWDEPTH=!SHOWDEPTH;e.target.classList.toggle("on",SHOWDEPTH);render();};
  $("btn-compact").onclick=e=>{COMPACT=!COMPACT;e.target.classList.toggle("on",COMPACT);render();};
  addEventListener("scroll",()=>{
    const h=document.body.scrollHeight-innerHeight;
    const p=h>0?scrollY/h:0;
    $("shade").style.opacity=Math.min(.72,p*.95);
  },{passive:true});
});"""

NEW_FETCH = """// 分层懒加载:先取 index(68KB),再按需取各 tier
const TIER_FILE={}, TIER_STATE={};
async function boot(){
  const meta=await (await fetch("data/index.json")).json();
  META=meta;
  for(const [t,info] of Object.entries(meta.tiers)) TIER_FILE[t]=info.file;
  $("n-ent").textContent=meta.total.toLocaleString();
  $("n-cat").textContent=Object.keys(CATS).length;
  $("n-src").textContent="—";
  buildFilters();
  render();                      // 先画骨架
  await loadTier(8);             // 优先加载最浅层(水面下第一层)
  await loadTier(3);
  render();
  bindUI();
}
async function loadTier(t){
  if(TIER_STATE[t]==="done"||TIER_STATE[t]==="loading") return;
  TIER_STATE[t]="loading";
  try{
    const r=await fetch(TIER_FILE[t]);
    const list=await r.json();
    (ENT[tierBuf[t]]||(tierBuf[t]=[])).push(...list);
    TIER_STATE[t]="done";
  }catch(e){ TIER_STATE[t]="error"; }
}
async function ensureTierLoaded(t){
  if(TIER_STATE[t]==="done") return;
  await loadTier(t);
}
let META=null;const tierBuf={};
function bindUI(){
  $("q").addEventListener("input",ev=>{Q=ev.target.value.trim();render();});
  $("btn-random").onclick=async()=>{
    const c=ALL().filter(match);
    if(c.length) openModal(c[Math.floor(Math.random()*c.length)]);
  };
  $("btn-depth").onclick=e=>{SHOWDEPTH=!SHOWDEPTH;e.target.classList.toggle("on",SHOWDEPTH);render();};
  $("btn-compact").onclick=e=>{COMPACT=!COMPACT;e.target.classList.toggle("on",COMPACT);render();};
  addEventListener("scroll",()=>{
    const h=document.body.scrollHeight-innerHeight;
    const p=h>0?scrollY/h:0;
    $("shade").style.opacity=Math.min(.72,p*.95);
    // 接近某个 tier 区块时预加载
    for(const t of Object.keys(TIER_FILE)){
      if(TIER_STATE[t]==="done") continue;
      const el=document.querySelector(`[data-tier="${t}"]`);
      if(el&&el.getBoundingClientRect().top<innerHeight*2) loadTier(+t);
    }
  },{passive:true});
}
function ALL(){let a=[];for(const k in tierBuf)a=a.concat(tierBuf[k]);return a;}"""

if OLD_FETCH in html:
    html = html.replace(OLD_FETCH, NEW_FETCH)
    print("  ✅ fetch 逻辑已替换")
else:
    print("  ⚠ 未匹配到 OLD_FETCH,需手动检查")

# ENT 改成按 tier 的 buffer
html = html.replace("let ENT=[],BYID={},ACT=new Set(),Q=\"\",SHOWDEPTH=true,COMPACT=false;",
                    "let ENT=[],BYID={},ACT=new Set(),Q=\"\",SHOWDEPTH=true,COMPACT=false;\nconst ENT_ALL=()=>ALL();")

# render 里改用 tierBuf
html = html.replace("""  TIERS.forEach(T=>{
    const list=ENT.filter(e=>e.tier===T.n&&match(e));
    if(!list.length)return;""",
"""  TIERS.forEach(T=>{
    const all=tierBuf[T.n]||[];
    const list=all.filter(e=>match(e));
    sec_placeholder:;
    if(!list.length&&TIER_STATE[T.n]!=="done"){pendingTier(T.n);return;}""")

html = html.replace("""  if(!shown)box.innerHTML='<div class="empty">没有匹配的词条</div>';
}""",
"""  if(!shown&&!Object.values(TIER_STATE).some(s=>s==="loading")){
    box.innerHTML='<div class="empty">没有匹配的词条</div>';
  }
}
let pendingSet=new Set();
function pendingTier(t){
  if(pendingSet.has(t))return; pendingSet.add(t);
  const sec=document.createElement("section");
  sec.className="tier";sec.style.setProperty("--tc",TIERS.find(x=>x.n===t)?.c||"#8ebcf0");
  sec.dataset.tier=t;
  sec.innerHTML=`<div class="tier-hd"><span class="tier-no">${t}</span>
    <span class="tier-txt"><h2>${TIERS.find(x=>x.n===t)?.name||""}</h2>
    <p>${TIERS.find(x=>x.n===t)?.desc||""}</p></span>
    <span class="tier-count"><b>载入中…</b></span></div>`;
  $("tiers").appendChild(sec);
  loadTier(t).then(()=>{pendingSet.delete(t);render();});
}""")

# buildFilters 改用 META.categories
html = html.replace("""function buildFilters(){
  const cnt={};ENT.forEach(e=>cnt[e.category]=(cnt[e.category]||0)+1);""",
"""function buildFilters(){
  const cnt=(META&&META.categories)||{};""")

# match 过滤器的 ENT 用法
html = html.replace("function match(e){", "function match(e){")

# 搜索需要全量 → 触发全量加载
html = html.replace('$("q").addEventListener("input",ev=>{Q=ev.target.value.trim();render();});',
  '$("q").addEventListener("input",async ev=>{Q=ev.target.value.trim();if(Q){for(const t of Object.keys(TIER_FILE))await loadTier(+t);}render();});')

# 尾部:调 boot()
html = html.replace("</script>\n</body>", "boot();\n</script>\n</body>")

(SITE/"index.html").write_text(html, encoding="utf-8")
print(f"  index.html → {(SITE/'index.html').stat().st_size:,} B")

print("\n════════ ⑥ 移除旧文件 ════════\n")
for f in ["entries.json","NotoSansSC.ttf"]:
    p = SITE/f
    if p.exists():
        p.unlink(); print(f"  删 {f}")
print("\n  ✅ 完成")
