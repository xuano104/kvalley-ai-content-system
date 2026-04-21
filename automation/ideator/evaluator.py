"""用 Gemini 評估 Sheet 中 status 為空的列，自動填 D-H"""
import json
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from google import genai

from .common import (
    COL_DATE, COL_KEYWORDS, COL_STATUS, COL_URL,
    SHEET_NAME, SPREADSHEET_ID,
    get_sheets_service, read_all_rows, update_row_fields,
)
from .fetcher import fetch_title_and_text

_REPO_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_REPO_ROOT / 'automation' / '.env')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# 由 LaunchAgent com.kvalley.notion-scan 每日 09:15 更新
# ideator 13:00 跑評估時讀這份，確保選題對齊當前業務
ACTIVITIES_FILE = Path(os.getenv('KVAI_ACTIVITIES_FILE',
    _REPO_ROOT / 'knowledge' / 'kv-key-activities.md'))

USER_OPTIONS = ['珊珊', '推手', '跨 TA', '不適合']

PRODUCT_OPTIONS = [
    'AI-Phase 0 免費診斷', 'AI-Phase 1 流程透視', 'AI-Phase 2 代建',
    'AI-Phase 3 共建', 'AI-Phase 4 自建', 'AI-卡牌工作坊', 'AI-產業 Demo',
    'AI-黑客松', 'AI-AI 導入講座系列', 'AI-RPA 自動化', 'AI-HR AI RPA',
    'AI-智慧工廠', 'AI-微型企業補助課程', 'AI-Profet-AI 機器學習實戰營',
    '管理-策略共識營 (OKR/OGSM)', '管理-績效管理/面談',
    '管理-中高階主管培訓 (MPT)', '管理-基層主管培訓 (TWI)',
    '管理-領導力發展', '管理-MBTI', '管理-問題分析與解決',
    '管理-服務禮儀/稽核', '管理-銀行保險業培訓', '管理-Chat 世代領導者密碼',
    '軟技能-溝通共情', '軟技能-協作', '軟技能-正向語言',
    '軟技能-團隊合作', '軟技能-拒絕內耗',
    '跨產品', '不適合',
]

STATUS_EVAL = {
    'recommend': 'ideator 推薦',
    'observe': 'ideator 觀察',
    'reject': 'ideator 不推薦',
}

