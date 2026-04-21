"""Ideator 每日 13:00 自動執行
1. NotebookLM 同步：抓 NotebookLM 新 source 進 Sheet
2. 評估：用 Gemini 評估 status 為空的列
3. Health log + macOS 通知
"""
import sys
import traceback

from .health import (
    append_health, check_missed_days, mark_today_ran, notify, ran_today,
    write_run_summary,
)


def main(force=False):
    if not force and ran_today():
        print('今天已經跑過，跳過')
        return

    check_missed_days()

    print('=== Ideator Daily Scan ===\n')
    errors = []

    # Step 1: NotebookLM 同步
    print('--- Step 1: NotebookLM 同步 ---')
    sync_items = []
    try:
        from .notebooklm_sync import sync
        sync_items = sync()
    except Exception as e:
        err = f'NotebookLM 同步失敗: {e}'
        errors.append(err)
        traceback.print_exc()
        if 'auth' in str(e).lower() or 'login' in str(e).lower():
            notify('NotebookLM 需要重新登入', '請執行：nlm login')

    # Step 2: 評估
    print('\n--- Step 2: Gemini 評估 ---')
    eval_details = []
    try:
        from .evaluator import evaluate_pending
        eval_details, eval_errors = evaluate_pending()
        errors.extend(eval_errors[:5])  # 最多記 5 個錯誤
    except Exception as e:
        err = f'評估失敗: {e}'
        errors.append(err)
        traceback.print_exc()

    # Step 3: 挑今日 5 篇選題（分散 user/product）
    print('\n--- Step 3: 今日 5 篇選題 ---')
    try:
        from .daily_picker import main as pick_main
        pick_main()
    except Exception as e:
        err = f'每日選題失敗: {e}'
        errors.append(err)
        traceback.print_exc()

    # Step 4: Pipeline sync（掃 pipeline 資料夾，回寫 Sheet status）
    print('\n--- Step 4: Pipeline Sync ---')
    pipeline_updated = 0
    try:
        from .pipeline_sync import sync as pipeline_sync
        pipeline_updated = pipeline_sync()
    except Exception as e:
        err = f'Pipeline sync 失敗: {e}'
        errors.append(err)
        traceback.print_exc()

    # Step 5: Health log
    write_run_summary(sync_items, eval_details, errors)
    mark_today_ran()

    # Step 4: 通知（只有錯誤才通知）
    sync_count = len(sync_items)
    eval_count = len(eval_details)
    if errors:
        notify(
            'Ideator 跑完但有錯',
            f'NotebookLM +{sync_count} / 評估 {eval_count} / 錯 {len(errors)}'
        )
    else:
        print(f'\n✅ 完成：NotebookLM +{sync_count} / 評估 {eval_count}')


if __name__ == '__main__':
    main(force='--force' in sys.argv)
