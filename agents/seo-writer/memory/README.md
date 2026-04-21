# SEO Writer Memory（空資料夾，隨使用累積）

這個資料夾會隨著你使用 SEO Writer Agent 慢慢長出內容。**初始是空的，這是正常的。**

## 預期會累積的檔案

| 檔案 | 內容 | 誰寫 |
|------|------|------|
| `log.md` | 每次會話結束時 append 一行摘要 | Claude（透過 `/save`） |
| `rewrites-log.md` | 已處理的文章清單，避免重複 | Claude |
| `preferences.md` | 你對寫作風格、配圖、SEO 的偏好 | Claude |

其他 memory 檔案會隨使用自動累積，不用預先建立。
