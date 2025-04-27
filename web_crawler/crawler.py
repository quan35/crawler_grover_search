"""
网络爬虫模块
支持关键词自动抓取，抓取网页标题和摘要。
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict

def simple_search_crawl(keyword: str, max_results: int = 50) -> List[Dict]:
    """
    使用Bing搜索，抓取前若干条结果的标题和摘要。
    :param keyword: 搜索关键词
    :param max_results: 最大抓取条数
    :return: [{'title': ..., 'summary': ..., 'url': ...}, ...]
    """
    headers = {"User-Agent": "Mozilla/5.0"}
    results = []
    page = 1
    while len(results) < max_results:
        first = (page - 1) * 10 + 1
        url = f"https://www.bing.com/search?q={keyword}&first={first}"
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        items = soup.select('.b_algo')
        if not items:
            break
        for item in items:
            title_tag = item.select_one('h2')
            summary_tag = item.select_one('.b_caption p')
            link_tag = title_tag.find('a') if title_tag else None
            if title_tag and link_tag:
                results.append({
                    'title': title_tag.text.strip(),
                    'summary': summary_tag.text.strip() if summary_tag else '',
                    'url': link_tag['href']
                })
            if len(results) >= max_results:
                break
        page += 1
    return results[:max_results]

