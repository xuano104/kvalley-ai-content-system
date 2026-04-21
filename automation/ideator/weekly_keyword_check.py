"""每週一 09:00 跑：檢查 notebooklm-map 關鍵字健康度

兩個檢查：
1. 詞太少/太泛：每本筆記本的 search terms 數量、以及是否含泛詞
2. Reject 率高的關鍵字：過去一週 evaluator 評為 reject 的文章，歸因到來源筆記本

產出：agent/logs/weekly-keyword-check-YYYY-MM-DD.md
"""
import os
import re
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

from .common import (
    COL_DATE, COL_KEYWORDS, COL_STATUS, COL_URL,
    get_sheets_service, read_all_rows,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
MAP_FILE = Path(os.getenv('KVAI_NBLM_MAP',
    _REPO_ROOT / 'agents' / 'ideator' / 'memory' / 'notebooklm-map.md'))
OUTPUT_DIR = Path(os.getenv('KVAI_LOGS_DIR',
    _REPO_ROOT / 'automation' / 'logs'))

# 太泛詞黑名單（出現這些要警告）
VAGUE_TERMS = {
    'ai', 'AI', '管理', 'management', 'leadership', '領導',
    'hr', 'HR', '培訓', 'training', '數位轉型',
}

MIN_TERMS_PER_NOTEBOOK = 8


def parse_notebooklm_map() -> dict:
    """解析 notebooklm-map.md，回傳 {notebook_name: [terms]}"""
    if not MAP_FILE.exists():
        return {}
    text = MAP_FILE.read_text(encoding='utf-8')
    result = {}
    current_nb = None
    current_terms = []
    for line in text.split('\n'):
        # "## 1. 主管培訓" or "## 主管培訓"
        m = re.match(r'^##\s+(?:\d+\.\s+)?(.+)$', line.strip())
        if m and not line.startswith('###'):
            # 儲存上一本
            if current_nb:
                result[current_nb] = current_terms
            current_nb = m.group(1).strip()
            current_terms = []
            continue
        # 子節跳過 (### English search terms, ### 中文搜尋詞)
        if line.strip().startswith('###'):
            continue
        # 清單項 - "..." 或 - term
        m2 = re.match(r'^\s*-\s+["\']?(.+?)["\']?\s*$', line)
        if m2 and current_nb:
            term = m2.group(1).strip('"\' ')
            if term:
                current_terms.append(term)
    # 最後一本
    if current_nb:
        result[current_nb] = current_terms
    return result


def check_term_coverage(notebook_terms: dict) -> list:
    """回傳每本筆記本的健康分析"""
    findings = []
    for nb, terms in notebook_terms.items():
        vague_hits = [t for t in terms if t.lower() in {v.lower() for v in VAGUE_TERMS}]
        issues = []
        if len(terms) < MIN_TERMS_PER_NOTEBOOK:
            issues.append(f'詞數 {len(terms)} < {MIN_TERMS_PER_NOTEBOOK}（建議補詞）')
        if vague_hits:
            issues.append(f'含泛詞：{", ".join(vague_hits)}')
        findings.append({
            'notebook': nb,
            'term_count': len(terms),
            'issues': issues,
        })
    return findings


def compute_reject_by_notebook(days=7) -> dict:
    """過去 N 天內，每本筆記本對應列的 reject 率。
    回傳 {notebook_name: {'total': n, 'reject': m, 'rate': pct}}"""
    service = get_sheets_service()
    rows = read_all_rows(service)
    since = date.today() - timedelta(days=days)

    stats = defaultdict(lambda: {'total': 0, 'reject': 0})
    for row in rows[1:]:
        padded = row + [''] * (8 - len(row))
        # 日期欄位過濾過去 N 天
        try:
            row_date = datetime.strptime(padded[COL_DATE].strip(), '%Y-%m-%d').date()
            if row_date < since:
                continue
        except (ValueError, IndexError):
            continue
        # 從 C 欄 (keywords) 抓 notebook 名稱
        # 格式可能是 "主管培訓 [WEB]" 或換行分隔多本 "AI組織變革\n主管培訓 [WEB]"
        # 同一 URL 在多本時，每本都計一次
        kw_raw = padded[COL_KEYWORDS].strip()
        if not kw_raw:
            continue
        status = padded[COL_STATUS].strip()
        for line in kw_raw.split('\n'):
            nb = re.sub(r'\s*\[[A-Z]+\]\s*$', '', line).strip()
            if not nb:
                continue
            stats[nb]['total'] += 1
            if status == 'ideator 不推薦':
                stats[nb]['reject'] += 1

    result = {}
    for nb, s in stats.items():
        if s['total'] == 0:
            continue
        result[nb] = {
            'total': s['total'],
            'reject': s['reject'],
            'rate': round(s['reject'] / s['total'] * 100, 1),
        }
    return result


def write_report(notebook_terms, coverage_findings, reject_stats):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    today = date.today().isoformat()
    path = OUTPUT_DIR / f'weekly-keyword-check-{today}.md'

    lines = [f'# 每週關鍵字健康檢查 — {today}']
    lines.append('')
    lines.append(f'資料來源：`notebooklm-map.md` × 過去 7 天 Gemini 評估結果')
    lines.append('')
    lines.append('---')
    lines.append('')
    lines.append('## 1. 詞太少 / 太泛的筆記本')
    lines.append('')
    flagged = [f for f in coverage_findings if f['issues']]
    if not flagged:
        lines.append('✅ 全部筆記本都通過檢查')
    else:
        lines.append('| 筆記本 | 詞數 | 問題 |')
        lines.append('|--------|------|------|')
        for f in flagged:
            lines.append(f'| {f["notebook"]} | {f["term_count"]} | {"; ".join(f["issues"])} |')
    lines.append('')
    lines.append('---')
    lines.append('')
    lines.append('## 2. Reject 率（過去 7 天）')
    lines.append('')
    if not reject_stats:
        lines.append('（過去 7 天沒有新資料進 Sheet，略過此項）')
    else:
        lines.append('| 筆記本 | 總數 | reject 數 | reject 率 |')
        lines.append('|--------|------|----------|----------|')
        for nb, s in sorted(reject_stats.items(), key=lambda x: -x[1]['rate']):
            warn = '⚠️' if s['rate'] >= 50 else ''
            lines.append(f'| {nb} | {s["total"]} | {s["reject"]} | {s["rate"]}% {warn} |')
        lines.append('')
        lines.append('**Reject 率 ≥ 50% 的筆記本**：該本的 search terms 可能撈到太多無關文章——值得檢討、調整。')
    lines.append('')
    lines.append('---')
    lines.append('')
    lines.append('## Chloe 的回應格式（回給 ideator 就好）')
    lines.append('')
    lines.append('```')
    lines.append('要加：[新方向的關鍵字，註明加進哪本]')
    lines.append('要刪：[不對味的關鍵字，註明哪本]')
    lines.append('要改：[過時或太泛的關鍵字，註明改成什麼]')
    lines.append('```')
    lines.append('')
    path.write_text('\n'.join(lines), encoding='utf-8')
    return path


def main():
    notebook_terms = parse_notebooklm_map()
    if not notebook_terms:
        print('⚠️ 讀不到 notebooklm-map.md')
        return None
    coverage = check_term_coverage(notebook_terms)
    reject = compute_reject_by_notebook(days=7)
    path = write_report(notebook_terms, coverage, reject)
    print(f'✅ 週報已寫入：{path}')
    flagged = [f for f in coverage if f['issues']]
    print(f'   詞不足/太泛的本：{len(flagged)}')
    high_reject = [nb for nb, s in reject.items() if s['rate'] >= 50]
    print(f'   Reject 率 ≥ 50% 的本：{len(high_reject)}')
    return path


if __name__ == '__main__':
    main()
