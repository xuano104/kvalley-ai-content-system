"""Health log + macOS 通知"""
import os
import subprocess
from datetime import date, datetime

from .common import HEALTH_LOG, LAST_RUN_FLAG


def ensure_log_dir():
    os.makedirs(os.path.dirname(HEALTH_LOG), exist_ok=True)


def append_health(line: str):
    ensure_log_dir()
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(HEALTH_LOG, 'a', encoding='utf-8') as f:
        f.write(f'- {ts} | {line}\n')


def write_run_summary(sync_items, eval_details, errors):
    """寫厚版 health log。
    sync_items: list of dict {url, title, notebook, type} 或 int（向後相容）
    eval_details: list of dict {row, url, status, user, product, title} 或 int
    """
    ensure_log_dir()
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    status_icon = '✅' if not errors else '⚠️'

    # 向後相容：如果傳 int 進來，退回舊版格式
    sync_is_int = isinstance(sync_items, int)
    eval_is_int = isinstance(eval_details, int)
    sync_count = sync_items if sync_is_int else len(sync_items)
    eval_count = eval_details if eval_is_int else len(eval_details)

    with open(HEALTH_LOG, 'a', encoding='utf-8') as f:
        f.write(f'\n## {ts} {status_icon}\n')
        f.write(f'- NotebookLM 同步：{sync_count} 筆新資料\n')
        if not sync_is_int and sync_items:
            for it in sync_items:
                notebook = it.get('notebook', '?')
                title = (it.get('title') or '(無標題)')[:60]
                url = it.get('url', '')
                f.write(f'    - [{notebook}] {title} — {url}\n')
        f.write(f'- 評估：{eval_count} 筆\n')
        if not eval_is_int and eval_details:
            for d in eval_details:
                row = d.get('row', '?')
                st = d.get('status', '?')
                user = d.get('user', '?')
                prod = d.get('product', '?')
                title = (d.get('title') or '(無標題)')[:50]
                f.write(f'    - Row {row} | {st} | {user} / {prod} | {title}\n')
        if errors:
            f.write(f'- 錯誤：\n')
            for e in errors:
                f.write(f'    - {e}\n')


def mark_today_ran():
    ensure_log_dir()
    with open(LAST_RUN_FLAG, 'w') as f:
        f.write(date.today().isoformat())


def ran_today() -> bool:
    if not os.path.exists(LAST_RUN_FLAG):
        return False
    with open(LAST_RUN_FLAG) as f:
        return f.read().strip() == date.today().isoformat()


def notify(title: str, message: str):
    """macOS 通知"""
    try:
        script = f'display notification "{message}" with title "{title}"'
        subprocess.run(['osascript', '-e', script], timeout=5, capture_output=True)
    except Exception:
        pass


def check_missed_days():
    """檢查是否連續 2 天沒跑，如果是就通知"""
    if not os.path.exists(LAST_RUN_FLAG):
        return
    with open(LAST_RUN_FLAG) as f:
        last = f.read().strip()
    try:
        last_date = datetime.strptime(last, '%Y-%m-%d').date()
        days_since = (date.today() - last_date).days
        if days_since >= 2:
            notify(
                'Ideator 很久沒跑了',
                f'{days_since} 天沒跑，請檢查 ~/Documents/agent/logs/ideator-health.md'
            )
    except Exception:
        pass
