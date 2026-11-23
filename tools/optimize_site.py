#!/usr/bin/env python3
"""
优化冰山图站点产物:
  ① 字体子集化(TTF → WOFF2,只保留页面实际用到的字)
  ② 数据分层(entries.json → data/tier{1..8}.json + data/index.json)

用法:
    PYTHONPATH=/opt/data/python-packages python3 tools/optimize_site.py <site_dir> <entities_json> <font_src>

在 GitHub Actions 里:
    python3 tools/optimize_site.py site site/entries.json site/NotoSansSC.ttf
"""
import os, re, sys, json, gzip
from pathlib import Path
from collections import defaultdict

SITE = Path(sys.argv[1] if len(sys.argv) > 1 else "site")
ENTRIES = Path(sys.argv[2] if len(sys.argv) > 2 else SITE/"entries.json")
FONT_SRC = Path(sys.argv[3] if len(sys.argv) > 3 else SITE/"NotoSansSC.ttf")
FONT_OUT = SITE/"NotoSansSC.woff2"
DATA = SITE/"data"
DATA.mkdir(parents=True, exist_ok=True)

print("════════ ① 读词条 ════════\n")
entries = json.load(open(ENTRIES, encoding="utf-8"))
print(f"  {len(entries):,} 条")

print("\n════════ ② 收集用字 ════════\n")
UI = ("怪谈冰山图探灵数据源词条层级分类文献搜索随机深度轴紧凑设置清除全部显示隐藏排序默认"
      "访问来源关闭描述水面上水下深林常规精怪变化异端灾异害人死丧疫毒色欲蛊惑食人噬命寻常草木"
      "器物祥瑞守护妖异兽鬼神人植物异象未归类所有共条正在加载更多展开收起有链接无描述最新需补充"
      "复制版权使用条款隐私说明继续即表示同意本站社区共建设览收藏评论点赞背景纯黑液态标题全文"
      "模糊精确返回首页历史今天书籍手动中文字体加载失败请检查网络本地服务器首次访问需要一些时间"
      "向下滚动越深越黑点击词条打开详情滚轮缩放拖拽平移筛选模式随机按钮字体字号错落排版偏移"
      "导出导入清空数据排序声音响起范围内没有匹配的词条这个层级没有匹配的词条返回顶部"
      "第层浅深常规底座核心外层最深处载入中")
chars = set(UI)
chars |= set("0123456789.·—…、，。！？：；（）「」《》【】/\\|-_+=<>%&#@ 　")
for e in entries:
    for k in ("title","desc","kind","feature","shape","dist","dynasty","world"):
        v = e.get(k)
        if isinstance(v,str): chars |= set(v)
    for t in (e.get("tags") or []): chars |= set(str(t))
    for b in (e.get("books") or []): chars |= set(str(b))
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
print(f"  TTF   {orig:>10,} B")
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

print("\n════════ ⑤ 清理中间产物 ════════\n")
for f in ["entries.json"]:
    p = SITE/f
    if p.exists():
        p.unlink(); print(f"  删 {f}")
print("\n  ✅ 完成")
