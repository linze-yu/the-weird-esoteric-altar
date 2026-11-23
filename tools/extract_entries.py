#!/usr/bin/env python3
"""
从探灵档案库的实体 Markdown 提取「冰山词条」。

用法:
    python3 tools/extract_entries.py <实体目录> <输出 json>
    python3 tools/extract_entries.py wiki/entities/cbaigui site/entries.json

输出字段(对应冰山图):
    title      标题        ← frontmatter title
    tier       层级 1-8    ← 派生:「基本信息」表的「特性」→ 危险/怪异度
    category   分类        ← 派生:「基本信息」表的「种类」→ 9 大类
    tags[]     标签        ← frontmatter tags + 种类 + 朝代
    desc       描述        ← 正文「## 基本介绍」段
    link       外链        ← frontmatter source
    books[]    文献        ← 正文「## 文献资料」段
    path       库内路径    ← 相对 vault 根
    kind/feature/shape/dist/dynasty/world  ← 「基本信息」表的其余列
"""
import re, json, sys
from pathlib import Path
from collections import Counter

FM = re.compile(r'^---\r?\n(.*?)\r?\n---\r?\n(.*)$', re.S)

# ── 冰山分类:从「种类」归到 9 大类(顺序即优先级)──
CATEGORY_RULES = [
    ("ghost",     ["鬼", "僵尸", "饿鬼", "魄", "魂"]),
    ("demon",     ["妖", "精怪", "妖精", "魔", "煞", "邪"]),
    ("beast",     ["异兽", "兽", "妖兽", "龙", "鸟", "虫", "蛇"]),
    ("deity",     ["神", "神兽", "仙", "菩萨", "佛", "精", "灵"]),
    ("human",     ["异人", "人", "尸"]),
    ("object",    ["物", "器", "宝", "符", "书"]),
    ("plant",     ["植物", "木", "花", "草", "树", "菌"]),
    ("phenomena", ["异象", "灾", "天", "象", "兆"]),
]
def to_category(kinds):
    k = (kinds or "").replace(" ", "")
    for cat, kws in CATEGORY_RULES:
        for kw in kws:
            if kw in k:
                return cat
    return "other"

# ── 冰山层级:从「特性」判危险/怪异度(1 浅 → 8 深)──
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
    f = (feat or "").replace(" ", "")
    for t, kws in TIER_RULES:
        for kw in kws:
            if kw in f:
                return t
    return 3

def clean(v):
    v = (v or "").strip()
    return "" if v in ("-", "", "—", "N/A", "null") else v

def section(body, name):
    """取某个 ## 小节的正文"""
    m = re.search(r'^#{2,4}\s*' + re.escape(name) + r'.*$', body, re.M)
    if not m:
        return ""
    rest = body[m.end():]
    nxt = re.search(r'^#{2,4}\s', rest, re.M)
    return rest[:nxt.start()] if nxt else rest

def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    src = Path(sys.argv[1])
    out = Path(sys.argv[2])
    if not src.is_dir():
        print(f"❌ 实体目录不存在: {src}")
        sys.exit(1)

    entries = []
    for p in sorted(src.glob("*.md")):
        raw = p.read_text(encoding="utf-8", errors="replace")
        m = FM.match(raw)
        if not m:
            continue
        fm, body = m.group(1), m.group(2)

        t = re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', fm, re.M)
        title = clean(t.group(1)) if t else p.stem

        def fld(name):
            mm = re.search(r'^\|\s*' + re.escape(name) + r'\s*\|\s*(.*?)\s*\|', body, re.M)
            return clean(mm.group(1)) if mm else ""

        kinds  = fld("种类"); feat = fld("特性"); shape = fld("外形")
        dist   = fld("分布"); dyn  = fld("朝代"); world = fld("世界")

        intro = re.sub(r'\s+', ' ', section(body, "基本介绍")).strip()
        books = [re.sub(r'\s+', ' ', l).strip()
                 for l in section(body, "文献资料").split("\n") if l.strip()][:6]

        src_m = re.search(r'^source:\s*(\S+)', fm, re.M)
        tg_m  = re.search(r'^tags:\s*\[(.*?)\]', fm, re.M)
        tags  = [x.strip().strip('"') for x in tg_m.group(1).split(",")] if tg_m else []
        tags  = [x for x in tags if x not in ("entity", "cbaigui")]

        entries.append({
            "id": p.stem,
            "title": title,
            "tier": to_tier(feat),
            "category": to_category(kinds),
            "tags": tags + ([kinds] if kinds else []) + ([dyn] if dyn else []),
            "desc": intro[:300],
            "link": src_m.group(1) if src_m else "",
            "kind": kinds, "feature": feat, "shape": shape,
            "dist": dist, "dynasty": dyn, "world": world,
            "books": books,
            "path": f"entities/cbaigui/{p.stem}.md",
        })

    if not entries:
        print(f"❌ 从 {src} 提取到 0 条词条 —— 检查目录路径")
        sys.exit(1)

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(entries, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    tiers = Counter(e["tier"] for e in entries)
    cats  = Counter(e["category"] for e in entries)
    withdesc = sum(1 for e in entries if len(e["desc"]) > 20)
    print(f"提取 {len(entries):,} 词条 → {out}")
    print(f"层级分布: {dict(sorted(tiers.items()))}")
    print(f"分类分布: {dict(cats.most_common())}")
    print(f"有描述: {withdesc:,} ({withdesc/len(entries)*100:.1f}%)")

if __name__ == "__main__":
    main()
