# protocols/mdi.py

import random
from components.sources import prepare_bb84_qubit, STATE_0, STATE_1, STATE_PLUS, STATE_MINUS
from components.channels import apply_lossy_channel
from analysis.key_rate import secure_key_rate

def simulate_bsm(qubit_a, qubit_b, alice_bit, bob_bit, alice_basis, bob_basis, rng):
    if qubit_a is None or qubit_b is None: return "fail"

    # In MDI, the BSM outcome depends on the relationship between the input states.
    # This is a physically grounded model.
    # Case 1: Same basis (Z or X)
    if alice_basis == bob_basis:
        if alice_bit == bob_bit:
            # States are identical (e.g., |0> and |0>). Project to Psi+ or Phi+.
            return "psi_plus" if rng.random() < 0.5 else "fail"
        else:
            # States are orthogonal (e.g., |0> and |1>). Project to Psi- or Phi-.
            return "psi_minus" if rng.random() < 0.5 else "fail"
    # Case 2: Different bases. The outcome is completely random and useless.
    else:
        return "fail"

def run_mdi_protocol(num_qubits, channel_loss_prob, hardware_noise_prob, source_leakage_prob, rng_seed):
    rng = random.Random(rng_seed)
    
    alice_key = [rng.randint(0,1) for _ in range(num_qubits)]
    alice_bases = [rng.randint(0,1) for _ in range(num_qubits)]
    bob_key = [rng.randint(0,1) for _ in range(num_qubits)]
    bob_bases = [rng.randint(0,1) for _ in range(num_qubits)]

    sifted_alice, sifted_bob = [], []

    for i in range(num_qubits):
        qubit_a = prepare_bb84_qubit(alice_key[i], alice_bases[i])
        qubit_b = prepare_bb84_qubit(bob_key[i], bob_bases[i])

        # Apply noise conceptually as a bit flip for this simple model
        if rng.random() < hardware_noise_prob: alice_key[i] = 1 - alice_key[i]
        if rng.random() < hardware_noise_prob: bob_key[i] = 1 - bob_key[i]
        
        qubit_a = apply_lossy_channel(qubit_a, channel_loss_prob, rng)
        qubit_b = apply_lossy_channel(qubit_b, channel_loss_prob, rng)

        announcement = simulate_bsm(qubit_a, qubit_b, alice_key[i], bob_key[i], alice_bases[i], bob_bases[i], rng)

        if announcement != "fail":
            sifted_alice.append(alice_key[i])
            if announcement == "psi_minus":
                sifted_bob.append(1 - bob_key[i])
            elif announcement == "psi_plus":
                sifted_bob.append(bob_key[i])
    
    sifted_len = len(sifted_alice)
    if sifted_len == 0: return {'qber':0, 'secure_key_rate':0, 'sifted_key_length':0}

    errors = sum(a != b for a, b in zip(sifted_alice, sifted_bob))
    qber = errors / sifted_len
    sifting_eff = sifted_len / num_qubits
    skr = secure_key_rate(qber, sifting_eff, leakage_rate=source_leakage_prob)

    return {'qber': qber, 'secure_key_rate': skr, 'sifted_key_length': sifted_len}