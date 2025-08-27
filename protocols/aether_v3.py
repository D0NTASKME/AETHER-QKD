import random; import numpy as np; from typing import Dict, Any
from components.sources import prepare_bb84_qubit; from components.channels import apply_lossy_channel
from components.aether_relay import simulate_perfect_bsm
from analysis.aether_analysis_v3 import run_aether_v3_analysis
from locking.core import build_adaptive_braid_v4_gate_list, compile_circuit
from physics.evolution import build_unitary_from_compiled, evolve_state_vector_noisily

def run_aether_v3_protocol(num_qubits, block_size, loss, noise, adversary, controller, seed) -> Dict[str, Any]:
    rng = random.Random(seed)
    stats = controller.run_diagnostics(2000, loss, adversary.strength, rng)
    decision = controller.make_adaptive_decision(stats)
    mode = decision['mode']
    print(f"\n[AETHER Protocol] Starting key exchange in '{mode}' mode.")
    if mode == 'Lock':
        gate_list = build_adaptive_braid_v4_gate_list(block_size, decision['locking_depth'], seed)
        compiled_lock = compile_circuit(block_size, gate_list)
        U_unlock = build_unitary_from_compiled(block_size, compiled_lock).conj().T
        print(f"[AETHER Protocol] Lock engaged. Compiled depth: {len(compiled_lock)}.")

    sifted_data = {'hq_alice':[], 'hq_bob':[], 'rc_alice':[], 'rc_bob':[]}
    num_blocks = num_qubits // block_size; total_leakage = 0.0
    for _ in range(num_blocks):
        ak = [rng.randint(0,1) for _ in range(block_size)]; ab = [rng.randint(0,1) for _ in range(block_size)]
        _, block_leakage = adversary.execute_source_attack(ak, rng); total_leakage += block_leakage
        bk = [rng.randint(0,1) for _ in range(block_size)]; bb = [rng.randint(0,1) for _ in range(block_size)]
        
        psi_init = np.eye(1, dtype=complex)
        for i in range(block_size): psi_init = np.kron(psi_init, prepare_bb84_qubit(ak[i], ab[i])) if i > 0 else prepare_bb84_qubit(ak[i], ab[i])
        eff_ak = ak.copy()
        if mode == 'Lock':
            psi_final = evolve_state_vector_noisily(psi_init, compiled_lock, noise, rng)
            psi_unlocked = U_unlock @ psi_final
            fidelity = np.abs(np.vdot(psi_init, psi_unlocked))**2
            if rng.random() > fidelity: eff_ak[rng.randint(0, block_size - 1)] ^= 1
        
        for i in range(block_size):
            if mode == 'NoLock' and rng.random() < noise: eff_ak[i] ^= 1
            if rng.random() < noise: bk[i] ^= 1
            qa = prepare_bb84_qubit(eff_ak[i], ab[i]); qb = prepare_bb84_qubit(bk[i], bb[i])
            qa = apply_lossy_channel(qa, loss, rng); qb = apply_lossy_channel(qb, loss, rng)
            announce = simulate_perfect_bsm(qa, qb, eff_ak[i], bk[i], ab[i], bb[i], rng)
            
            if announce != "fail":
                if ab[i] == bb[i]:
                    sifted_data['hq_alice'].append(eff_ak[i])
                    if announce in ["psi_minus", "phi_minus"]: sifted_data['hq_bob'].append(1 - bk[i])
                    else: sifted_data['hq_bob'].append(bk[i])
                else: # DIAGNOSTIC STREAM
                    sifted_data['rc_alice'].append(eff_ak[i])
                    # This rule is now used ONLY for QBER calculation, not key.
                    # A consistent (but arbitrary) rule is fine for diagnostics.
                    if (ab[i] == 0): sifted_data['rc_bob'].append(bk[i] if announce in ["psi_minus","phi_plus"] else 1-bk[i])
                    else: sifted_data['rc_bob'].append(bk[i] if announce in ["psi_minus", "phi_minus"] else 1-bk[i])

    leakage_prob = total_leakage / num_blocks if num_blocks > 0 else 0
    final_results = run_aether_v3_analysis(sifted_data, num_qubits, (mode=='Lock'), leakage_prob)
    final_results['mode_chosen'] = mode
    return final_results