"""
本地无序数据库管理模块
负责数据的存储、加载、查询，支持与爬虫和聚合模块的数据流集成。
"""
import json
from typing import List, Dict, Optional

class LocalDatabase:
    def __init__(self, db_file: str = "database.json"):
        self.db_file = db_file
        self.data = []
        self.load()

    def load(self):
        try:
            with open(self.db_file, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.data = []

    def save(self):
        with open(self.db_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def add_items(self, items: List[Dict]):
        # 以(title, url)为唯一键，避免重复写入
        existing_keys = set((item.get('title', ''), item.get('url', '')) for item in self.data)
        new_items = []
        for item in items:
            key = (item.get('title', ''), item.get('url', ''))
            if key not in existing_keys:
                existing_keys.add(key)
                new_items.append(item)
        if new_items:
            self.data.extend(new_items)
            self.save()

    def query(self, keyword: str) -> List[Dict]:
        return [item for item in self.data if keyword in item.get("title", "") or keyword in item.get("summary", "")]

    def all(self) -> List[Dict]:
        return self.data
    
    def query_with_ranking(self, keyword: str) -> List[Dict]:
        """实现基于相关性的搜索结果排序"""
        results = self.query(keyword)
        # 根据关键词在标题和摘要中的出现频率、位置等因素计算相关性分数
        return sorted(results, key=lambda x: self._calculate_relevance(x, keyword), reverse=True)
    
    def _calculate_relevance(self, item: Dict, keyword: str) -> float:
        """计算搜索结果与关键词的相关性分数"""
        score = 0.0
        title = item.get('title', '')
        summary = item.get('summary', '')
        
        # 标题中包含关键词权重更高
        if keyword.lower() in title.lower():
            score += 10.0
            # 标题开头包含关键词权重更高
            if title.lower().startswith(keyword.lower()):
                score += 5.0
                
        # 摘要中包含关键词
        if keyword.lower() in summary.lower():
            score += 5.0
            
        return score

