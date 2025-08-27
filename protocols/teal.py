# protocols/teal.py
"""
TEAL Protocol Implementation for AETHER.
Supports both 'Lock' and 'NoLock' adaptive modes with block-based qubit processing.
"""

import random
import numpy as np
from typing import Dict, Any

from components.sources import prepare_bb84_qubit
from components.channels import apply_lossy_channel
from analysis.finite_key_analysis_v2 import calculate_finite_key_rate
from locking.core import build_adaptive_braid_v4_gate_list, compile_circuit
from physics.evolution import build_unitary_from_compiled, evolve_state_vector_noisily


def _bsm_mdi(qa, qb, ak, bk, ab, bb, rng):
    """
    Simplified Bell-State Measurement (MDI).
    Returns 'psi_plus', 'psi_minus', or 'fail'.
    """
    if qa is None or qb is None:
        return "fail"
    if ab == bb:
        if ak == bk and rng.random() < 0.5:
            return "psi_plus"
        elif ak != bk and rng.random() < 0.5:
            return "psi_minus"
        else:
            return "fail"
    else:
        return "fail"


def run_teal_protocol(
    num_qubits: int,
    block_size: int,
    channel_loss_prob: float,
    hardware_noise_prob: float,
    source_leakage_prob: float,
    controller,
    rng_seed: int
) -> Dict[str, Any]:
    """
    Run the TEAL adaptive QKD protocol.
    - num_qubits: total qubits to simulate
    - block_size: number of qubits per adaptive block
    - channel_loss_prob: probability of qubit loss in channel
    - hardware_noise_prob: per-qubit hardware error probability
    - source_leakage_prob: fraction of source-side leakage
    - controller: AETHER controller object (makes adaptive mode decisions)
    - rng_seed: random number seed for reproducibility
    """
    rng = random.Random(rng_seed)
    total_qubits = num_qubits

    # --- Step 1: Controller diagnostics & adaptive decision ---
    stats = controller.run_diagnostics(2000, channel_loss_prob, source_leakage_prob, rng)
    decision = controller.make_adaptive_decision(stats)
    mode = decision['mode']
    print(f"\n[TEAL Protocol] Starting in '{mode}' mode.")

    # --- Step 2: Prepare locking unitary if in 'Lock' mode ---
    if mode == 'Lock':
        gate_list = build_adaptive_braid_v4_gate_list(block_size, decision['locking_depth'], rng_seed)
        compiled_lock = compile_circuit(block_size, gate_list)
        U_unlock = build_unitary_from_compiled(block_size, compiled_lock).conj().T
        print(f"[TEAL Protocol] Lock engaged. Compiled depth: {len(compiled_lock)}.")

    # --- Step 3: Process qubits in blocks ---
    sifted_alice, sifted_bob = [], []
    num_blocks = num_qubits // block_size

    for _ in range(num_blocks):
        # Random key and basis for each qubit in the block
        ak = [rng.randint(0, 1) for _ in range(block_size)]
        ab = [rng.randint(0, 1) for _ in range(block_size)]
        bk = [rng.randint(0, 1) for _ in range(block_size)]
        bb = [rng.randint(0, 1) for _ in range(block_size)]

        # Prepare initial state vector for the block
        psi_init = np.eye(1, dtype=complex)
        for i in range(block_size):
            psi_init = np.kron(psi_init, prepare_bb84_qubit(ak[i], ab[i])) if i > 0 else prepare_bb84_qubit(ak[i], ab[i])

        eff_ak = ak.copy()

        # --- Step 3a: Apply locking unitary if required ---
        if mode == 'Lock':
            psi_final = evolve_state_vector_noisily(psi_init, compiled_lock, hardware_noise_prob, rng)
            psi_unlocked = U_unlock @ psi_final
            fidelity = np.abs(np.vdot(psi_init, psi_unlocked))**2
            if rng.random() > fidelity:
                eff_ak[rng.randint(0, block_size - 1)] ^= 1  # flip one qubit randomly

        # --- Step 3b: Apply per-qubit noise and channel losses ---
        for i in range(block_size):
            if mode == 'NoLock' and rng.random() < hardware_noise_prob:
                eff_ak[i] ^= 1
            if rng.random() < hardware_noise_prob:
                bk[i] ^= 1

            qa = prepare_bb84_qubit(eff_ak[i], ab[i])
            qb = prepare_bb84_qubit(bk[i], bb[i])

            qa = apply_lossy_channel(qa, channel_loss_prob, rng)
            qb = apply_lossy_channel(qb, channel_loss_prob, rng)

            announce = _bsm_mdi(qa, qb, eff_ak[i], bk[i], ab[i], bb[i], rng)

            if announce != "fail":
                sifted_alice.append(eff_ak[i])
                if announce == "psi_minus":
                    sifted_bob.append(1 - bk[i])
                else:
                    sifted_bob.append(bk[i])

    # --- Step 4: Compute finite-key secure rate ---
    sifted_len = len(sifted_alice)
    errors = sum(a != b for a, b in zip(sifted_alice, sifted_bob))
    leakage_final = source_leakage_prob if mode == 'NoLock' else 0.0

    results = calculate_finite_key_rate(
        sifted_len,
        errors,
        total_qubits,
        source_leakage_rate=leakage_final
    )
    results['mode_chosen'] = mode

    return results
