# NotebookLM 研究工作流（全系統共用）

> 所有 agent 在產出內容、做策略判斷、寫報告前，**先查 NotebookLM**。
> 帳號：`open@asia-learning.com`，透過 `notebooklm-mcp` 存取。
> 對照表：`../agents/topic-ideator/memory/notebooklm-map.md`（關鍵字 ↔ notebook）。

---

## 哪些 agent 應該用

| Agent | 用途 |
|-------|------|
| seo-writer | 寫稿前撈引用（Gallup/McKinsey/HBR 等機構數據） |
| topic-ideator | 選題前撈產業訊號與觀點來源 |
| analytics | 競品/產業對照時撈外部視角 |
| orchestrator | 策略判斷前的事實查核 |
| social / website / video | 貼文或腳本需要「一個可信數字」時撈 |

---

## 標準流程（4 步）

### 1. 對照主題選 notebook
開 `agents/topic-ideator/memory/notebooklm-map.md`，找主題對應的 notebook。不確定就 `notebook_list` 列出所有本。

**現有核心 notebook（2026-04）：**
- AI組織變革（15 份）— HR × AI 主題首選，Gallup/Forrester/McKinsey/Bersin
- The AI Cards Guide to Strategic Implementation（19 份）— 企業導入框架
- 主管培訓（9 份）、領導風格（5 份）、企業AI導入（5 份）、職場溝通（4 份）
- 拒絕內耗（2 份）、工程監造與執行流程（共享，1 份）

### 2. 設計查詢
query 必須包含：
- 明確問題（不是關鍵字）
- 要求「具體數字和引用來源」
- 指名期望的機構（HBR、McKinsey、Gallup、WEF、Josh Bersin、Forrester、Gartner 等）

**範例（好）**：
> 員工學 AI 的心理障礙有哪些研究數據？特別是腦科學／壓力／前額葉對學習的影響。請提供具體數字和引用來源。

**範例（壞）**：
> AI 學習障礙

### 3. 撈到有引用的 insight
NotebookLM 會自動附 citations。每條都會標 source_id 與原文片段。
**品質標準**：每篇產出至少 3 個有具名來源的 insight，優先國際機構。

### 4. 融合改寫，不直譯
把 insight 融進自己的語氣、自己的文章結構。不要複製 NotebookLM 的回答段落。

---

## 紅線

- **不可編造 NotebookLM 沒有的引用**。若 notebook 裡沒有，明講 + 選擇處理方式：(a) 用公開科學共識處理，不加引用 (b) 補做 `research_start` 蒐新資料 (c) 刪掉該角度。
- **不可每個 agent 自己蒐資料再存一份**。先查 NotebookLM，沒有再補。
- **auth 錯誤 → 跑 `nlm login`**，不要自行重試。

---

## MCP 工具速查

| Tool | 用途 |
|------|------|
| `mcp__notebooklm-mcp__notebook_list` | 列出所有 notebook |
| `mcp__notebooklm-mcp__notebook_query` | 對單一 notebook 提問（附 citations） |
| `mcp__notebooklm-mcp__cross_notebook_query` | 跨多本搜尋 |
| `mcp__notebooklm-mcp__research_start` | NotebookLM 自己去網路蒐新資料（慢但有 web search） |
| `mcp__notebooklm-mcp__source_add` | 加新 source 到 notebook |

---

## 為什麼這個 workflow 重要

智谷內容的品味標準是「被理性的東西填滿知覺」。NotebookLM 是全系統的「理性資產庫」——一個 agent 撈過的資料，下次其他 agent 可以直接用。不要讓每個 agent 都重新開始蒐資料。

實測結果：seo-writer 在一篇珊珊 TA 文章上，加入 NotebookLM 撈的五個國際引用後，persona-reviewer 評分從預期 22 拉到 24/25。引用密度對文章可信度有直接影響。
