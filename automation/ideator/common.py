"""共用工具：Sheet 存取、URL 正規化、Path"""
import os
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = os.getenv('KVAI_SHEET_ID', '1RxSb3bArkcqVQmQyM6ppfRm9GAXCjdHxHLCgIWxro8U')
SHEET_NAME = os.getenv('KVAI_SHEET_NAME', '自動化題材庫 (回溯精華版)')
# AGENT_DIR 指向自動化根目錄（含 token.json、.env），預設為 automation/ideator 的上兩層
AGENT_DIR = os.getenv('KVAI_AGENT_DIR',
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'automation')))
HEALTH_LOG = os.path.join(AGENT_DIR, 'logs', 'ideator-health.md')
LAST_RUN_FLAG = os.path.join(AGENT_DIR, 'logs', 'ideator-last-run.txt')

# 欄位 index
COL_DATE = 0
COL_URL = 1
COL_KEYWORDS = 2
COL_SEARCH_TERMS = 3
COL_STATUS = 4
COL_USER = 5
COL_PRODUCT = 6
COL_TITLE = 7


def get_sheets_service():
    os.chdir(AGENT_DIR)
    creds = Credentials.from_authorized_user_file(
        'token.json',
        ['https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/gmail.readonly']
    )
    return build('sheets', 'v4', credentials=creds)


def normalize_url(url: str) -> str:
    if not url:
        return ''
    try:
        p = urlparse(url.strip())
        q = [(k, v) for k, v in parse_qsl(p.query)
             if not (k.startswith('utm_') or k in ('fbclid', 'gclid', 'mc_cid', 'mc_eid'))]
        path = p.path.rstrip('/')
        return urlunparse((p.scheme.lower(), p.netloc.lower(), path, '', urlencode(q), ''))
    except Exception:
        return url.strip()


def read_all_rows(service):
    return service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{SHEET_NAME}!A:H"
    ).execute().get('values', [])


def append_rows(service, rows):
    """只寫 A/B/C 三欄（radar-style），D-H 留空"""
    if not rows:
        return
    service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{SHEET_NAME}!A:C",
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body={'values': rows}
    ).execute()


def update_row_fields(service, row_number, fields):
    """更新單列的 D-H 欄位。row_number 是 1-indexed（含 header 所以實際資料從 2 開始）。
    fields: dict {'search_terms': ..., 'status': ..., 'user': ..., 'product': ..., 'title': ...}
    """
    values = [
        fields.get('search_terms', ''),
        fields.get('status', ''),
        fields.get('user', ''),
        fields.get('product', ''),
        fields.get('title', ''),
    ]
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{SHEET_NAME}!D{row_number}:H{row_number}",
        valueInputOption="USER_ENTERED",
        body={'values': [values]}
    ).execute()


def get_existing_urls(service):
    """回傳 Sheet 中所有 normalized URL 的 set"""
    rows = read_all_rows(service)
    urls = set()
    for row in rows[1:]:
        if len(row) > COL_URL:
            nurl = normalize_url(row[COL_URL])
            if nurl:
                urls.add(nurl)
    return urls
