"""Brief 自動生成器

Chloe 看完 daily_picks 後說「寫 #3 #5」→ ideator 呼叫這支：
1. 讀 Sheet 該列的 URL, title, user, product, search_terms, keywords
2. fetch URL 內文
3. 用 Gemini 產生完整 brief markdown（含 source_url, Meta, H2 骨架, 痛點, 收穫）
4. 寫到 pipeline/01-queue/YYYY-MM-DD_[slug].md
5. 呼叫者再跑 pipeline_sync 自動把 Sheet status 推到「Brief 完成」
"""
import json
import os
import re
from datetime import date
from pathlib import Path

from dotenv import load_dotenv
from google import genai

from .common import (
    COL_KEYWORDS, COL_PRODUCT, COL_SEARCH_TERMS, COL_STATUS, COL_TITLE,
    COL_URL, COL_USER, SPREADSHEET_ID, SHEET_NAME,
    get_sheets_service, read_all_rows,
)
from .evaluator import load_activities_context
from .fetcher import fetch_title_and_text

_REPO_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_REPO_ROOT / 'automation' / '.env')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

PIPELINE_DIR = Path(os.getenv('KVAI_PIPELINE_DIR', _REPO_ROOT / 'pipeline'))
QUEUE_DIR = PIPELINE_DIR / '01-queue'
REVIEW_DIR = PIPELINE_DIR / '00-review'

BRIEF_PROMPT = """你是智谷網絡的 brief 撰寫員。Chloe 已經選定這篇主題要寫成文章，你的任務是把它轉成一份完整 brief，讓 seo-writer 可以接手寫全文。

## 選定主題

- 來源 URL：{url}
- 初步標題（evaluator 給的）：{sheet_title}
- 目標 TA：{user}
- 對應產品：{product}
- 搜尋關鍵字：{search_terms}
- NotebookLM 筆記本：{notebook_keyword}

## 來源頁面內容（前 3000 字）

---
{fetched_text}
---

## 公司當前活動（業務對齊用）

{activities_context}

## 你的任務

輸出 JSON（只回 JSON，不要其他文字）：

```json
{{
  "title": "最終版文章標題（20-30 字，old money 感，不要工商腔）",
  "meta_title": "SEO Meta Title（60 字以內，含主關鍵字）",
  "meta_description": "Meta Description（120-155 字，含主關鍵字 + 具體數據鉤子）",
  "article_type": "趨勢 | 工具 | 故事 | 人文關懷 | 人物誌",
  "writing_style": "jimmy-lin | style-analytical | style-narrative | style-practical | style-editorial",
  "main_keyword": "SEO 主關鍵字（1 個）",
  "secondary_keywords": ["次要關鍵字 1", "次要關鍵字 2", "次要關鍵字 3"],
  "core_pain": "一句話：這篇文章解決目標 TA 的什麼具體焦慮",
  "reader_takeaway": "讀者讀完應該產生什麼具體想法或行動",
  "h2_outline": [
    {{"h2": "H2-1 標題（能獨立成一句有價值的話）", "task": "這段要做什麼", "content_hint": "可用的數據/案例/引用方向"}},
    {{"h2": "H2-2 ...", "task": "...", "content_hint": "..."}},
    {{"h2": "H2-3 ...", "task": "...", "content_hint": "..."}},
    {{"h2": "H2-4 ...", "task": "...", "content_hint": "..."}},
    {{"h2": "H2-5 第一週/下週能做的一件事", "task": "給讀者具體行動", "content_hint": "..."}}
  ],
  "slug": "檔名用的英文 slug（小寫連字號）"
}}
```

## 品質標準（Chloe 品味底線）

- **old money 感，不是工商感**：像 HBR/BCG 的文章，不像業務 DM
- 標題要有**衝突或反直覺**，不要像書名
- Meta Description 開頭要有**硬數據**
- H2 每一個都能**獨立成句**（Chloe 會先掃 H2 決定要不要讀）
- 「第一週能做的事」必備——推手和珊珊都需要「下週可執行」的起點
- 禁用 AI 式句型：「這不是 X，而是 Y」/「與其說是 X，不如說是 Y」

## 風格選擇

- **推手**（總經理/副總/CTO）→ style-analytical（BCG/McKinsey 分析感）
- **珊珊**（HRD）情感共鳴重 → style-narrative
- 珊珊實戰需求重 → style-practical
- 思想領導力 / 跨 TA → style-editorial 或 style-analytical
"""


