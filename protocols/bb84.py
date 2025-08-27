# protocols/bb84.py

import random
import numpy as np
from typing import Dict, Any

# --- Import all our perfected, modular components ---
from components.sources import prepare_bb84_qubit
from components.channels import apply_lossy_channel
from components.relays import measure_qubit
from analysis.key_rate import secure_key_rate

# Vetted quantum objects needed for the noise model
I2 = np.eye(2, dtype=complex)
PAULI_1Q_LIST = [
    np.eye(2, dtype=complex),
    np.array([[0,1],[1,0]], dtype=complex), # X
    np.array([[0,-1j],[1j,0]], dtype=complex), # Y
    np.array([[1,0],[0,-1]], dtype=complex)  # Z
]

def run_bb84_protocol(
    num_qubits: int,
    channel_loss_prob: float,
    hardware_noise_prob: float,
    source_leakage_prob: float,
    rng_seed: int
) -> Dict[str, Any]:
    """
    A faithful, physically-grounded simulation of the BB84 protocol.
    
    This simulation includes:
    - A rigorous noise model (Pauli errors) for the source.
    - Channel loss.
    - A final key rate calculation that accounts for source leakage, against
      which BB84 has no architectural defense.
    """
    rng = random.Random(rng_seed)
    
    # --- Alice's Preparation ---
    alice_key = [rng.randint(0, 1) for _ in range(num_qubits)]
    alice_bases = [rng.randint(0, 1) for _ in range(num_qubits)]
    
    # --- Bob's Preparation ---
    bob_bases = [rng.randint(0, 1) for _ in range(num_qubits)]
    
    # --- Simulation Loop ---
    sifted_alice, sifted_bob = [], []
    for i in range(num_qubits):
        
        # 1. Alice prepares her ideal qubit
        qubit = prepare_bb84_qubit(alice_key[i], alice_bases[i])
        
        # 2. Hardware noise is applied at the source
        if rng.random() < hardware_noise_prob:
            # Apply a random, non-identity Pauli error (X, Y, or Z)
            error_gate = PAULI_1Q_LIST[rng.randint(1, 3)]
            qubit = error_gate @ qubit
        
        # 3. Qubit travels through the lossy channel
        qubit_after_channel = apply_lossy_channel(qubit, channel_loss_prob, rng)
        
        # 4. Bob measures the qubit
        bob_measurement = measure_qubit(qubit_after_channel, bob_bases[i])

        # 5. Sifting Condition
        if bob_measurement is not None and alice_bases[i] == bob_bases[i]:
            sifted_alice.append(alice_key[i])
            sifted_bob.append(bob_measurement)

    # --- Analysis ---
    sifted_len = len(sifted_alice)
    if sifted_len == 0:
        return {'qber': 0, 'secure_key_rate': 0, 'sifted_key_length': 0}
    
    errors = sum(a != b for a, b in zip(sifted_alice, sifted_bob))
    qber = errors / sifted_len
    sifting_eff = sifted_len / num_qubits
    
    # BB84 has no architectural defense against source leakage, so the full
    # leakage rate must be subtracted from its security.
    skr = secure_key_rate(qber, sifting_eff, leakage_rate=source_leakage_prob)

    return {'qber': qber, 'secure_key_rate': skr, 'sifted_key_length': sifted_len}