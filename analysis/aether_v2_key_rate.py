# analysis/aether_v2_key_rate.py

import math
from typing import Dict

def shannon_entropy(p: float) -> float:
    if p <= 0 or p >= 1: return 0.0
    return -p * math.log2(p) - (1 - p) * math.log2(1 - p)

def calculate_aether_v2_secure_key_rates(
    sifted_data: Dict[str, list],
    total_initial_qubits: int,
    leakage_rate: float = 0.0,
    error_correction_efficiency: float = 1.1
) -> Dict[str, float]:
    """
    Calculates the secure key rates for the AETHER v2 protocol.
    This version assumes a perfect BSM, meaning the recycled stream bits
    are now also high quality.
    """
    
    # --- In AETHER v2, all sifted bits are high quality. ---
    # We can combine the streams for analysis.
    key_alice = sifted_data['hq_alice'] + sifted_data['rc_alice']
    key_bob = sifted_data['hq_bob'] + sifted_data['rc_bob']
    sifted_len = len(key_alice)
    
    qber = 0.0
    skr = 0.0
    
    if sifted_len > 0:
        errors = sum(a != b for a, b in zip(key_alice, key_bob))
        qber = errors / sifted_len
        sifting_eff = sifted_len / total_initial_qubits
        
        eve_info = shannon_entropy(qber) + shannon_entropy(leakage_rate)
        bob_cost = error_correction_efficiency * shannon_entropy(qber)
        rate = sifting_eff * (1 - eve_info - bob_cost)
        skr = max(0.0, rate)
        
    return {
        'qber': qber,
        'secure_key_rate': skr,
        'sifted_key_length': sifted_len
    }