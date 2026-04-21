"""從 NotebookLM 抓新的 sources 匯入 Sheet（只寫 A/B/C）"""
import json
import subprocess
from datetime import date

from .common import append_rows, get_existing_urls, get_sheets_service, normalize_url

# type → [tag]
TYPE_TAG = {
    'web_page': '[WEB]',
    'youtube_video': '[YT]',
    'google_doc': '[DOC]',
    'pdf': '[PDF]',
    'text': '[NOTE]',
}


def run_nlm(args):
    """Run nlm CLI, return JSON."""
    result = subprocess.run(
        ['nlm'] + args + ['--json'],
        capture_output=True,
        text=True,
        timeout=60,
    )
    if result.returncode != 0:
        raise RuntimeError(f'nlm {" ".join(args)} failed: {result.stderr}')
    return json.loads(result.stdout)


def list_notebooks():
    return run_nlm(['notebook', 'list'])


def list_sources(notebook_id):
    try:
        return run_nlm(['source', 'list', notebook_id])
    except Exception as e:
        print(f'  ⚠️ 讀取 notebook {notebook_id} sources 失敗：{e}')
        return []


def collect_candidates():
    """遍歷所有 notebook，收集 (url, title, notebook_title, type) 清單"""
    candidates = []
    notebooks = list_notebooks()
    print(f'📚 NotebookLM 共 {len(notebooks)} 個 notebook')
    for nb in notebooks:
        nb_id = nb['id']
        nb_title = nb['title']
        count = nb.get('source_count', 0)
        if count == 0:
            continue
        sources = list_sources(nb_id)
        for src in sources:
            url = src.get('url')
            if not url:
                continue  # 沒 URL 的 source 跳過（PDF、筆記）
            candidates.append({
                'url': url,
                'title': src.get('title', ''),
                'notebook': nb_title,
                'type': src.get('type', 'web_page'),
            })
    return candidates


def sync():
    """主流程：把 NotebookLM 有但 Sheet 沒有的 source 匯入 Sheet。
    回傳 list of dict：[{url, title, notebook, type}, ...]"""
    service = get_sheets_service()
    existing_urls = get_existing_urls(service)
    print(f'📊 Sheet 已有 {len(existing_urls)} 筆 URL')

    candidates = collect_candidates()
    print(f'🔍 NotebookLM 候選 {len(candidates)} 筆（有 URL 的 sources）')

    # 以 normalized URL 去重，優先保留第一次出現（不同 notebook 同一 URL 只匯入一次）
    new_rows = []
    new_items = []
    seen_in_batch = set()
    today = date.today().isoformat()

    for c in candidates:
        nurl = normalize_url(c['url'])
        if not nurl or nurl in existing_urls or nurl in seen_in_batch:
            continue
        seen_in_batch.add(nurl)
        tag = TYPE_TAG.get(c['type'], '[WEB]')
        keyword = f'{c["notebook"]} {tag}'
        new_rows.append([today, c['url'], keyword])
        new_items.append(c)

    if not new_rows:
        print('✅ 沒有新 source 需要匯入')
        return []

    append_rows(service, new_rows)
    print(f'✅ 匯入 {len(new_rows)} 筆新 source 到 Sheet')
    return new_items


if __name__ == '__main__':
    sync()
