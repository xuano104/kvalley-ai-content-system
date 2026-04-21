"""每日選題 picker：從 ideator 推薦池挑 N 篇，強制分散

規則：
- 來源池：status = 'ideator 推薦' 的所有列
- 每個 product 最多 1 篇（避免同質）
- 三個 user (珊珊/推手/跨 TA) 至少各 1 篇（如果池子有的話）
- 優先：較新的列 > 較舊的
- 一個旗艦（recommend 中你最該寫的）+ 其他量產
"""
import os
from collections import Counter
from datetime import date

from .common import (
    COL_DATE, COL_KEYWORDS, COL_PRODUCT, COL_SEARCH_TERMS, COL_STATUS,
    COL_TITLE, COL_URL, COL_USER, get_sheets_service, normalize_url, read_all_rows,
)
from .pipeline_sync import scan_pipeline

DAILY_TARGET = 5
PICKS_DIR = os.getenv('KVAI_PICKS_DIR',
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logs')))


def pick_today(target=DAILY_TARGET):
    """挑當日 target 篇，回傳 list of dict"""
    service = get_sheets_service()
    rows = read_all_rows(service)

    # 防重複守門：掃 pipeline 四個資料夾，任何出現過 source_url 的一律排除
    # 即使 pipeline_sync 還沒回寫 Sheet status 也能擋下
    pipeline_urls = set(scan_pipeline().keys())

    pool = []
    excluded = 0
    for idx, row in enumerate(rows[1:], start=2):
        p = row + [''] * (8 - len(row))
        if p[COL_STATUS].strip() != 'ideator 推薦':
            continue
        nurl = normalize_url(p[COL_URL])
        if nurl and nurl in pipeline_urls:
            excluded += 1
            continue
        pool.append({
            'row': idx,
            'date': p[COL_DATE],
            'url': p[COL_URL],
            'keywords': p[COL_KEYWORDS],
            'search_terms': p[COL_SEARCH_TERMS],
            'user': p[COL_USER],
            'product': p[COL_PRODUCT],
            'title': p[COL_TITLE],
        })
    if excluded:
        print(f'🚫 排除 {excluded} 筆已出現在 pipeline 的候選（避免重複寫）')

    # 排序：新的優先（這裡用 row index 反序，越後面通常越新）
    pool.sort(key=lambda x: x['row'], reverse=True)

    picks = []
    used_products = Counter()
    used_users = Counter()

    # Phase 1：強制三個 user 各至少 1 篇
    user_targets = ['珊珊', '推手', '跨 TA']
    for u in user_targets:
        for item in pool:
            if item in picks:
                continue
            if item['user'] != u:
                continue
            if used_products[item['product']] >= 1:
                continue
            picks.append(item)
            used_products[item['product']] += 1
            used_users[item['user']] += 1
            break

    # Phase 2：補齊到 target，繼續分散 product
    for item in pool:
        if len(picks) >= target:
            break
        if item in picks:
            continue
        if used_products[item['product']] >= 1:
            continue
        picks.append(item)
        used_products[item['product']] += 1
        used_users[item['user']] += 1

    # Phase 3：池子太集中、不夠 target，放寬 product 限制
    for item in pool:
        if len(picks) >= target:
            break
        if item in picks:
            continue
        picks.append(item)
        used_products[item['product']] += 1
        used_users[item['user']] += 1

    return picks


def write_picks_file(picks):
    os.makedirs(PICKS_DIR, exist_ok=True)
    path = os.path.join(PICKS_DIR, f'daily-picks-{date.today().isoformat()}.md')
    lines = [f'# 今日選題 — {date.today().isoformat()}\n']
    lines.append(f'共 {len(picks)} 篇，從 ideator 推薦池中挑出，分散 user / product\n')
    lines.append('---\n')
    for i, p in enumerate(picks, 1):
        lines.append(f'## {i}. {p["title"]}\n')
        lines.append(f'- **Sheet row**：{p["row"]}')
        lines.append(f'- **User**：{p["user"]}')
        lines.append(f'- **Product**：{p["product"]}')
        lines.append(f'- **Search terms**：')
        for term in (p['search_terms'] or '').split('\n'):
            if term.strip():
                lines.append(f'    - {term.strip()}')
        lines.append(f'- **來源**：{p["keywords"]}')
        lines.append(f'- **URL**：{p["url"]}')
        lines.append('')

    lines.append('---\n')
    lines.append('## 確認流程\n')
    lines.append('Chloe 看完上方 5 篇後：')
    lines.append('1. 開 Google Sheet')
    lines.append('2. 把要寫的列 status 改成 `Chloe 選定但還沒寫`')
    lines.append('3. 不要的就跳過（status 維持 `ideator 推薦`，明天 picker 不會再選）')
    lines.append('   或改成 `捨棄` 永久退出選題池')

    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    return path


def main():
    picks = pick_today()
    if not picks:
        print('⚠️ 池子裡沒有 ideator 推薦的列')
        return None
    path = write_picks_file(picks)
    print(f'✅ 今日 {len(picks)} 篇選題已寫入：{path}')
    print()
    for i, p in enumerate(picks, 1):
        print(f'  {i}. [{p["user"]} / {p["product"]}] {p["title"][:40]}')
    return path


if __name__ == '__main__':
    main()
