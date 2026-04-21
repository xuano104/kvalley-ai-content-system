---
name: research-topic
description: 寫稿前必跑。從 NotebookLM 撈出 3-5 個有引用來源的 insight，當作文章的事實彈藥。
trigger: 開始寫新文章前、從 01-topics/ 讀到 brief 後的第一個動作。
---

# NotebookLM 研究撈取 Skill

## 為什麼有這個 skill

seo-writer 如果自己憑經驗寫，容易「有觀點沒證據」。
NotebookLM 已經有智谷全系統整理好的研究庫——不用再自己蒐資料，直接撈有引用的 insight 融進文章。

## 執行流程

### Step 1：確認主題 → 選 notebook
1. 讀 brief 的主關鍵字 + H2 結構
2. 對照 `../topic-ideator/memory/notebooklm-map.md` 找到對應 notebook
3. 若不確定 → `mcp__notebooklm-mcp__notebook_list` 列出所有本

### Step 2：下查詢
針對文章的核心論點設計 query，必須包含：
- 「請提供具體數字和引用來源」
- 指名期望看到的機構（HBR、McKinsey、Gallup、Gartner、WEF、Josh Bersin、Forrester 等）
- 請 NotebookLM 標注引用（tool 會自動附 citations）

主 notebook 查不夠 → 用 `mcp__notebooklm-mcp__cross_notebook_query` 跨本搜。

### Step 3：整理成「可引用清單」
輸出格式（給寫稿時直接套）：

```
## NotebookLM 撈到的引用（供文章融入）

1. **[機構 + 年份]**：[數據 / 觀點]
   - 來源：[source_id 或論文名]
   - 可用在：[哪個 H2 / 哪個論點]

2. ...
```

**品質標準**：至少 3 個有具名來源的 insight，優先國際機構。

### Step 4：誠實標注「沒撈到」的部分
若 brief 要求的某類研究（例：Huberman 腦科學）NotebookLM 裡沒有直接來源——**明講**，不要編造引用。作者可選擇：
(a) 用公開科學共識處理（不加引用）
(b) 補做 `research_start` 補資料
(c) 刪掉該角度

## 紅線
- 不可編造 NotebookLM 沒有的引用
- 不可直接翻譯 NotebookLM 的回答——要融合改寫
- auth 錯誤 → 提示跑 `nlm login`，不自行重試
