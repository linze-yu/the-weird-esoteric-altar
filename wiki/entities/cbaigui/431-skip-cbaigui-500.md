---
title: cbaigui ID 431 跳过（cbaigui 服务端 500 错误）
description: cbaigui 服务端 500 错误，无法获取 ID 431 内容，跳过本 ID
source: https://cbaigui.com/monster/431
source_type: web
site: cbaigui（纪妖，原名知妖）
captured_date: 2026-07-01

fetch_method: TinyFish Fetch API（curl REST 路径，1 URL serial）
fetch_latency_ms: 4000
format: markdown
raw_url: https://cbaigui.com/monster/431
tags: [cbaigui-431, 跳过, 服务端500, cbaigui_500_error]
---

## 基本属性（cbaigui 元信息）

| 字段 | 内容 |
|:--|:--|
| **名字** | 未知（cbaigui 500 错误） |
| **种类** | 未知 |
| **特性** | 未知 |
| **朝代** | 未知 |

## 跳过原因

```
cbaigui API 响应：
{"results":[],"errors":[{"url":"https://cbaigui.com/monster/431","error":"target_http_error","status":500}]}
```

cbaigui.com 网站对该 URL 返回 HTTP 500 内部服务器错误，无法获取该 ID 的妖怪信息。

按 §1.14 流程失败案例恢复——本会话已失败 1 次 30s 超时（ID 427）后恢复 + 1 次服务端 500（ID 431）。本会话**不重复抓同一 ID**，以免触发服务器。
