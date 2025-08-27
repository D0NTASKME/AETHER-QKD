# analysis/aether_analysis.py

import math
from typing import Dict

def shannon_entropy(p: float) -> float:
    if p <= 0 or p >= 1: return 0.0
    return -p * math.log2(p) - (1 - p) * math.log2(1 - p)

def run_aether_analysis(
    sifted_data: Dict[str, list],
    total_initial_qubits: int,
    is_lock_mode: bool,
    source_leakage_prob: float,
    error_correction_efficiency: float = 1.1
) -> Dict[str, float]:
    """
    The definitive analysis engine for the AETHER protocol. It correctly
    processes the dual information streams to calculate a final secure key rate.
    """
    
    # --- Step 1: Analyze the Diagnostic Stream (Recycled Bits) ---
    rc_alice = sifted_data.get('rc_alice', [])
    rc_bob = sifted_data.get('rc_bob', [])
    
    qber_from_diagnostics = 0.0
    if len(rc_alice) > 20: # Require a minimum number of samples for a good estimate
        errors_rc = sum(a != b for a, b in zip(rc_alice, rc_bob))
        qber_from_diagnostics = errors_rc / len(rc_alice)

    # --- Step 2: Analyze the Secret Stream (High-Quality Bits) ---
    hq_alice = sifted_data.get('hq_alice', [])
    hq_sifted_length = len(hq_alice)
    
    # --- Step 3: Calculate the Final Secure Key Rate ---
    sifting_efficiency = hq_sifted_length / total_initial_qubits if total_initial_qubits > 0 else 0
    
    # The lock's purpose is to nullify the source leakage.
    effective_leakage = source_leakage_prob if not is_lock_mode else 0.0
    
    # Information Eve could have from channel noise, precisely estimated by the diagnostic stream.
    eve_channel_info = shannon_entropy(qber_from_diagnostics)
    
    # Information Eve could have from a source attack.
    eve_leakage_info = shannon_entropy(effective_leakage)
    
    # Information Bob needs to correct errors in the secret stream.
    bob_error_correction_cost = error_correction_efficiency * shannon_entropy(qber_from_diagnostics)

    # The final rate is the efficiency of the secret stream, reduced by all costs.
    rate = sifting_efficiency * (1 - eve_channel_info - eve_leakage_info - bob_error_correction_cost)
    
    skr = max(0.0, rate)
    
    return {
        'diagnostic_qber': qber_from_diagnostics,
        'secure_key_rate': skr,
        'sifted_key_length': hq_sifted_length
    }