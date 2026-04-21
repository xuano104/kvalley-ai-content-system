# Analytics Memory（空資料夾，隨使用累積）

這個資料夾會隨著你使用 Analytics Agent 慢慢長出內容。**初始是空的，這是正常的。**

## 預期會累積的檔案

| 檔案 | 內容 | 誰寫 |
|------|------|------|
| `log.md` | 每次會話結束時 append 一行摘要 | Claude |
| `analytics-log.md` | 已分析過的文章、追蹤中的指標 | Claude |
| `preferences.md` | 你關心的指標、KPI、回報偏好 | Claude |

這裡的記憶讓 Agent 記得「上次我已經分析過這篇文章的什麼指標」，避免重複工作。
