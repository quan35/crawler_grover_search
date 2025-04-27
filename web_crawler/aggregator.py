"""
网络内容聚合与去重模块
将爬虫抓取的内容聚合、清洗、去重，便于后续数据库管理与搜索。
"""
from typing import List, Dict
import pandas as pd

def aggregate_and_deduplicate(data: List[Dict]) -> List[Dict]:
    """
    聚合并去重爬取结果。
    """
    # 改进去重：按(title, url)去重
    seen = set()
    unique_data = []
    for item in data:
        key = (item.get('title', ''), item.get('url', ''))
        if key not in seen:
            seen.add(key)
            unique_data.append(item)
    return unique_data

