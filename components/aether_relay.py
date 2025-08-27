# components/aether_relay.py

import random
from typing import Dict, Any

def simulate_perfect_bsm(
    qubit_a,
    qubit_b,
    alice_bit: int,
    bob_bit: int,
    alice_basis: int,
    bob_basis: int,
    rng: random.Random
) -> str:
    """
    Simulates a perfect, next-generation Bell State Measurement (BSM) device.

    This advanced relay can distinguish all four Bell states with 100% efficiency.
    This is the theoretical maximum performance for an MDI relay.
    """
    if qubit_a is None or qubit_b is None:
        return "fail" # Photon loss is the only reason for failure

    # The BSM outcome is deterministically determined by the input states.
    if alice_basis == bob_basis: # Matched Bases
        if alice_bit == bob_bit:
            # e.g., |0>|0> or |+>|+>. These project to the Phi+ or Psi+ states.
            # We will assign them to two distinct success types.
            return "phi_plus" if rng.random() < 0.5 else "psi_plus"
        else: # alice_bit != bob_bit
            # e.g., |0>|1> or |+>|->. These project to the Phi- or Psi- states.
            return "phi_minus" if rng.random() < 0.5 else "psi_minus"
            
    else: # Mismatched Bases
        # Even with mismatched bases, the two-qubit state is always one of the four
        # Bell states in a rotated basis. A perfect BSM can always identify it.
        # The specific outcome determines the correlation. For simplicity, we
        # assign them to the four outcomes with equal probability.
        outcome = rng.random()
        if outcome < 0.25: return "psi_minus"
        elif outcome < 0.50: return "psi_plus"
        elif outcome < 0.75: return "phi_minus"
        else: return "phi_plus"