# Ideator Memory（空資料夾，隨使用累積）

這個資料夾會隨著你使用 Ideator Agent 慢慢長出內容。**初始是空的，這是正常的。**

## 預期會累積的檔案

| 檔案 | 內容 | 誰寫 |
|------|------|------|
| `log.md` | 每次會話結束時 append 一行摘要 | Claude（透過 `/save`） |
| `ideator-context.md` | 最近選題的決策脈絡，下次可接續 | Claude |
| `topics-log.md` | 已發想主題清單，避免重複 | Claude |
| `topics-master.md` | 跨 agent 共享的主題總表 | Claude |
| `notebooklm-map.md` | NotebookLM 關鍵字對照表 | Claude 或人工維護 |
| `business-overview.md` | 你公司的業務脈絡（三支柱、服務、活動）| 人工填寫 |
| `topic-selection-rules.md` | 你團隊的選題規則與禁忌 | 人工填寫 |

## 建議怎麼開始

1. 先填 `business-overview.md`——Ideator 選題前會讀這份
2. 先填 `topic-selection-rules.md`——寫下你們的選題原則
3. 其他檔案會隨使用自動累積，不用預先建立
