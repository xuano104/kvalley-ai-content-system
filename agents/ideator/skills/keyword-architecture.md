---
name: keyword-architecture
description: 把模糊的主題方向拆成三層關鍵字（主題/角度/證據），確保丟給 NotebookLM 的 query 是「研究題目」不是「關鍵字」。
trigger: ideator 收到種子靈感（從 persona 或 NotebookLM 新料）後的第一步。在 notebook-routing 之前跑。
---

# Keyword Architecture Skill

## 為什麼有這個 skill

NotebookLM 不是 Google。丟「AI 培訓」回傳一坨泛泛之談；丟「為什麼多數企業 AI 培訓在第 6 個月卡住？」回傳可引用的研究與數據。

這個 skill 強制 ideator 把每個種子**拆成三層**，確保 query 有深度。

---

## 三層結構

### Layer A — 主題關鍵字（名詞短語）
**功能：** 對應到哪本 NotebookLM 筆記本
**形式：** 2-4 個字的名詞
**例：**
- ✅「HR 準備度」「中階主管轉型」「組織抗拒」
- ❌「AI 培訓怎麼做」（這是問句，不是關鍵字）
- ❌「關於 AI 的一些想法」（太泛）

### Layer B — 角度問句（真正的 query）
**功能：** 真正丟給 NotebookLM 的提問
**形式：** 完整問句，帶觀點、帶衝突、帶時間/對象條件
**每個主題產出 3 個候選 Layer B，選最犀利的那個當正式 query**

**好的 Layer B 長這樣：**
- ✅「為什麼 HR 在 AI 導入案裡常是最後被找上、卻最早被責怪？」（有衝突、有對象）
- ✅「Josh Bersin 對 2026 HR 角色重塑的預測，和 Gartner 有何不同？」（有對比）
- ✅「中階主管在 AI 轉型中最常被忽略的三個風險是什麼？」（有具體數量要求）

**爛的 Layer B：**
- ❌「AI 對 HR 有什麼影響」（沒觀點、沒衝突）
- ❌「HR 如何使用 AI」（太籠統，可以寫成一本書）

### Layer C — 證據關鍵字（抓引用和數據）
**功能：** 讓文章有 BCG/HBR 感——不是感想，是引用
**形式：** 對 NotebookLM 的具體要求
**例：**
- 「列出 2025 年後關於 HR AI 採用率的三個數據點與原始來源」
- 「找出 WEF Future of Jobs 報告中提到組織抗拒的段落原文」
- 「如果資料中有 Josh Bersin / Gartner / WEF / McKinsey 的觀點，分別列出」

**Layer C 的鐵律：** 至少要求一個「具體數字」+ 一個「權威來源」。

---

## 執行 SOP

對每個種子靈感：

```
種子：「中階主管在 AI 轉型中推不動」
  ↓
Layer A（主題關鍵字）：
  - 中階主管轉型
  - AI 導入瓶頸
  → 對應筆記本：「AI組織變革」「主管培訓」
  ↓
Layer B（角度問句，產 3 選 1）：
  候選 1：中階主管在 AI 轉型中扮演什麼角色？（太泛，略）
  候選 2：為什麼 AI 轉型在第 6 個月卡住？是工具問題還是人？（有衝突，較好）
  候選 3：在企業 AI 導入過程中，中階主管是 AI 轉型失敗的關鍵瓶頸嗎？有哪些數據支持？（★ 選這個）
  ↓
Layer C（證據要求）：
  - 請列出具體數據點、原始來源
  - 中階主管最常見的三個抗拒型態或 pain points
  - 如果資料中有 Josh Bersin、Gartner、WEF、McKinsey 的觀點，請分別列出
```

→ 最終丟進 `notebook_query` 的 query = Layer B + Layer C 組合成一段。

---

## 輸出格式（傳給下一個 skill 的結構）

```yaml
seed: 中階主管在 AI 轉型中推不動
layer_a_keywords:
  - 中階主管轉型
  - AI 導入瓶頸
candidate_notebooks:  # 暫列，由 notebook-routing skill 最終決定
  - AI組織變革
  - 主管培訓
layer_b_query: |
  在企業 AI 導入過程中，中階主管扮演什麼角色？
  有沒有研究或數據指出中階主管是 AI 轉型失敗的關鍵瓶頸？
layer_c_requirements: |
  請列出具體數據點、原始來源。
  中階主管最常見的三個抗拒型態或 pain points。
  如果資料中有 Josh Bersin、Gartner、WEF、McKinsey 的觀點，請分別列出。
```

---

## 失敗模式自我檢查

產出後 ideator 自問：
1. Layer A 關鍵字能不能直接對應到某本筆記本？（不能→重拆）
2. Layer B 有沒有觀點/衝突/對比？（沒有→重寫）
3. Layer C 有沒有要求具體數字+權威來源？（沒有→補）

三個都過才進 notebook-routing。
