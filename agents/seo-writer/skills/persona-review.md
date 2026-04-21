---
name: persona-review
description: 呼叫 persona-reviewer agent 審稿並自動套用低風險微調。
trigger: 草稿寫完後、搬到 03-ready/ 之前。
---

# Persona 審核 Skill

## 執行流程

### Step 1：判斷審核模式
- brief TA = 珊珊 → 珊珊五關（滿分 25，及格 18，目標 22+）
- brief TA = 數位轉型推手 → 推手四關（滿分 20，及格 15，目標 17+）
- 思想領導力 → 雙視角掃描

### Step 2：Spawn reviewer
用 `Agent` 工具（`subagent_type: general-purpose`），prompt 必含：
- 指定模式（珊珊 / 推手 / 雙視角）
- 要求讀 `agents/persona-reviewer/CLAUDE.md`
- 待審檔案完整路徑
- brief 路徑
- 輸出：五關分數 + 總分 + 前三修改點 + 是否建議改 v2
- 報告 400 字內

### Step 3：回報 Chloe + 問下一步
顯示分數與前三修改點。問：
- 全過且 >目標：直接套微調定稿？
- 及格但有漏洞：要改還是先定稿？
- 不及格：改 v2（最多 2 輪，2 輪不過就回頭討論角度）

### Step 4：套微調（用戶同意後）
**可自動套**：
- 內連格式 markdown 順序
- Meta 字數 / CTA 補上
- 明確的一句話補充（例：資安安撫句）

**不可自動套，要先討論**：
- H2 標題改寫
- 整段重寫
- 論點改變

## 紅線
- 不能用 seo-writer 自己審自己的稿——必須用 Agent 呼叫獨立 reviewer
- 微調後要記錄改了什麼（v1.1 的改動清單）
