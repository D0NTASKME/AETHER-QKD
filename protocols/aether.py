# protocols/aether.py

import random
import numpy as np
from typing import Dict, Any

from components.sources import prepare_bb84_qubit
from components.channels import apply_lossy_channel
from analysis.aether_analysis import run_aether_analysis
from locking.core import build_adaptive_braid_v4_gate_list, compile_circuit
from physics.evolution import build_unitary_from_compiled, evolve_state_vector_noisily

def _simulate_bsm(qubit_a, qubit_b, alice_bit, bob_bit, alice_basis, bob_basis, rng):
    if qubit_a is None or qubit_b is None: return "fail"
    if alice_basis == bob_basis:
        return "psi_plus" if alice_bit == bob_bit else "psi_minus"
    else:
        return "phi_plus" if alice_bit == bob_bit else "phi_minus"

def run_aether_protocol(
    num_qubits: int, block_size: int, loss: float,
    noise: float, adversary, controller, seed: int
) -> Dict[str, Any]:
    rng = random.Random(seed)
    total_qubits = num_qubits
    
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
    num_blocks = num_qubits // block_size
    total_leakage = 0.0
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
            announce = _simulate_bsm(qa, qb, eff_ak[i], bk[i], ab[i], bb[i], rng)
            
            if announce != "fail":
                if ab[i] == bb[i]:
                    sifted_data['hq_alice'].append(eff_ak[i])
                    if announce in ["psi_minus", "phi_minus"]: sifted_data['hq_bob'].append(1 - bk[i])
                    else: sifted_data['hq_bob'].append(bk[i])
                else:
                    sifted_data['rc_alice'].append(eff_ak[i])
                    if (ab[i]==0): # Z-X
                        sifted_data['rc_bob'].append(bk[i] if announce in ["psi_minus","phi_plus"] else 1-bk[i])
                    else: # X-Z
                        sifted_data['rc_bob'].append(bk[i] if announce in ["psi_minus", "phi_minus"] else 1-bk[i])

    leakage_prob = total_leakage / num_blocks if num_blocks > 0 else 0
    
    # *** BUG FIX IS HERE: Correctly pass the argument ***
    final_results = run_aether_analysis(
        sifted_data=sifted_data,
        total_initial_qubits=total_qubits,
        is_lock_mode=(mode=='Lock'),
        source_leakage_prob=leakage_prob
    )
    final_results['mode_chosen'] = mode
    return final_results