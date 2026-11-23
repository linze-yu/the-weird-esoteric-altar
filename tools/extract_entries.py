#!/usr/bin/env python3
"""
从 The Weird-Esoteric Altar 的 md 提取「冰山词条」。
纯函数:读 wiki/ → 输出 entries.json。可反复跑。
"""
import re, json, sys
from pathlib import Path
from collections import Counter

W = Path(sys.argv[1] if len(sys.argv)>1 else "/mnt/data/The Weird-Esoteric Altar/wiki")
OUT = Path(sys.argv[2] if len(sys.argv)>2 else "entries.json")

FM = re.compile(r'^---\r?\n(.*?)\r?\n---\r?\n(.*)$', re.S)

# ── 冰山分类:从「种类」字段归到 8 个大类 ──
CATEGORY_RULES = [
    ("ghost",     ["鬼", "僵尸", "饿鬼", "僵尸", "魄", "魂"]),
    ("demon",     ["妖", "精怪", "妖精", "魔", "煞", "邪"]),
    ("beast",     ["异兽", "兽", "妖兽", "龙", "鸟", "虫", "蛇", "兽"]),
    ("deity",     ["神", "神兽", "仙", "菩萨", "佛", "精", "灵"]),
    ("human",     ["异人", "人", "尸"]),
    ("object",    ["物", "器", "宝", "符", "书"]),
    ("plant",     ["植物", "木", "花", "草", "树", "菌"]),
    ("phenomena", ["异象", "灾", "天", "象", "兆"]),
]
def to_category(kinds):
    k = kinds.replace(" ", "")
    for cat, kws in CATEGORY_RULES:
        for kw in kws:
            if kw in k: return cat
    return "other"

# ── 冰山层级:从「特性」判危险/怪异度,1(浅)→8(深) ──
TIER_RULES = [
    (8, ["食人", "杀人", "食脑", "饮血", "剖", "剜"]),
    (7, ["色欲", "淫", "媚", "诱", "缠", "吸精"]),
    (6, ["死亡", "疾病", "瘟", "疫", "毒", "尸"]),
    (5, ["灾异", "恶作剧", "惊吓", "噬", "夺", "害"]),
    (4, ["变化", "器物成精", "复活", "化", "预知", "象征"]),
    (3, ["鬼", "魂", "死后化身", "灵魂", "亡"]),
    (2, ["威", "威严", "守护", "辟邪", "祥瑞", "对人有益", "可使役", "生产"]),
    (1, ["可食用", "草木", "金属", "光", "音律", "才学", "言语", "迅捷"]),
]
def to_tier(feat):
    f = feat.replace(" ", "")
    for t, kws in TIER_RULES:
        for kw in kws:
            if kw in f: return t
    return 3

def clean(v):
    v = (v or "").strip()
    return "" if v in ("-", "", "—", "N/A") else v

entries = []
for p in sorted((W/"entities/cbaigui").glob("*.md")):
    raw = p.read_text(encoding="utf-8", errors="replace")
    m = FM.match(raw)
    if not m: continue
    fm, body = m.group(1), m.group(2)
    t = re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', fm, re.M)
    title = clean(t.group(1)) if t else p.stem
    def fld(name):
        mm = re.search(rf'^\|\s*{name}\s*\|\s*(.*?)\s*\|', body, re.M)
        return clean(mm.group(1)) if mm else ""
    kinds  = fld("种类"); feat = fld("特性"); shape = fld("外形")
    dist  = fld("分布"); dyn  = fld("朝代"); world = fld("世界")
    # 基本介绍段
    intro = ""
    mi = re.search(r'^##+\s*基本介绍\s*$', body, re.M)
    if mi:
        rest = body[mi.end():]
        nxt = re.search(r'^##+\s', rest, re.M)
        seg = rest[:nxt.start()] if nxt else rest
        intro = re.sub(r'\s+', ' ', seg).strip()
    # 文献
    books = []
    mb = re.search(r'^##+\s*文献资料.*?$', body, re.M)
    if mb:
        rest = body[mb.end():]
        nxt = re.search(r'^##+\s', rest, re.M)
        seg = rest[:nxt.start()] if nxt else rest
        books = [re.sub(r'\s+',' ',l).strip() for l in seg.split("\n") if l.strip()][:6]
    src = re.search(r'^source:\s*(\S+)', fm, re.M)
    # tags
    mt = re.search(r'^tags:\s*\[(.*?)\]', fm, re.M)
    tags = [x.strip().strip('"') for x in mt.group(1).split(",")] if mt else []
    tags = [t for t in tags if t not in ("entity","cbaigui")]
    entries.append({
        "id": p.stem,
        "title": title,
        "tier": to_tier(feat),
        "category": to_category(kinds),
        "tags": tags + ([kinds] if kinds else []) + ([dyn] if dyn else []),
        "desc": intro[:300],
        "link": src.group(1) if src else "",
        "kind": kinds, "feature": feat, "shape": shape,
        "dist": dist, "dynasty": dyn, "world": world,
        "books": books,
        "path": f"entities/cbaigui/{p.stem}.md",
    })

OUT.write_text(json.dumps(entries, ensure_ascii=False, indent=1), encoding="utf-8")
tiers = Counter(e["tier"] for e in entries)
cats  = Counter(e["category"] for e in entries)
print(f"提取 {len(entries):,} 词条 → {OUT}")
print(f"层级分布: {dict(sorted(tiers.items()))}")
print(f"分类分布: {dict(cats.most_common())}")
withdesc = sum(1 for e in entries if len(e["desc"]) > 20)
print(f"有描述: {withdesc:,} ({withdesc/len(entries)*100:.1f}%)")
