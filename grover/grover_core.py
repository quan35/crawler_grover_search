"""
Grover算法主逻辑模块
支持无序数据库的目标搜索，集成Oracle门，支持概率分布可视化。
"""
from qiskit import QuantumCircuit
from qiskit_aer import Aer  # Import Aer from the dedicated package
from qiskit import transpile
from qiskit.visualization import plot_histogram

import numpy as np
from typing import List, Any, Tuple, Dict, Optional
try:
    from .oracle import create_oracle
except ImportError:
    from oracle import create_oracle

def grover_search(database: List[Any], target: Any, shots: int = 1024, auto_iterations: bool = True) -> Tuple[Any, Dict[str, int]]:
    """
    改进的Grover搜索，支持自适应迭代次数
    
    Args:
        database: 要搜索的数据库列表
        target: 要查找的目标项
        shots: 量子模拟运行次数
        auto_iterations: 是否自动优化迭代次数
        
    Returns:
        tuple: (找到的项目, 量子态测量结果)
        
    Raises:
        ValueError: 当目标不在数据库中时抛出
    """
    # 参数验证
    if not database:
        raise ValueError("数据库为空")
    if not target:
        raise ValueError("搜索目标不能为空")
        
    # 计算比特数
    n = int(np.ceil(np.log2(len(database))))
    N = 2 ** n
    
    # 自适应计算最优迭代次数
    if auto_iterations:
        # 对于不同规模的数据库优化迭代次数
        if N <= 4:
            iterations = 1
        elif N <= 16:
            iterations = int(np.floor(np.pi/4 * np.sqrt(N)))
        else:
            # 大规模搜索时略微减少迭代次数，避免过度旋转
            iterations = int(np.floor(np.pi/4 * np.sqrt(N) * 0.9))
    else:
        iterations = int(np.floor(np.pi/4 * np.sqrt(N)))
    
    # 数据编码：补齐到2^n
    pad_db = list(database) + [None] * (N - len(database))
    try:
        idx = pad_db.index(target)
    except ValueError:
        # 如果没找到完全匹配，尝试模糊匹配
        fuzzy_matched = False
        for i, item in enumerate(pad_db):
            if item and target in item:
                idx = i
                fuzzy_matched = True
                break
        if not fuzzy_matched:
            raise ValueError(f"目标'{target}'不在数据库中！")
    
    target_state = [int(x) for x in bin(idx)[2:].zfill(n)]

    # 1. 初始化量子比特
    qc = QuantumCircuit(n, n)
    qc.h(range(n))

    # 2. 构建Oracle门
    oracle = create_oracle(n, target_state)

    # 3. 构建扩散算子（反射）
    def diffusion(n):
        circ = QuantumCircuit(n)
        circ.h(range(n))
        circ.x(range(n))
        circ.h(n-1)
        circ.mcx(list(range(n-1)), n-1)
        circ.h(n-1)
        circ.x(range(n))
        circ.h(range(n))
        circ.name = "Diffusion"
        return circ

    # 4. 应用迭代
    for _ in range(iterations):
        qc.append(oracle.to_gate(), range(n))
        qc.append(diffusion(n).to_gate(), range(n))

    # 5. 测量
    qc.measure(range(n), range(n))

    # 6. 仿真
    backend = Aer.get_backend('qasm_simulator')
    tqc = transpile(qc, backend)
    job = backend.run(tqc, shots=shots)
    result = job.result()
    counts = result.get_counts()

    # 7. 解析结果
    max_state = max(counts, key=counts.get)
    found_idx = int(max_state, 2)
    if found_idx < len(database):
        found = pad_db[found_idx]
    else:
        # 防止索引超出范围
        found = None
        
    return found, counts

def generate_grover_circuit_image(database: List[Any], target: Any, output_path: Optional[str] = None):
    """
    生成Grover量子电路图并保存
    
    Args:
        database: 要搜索的数据库列表
        target: 要查找的目标项
        output_path: 保存路径，如果为None则返回图形对象而不保存
        
    Returns:
        生成的图形对象 (如果output_path为None)
    """
    # 计算比特数
    n = int(np.ceil(np.log2(len(database))))
    N = 2 ** n
    
    # 确定目标状态
    pad_db = list(database) + [None] * (N - len(database))
    try:
        idx = pad_db.index(target)
    except ValueError:
        # 默认使用第一个位置作为示例
        idx = 0
        
    target_state = [int(x) for x in bin(idx)[2:].zfill(n)]
    
    # 构建电路
    qc = QuantumCircuit(n, n)
    qc.h(range(n))
    
    # 添加Oracle
    oracle = create_oracle(n, target_state)
    qc.append(oracle.to_gate(), range(n))
    
    # 添加扩散算子
    circ = QuantumCircuit(n)
    circ.h(range(n))
    circ.x(range(n))
    circ.h(n-1)
    circ.mcx(list(range(n-1)), n-1)
    circ.h(n-1)
    circ.x(range(n))
    circ.h(range(n))
    circ.name = "Diffusion"
    qc.append(circ.to_gate(), range(n))
    
    # 测量
    qc.measure(range(n), range(n))
    
    # 绘制电路
    circuit_diagram = qc.draw(output='mpl', style={'name': True, 'backgroundcolor': '#FFFFFF'})
    
    # 保存或返回
    if output_path:
        circuit_diagram.savefig(output_path, bbox_inches='tight')
    else:
        return circuit_diagram

def simulate_and_plot(database: List[Any], target: Any, shots: int = 1024) -> tuple:
    """
    执行Grover搜索并生成结果分布图
    
    Args:
        database: 要搜索的数据库列表
        target: 要查找的目标项
        shots: 模拟次数
        
    Returns:
        tuple: (找到的目标, 测量结果字典, 图形对象)
    """
    found, counts = grover_search(database, target, shots)
    
    # 生成可视化图形
    fig = plot_histogram(counts, 
                         title='Grover搜索结果分布', 
                         figsize=(10, 6),
                         color='#5899DA',
                         bar_labels=True)
    
    return found, counts, fig
