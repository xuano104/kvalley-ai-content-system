# 智谷 AI 行銷系統運作流與分工（2026-04 定版）

> **所有 agent 必讀**。這是整個系統的唯一分工依據——誰該做什麼、誰該交棒給誰、誰守哪條紅線。
> 配套文件：`./notebooklm-workflow.md`（NotebookLM 共用規則）

---

## 分工矩陣

| Agent | 角色 | 輸入 | 輸出 | NotebookLM 用途 | 紅線 |
|-------|------|------|------|----------------|------|
| **Chloe** | 策略方向 + 最終品質把關 + WP 上架 | 商業目標、市場判斷 | 指令 / 03-ready 採用決定 | — | 她是閘門，不替她預判 |
| **orchestrator** | 總指揮 + 任務分派 | Chloe 指令 | brief → `pipeline/01-queue/`、回報 | 策略前事實查核 | 不寫內容、不替 Chloe 做最終品質判斷 |
| **topic-ideator** | 主題策展 + NotebookLM 守門人 | TA + 方向 | 主題清單（含 persona 審核分數）、維護 `notebooklm-map.md` | 選題前掃訊號、維護對照表、補 source | 產題必過 persona 審；推薦舊題也要列審核分數 |
| **seo-writer** | 文章生產 | brief | v1 → `02-drafts/` → v1.1 定稿 | **寫稿前強制撈引用** | 不編造引用；跳過 research 視為違規 |
| **persona-reviewer** | 審稿品管 | v1 草稿 | 評分 + 前三修改點 | — | 不替 seo-writer 改稿，只給評分與建議 |
| **analytics** | 數據 + 外部訊號 | 指標 / 時段 / 問題 | PDCA、訊號摘要給 orchestrator | 產業對照、外部佐證 | PDCA 結論必須「數據 + NotebookLM 佐證」雙來源 |
| **social / website / video** | 行銷執行 | 主題 + 素材 | 貼文 / 頁面 / 腳本 | 需要可信數字時撈 | 依需求執行，不做策略判斷 |

---

## 標準內容生產鏈

```
Chloe：「這季主打 XX 主題」
   ▼
orchestrator → 呼叫 ideator 選題
   ▼
topic-ideator
   ① 查 NotebookLM 找訊號
   ② 產主題建議
   ③ 強制跑 persona-review skill
   ④ 回報清單（含每題審核分數）
   ▼
orchestrator → 整合成 brief，寫進 pipeline/01-queue/
   ▼
seo-writer
   /write-from-brief
   ├─ /research-topic（NotebookLM 撈 ≥3 個有引用 insight）
   ├─ 按 article-template 寫 v1 → 02-drafts/
   /persona-review（spawn persona-reviewer）
   ├─ 珊珊 25 分制 / 推手 20 分制
   ├─ 不及格自動改 v2（最多 2 輪）
   └─ 套低風險微調 → v1.1
   /ship-to-ready
   └─ SEO checklist + 搬到 03-ready/
   ▼
Chloe 審稿 → WP 上架 → 04-published/
   ▼
social / website / video（配套素材）
   ▼
analytics
   GA4 / GSC 追成效 → NotebookLM 產業對照 → PDCA 回 orchestrator
   ▼
orchestrator 調整下一季策略
```

---

## 自動觸發對應表（誰該主動動手）

| 事件 | 自動觸發 |
|------|---------|
| Chloe 點「我要 X 主題的文章」 | orchestrator → ideator → brief → seo-writer |
| Chloe 點「給我新主題建議」 | orchestrator → ideator（含 persona 審核清單） |
| seo-writer 寫完 v1 | 自動呼叫 persona-reviewer，不用 Chloe 觸發 |
| reviewer 給 >目標分數 | seo-writer 自動套低風險微調 → 03-ready/ |
| reviewer 給不及格 | seo-writer 自動改 v2（最多 2 輪，兩輪不過回 Chloe 討論） |
| 文章上架後 7 天 | analytics 自動拉 GA4/GSC 出 PDCA 給 orchestrator |
| ideator 建新 notebook / 加 source | 同步更新 `notebooklm-map.md`（否則全系統找不到） |

---

## NotebookLM 使用分工（避免重複蒐資料）

| 時機 | 誰做 | Tool |
|-----|------|------|
| 選題前掃訊號 | ideator | `cross_notebook_query` |
| 寫稿前撈引用 | seo-writer | `notebook_query` |
| 策略判斷前查核 | orchestrator | `cross_notebook_query` |
| 競品/產業對照 | analytics | `notebook_query` |
| 補新 source / 建新 notebook | ideator（守門人） | `source_add` / `research_start` |
| 需要一個可信數字 | social / website / video | 先問 seo-writer 有沒有撈過 |

**黃金法則**：一個 agent 撈過的資料，寫進對應 notebook 或文章後，下次其他 agent 直接用。

---

## 三道品管閘門

1. **ideator persona-review**：不及格不進主題清單
2. **seo-writer → persona-reviewer**：不及格自動改 v2
3. **Chloe 最終審**：WP 上架前的人類判斷（品味、風險、時機）

前兩道自動化，第三道是 Chloe 本人。三道都過才見讀者。

---

## 對每個 agent 的一句話原則

- **orchestrator**：我分派，不下手。
- **topic-ideator**：我選題 + 維護 NotebookLM，所有文章的起點在我。
- **seo-writer**：我寫稿，寫之前一定先撈 NotebookLM。
- **persona-reviewer**：我只打分，不改稿。
- **analytics**：我報數 + 對照，不做策略。
- **social / website / video**：我配合文章產素材，不獨立做方向。
- **Chloe**：我做最終決定，品味由我守。

---

## 為什麼這樣分

避免三個失敗模式：
1. **策略與執行混在一起** → 所以 orchestrator 不寫稿，seo-writer 不訂策略
2. **審稿的人同時寫稿會放水** → 所以 persona-reviewer 獨立存在
3. **每個 agent 自己蒐資料** → 所以 NotebookLM 集中、ideator 當守門人

保留 Chloe 的最終閘門，是因為這套系統的品質天花板由她的品味決定，不該由 agent 自動放行。
