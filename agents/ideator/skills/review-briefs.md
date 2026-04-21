---
name: review-briefs
description: Chloe 主動說要寫文章時觸發——ideator 現場從 Sheet 挑候選、生 brief、等 Chloe 審核、依她指示更新 Sheet status
trigger: Chloe 說「幫我看今天可以寫什麼」「幫我找幾篇來寫」「給我看有什麼可以寫的」「我要選題」
---

# Review Briefs 技能

## 觸發條件

Chloe 主動提起要寫文章 / 選題時。**這個 skill 不會定時自動跑，一律由 Chloe 觸發。**

## 完整流程

### 第一步：挑候選（現場做）

1. 讀最新的 `agent/logs/daily-picks-YYYY-MM-DD.md`
   - 如果今天的還沒跑（早於 13:00）或沒檔案：手動跑 picker
   - `cd automation && python3 -m ideator.daily_picker`
2. 取出 N 篇候選（預設 5 篇，Chloe 也可以指定「多挑幾篇」）

### 第二步：為候選現場生 brief

```bash
cd automation && python3 -m ideator.brief_generator <row_1> <row_2> ...
```

- 會寫進 `pipeline/00-review/YYYY-MM-DD/<slug>_row<N>.md`
- **不動 Sheet status**（重要！Chloe 還沒審）

### 第三步：秀給 Chloe

對每份 brief 顯示：
- 編號（#1, #2...）+ Sheet row 號
- 標題、Meta Description
- 目標 TA + 寫作風格
- H2 結構（5 個標題一行）
- 核心痛點 + 讀者收穫

**不要把整份 brief 貼出來**，只秀關鍵資訊讓 Chloe 能快速判斷。

### 第四步：解析 Chloe 的決定

Chloe 的回應可能長這樣：
```
通過 #1
直接寫 #3
#2 暫緩
#4 不要
#5 換一個對珊珊的角度再生
```

逐個 pick 辨識她的意圖：
- 「通過」「要」「寫」→ approve（brief 進 01-queue/，status「Chloe 選定但還沒寫」→ pipeline_sync 推「Brief 完成」）
- 「暫緩」「先不寫」「留著」→ hold
- 「不要」「刪」「捨棄」→ reject
- 「換角度」「重生」「重來」→ regenerate（同時接收新角度指示）

### 第五步：依決定處理

```python
# Python 內部呼叫（給範例）
from ideator.brief_generator import approve_brief, hold_brief, reject_brief, generate_brief
from pathlib import Path

# 通過
approve_brief(row_idx=142, brief_path=Path('.../00-review/2026-04-17/slug_row142.md'))

# 暫緩
hold_brief(row_idx=140)

# 不要
reject_brief(row_idx=141, brief_path=Path('.../00-review/2026-04-17/slug_row141.md'))

# 換角度重生
generate_brief(row_idx=144, extra_angle='Chloe 要求：改成對珊珊的角度，強調 HR 的心理壓力')
# 再秀新 brief 給 Chloe，進入新一輪審核
```

**CLI 快速方式：**

```bash
# 通過（移到 01-queue，status 改「Chloe 選定但還沒寫」→ pipeline_sync 推「Brief 完成」）
python3 -c "from ideator.brief_generator import approve_brief; from pathlib import Path; approve_brief(142, Path('<brief 路徑>'))"

# 暫緩
python3 -c "from ideator.brief_generator import hold_brief; hold_brief(140)"

# 不要
python3 -c "from ideator.brief_generator import reject_brief; from pathlib import Path; reject_brief(141, Path('<brief 路徑>'))"
```

處理完通過的之後**跑一次 pipeline_sync**：
```bash
python3 -m ideator.pipeline_sync
```

### 第六步：回報給 Chloe

```
已處理完畢：
✅ 通過：#1 (Row 144)、#3 (Row 142) → 進 01-queue，status「Brief 完成」
⏸️  暫緩：#2 (Row 143) → brief 留在 00-review，status「暫緩」
❌ 不要：#4 (Row 141) → brief 已刪，status「捨棄」
🔄 換角度：#5 (Row 140) → 已重生，請再看一次

下一步：開新對話叫 seo-writer 寫 #1 #3 的全文。
```

---

## 狀態對照表

| Chloe 的決定 | Brief 檔案去哪 | Sheet status 變什麼 |
|-------------|--------------|-------------------|
| 通過 | `00-review/` → `01-queue/` | **Chloe 選定但還沒寫** → pipeline_sync 後「Brief 完成」 |
| 暫緩 | 留在 `00-review/` | 暫緩 |
| 不要 | 刪除 | 捨棄 |
| 換角度重生 | 覆蓋原 brief（同 row 同檔） | 不動（維持 ideator 推薦） |

---

## 紅線

- **現場生 brief 才會動 Gemini**——Chloe 沒叫你做就不要預先生
- **status 改動一律在 Chloe 明確表態之後**——不要代替她決定
- **「換角度」必須帶 Chloe 的新指示**——她沒給方向就回問她，別自己猜
- 每份 brief 的 `source_url` 永遠是 Sheet 該列的 URL
