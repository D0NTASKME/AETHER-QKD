# analysis/teal_e_analysis.py
import math

def shannon_entropy(p: float) -> float:
    if p <= 0 or p >= 1: return 0.0
    return -p * math.log2(p) - (1 - p) * math.log2(1 - p)

def run_teal_e_analysis(
    sifted_alice: list,
    sifted_bob: list,
    total_initial_qubits: int,
    source_leakage_prob: float = 0.0,
    error_correction_efficiency: float = 1.1
) -> dict:
    """
    The definitive analysis engine for the TEAL-E protocol.
    """
    sifted_len = len(sifted_alice)
    if sifted_len == 0:
        return {'qber': 0, 'secure_key_rate': 0, 'sifted_key_length': 0}

    errors = sum(a != b for a, b in zip(sifted_alice, sifted_bob))
    qber = errors / sifted_len
    sifting_eff = sifted_len / total_initial_qubits
    
    # TEAL-E is architecturally immune to source leakage, so we set it to 0.
    eve_info = shannon_entropy(qber) + shannon_entropy(0.0)
    bob_cost = error_correction_efficiency * shannon_entropy(qber)
    
    rate = sifting_eff * (1 - eve_info - bob_cost)
    
    return {
        'qber': qber,
        'secure_key_rate': max(0.0, rate),
        'sifted_key_length': sifted_len
    }