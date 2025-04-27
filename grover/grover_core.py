"""
Grover算法主逻辑模块
支持无序数据库的目标搜索，集成Oracle门，支持概率分布可视化。
"""
from qiskit import QuantumCircuit
try:
    from qiskit.providers.aer import Aer
except ImportError:
    from qiskit_aer import Aer
from qiskit import transpile

import numpy as np
from typing import List, Any
from .oracle import create_oracle

def grover_search(database: List[Any], target: Any, shots: int = 1024):
    """
    对无序数据库database，利用Grover算法搜索目标target。
    :param database: 数据库（如字符串、数字等）
    :param target: 目标内容
    :param shots: 采样次数
    :param visualize: 是否可视化概率分布
    :return: 搜索到的目标及概率分布
    """
    n = int(np.ceil(np.log2(len(database))))
    N = 2 ** n
    # 数据编码：补齐到2^n
    pad_db = list(database) + [None] * (N - len(database))
    try:
        idx = pad_db.index(target)
    except ValueError:
        raise ValueError("目标不在数据库中！")
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

    # 4. 计算迭代次数
    iterations = int(np.floor(np.pi/4 * np.sqrt(N)))
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
    found = pad_db[found_idx]
    return found, counts
