import math
def shannon_entropy(p: float) -> float:
    if p <= 0 or p >= 1: return 0.0
    return -p * math.log2(p) - (1 - p) * math.log2(1 - p)

def run_aether_v3_analysis(
    sifted_data: dict, total_qubits: int, is_lock_mode: bool, source_leakage: float
):
    # --- Step 1: Use the Recycled Stream for Diagnostics ---
    rc_alice = sifted_data.get('rc_alice', []); rc_bob = sifted_data.get('rc_bob', [])
    qber_diag = 0.0
    if len(rc_alice) > 20:
        errors_rc = sum(a != b for a, b in zip(rc_alice, rc_bob))
        qber_diag = errors_rc / len(rc_alice)

    # --- Step 2: Calculate Secure Key from the Secret HQ Stream ---
    hq_alice = sifted_data.get('hq_alice', [])
    hq_sifted_len = len(hq_alice)
    sifting_eff = hq_sifted_len / total_qubits if total_qubits > 0 else 0.0
    
    leakage = source_leakage if not is_lock_mode else 0.0
    
    # Costs are determined by the hyper-accurate QBER from the diagnostic stream
    eve_info = shannon_entropy(qber_diag) + shannon_entropy(leakage)
    bob_cost = shannon_entropy(qber_diag) * 1.1 # Error correction
    
    rate = sifting_eff * (1 - eve_info - bob_cost)
    
    return {'diagnostic_qber': qber_diag, 'secure_key_rate': max(0.0, rate), 'sifted_key_length': hq_sifted_len}