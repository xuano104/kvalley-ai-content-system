# 智谷圖片 Prompt 風格指南
最後更新：2026-03-21
標竿來源：`pipeline/02-in-progress/2026-03-13_用AI反而更累_v4.md`（Section 圖 1 & 圖 2）

> 所有文章的圖片 prompt，無論封面或內文，都以這份指南為標準。
> 這不是攝影棚商業照的語言，是 SWPA（Sony World Photography Awards）等級的敘事攝影。

---

## 01 總體風格定義

**必須具備的三個核心元素：**

1. **攝影等級**：Sony World Photography Awards (SWPA) award-winning level photograph
2. **影像質感**：cinematic 35mm film quality（有顆粒感、有溫度，不是數位乾淨感）
3. **敘事核心**：每張圖要有一句「Narrative Core」——這張圖在說什麼故事？情緒是什麼？

---

## 02 Prompt 結構（必須完整）

每張 bananapro/Midjourney/AI 圖片 prompt 都要依序包含：

```
**Style:** [攝影等級 + 影像質感 + 整體調性]

**Subject:** [主角：族裔、年齡段、角度、服裝、表情/肢體語言]

**Key Narrative Elements:**
* [道具 1：具體物件 + 它在畫面裡代表什麼]
* [道具 2：背景細節、空間元素]

**Background:** [場景、時間、燈光環境]

**Composition:** [景別、角度、景深]

**Narrative Core:** [一句話說明這張圖的情緒真相]
```

---

## 03 主角設定原則

- **族裔**：以東亞職場人物（East Asian professional）為主，**偶爾可用西方人**——特別是段落引用西方案例／公司／研究（Duolingo、Klarna、Kraft Heinz、Palantir、Gallup、HBR 等）時，用西方主角更呼應內容來源。每篇 6 張裡有 1-2 張西方人物是合理節奏
- **角度**：side-profile（側臉）、three-quarter profile（四分之三側面）、silhouette（背影）
  → **絕對不要正面大頭照**
- **表情**：情緒要有層次——不是誇張哭泣或大笑，是那種「內在狀態外溢出來的瞬間」
- **服裝**：職場感但有個性（結構感西裝、剪裁感牛仔夾克、細紋毛衣）
  → 不要制式西裝+白襯衫
- **動作必須明確**（2026-04-17 Chloe 新增）：主角要在做一個觀眾秒讀的敘事動詞（放下、推開、指、跪、封、轉身）。光「坐著看」「站著想」會讓讀者不知道圖片在表達什麼

---

## 04 光線設定原則

**核心技法：雙光源製造張力**

| 光源 1（主） | 光源 2（副） | 傳達的張力 |
|-------------|-------------|-----------|
| 暖光桌燈 amber warm | 螢幕冷藍光 cool screen glow | 人性 vs. 數位 |
| 遠處暖色窗光 | 冷藍灰辦公室環境光 | 希望 vs. 現實 |
| 黃金時刻日落光 | 筆電螢幕 AI 介面光 | 願景 vs. 當下 |

→ 不要只有一種光源，光線的對比本身就是敘事

---

## 05 色調指引

**智谷文章圖片的典型色調（三種）：**

| 情境 | 主色調 | 說明 |
|------|--------|------|
| 疲憊/壓力類 | warm grey + dark navy + dim gold | 沉靜耗盡感，Monocle 雜誌美學 |
| 觀望/抉擇類 | cool grey-blue (desaturated) + single amber accent | 懸而未決，時間靜止感 |
| 願景/執行類 | rich warm gold + deep brown + cool screen highlight | 雄心 + 沉穩，高端智識感 |

---

## 06 空間與構圖原則

- **景別**：medium close-up（胸部以上）適合情緒類；wide shot（全景）適合孤獨/抉擇類
- **景深**：淺景深（shallow depth of field）為主——主角清晰，背景虛化
- **構圖邏輯**：空間要傳達心理狀態
  - 人物很小、空間很大 → 孤立感、壓力感
  - 人物充滿畫面 → 聚焦感、存在感
  - 線條（桌邊、窗框）引導視線到主角 → 命運感、不可迴避感

---

## 07 視覺隱喻原則

**允許使用的隱喻方式：**
- 輕煙/熱氣（暗示腦過載，不是真的冒煙）
- 未被觸碰的工具（筆電開著但沒人用 → 員工在觀望）
- 半空的咖啡杯（已進入某種狀態但還沒結束）
- 窗外世界繼續前進，人在室內靜止

**絕對不要出現的元素：**
- ❌ 卡通或漫畫風格
- ❌ 藍色科技光暈（Matrix 感、科幻感）
- ❌ 機器人、AI icon、電路板
- ❌ 高飽和度、廣告感色調
- ❌ 人物看向鏡頭（打破第四面牆感）

---

## 08 每張圖必須附的中文精簡提示語

在完整英文 prompt 之後，提供一段給 bananapro 的**中文精簡提示語**（50–80 字），格式如下：

```
> Section 圖 X：[主角描述]，[姿勢/動作]，[關鍵道具]，[背景/場景]，[光線]，[色調]，[景別/角度]，35mm 電影底片質感，SWPA 攝影風格，[情緒/氛圍關鍵詞]
```

---

## 09 Narrative Core 怎麼寫

這是整個 prompt 最重要的一句話。它說明這張圖的「情緒真相」。

**公式**：`[主角做了/正在經歷什麼] + [這張圖想讓讀者感受到什麼]`

**標竿範例：**
> "Three tools amplify. Five tools fragment. This is the precise moment when technology stops serving its user — and starts consuming her."

> "Employees don't refuse openly. They wait. This image captures the silence that HR leaders must learn to read — before it becomes disengagement."

---

## 10 配圖建議：每篇文章的標準配置（2026-04-17 Chloe 更新）

**每篇文章配 1 張封面 + 每個 H2 一張。** 五個 H2 的文章配 6 張，不是舊版的 3 張。

| 圖片 | 功能 | 規則 |
|------|------|------|
| 封面（Hero） | 吸引點擊、傳達文章基調 | **必須有人**。要有高度（Ralph Lauren old money 那種知識感）+ 一點點戲劇化。不是純抽象環境感，也不是過度衝突感 |
| H2-1 圖 | 對應第一個核心論點 | 優先有人，情緒清晰 |
| H2-2 圖 | 對應第二個核心論點 | 優先有人，可用背影/側影 |
| H2-3 圖 | 對應第三個核心論點 | 優先有人。若該段是純數據/框架/概念，內容真的不適合搭配人物時，可走環境/物件/場景隱喻——不要為了「都有人」硬塞 |
| H2-4 圖 | 對應第四個核心論點 | 同上 |
| H2-5 圖 | 對應第五個核心論點（通常是行動建議） | 同上 |

**生成流程：** 先生一篇驗風格（Chloe 掃過確認）再 batch 其他篇。不要一次跑完整批然後發現風格要改。