def slugify(text: str, max_len=50) -> str:
    """簡單 slugify：保留英數字和連字號，中文保留"""
    text = text.strip()
    # 替換空白與標點為連字號
    text = re.sub(r'[\s\W]+', '-', text, flags=re.UNICODE)
    text = text.strip('-').lower()
    return text[:max_len] or 'untitled'


def get_client():
    if not GEMINI_API_KEY:
        raise RuntimeError('找不到 GEMINI_API_KEY')
    return genai.Client(api_key=GEMINI_API_KEY)


def load_row(service, row_idx):
    rows = read_all_rows(service)
    if row_idx < 2 or row_idx > len(rows):
        raise ValueError(f'Row {row_idx} 超出範圍（有效 2-{len(rows)}）')
    padded = rows[row_idx - 1] + [''] * (8 - len(rows[row_idx - 1]))
    return {
        'row': row_idx,
        'url': padded[COL_URL].strip(),
        'keywords': padded[COL_KEYWORDS].strip(),
        'search_terms': padded[COL_SEARCH_TERMS].strip(),
        'status': padded[COL_STATUS].strip(),
        'user': padded[COL_USER].strip(),
        'product': padded[COL_PRODUCT].strip(),
        'title': padded[COL_TITLE].strip(),
    }


def mark_selected(service, row_idx):
    """把 Sheet E 欄（status）改成『Chloe 選定但還沒寫』"""
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{SHEET_NAME}!E{row_idx}",
        valueInputOption="USER_ENTERED",
        body={'values': [['Chloe 選定但還沒寫']]}
    ).execute()


def format_h2(h2_list) -> str:
    """把 h2_outline JSON 轉成 markdown"""
    lines = []
    for i, h2 in enumerate(h2_list, 1):
        lines.append(f'### H2-{i}：{h2.get("h2", "").strip()}')
        task = h2.get('task', '').strip()
        hint = h2.get('content_hint', '').strip()
        if task:
            lines.append(f'**任務：** {task}')
        if hint:
            lines.append(f'**內容方向：** {hint}')
        lines.append('')
    return '\n'.join(lines)


def brief_markdown(data: dict, row_data: dict) -> str:
    """把 Gemini JSON 輸出組成 brief markdown"""
    today = date.today().isoformat()
    secondary = '、'.join(data.get('secondary_keywords', []))
    notebook = (row_data['keywords'].split('\n')[0] if row_data['keywords'] else '').strip()
    notebook = re.sub(r'\s*\[[A-Z]+\]\s*$', '', notebook)

    md = f"""# Brief：{data.get('title', '')}

**source_url**：{row_data['url']}
**Sheet row**：{row_data['row']}
**產出日期**：{today}

---

**Meta Title**：{data.get('meta_title', '')}
**Meta Description**：{data.get('meta_description', '')}
**目標 TA**：{row_data['user']}
**文章類型**：{data.get('article_type', '')}
**寫作風格**：{data.get('writing_style', '')}
**支柱對應產品**：{row_data['product']}
**主關鍵字**：{data.get('main_keyword', '')}
**次要關鍵字**：{secondary}
**NotebookLM 關鍵字**：{notebook}

---

## 核心痛點

{data.get('core_pain', '')}

**讀者讀完應該想：** {data.get('reader_takeaway', '')}

---

## H2 結構（seo-writer 從 NotebookLM「{notebook}」本擴寫）

{format_h2(data.get('h2_outline', []))}

---

## 給 seo-writer 的備註

- Brief 由 ideator `brief_generator.py` 自動產出（Gemini 2.5 Flash）
- 所有觀點/數據/案例從 NotebookLM「{notebook}」本撈，避免自行瞎掰
- H2 骨架可調整但不要全改；如有重大方向變動先問 Chloe
"""
    return md


