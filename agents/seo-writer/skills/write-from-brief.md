---
name: write-from-brief
description: 從 01-queue/ 的 brief 到 02-in-progress/ v1 一鍵完成。自動串 research-topic + article-template + SEO 規範。
trigger: 用戶說「寫某某 brief」「把 Article X 寫出來」時。
---

# Brief → v1 草稿 Skill

## 執行流程（嚴格順序）

### Step 1：讀資料
- brief：`../../pipeline/01-queue/<指定檔>`
- 黃金範本：`../../knowledge/article-template.md`
- TA persona：`../../knowledge/personas/{shanshan|dt-pusher}.md`（依 brief 指定）
- 內連對照：`../../knowledge/sitemap-links.md`

### Step 2：跑 `/research-topic`
強制跑。撈到的引用清單記在腦中，寫稿時融入。

### Step 3：寫 v1
- 依 brief 的 H2 骨架
- Chloe 三個品質問題過一遍（填滿知覺、H2 獨立站得住、沒有促銷感）
- SEO 規範全過：字數 1200–2000、主關鍵字在標題/首段/≥2 H2/結論、Meta 120–155 字、≥1 內連、CTA

### Step 4：存檔
路徑：`../../pipeline/02-in-progress/YYYY-MM-DD-<slug>-v1.md`
命名用 brief 的主題英文 slug（例 `brain-science-article-v1.md`）。

### Step 5：回報
一行摘要：「已寫完 [標題]，NotebookLM 撈了 X 個引用，SEO 規範全過。要跑 /persona-review 嗎？」

## 紅線
- 不可跳過 `/research-topic`（就算感覺題目很熟）
- 內連用 `[文字](/url/)` 正確 markdown 順序
- Meta Description 必含主關鍵字 + CTA
