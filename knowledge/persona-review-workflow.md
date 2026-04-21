# Persona 審核工作流（全系統共用）

> **所有 agent 必讀。** ideator、seo-writer、persona-reviewer、content-engine、orchestrator 都會用到這條工作流。
> 維護者：ideator（新增規則時以 ideator 為主，但其他 agent 可提 PR）
> 最後更新：2026-04-13

---

## 為什麼有這份文件

Persona 審核分三個時間點發生，每個 agent 負責其中一段。文件存在 `knowledge/` 讓所有 agent 對齊同一套標準，不會各做各的。

---

## 三個審核時機

### 時機 1｜Ideator 產出主題時（入口關）
**負責人：** topic-ideator
**工具：** `agents/topic-ideator/skills/persona-review.md`

**做什麼：**
- 每個新主題產出後，**必跑** Reviewer Mode
  - 珊珊本位：`knowledge/personas/shanshan.md` 四關（開頭 / 信任 / 可行性 / 行動）
  - 推手本位：`knowledge/personas/dt-pusher.md` 四關評分（策略 / 說服 / ROI / 行動，滿分 20，及格 15）
  - 思想領導力：雙視角掃描 + BCG/HBR 感檢查
- 不及格 → 改切角重審（最多 2 輪）→ 仍不及格：先檢查是不是**缺素材**（用 NotebookLM 補料）再重審 → 真的救不回來才換題
- **不及格不進 topics-master.md / Google Sheet**

### 時機 2｜從舊清單推薦給 Chloe 時（抽查關）
**負責人：** topic-ideator（或 orchestrator）

**做什麼：**
- 即使主題是從既有清單挑，**推薦訊息裡必列每題的 persona 審核結果**
- Chloe 要做「挑哪幾篇寫」的決策時，persona 分數是關鍵依據
- 若審核結果久未更新（GSC 趨勢變、persona 痛點更新），補一次輕審並註明重審日期

### 時機 3｜Seo-writer 寫完後（出口關）
**負責人：** persona-reviewer agent

**做什麼：**
- 用完整 Reviewer Mode 過一次全文（不是標題）
- 不及格 → 退回 seo-writer 修改（最多 2 輪）
- 通過 → 進 `pipeline/03-ready/`

---

## Persona Reviewer Mode 出處

| Persona | 檔案 | 段落 |
|---------|------|------|
| HRD 珊珊 | `knowledge/personas/shanshan.md` | 第 114–143 行（四關） |
| 數位轉型推手 | `knowledge/personas/dt-pusher.md` | 第 68–107 行（四關評分，20 分制） |

---

## 推薦訊息標準格式（ideator 交給 Chloe 時）

```
推薦 3 篇：

1. Topic #11 「McKinsey：越逼績效⋯⋯」
   Persona：推手 | 審核：策略✅ 說服✅ ROI🟡 行動✅ → 預估 16/20

2. Topic #13 「HBR：倦怠的主因⋯⋯」
   Persona：珊珊 | 審核：開頭✅ 信任✅ 可行性✅ 行動✅ → 四關全過

3. Topic #15 「$665B AI 投資⋯⋯」
   Persona：推手 | 審核：策略✅ 說服✅ ROI✅ 行動✅ → 19/20
```

---

## 常見失敗模式（產出主題時自我警覺）

| 模式 | 範例 | 為何不及格 |
|------|------|----------|
| 學術腔 | 「HR 在 AI 導入中的結構性位置」 | 珊珊要「我下週能做什麼」 |
| 有觀點沒彈藥 | 「問題不在工具在人」 | 推手要「一句話給老闆」+ ROI 數字 |
| 標題像書名 | 「AI 時代的人才重塑」 | 珊珊掃 H2 時跳過，太泛 |
| 促銷感 | 「三個技巧讓你成為必備 HR」 | Chloe 直接退件（用力過猛） |

---

## 紅線（所有 agent 共同遵守）

1. 主題未過 Persona 審核，不進 `topics-master.md` 或 Google Sheet
2. 推薦給 Chloe 時，**每題都要附 persona 審核分數**，不要讓她自己翻
3. Seo-writer 寫完全文一律過 persona-reviewer 再進 `03-ready/`
4. 任何 agent 修改這份 workflow 規則，要同步更新：
   - `agents/topic-ideator/skills/persona-review.md`
   - 本檔案
