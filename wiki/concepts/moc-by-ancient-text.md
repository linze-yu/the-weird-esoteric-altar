---
type: moc
title: MOC · 按古籍
description: 按出处古籍分类的妖怪地图 — 14 个古籍 hub + 引用妖怪列表
created: 2026-07-02
updated: 2026-07-19
tags: [MOC, 古籍, 索引]
scope: 3509+ 妖怪笔记
---

# MOC · 按古籍

> **本 MOC 是 cbaigui 反塌陷整改的核心入口**,把所有妖怪按**出处古籍**分组。

## 18 个古籍 hub (按引用妖怪数降序)

| # | 古籍 | 引用妖怪数 | 朝代 | hub 节点 |
|:-:|:--|:-:|:-:|:--|
| 1 | [[ancient-text-shanhaijing|山海经]] | 232 | 先秦 | 上古神话源头 |
| 2 | [[ancient-text-taipingguangji|太平广记]] | 193 | 北宋 | 妖怪文化集大成 |
| 3 | [[ancient-text-youyang-zazu|酉阳杂俎]] | 111 | 唐 | 唐代笔记代表作 |
| 4 | [[ancient-text-soushenji|搜神记]] | 103 | 东晋 | 志怪小说奠基 |
| 5 | [[ancient-text-taipingyulan|太平御览]] | 81 | 北宋 | 大型类书 |
| 6 | [[ancient-text-shuyiji|述异记]] | 79 | 南北朝 | 神话传说记录 |
| 7 | [[ancient-text-yijianzhi|夷坚志]] | 70 | 南宋 | 个人编纂规模最大 |
| 8 | [[ancient-text-shiyiji|拾遗记]] | 54 | 东晋 | 神话题材 |
| 9 | [[ancient-text-guangyiji|广异记]] | 42 | 唐 | 唐代三大志怪之一 |
| 10 | [[ancient-text-bowuzhi|博物志]] | 41 | 西晋 | 博物学源头 |
| 11 | [[ancient-text-xuanshizhi|宣室志]] | 28 | 唐 | 异梦类题材 |
| 12 | [[ancient-text-youminglu|幽明录]] | 25 | 南北朝 | 刘义庆作品 |
| 13 | [[ancient-text-jisenlu|稽神录]] | 24 | 五代宋初 | 宋初过渡期 |
| 14 | [[ancient-text-xuanzhongji|玄中记]] | 21 | 南北朝 | 郭璞作品 |
| 15 | **[[ancient-text-yiyuan|异苑]]** | 待统计 | 南朝宋 | 晋宋志怪代表作 |
| 16 | **[[ancient-text-youminglu|幽明录]]** | 25 | 南朝宋 | 刘义庆作品（鲁迅辑本） |
| 17 | **[[ancient-text-duyizhi|独异志]]** | 待统计 | 中唐 | 笔记杂俎体 |
| 18 | **[[ancient-text-xuanguailu|玄怪录]]** | 5 | 唐 | 唐代传奇代表作 |

## 阅读路径

**想了解妖怪文化的源头** → 从 [[ancient-text-shanhaijing|古籍-山海经]] 开始
**想了解宋代妖怪集大成** → 从 [[ancient-text-taipingguangji|古籍-太平广记]] 开始
**想了解志怪小说源流** → 晋代 [[ancient-text-soushenji|古籍-搜神记]] → 唐代 [[ancient-text-guangyiji|古籍-广异记]] → 宋代 [[ancient-text-yijianzhi|古籍-夷坚志]]
**想了解博物学传统** → [[ancient-text-shanhaijing|古籍-山海经]] → [[ancient-text-bowuzhi|古籍-博物志]] → [[ancient-text-youyang-zazu|古籍-酉阳杂俎]]

## 跨 hub 主题

- **志怪小说谱系**: [[ancient-text-soushenji|古籍-搜神记]] → [[ancient-text-shiyiji|古籍-拾遗记]] → [[ancient-text-youminglu|古籍-幽明录]] → [[ancient-text-guangyiji|古籍-广异记]] → [[ancient-text-xuanshizhi|古籍-宣室志]] → [[ancient-text-jishenlu|古籍-稽神录]] → [[ancient-text-yijianzhi|古籍-夷坚志]]
- **类书传统**: [[ancient-text-taipingguangji|古籍-太平广记]] + [[ancient-text-taipingyulan|古籍-太平御览]]
- **博物学谱系**: [[ancient-text-shanhaijing|古籍-山海经]] → [[ancient-text-bowuzhi|古籍-博物志]] → [[ancient-text-youyang-zazu|古籍-酉阳杂俎]]
- **笔记传统**: [[ancient-text-shuyiji|古籍-述异记]] + [[ancient-text-shiyiji|古籍-拾遗记]] + [[ancient-text-youminglu|古籍-幽明录]]

## 反塌陷机制

- 每个 hub 节点都有 `related` 字段,反向链接自动建立
- 每个妖怪笔记 frontmatter 都有 `related: ["[[古籍-X]]"]`,自动归类到本 MOC
- 14 个 hub + 4 个 MOC 共同形成「在孤岛上空搭的网」

## Related

- [[moc-by-dynasty|MOC · 按朝代]]
- [[moc-by-type|MOC · 按类型]]
- [[moc-by-region|MOC · 按地域]]
- 全部 hub: [[ancient-text-shanhaijing|古籍-山海经]] / [[ancient-text-taipingguangji|古籍-太平广记]] / [[ancient-text-youyang-zazu|古籍-酉阳杂俎]] / [[ancient-text-soushenji|古籍-搜神记]] / [[ancient-text-shuyiji|古籍-述异记]]