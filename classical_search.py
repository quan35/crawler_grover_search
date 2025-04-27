"""
经典搜索算法实现模块
用于与Grover量子搜索进行效率对比。
"""
from typing import List, Any

def classical_linear_search(database: List[Any], target: Any) -> int:
    """
    经典线性搜索算法。
    :param database: 无序数据库（列表）
    :param target: 搜索目标
    :return: 目标索引（未找到返回-1）
    """
    for idx, item in enumerate(database):
        if item == target:
            return idx
    return -1

# 用于性能测试和对比
if __name__ == "__main__":
    db = ["apple", "banana", "os", "linux", "windows"]
    target = "os"
    idx = classical_linear_search(db, target)
    print(f"Target '{target}' found at index: {idx}")
