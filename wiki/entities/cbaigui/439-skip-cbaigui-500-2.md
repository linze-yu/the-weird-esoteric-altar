---
title: cbaigui ID 439 跳过（cbaigui 服务端 500 错误第二次）
description: cbaigui 服务端 500 错误第二次（本会话），无法获取 ID 439 内容，跳过
source: https://cbaigui.com/monster/439
source_type: web
site: cbaigui（纪妖，原名知妖）
captured_date: 2026-07-01

fetch_method: TinyFish Fetch API（curl REST 路径，1 URL serial）
fetch_latency_ms: 4000
format: markdown
raw_url: https://cbaigui.com/monster/439
tags: [cbaigui-439, 跳过, 服务端500, cbaigui_500_error_2]
---

## 跳过原因

```
cbaigui API 响应：
{"results":[],"errors":[{"url":"https://cbaigui.com/monster/439","error":"target_http_error","status":500}]}
```

cbaigui.com 网站对该 URL 返回 HTTP 500 内部服务器错误，无法获取该 ID 的妖怪信息。

按 §1.14 流程失败案例恢复——本会话**第二次**触发 cbaigui 服务端 500（第一次：ID 431）。本会话**不重复抓同一 ID**，以免触发服务器。
