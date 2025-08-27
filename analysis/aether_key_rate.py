# analysis/aether_key_rate.py
import math
def shannon_entropy(p: float) -> float:
    if p <= 0 or p >= 1: return 0.0
    return -p * math.log2(p) - (1 - p) * math.log2(1 - p)

def calculate_aether_key_rate(qber_from_diagnostics, hq_sifted_len, total_qubits, leakage_rate=0.0):
    sifting_eff = hq_sifted_len / total_qubits
    eve_info = shannon_entropy(qber_from_diagnostics) + shannon_entropy(leakage_rate)
    bob_cost = shannon_entropy(qber_from_diagnostics) * 1.1 # Error correction efficiency
    rate = sifting_eff * (1 - eve_info - bob_cost)
    return {'qber': qber_from_diagnostics, 'secure_key_rate': max(0.0, rate), 'sifted_key_length': hq_sifted_len}