PROMPT_TEMPLATE = """你是智谷網絡的選題引擎。請評估這篇文章對智谷的內容策略價值。

## 智谷業務（記住才能判斷）

智谷是 B2B 企業培訓 + AI 顧問公司。三大支柱：
1. **AI 顧問**：五階段服務（診斷→流程透視→代建→共建→自建）、卡牌工作坊、產業 Demo、智慧工廠、HR AI RPA、AI Talk 系列
2. **管理培訓**：策略共識營(OKR/OGSM)、績效管理、主管培訓(MPT/TWI)、領導力、MBTI、服務禮儀
3. **辦公室軟技能**：溝通、協作、正向語言、團隊合作、拒絕內耗

## ★ 智谷正在跑的活動（業務對齊最關鍵）

以下是從公司 Notion「公司關鍵經營活動」當日同步的內容——這是公司**現在正在推**的事。
評估文章時要優先想：這篇內容能不能直接支撐下面任何一場活動的宣傳、預熱、回顧、或素材？

{activities_context}

**若文章主題能明確對應某場活動** → status 偏 recommend、title 往活動角度包裝、reason 要點名對應哪場活動。
**若文章有趣但跟所有活動都無關** → 要嚴格得多（往 observe 或 reject 靠）。寧可少選、不要讓選題跟業務脫節。

## 兩個 TA persona

- **珊珊** = HRD / HR Manager / 教育訓練專員，30-45 歲女性
  關心：員工培訓、AI 落地、HR 數位化、不被取代焦慮、課後實踐率
- **推手** = 數位轉型推手 = 總經理 / 副總 / 技術長 / 營運長，40-55 歲
  關心：組織轉型、ROI、戰略視角、跟老闆說的語言彈藥

## 文章資訊

- URL：{url}
- NotebookLM 主題標籤：{notebook_keyword}
- 抓到的頁面標題：{fetched_title}
- 頁面內容前段（最多 3000 字）：
---
{fetched_text}
---

## 你的任務

輸出 JSON（只回 JSON，不要其他文字）：

```json
{{
  "search_terms": ["主關鍵字", "次關鍵字1", "次關鍵字2"],
  "status": "recommend|observe|reject",
  "user": "珊珊|推手|跨 TA|不適合",
  "product": "從產品清單選一個精準的",
  "title": "建議的繁中文章標題（10-25 字，會吸引讀者點擊）",
  "reason": "一句話說明為什麼這樣判斷"
}}
```

## 評估規則

- **recommend**：主題明確、有智谷可發揮的角度、TA 會搜尋、有具體案例或數據
- **observe**：主題相關但素材不夠完整 / 可以等更多資訊
- **reject**：跟智谷三支柱無關 / 已過時 / 太技術 / 太廣泛 / 純產品介紹

## 重要！避免偷懶

**「跨 TA」和「跨產品」是最後手段，不是預設選項。**

- user：絕大多數文章只打中一個 TA。HR/培訓/員工發展類 → 珊珊；策略/ROI/組織轉型類 → 推手。**只有當文章內容真的同時深入觸及兩個角色的關切，才選「跨 TA」。** 如果不確定，選更接近的那個，不要選跨 TA。
- product：從 31 個選項裡挑**最精準**的一個。例如：
  - 文章在講 OKR/KPI/目標管理 → 「管理-策略共識營 (OKR/OGSM)」
  - 文章在講主管如何帶人 → 「管理-中高階主管培訓 (MPT)」或「管理-領導力發展」
  - 文章在講 HR 自動化 → 「AI-HR AI RPA」
  - 文章在講 AI 培訓怎麼做 → 「AI-卡牌工作坊」（優先）；只有真的在講「公開講座」才選「AI-AI 導入講座系列」
  - **警告：「AI-AI 導入講座系列」近期被選過頭。** 除非文章主題真的是「企業 AI 導入講座」否則不要選這個——優先選更具體的：HR AI RPA、智慧工廠、卡牌工作坊、Phase 1 流程透視 等。
  - 文章在講製造業數位轉型 → 「AI-智慧工廠」
  - **不要亂選「跨產品」作為偷懶出口。** 只有文章真的涵蓋多個產品線才選。

## search_terms 規範

- 最多 5 個，繁體中文，3-8 字
- 第一個是主關鍵字（最重要）
- 對應台灣讀者會 Google 的詞
- 避免：英文、太廣（「AI」「管理」）、太長句子

## 產品清單（product 必須從以下挑，不可自創）

{products}

## 禁忌（遇到直接 reject）

- ChatGPT 指令大全 / Prompt 教學（已過時）
- AI 工具比較 / AI 工具推薦（不是智谷定位）
- 純技術文（API、LLM、token、embedding）
- 太廣泛（「AI 的未來」「數位轉型趨勢」）
- 純產品發表新聞（沒有深度分析）
"""


def get_client():
    if not GEMINI_API_KEY:
        raise RuntimeError('找不到 GEMINI_API_KEY')
    return genai.Client(api_key=GEMINI_API_KEY)


def load_activities_context() -> str:
    """讀取 knowledge/kv-key-activities.md（Notion 每日同步）。
    檔案不存在或讀取失敗時回傳 fallback 說明，不讓評估流程中斷。"""
    try:
        if not ACTIVITIES_FILE.exists():
            return '（活動同步檔不存在，評估時請以三支柱原則判斷業務對齊）'
        text = ACTIVITIES_FILE.read_text(encoding='utf-8')
        # 過長就截——實務上 210 行內沒問題，但保險
        if len(text) > 8000:
            text = text[:8000] + '\n…（截斷，僅取前段）'
        return text
    except Exception as e:
        return f'（讀取活動檔失敗：{e}，評估時請以三支柱原則判斷業務對齊）'


def extract_title_from_url(url: str) -> str:
    """從 URL 推測標題（簡單啟發式：取 path 最後一段）"""
    try:
        parts = url.rstrip('/').split('/')
        return parts[-1].replace('-', ' ').replace('_', ' ')
    except Exception:
        return url


