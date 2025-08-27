# components/relays.py

import numpy as np
import random

# Import state definitions from the sources module
from components.sources import prepare_bb84_qubit, STATE_0, STATE_1, STATE_PLUS, STATE_MINUS

def measure_qubit(photon_state, basis_choice: int, rng=None):
    """
    Simulates the measurement of a single qubit in one of the BB84 bases.
    This is the final, vetted version compatible with the full test suite.
    """
    if photon_state is None:
        return None

    if basis_choice not in [0, 1]:
        raise ValueError(f"Invalid basis_choice: {basis_choice}. Must be 0 or 1.")

    # Use the provided random generator if it exists, otherwise use the global one.
    rand_gen = rng if rng is not None else random
    
    # Select the measurement basis vectors
    if basis_choice == 0:  # Z-basis
        basis_0_vector = STATE_0
    else:  # X-basis
        basis_0_vector = STATE_PLUS

    # Calculate the probability of the '0' outcome
    inner_product = np.vdot(basis_0_vector, photon_state)
    prob_0 = np.abs(inner_product)**2

    # Simulate the quantum collapse using the specified random generator
    if rand_gen.random() < prob_0:
        return 0
    else:
        return 1

# The __main__ block is no longer needed as we now have a dedicated test file.
# You can delete it or leave it, but we will rely on test_components.py from now on.