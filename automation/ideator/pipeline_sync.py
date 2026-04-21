"""Pipeline Sync：掃 pipeline 四個資料夾，把生產進度回寫 Sheet status

流程：
1. 掃 pipeline/01-queue/ → 03-ready/ 每個 .md 檔
2. 讀 source_url（如果有）
3. 比對 Sheet B 欄（網址），找到對應的列
4. 根據檔案所在資料夾更新 E 欄 status
"""
import os
import re

from .common import (
    COL_STATUS, COL_URL,
    SPREADSHEET_ID, SHEET_NAME,
    get_sheets_service, normalize_url, read_all_rows, update_row_fields,
)

PIPELINE_DIR = os.getenv('KVAI_PIPELINE_DIR',
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'pipeline')))

# 資料夾 → status 對照
FOLDER_STATUS = {
    '01-queue': 'Brief 完成',
    '02-in-progress': '寫作中',
    '03-ready': '已完稿',
    '04-published': '已上架',
}


def extract_source_url(filepath):
    """從 brief/article .md 檔讀取 source_url"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            # 只讀前 30 行（metadata 區）
            for i, line in enumerate(f):
                if i > 30:
                    break
                # 支援多種格式：
                # source_url: https://...
                # **source_url**：https://...
                # **source_url：** https://...
                # source_url：https://...
                # - **source_url**：https://... (bullet list)
                m = re.match(r'[-*]?\s*\**\s*source_url\s*\**\s*[：:]\s*\**\s*(https?://\S+)', line.strip())
                if m:
                    return m.group(1).strip()
    except Exception:
        pass
    return None


def scan_pipeline():
    """掃描所有 pipeline 資料夾，回傳 {normalized_url: status}"""
    url_to_status = {}
    for folder, status in FOLDER_STATUS.items():
        folder_path = os.path.join(PIPELINE_DIR, folder)
        if not os.path.isdir(folder_path):
            continue
        for fname in os.listdir(folder_path):
            if not fname.endswith('.md'):
                continue
            fpath = os.path.join(folder_path, fname)
            source_url = extract_source_url(fpath)
            if not source_url:
                continue
            nurl = normalize_url(source_url)
            if nurl:
                # 越後面的資料夾 = 越新的狀態，覆蓋舊的
                # 例如同一篇在 01-queue 和 03-ready 都有，以 03-ready 為準
                existing_priority = list(FOLDER_STATUS.values())
                if nurl in url_to_status:
                    old_idx = existing_priority.index(url_to_status[nurl])
                    new_idx = existing_priority.index(status)
                    if new_idx > old_idx:
                        url_to_status[nurl] = status
                else:
                    url_to_status[nurl] = status
    return url_to_status


def sync():
    """主流程：掃 pipeline → 回寫 Sheet"""
    url_to_status = scan_pipeline()
    if not url_to_status:
        print('📁 Pipeline 裡沒有帶 source_url 的檔案')
        return 0

    service = get_sheets_service()
    rows = read_all_rows(service)

    updated = 0
    for idx, row in enumerate(rows[1:], start=2):
        padded = row + [''] * (8 - len(row))
        url = padded[COL_URL].strip()
        current_status = padded[COL_STATUS].strip()
        if not url:
            continue
        nurl = normalize_url(url)
        if nurl not in url_to_status:
            continue

        new_status = url_to_status[nurl]

        # 不要把 Chloe 手動設的狀態覆蓋回去
        # 規則：只有「往前推進」才更新（不往後退）
        STATUS_ORDER = [
            '新', 'ideator 推薦', 'ideator 觀察', 'ideator 不推薦',
            'Chloe 選定但還沒寫', 'Chloe 選定，已寫', '改寫舊文', '暫緩',
            'Brief 完成', '寫作中', '送 persona 審核中', '審核未過修改中',
            '已完稿', '已上架',
        ]
        try:
            current_idx = STATUS_ORDER.index(current_status) if current_status in STATUS_ORDER else -1
            new_idx = STATUS_ORDER.index(new_status) if new_status in STATUS_ORDER else -1
        except ValueError:
            continue

        if new_idx > current_idx:
            # 只更新 status，不動其他欄位
            service.spreadsheets().values().update(
                spreadsheetId=SPREADSHEET_ID,
                range=f"{SHEET_NAME}!E{idx}",
                valueInputOption="USER_ENTERED",
                body={'values': [[new_status]]}
            ).execute()
            updated += 1
            print(f'  ✅ Row {idx}: {current_status or "(空白)"} → {new_status}')

    if updated:
        print(f'\n✅ 更新 {updated} 列 status')
    else:
        print('📁 Pipeline 狀態與 Sheet 同步，無需更新')
    return updated


if __name__ == '__main__':
    sync()
