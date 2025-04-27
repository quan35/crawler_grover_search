"""
多源聚合爬虫模块
自动调用Bing和知乎爬虫，合并去重结果。
"""
from typing import List, Dict
from web_crawler.crawler import simple_search_crawl
from web_crawler.baidu import baidu_search_crawl
from web_crawler.sogou import sogou_search_crawl

def multi_source_crawl(keyword: str) -> List[Dict]:
    """
    聚合Bing、百度、搜狗搜索结果，自动抓取最大可得数据。
    """
    bing_results = simple_search_crawl(keyword)
    baidu_results = baidu_search_crawl(keyword)
    sogou_results = sogou_search_crawl(keyword)
    # 合并并去重（按title+url）
    seen = set()
    merged = []
    for item in bing_results + baidu_results + sogou_results:
        key = (item.get('title', ''), item.get('url', ''))
        if key not in seen:
            seen.add(key)
            merged.append(item)
    return merged
