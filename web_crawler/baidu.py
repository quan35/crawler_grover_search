"""
百度搜索爬虫模块
通过百度搜索接口抓取相关内容。
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict

def baidu_search_crawl(keyword: str) -> List[Dict]:
    """
    通过百度搜索抓取相关内容（标题、摘要、URL）。
    """
    headers = {"User-Agent": "Mozilla/5.0"}
    results = []
    page = 0
    # 默认最多抓取5页（每页10条）
    max_pages = 5
    while page < max_pages:
        pn = page * 10
        url = f"https://www.baidu.com/s?wd={keyword}&pn={pn}"
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        items = soup.select('div.result')
        if not items:
            break
        for item in items:
            title_tag = item.select_one('h3')
            summary_tag = item.select_one('.c-abstract')
            link_tag = title_tag.select_one('a') if title_tag else None
            if title_tag and link_tag:
                url_full = link_tag['href']
                results.append({
                    'title': title_tag.text.strip(),
                    'summary': summary_tag.text.strip() if summary_tag else '',
                    'url': url_full
                })
        page += 1
    return results
