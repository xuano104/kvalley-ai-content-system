產出當週 WBR（Weekly Business Review）並推上 Google Sheet。

週次：$ARGUMENTS（例：W15，沒給就用**上週完整 ISO 週**，不是今天所在的那週）

## 執行步驟

### 1. 確認週次與日期區間
- 週次按 **ISO 週標準**（Mon–Sun）
- 沒給週次 → 用「今天 ISO 週 − 1」（WBR 講的是已結束的上週）
- 日期區間必須是 **嚴格 ISO Mon–Sun（7 天）**，不再 8 天跨週

### 2. 抓數據
- GSC 深度：讀 `../../logs/intel/` 最新的 `*-gsc-deep.md`
- GA4 週報：讀 `../../logs/intel/` 最新的 `*-ga4-weekly.md`
- 檢查：intel 檔的日期區間是否對齊 ISO Mon–Sun？不對齊要在 Summary 備註，**下週要修 friday-weekly-report.py**
- 如果檔案不存在 → 停下來告訴 Chloe「這週 intel 還沒跑，請先執行 friday-weekly-report.py」

### 3. 產生 3 個 CSV（寫到 `/tmp/wbr-<週次>/`，推完自動刪）

**1_Dashboard.csv（Summary）**：
- Headline：一行 insight
- KPI 表（指標 / 本週 / 目標 / 達成率 / 狀態）
  - 主 KPI：AI 引用次數、諮詢送出、進站人數、平均停留、跳出率、內容產出
  - Clicks 為參考指標
- 本週關鍵洞察（最多 3 點）
- 本週需決策（帶選項 + 推薦）

**2_Variance.csv（Deep-dive）**：
- 當週只挖一件事
- 現象 / 假設（高/中/低信心）/ 下週驗證行動

**3_Actions.csv — Chloe-only 規則（重要！）**：
- **只列 Owner = Chloe 的事項**——其他 agent 的任務由你**直接派單到 orchestrator inbox**，不列在此
- 派單路徑：`../../agents/orchestrator/tasks/inbox/<agent>/YYYY-MM-DD_<name>.md`
  - Analytics 自派任務：`inbox/analytics/`
  - Content Engine：`inbox/content-engine/`
  - Website：`inbox/website/` | Social：`inbox/social/` | Video：`inbox/video/`
  - 每個 brief 含：目標、步驟、驗收、來源（本 WBR）、Due
- Actions CSV 尾行補一列「備註」：簡述有哪些事已派到其他 agent，讓 Chloe 知道但不用管

### 4. 文章標題規則
- 不用 `/24613` 這種 slug，一律用文章標題，不知道標「（待查）」

### 5. 推 Sheet + 匯出 md
```bash
python3 agents/analytics/scripts/push_wbr_to_sheet.py <週次> /tmp/wbr-<週次>
python3 agents/analytics/scripts/export_wbr_md.py <週次>
rm -rf /tmp/wbr-<週次>
```
結果：
- Shared Drive「智谷 WBR」新增 Sheet `智谷 WBR W<週次> (YYYY-MM-DD ~ YYYY-MM-DD)`，3 分頁 `Summary / Deep-dive / Actions`（無週次前綴）
- 本地 `reports/智谷 WBR W<週次> (...).md`
- Shared Drive ID：`0AOc_siqQ_zJzUk9PVA`

### 6. 回報格式
- Sheet 連結（該週 Sheet 的 URL，不是資料夾）
- 本地 md 路徑
- 本週最需要 Chloe/Jimmy 注意的 1 件事
- 已派發到其他 agent 的任務清單（brief 路徑）

## 寫作風格規範
- 每格 ≤ 30 字
- 不用「THE ONE THING」「本週一句話」這種包裝詞
- Title 就是 insight（不要寫「KPI Dashboard」，寫「Clicks -35%，X 原因」）
- 狀態用 🔴🟡🟢⚫ emoji

## 不做
- 不改已發佈文章的 Meta Title（SEO 行動已停）
- 不追關鍵字排名為主要 KPI
- 不把 Raw data 推上 Sheet
- 不把其他 agent 的任務塞進 Actions 分頁給 Chloe——直接派單