def evaluate_one(client, url, notebook_keyword, activities_context=None) -> dict:
    """評估一筆，回傳 dict（search_terms, status, user, product, title, reason）"""
    fetched_title, fetched_text = fetch_title_and_text(url)
    if not fetched_title:
        fetched_title = extract_title_from_url(url)
    if not fetched_text:
        fetched_text = '（無法抓取內容，僅根據 URL 與 notebook 主題判斷）'

    if activities_context is None:
        activities_context = load_activities_context()

    prompt = PROMPT_TEMPLATE.format(
        url=url,
        notebook_keyword=notebook_keyword or '（未分類）',
        fetched_title=fetched_title,
        fetched_text=fetched_text,
        products='\n'.join(f'  - {p}' for p in PRODUCT_OPTIONS),
        activities_context=activities_context,
    )

    resp = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
    )
    text = resp.text.strip()
    # 移除 markdown code fence
    text = re.sub(r'^```(?:json)?\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    return json.loads(text)


def format_search_terms(terms) -> str:
    """list/str → 換行分隔（最多 5 個）"""
    if isinstance(terms, str):
        items = [t.strip() for t in re.split(r'[,，\n]', terms) if t.strip()]
    elif isinstance(terms, list):
        items = [str(t).strip() for t in terms if str(t).strip()]
    else:
        items = []
    # 去重保留順序
    seen = set()
    unique = []
    for t in items:
        if t not in seen:
            seen.add(t)
            unique.append(t)
    return '\n'.join(unique[:5])


def normalize_user(value) -> str:
    """Gemini 沒給或無法對應 → 回空字串（不幻覺）"""
    if not value:
        return ''
    v = str(value).strip()
    if v in USER_OPTIONS:
        return v
    # 寬鬆對應（只接受明確訊號，不猜）
    if '珊' in v:
        return '珊珊'
    if '推' in v or '轉型' in v:
        return '推手'
    if '跨' in v:
        return '跨 TA'
    return ''


def normalize_product(value) -> str:
    """Gemini 沒給或無法對應 → 回空字串（不幻覺）"""
    if not value:
        return ''
    v = str(value).strip()
    if v in PRODUCT_OPTIONS:
        return v
    # 模糊比對（只在有明確包含關係時對應）
    for p in PRODUCT_OPTIONS:
        if v in p or p in v:
            return p
    return ''


def evaluate_pending(limit=None) -> tuple:
    """評估 status 為空的列。回傳 (details, errors)；details 為 list of dict"""
    service = get_sheets_service()
    rows = read_all_rows(service)
    if not rows:
        return [], []

    client = get_client()
    activities_context = load_activities_context()  # 本輪只讀一次，所有列共用
    details = []
    errors = []

    for idx, row in enumerate(rows[1:], start=2):  # row 2 = 第一筆資料
        padded = row + [''] * (8 - len(row))
        status = padded[COL_STATUS].strip()
        url = padded[COL_URL].strip()
        if status:
            continue
        if not url:
            continue

        if limit and len(details) >= limit:
            break

        try:
            result = evaluate_one(client, url, padded[COL_KEYWORDS], activities_context)
            # 規則：Gemini 沒回的欄位保持空白，不造假
            raw_status = result.get('status')
            status_cn = STATUS_EVAL.get(raw_status, '') if raw_status else ''
            user = normalize_user(result.get('user'))
            product = normalize_product(result.get('product'))
            title = str(result.get('title', '')).strip()
            update_row_fields(service, idx, {
                'search_terms': format_search_terms(result.get('search_terms', [])),
                'status': status_cn,
                'user': user,
                'product': product,
                'title': title,
            })
            details.append({
                'row': idx,
                'url': url,
                'status': status_cn or '(空)',
                'user': user or '(空)',
                'product': product or '(空)',
                'title': title or '(空)',
            })
            print(f'  ✅ Row {idx}: {raw_status or "(空)"} → {title[:30]}')
        except Exception as e:
            err = f'Row {idx} ({url[:50]}): {e}'
            errors.append(err)
            print(f'  ❌ {err}')

    return details, errors


if __name__ == '__main__':
    import sys
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else None
    details, errs = evaluate_pending(limit)
    print(f'\n處理 {len(details)} 筆，{len(errs)} 個錯誤')
