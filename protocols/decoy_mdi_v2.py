# protocols/decoy_mdi_v3.py

import random
from typing import Dict, Any

from components.sources import prepare_bb84_qubit
from components.channels import apply_lossy_channel
from analysis.finite_key_analysis_v2 import calculate_finite_key_rate

def _bsm_mdi(qa, qb, ak, bk, ab, bb, rng):
    """
    Simulate a simplified Bell-State Measurement (BSM) for MDI-QKD.

    Args:
        qa, qb: Qubit states after channel.
        ak, bk: Alice and Bob's bit values.
        ab, bb: Alice and Bob's bases (0=X, 1=Z).
        rng: random.Random instance.

    Returns:
        "psi_plus", "psi_minus", or "fail"
    """
    if qa is None or qb is None:
        return "fail"

    # BSM only works if bases match
    if ab == bb:
        # Simplified 50% probabilistic outcome
        if ak == bk:
            return "psi_plus" if rng.random() < 0.5 else "fail"
        else:
            return "psi_minus" if rng.random() < 0.5 else "fail"
    return "fail"


def run_decoy_mdi_protocol(
    num_qubits: int,
    channel_loss_prob: float,
    hardware_noise_prob: float,
    source_leakage_prob: float,
    rng_seed: int
) -> Dict[str, Any]:
    """
    Run a simplified decoy-state MDI-QKD simulation.

    Assumptions/Simplifications:
        - Three-state decoy method (signal, weak decoy, vacuum)
        - Only signal-signal rounds are used for key generation
        - BSM is probabilistic, ignores detector inefficiencies
        - Decoy analysis is simplified: finite-key penalty applied, but
          yields are estimated from sifted key only
        - Noise and channel loss are applied independently to each qubit

    Args:
        num_qubits: total qubits generated per party
        channel_loss_prob: probability a qubit is lost in the channel
        hardware_noise_prob: probability of a bit flip in the hardware
        source_leakage_prob: probability Eve has partial source info
        rng_seed: seed for reproducible randomness

    Returns:
        Dictionary containing SKR, QBER, sifting efficiency, etc.
    """
    rng = random.Random(rng_seed)

    # Decoy-state probabilities
    state_probs = {"signal": 0.8, "decoy": 0.1, "vacuum": 0.1}

    # Generate raw keys, bases, and decoy types for Alice and Bob
    alice_key = [rng.randint(0, 1) for _ in range(num_qubits)]
    alice_bases = [rng.randint(0, 1) for _ in range(num_qubits)]
    alice_types = rng.choices(list(state_probs.keys()), weights=list(state_probs.values()), k=num_qubits)

    bob_key = [rng.randint(0, 1) for _ in range(num_qubits)]
    bob_bases = [rng.randint(0, 1) for _ in range(num_qubits)]
    bob_types = rng.choices(list(state_probs.keys()), weights=list(state_probs.values()), k=num_qubits)

    sifted_alice, sifted_bob = [], []

    for i in range(num_qubits):
        # Only signal-signal rounds contribute to the key
        if alice_types[i] != "signal" or bob_types[i] != "signal":
            continue

        # Prepare qubits after hardware noise
        if rng.random() < hardware_noise_prob:
            alice_key[i] ^= 1
        if rng.random() < hardware_noise_prob:
            bob_key[i] ^= 1

        qubit_a = prepare_bb84_qubit(alice_key[i], alice_bases[i])
        qubit_b = prepare_bb84_qubit(bob_key[i], bob_bases[i])

        # Apply channel loss
        qa_channel = apply_lossy_channel(qubit_a, channel_loss_prob, rng)
        qb_channel = apply_lossy_channel(qubit_b, channel_loss_prob, rng)

        # Perform simplified BSM
        bsm_result = _bsm_mdi(qa_channel, qb_channel, alice_key[i], bob_key[i], alice_bases[i], bob_bases[i], rng)

        # Basis matching and BSM success
        if alice_bases[i] == bob_bases[i] and bsm_result != "fail":
            sifted_alice.append(alice_key[i])
            if bsm_result == "psi_minus":
                sifted_bob.append(1 - bob_key[i])
            else:
                sifted_bob.append(bob_key[i])

    sifted_len = len(sifted_alice)
    errors = sum(a != b for a, b in zip(sifted_alice, sifted_bob))

    # Compute finite-key secure key rate
    results = calculate_finite_key_rate(
        sifted_key_len=sifted_len,
        num_errors=errors,
        total_initial_qubits=num_qubits,
        source_leakage_rate=source_leakage_prob
    )

    # Annotate additional metadata for clarity
    results["sifting_efficiency"] = sifted_len / num_qubits
    results["total_qubits"] = num_qubits
    results["qber"] = errors / sifted_len if sifted_len > 0 else None

    return results
