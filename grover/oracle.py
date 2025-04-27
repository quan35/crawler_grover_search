"""
Grover算法 Oracle门模块
实现可配置目标态的Oracle门，并可集成到Grover主逻辑。
"""
from qiskit import QuantumCircuit
from typing import List

def create_oracle(n_qubits: int, target_state: List[int]) -> QuantumCircuit:
    """
    构建针对指定目标态的Oracle门。
    :param n_qubits: 量子比特数
    :param target_state: 目标比特串（如[1,0,1]）
    :return: Oracle门电路
    """
    oracle = QuantumCircuit(n_qubits)
    # 对目标比特为0的位先做X门
    for i, bit in enumerate(target_state):
        if bit == 0:
            oracle.x(i)
    # 多控Z门（等效于多控X和Z组合）
    if n_qubits == 1:
        oracle.z(0)
    else:
        oracle.h(n_qubits-1)
        oracle.mcx(list(range(n_qubits-1)), n_qubits-1)
        oracle.h(n_qubits-1)
    # 恢复X门
    for i, bit in enumerate(target_state):
        if bit == 0:
            oracle.x(i)
    oracle.name = "Oracle"
    return oracle