def generate_brief(row_idx: int, extra_angle: str = None, dry_run: bool = False) -> Path:
    """主流程：寫 brief 到 pipeline/00-review/YYYY-MM-DD/（暫存區，等 Chloe 審核）
    注意：這個函式**不動 Sheet status**，status 由 review 流程（Chloe 決定後）才更新。

    extra_angle: Chloe 說「換角度 #X」時傳進來的新角度指示，會併進 Gemini prompt。
    """
    service = get_sheets_service()
    row_data = load_row(service, row_idx)
    if not row_data['url']:
        raise ValueError(f'Row {row_idx} 沒有 URL，無法產 brief')

    # Step 1: fetch 內文
    fetched_title, fetched_text = fetch_title_and_text(row_data['url'])
    if not fetched_text:
        fetched_text = '（無法抓取內文，請 seo-writer 從 NotebookLM 補素材）'

    # Step 2: 呼叫 Gemini
    client = get_client()
    prompt = BRIEF_PROMPT.format(
        url=row_data['url'],
        sheet_title=row_data['title'] or fetched_title or '(無)',
        user=row_data['user'] or '（待判斷）',
        product=row_data['product'] or '（待判斷）',
        search_terms=row_data['search_terms'] or '(無)',
        notebook_keyword=row_data['keywords'] or '(無)',
        fetched_text=fetched_text,
        activities_context=load_activities_context(),
    )
    if extra_angle:
        prompt += f'\n\n## Chloe 指定的新角度（重生用）\n\n{extra_angle}\n請按照這個角度重新發想 brief。'

    resp = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
    text = resp.text.strip()
    text = re.sub(r'^```(?:json)?\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    data = json.loads(text)

    # Step 3: 組 markdown 寫檔
    md = brief_markdown(data, row_data)
    slug = data.get('slug') or slugify(data.get('title', '')) or f'row-{row_idx}'
    today = date.today().isoformat()
    today_dir = REVIEW_DIR / today
    path = today_dir / f'{slug}_row{row_idx}.md'

    if dry_run:
        print(f'[DRY-RUN] Would write: {path}')
        print(f'--- brief preview (first 500 chars) ---\n{md[:500]}')
        return path

    today_dir.mkdir(parents=True, exist_ok=True)
    path.write_text(md, encoding='utf-8')
    return path


def generate_batch(row_indices: list[int], dry_run: bool = False):
    """批次產 brief 到暫存區，失敗不中斷。不動 Sheet status。"""
    results = []
    for idx in row_indices:
        try:
            path = generate_brief(idx, dry_run=dry_run)
            results.append((idx, 'ok', path))
            print(f'✅ Row {idx} → {path.relative_to(REVIEW_DIR.parent)}')
        except Exception as e:
            results.append((idx, 'error', str(e)))
            print(f'❌ Row {idx}: {e}')
    return results


# ===== Review 動作（Chloe 做完決定後呼叫） =====

STATUS_APPROVED = 'Chloe 選定但還沒寫'
STATUS_HOLD = '暫緩'
STATUS_REJECT = '捨棄'


def approve_brief(row_idx: int, brief_path: Path) -> Path:
    """Chloe 通過 → 把 brief 從 00-review/ 移到 01-queue/，status 改「Chloe 選定但還沒寫」。
    之後 pipeline_sync 會看到 01-queue/ 的 brief，推到「Brief 完成」。"""
    if not brief_path.exists():
        raise FileNotFoundError(f'Brief 不在：{brief_path}')
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    new_name = f'{today}_{brief_path.stem.rsplit("_row", 1)[0]}.md'
    target = QUEUE_DIR / new_name
    brief_path.rename(target)

    service = get_sheets_service()
    _update_status(service, row_idx, STATUS_APPROVED)
    return target


def hold_brief(row_idx: int) -> None:
    """Chloe 暫緩 → brief 留在 00-review/，status 改『暫緩』"""
    service = get_sheets_service()
    _update_status(service, row_idx, STATUS_HOLD)


def reject_brief(row_idx: int, brief_path: Path) -> None:
    """Chloe 不要 → 刪 brief，status 改『捨棄』"""
    if brief_path.exists():
        brief_path.unlink()
    service = get_sheets_service()
    _update_status(service, row_idx, STATUS_REJECT)


def _update_status(service, row_idx: int, new_status: str):
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{SHEET_NAME}!E{row_idx}",
        valueInputOption="USER_ENTERED",
        body={'values': [[new_status]]}
    ).execute()


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print('用法：python -m ideator.brief_generator <row_idx> [<row_idx> ...]')
        print('      python -m ideator.brief_generator --dry 3 5  (乾跑測試)')
        sys.exit(1)
    dry = '--dry' in sys.argv
    indices = [int(a) for a in sys.argv[1:] if a.isdigit()]
    generate_batch(indices, dry_run=dry)
