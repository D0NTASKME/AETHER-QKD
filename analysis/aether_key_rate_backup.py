# analysis/aether_key_rate.py

import math
from typing import Dict

def shannon_entropy(p: float) -> float:
    """Calculates the binary Shannon entropy H(p)."""
    if p <= 0 or p >= 1: return 0.0
    return -p * math.log2(p) - (1 - p) * math.log2(1 - p)

def calculate_secure_key_rates(
    sifted_data: Dict[str, list],
    total_initial_qubits: int,
    leakage_rate: float = 0.0,
    error_correction_efficiency: float = 1.1
) -> Dict[str, float]:
    """
    Calculates the secure key rates for the AETHER protocol from its two streams.
    This is the advanced analysis engine.
    """
    
    # --- Analysis of the High-Quality (Matched Basis) Stream ---
    key_hq_alice = sifted_data['hq_alice']
    key_hq_bob = sifted_data['hq_bob']
    sifted_len_hq = len(key_hq_alice)
    
    qber_hq = 0.0
    skr_hq = 0.0
    
    if sifted_len_hq > 0:
        errors_hq = sum(a != b for a, b in zip(key_hq_alice, key_hq_bob))
        qber_hq = errors_hq / sifted_len_hq
        sifting_eff_hq = sifted_len_hq / total_initial_qubits
        
        # This stream is vulnerable to the full source leakage
        eve_info_hq = shannon_entropy(qber_hq) + shannon_entropy(leakage_rate)
        bob_cost_hq = error_correction_efficiency * shannon_entropy(qber_hq)
        rate_hq = sifting_eff_hq * (1 - eve_info_hq - bob_cost_hq)
        skr_hq = max(0.0, rate_hq)

    # --- Analysis of the Recycled (Mismatched Basis) Stream ---
    key_rc_alice = sifted_data['rc_alice']
    key_rc_bob = sifted_data['rc_bob']
    sifted_len_rc = len(key_rc_alice)

    qber_rc = 0.0
    skr_rc = 0.0

    if sifted_len_rc > 0:
        errors_rc = sum(a != b for a, b in zip(key_rc_alice, key_rc_bob))
        qber_rc = errors_rc / sifted_len_rc
        sifting_eff_rc = sifted_len_rc / total_initial_qubits

        # In the mismatched basis, the correlation is weaker. The theoretical
        # mutual information I(A:B) is less than 1. For a simple model,
        # we can say the maximum achievable rate is lower. Let's use a factor.
        # This is a placeholder for a much more complex mutual information calculation.
        max_rate_recycled = 0.5 # bits of info per sifted bit
        
        eve_info_rc = shannon_entropy(qber_rc)
        bob_cost_rc = error_correction_efficiency * shannon_entropy(qber_rc)
        rate_rc = sifting_eff_rc * (max_rate_recycled - eve_info_rc - bob_cost_rc)
        skr_rc = max(0.0, rate_rc)
        
    # --- Final Results ---
    total_skr = skr_hq + skr_rc
    
    return {
        'qber_hq': qber_hq,
        'secure_key_rate_hq': skr_hq,
        'qber_recycled': qber_rc,
        'secure_key_rate_recycled': skr_rc,
        'total_secure_key_rate': total_skr
    }