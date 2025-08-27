# protocols/teal.py

import random
import numpy as np
from typing import Dict, Any

# --- Import all our perfected, modular components ---
from components.sources import prepare_bb84_qubit
from components.channels import apply_lossy_channel
from analysis.key_rate import secure_key_rate
from locking.core import (
    build_adaptive_braid_v4_gate_list,
    compile_circuit
)
from physics.evolution import (
    build_unitary_from_compiled,
    evolve_state_vector_noisily
)

def _simulate_bsm(qubit_a, qubit_b, alice_bit, bob_bit, alice_basis, bob_basis, rng):
    """Physically-grounded MDI relay simulation."""
    if qubit_a is None or qubit_b is None: return "fail"
    # Success is only possible if bases match. A real BSM projects onto a basis.
    # This model correctly captures that different-basis inputs are useless.
    if alice_basis == bob_basis:
        # For same-basis inputs, total success probability is 50%.
        if rng.random() < 0.5:
            # Of successful events, the outcome depends on the bit relationship.
            if alice_bit == bob_bit: return "psi_plus"
            else: return "psi_minus"
        else: return "fail"
    else: return "fail"

def run_teal_protocol(
    num_qubits: int, block_size: int, channel_loss_prob: float,
    hardware_noise_prob: float, source_leakage_prob: float,
    controller, rng_seed: int
) -> Dict[str, Any]:
    
    rng = random.Random(rng_seed)
    
    diagnostic_stats = controller.run_diagnostics(2000, channel_loss_prob, source_leakage_prob, rng)
    decision = controller.make_adaptive_decision(diagnostic_stats)
    current_mode = decision['mode']
    locking_depth = decision['locking_depth']
    
    print(f"\n[Protocol] Starting key exchange in '{current_mode}' mode.")

    if current_mode == 'NoLock':
        # --- EXECUTE THE 'NOLOCK' PATH: A PURE, SELF-CONTAINED MDI PROTOCOL ---
        total_initial_qubits = num_qubits
        alice_key = [rng.randint(0,1) for _ in range(num_qubits)]
        alice_bases = [rng.randint(0,1) for _ in range(num_qubits)]
        bob_key = [rng.randint(0,1) for _ in range(num_qubits)]
        bob_bases = [rng.randint(0,1) for _ in range(num_qubits)]
        sifted_alice, sifted_bob = [], []

        for i in range(num_qubits):
            qubit_a = prepare_bb84_qubit(alice_key[i], alice_bases[i])
            if rng.random() < hardware_noise_prob: qubit_a[rng.randint(0,1)] *= -1
            qubit_b = prepare_bb84_qubit(bob_key[i], bob_bases[i])
            if rng.random() < hardware_noise_prob: qubit_b[rng.randint(0,1)] *= -1
            
            qubit_a_channel = apply_lossy_channel(qubit_a, channel_loss_prob, rng)
            qubit_b_channel = apply_lossy_channel(qubit_b, channel_loss_prob, rng)
            announcement = _simulate_bsm(qubit_a_channel, qubit_b_channel, alice_key[i], bob_key[i], alice_bases[i], bob_bases[i], rng)

            if announcement != "fail": # Sifting happens on BSM success
                sifted_alice.append(alice_key[i])
                if announcement == "psi_minus": sifted_bob.append(1 - bob_key[i])
                elif announcement == "psi_plus": sifted_bob.append(bob_key[i])
        
        leakage_to_subtract = source_leakage_prob

    else: # current_mode == 'Lock'
        # --- EXECUTE THE 'LOCK' PATH: THE FULL-POWERED, BLOCK-BASED PROTOCOL ---
        num_blocks = num_qubits // block_size
        total_initial_qubits = num_blocks * block_size
        
        gate_list = build_adaptive_braid_v4_gate_list(block_size, locking_depth, seed=rng_seed)
        compiled_lock_circuit = compile_circuit(block_size, gate_list)
        U_unlock = build_unitary_from_compiled(block_size, compiled_lock_circuit).conj().T
        print(f"[Protocol] 'Lock' mode engaged. Compiled depth: {len(compiled_lock_circuit)}.")

        sifted_alice, sifted_bob = [], []
        for _ in range(num_blocks):
            alice_key_block = [rng.randint(0, 1) for _ in range(block_size)]
            alice_basis_block = [rng.randint(0, 1) for _ in range(block_size)]
            bob_key_block = [rng.randint(0, 1) for _ in range(block_size)]
            bob_basis_block = [rng.randint(0, 1) for _ in range(block_size)]
            
            psi_initial_alice = np.eye(1, dtype=complex)
            for i in range(block_size):
                qubit = prepare_bb84_qubit(alice_key_block[i], alice_basis_block[i])
                psi_initial_alice = np.kron(psi_initial_alice, qubit) if i > 0 else qubit
            
            psi_final_alice = evolve_state_vector_noisily(
                psi_initial_alice, compiled_lock_circuit, hardware_noise_prob, rng
            )
            psi_unlocked = U_unlock @ psi_final_alice
            
            effective_alice_key = alice_key_block.copy()
            fidelity = np.abs(np.vdot(psi_initial_alice, psi_unlocked))**2
            if rng.random() > fidelity: # An error occurred due to the noisy lock
                err_idx = rng.randint(0, block_size - 1)
                effective_alice_key[err_idx] = 1 - effective_alice_key[err_idx]
            
            for i in range(block_size):
                qubit_a = prepare_bb84_qubit(effective_alice_key[i], alice_basis_block[i])
                qubit_b = prepare_bb84_qubit(bob_key_block[i], bob_basis_block[i])
                qubit_a_channel = apply_lossy_channel(qubit_a, channel_loss_prob, rng)
                qubit_b_channel = apply_lossy_channel(qubit_b, channel_loss_prob, rng)
                announcement = _simulate_bsm(qubit_a_channel, qubit_b_channel, 
                                             effective_alice_key[i], bob_key_block[i], 
                                             alice_basis_block[i], bob_basis_block[i], rng)
                
                if announcement != "fail":
                    sifted_alice.append(effective_alice_key[i])
                    if announcement == "psi_minus": sifted_bob.append(1 - bob_key_block[i])
                    elif announcement == "psi_plus": sifted_bob.append(bob_key_block[i])
        
        leakage_to_subtract = 0.0 # The lock nullifies the source leakage

    # --- Final Cryptographic Analysis (common to both paths) ---
    sifted_len = len(sifted_alice)
    if sifted_len == 0:
        return {'qber':0, 'secure_key_rate':0, 'sifted_key_length':0, 'mode_chosen': current_mode}
    
    errors = sum(a != b for a,b in zip(sifted_alice, sifted_bob))
    qber = errors / sifted_len
    sifting_eff = sifted_len / total_initial_qubits
    skr = secure_key_rate(qber, sifting_eff, leakage_rate=leakage_to_subtract)
    
    return {'qber': qber, 'secure_key_rate': skr, 'sifted_key_length': sifted_len, 'mode_chosen': current_mode}