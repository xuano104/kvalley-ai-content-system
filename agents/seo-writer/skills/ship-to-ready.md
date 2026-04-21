---
name: ship-to-ready
description: 定稿搬家。SEO 規範最後把關 + 移到 03-ready/ + 更新 log。
trigger: 草稿通過 persona-review 微調後。
---

# 定稿搬家 Skill

## 執行流程

### Step 1：最後把關（checklist）

| 檢查項 | 標準 |
|--------|------|
| 字數 | 1200–2000 |
| H1 | ≤60 字、含主關鍵字 |
| Meta Title | ≤60 字 |
| Meta Description | 120–155 字、含主關鍵字、有 CTA hook |
| 主關鍵字出現 | 標題 + 首段 + ≥2 H2 + 結論 |
| H2 數量 | 3–5 個 |
| H2 品質 | 每個能獨立站成一句有價值的話（Chloe 標準） |
| 內連 | ≥1 個、markdown 格式 `[文字](/url/)` 正確 |
| CTA | 明確、不促銷感 |
| Persona 審核 | 已過關（分數記錄在內） |

任何一項不過 → **不搬、回報要修什麼**。

### Step 2：搬家
- 從 `../../pipeline/02-in-progress/` 複製到 `../../pipeline/03-ready/`
- 檔名拿掉 `-vN`，用乾淨版（例：`2026-04-13-brain-science-article.md`）
- 原 draft 保留在 02-in-progress/（作為版本歷史）

### Step 3：更新 log
追加一行到 `./memory/rewrites-log.md`：
```
YYYY-MM-DD | [標題] | TA: [珊珊/推手] | Persona 評分: X/25 | 路徑: 03-ready/xxx.md
```

### Step 4：回報 Chloe
一行：「[標題] 已進 03-ready/，評分 X/25，可上 WP。」

## 紅線
- 沒跑過 `/persona-review` 不能搬
- H2 品質 check 要自己嚴格——Chloe 先掃 H2，這是她的第一道閘門
- 搬之後不再改 03-ready/ 的檔（要改回到 02-drafts/ 重走流程）
