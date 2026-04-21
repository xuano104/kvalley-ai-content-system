"""簡單的 URL content fetcher，抓頁面標題 + 前 N 字文字"""
import re
from urllib.request import Request, urlopen

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/124.0 Safari/537.36'
    ),
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9,zh-TW;q=0.8',
}


def strip_html(html: str) -> str:
    # 去 script/style
    html = re.sub(r'<script[^>]*>.*?</script>', ' ', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<style[^>]*>.*?</style>', ' ', html, flags=re.DOTALL | re.IGNORECASE)
    # 去標籤
    text = re.sub(r'<[^>]+>', ' ', html)
    # 空白正規化
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def fetch_title_and_text(url: str, max_chars=3000, timeout=8):
    """回傳 (title, text)。失敗回 (None, None)"""
    try:
        req = Request(url, headers=HEADERS)
        with urlopen(req, timeout=timeout) as resp:
            raw = resp.read(200_000)  # 最多讀 200KB
            encoding = resp.headers.get_content_charset() or 'utf-8'
            html = raw.decode(encoding, errors='replace')
    except Exception:
        return None, None

    # 抓 title
    title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
    title = strip_html(title_match.group(1)).strip() if title_match else None

    # 抓 meta description（當 fallback）
    text = strip_html(html)
    if len(text) > max_chars:
        text = text[:max_chars]

    return title, text
