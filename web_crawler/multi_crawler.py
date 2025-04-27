"""
多源聚合爬虫模块
自动调用Bing和知乎爬虫，合并去重结果。
"""
from typing import List, Dict, Callable, Optional
from web_crawler.crawler import simple_search_crawl
from web_crawler.baidu import baidu_search_crawl
from web_crawler.sogou import sogou_search_crawl
import time

def multi_source_crawl(keyword: str, progress_callback: Optional[Callable[[int], None]] = None) -> List[Dict]:
    """
    聚合Bing、百度、搜狗搜索结果，自动抓取最大可得数据。
    
    Args:
        keyword: 搜索关键词
        progress_callback: 进度回调函数，接受0-100的整数表示进度百分比
        
    Returns:
        合并后的搜索结果列表
    """
    # 初始化进度
    if progress_callback:
        progress_callback(5)
    
    # Bing搜索
    bing_results = simple_search_crawl(keyword)
    if progress_callback:
        progress_callback(30)
        time.sleep(0.1)  # 短暂停顿，便于用户观察进度变化
    
    # 百度搜索
    baidu_results = baidu_search_crawl(keyword)
    if progress_callback:
        progress_callback(60)
        time.sleep(0.1)
    
    # 搜狗搜索
    sogou_results = sogou_search_crawl(keyword)
    if progress_callback:
        progress_callback(85)
        time.sleep(0.1)
    
    # 合并并去重（按title+url）
    seen = set()
    merged = []
    for item in bing_results + baidu_results + sogou_results:
        key = (item.get('title', ''), item.get('url', ''))
        if key not in seen:
            seen.add(key)
            merged.append(item)
    
    # 完成
    if progress_callback:
        progress_callback(100)
    
    return merged
