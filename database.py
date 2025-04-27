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

