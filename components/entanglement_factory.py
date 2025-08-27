# components/entanglement_factory.py

import random
from typing import List, Tuple

from components.sources import prepare_bb84_qubit
from components.channels import apply_lossy_channel

class EntanglementFactory:
    """
    An industry-grade simulation of an MDI-based entanglement source.
    This is the core engine of the TEAL-E and AETHER protocols.
    """

    def __init__(self, alice_channel_loss, bob_channel_loss, bsm_success_prob=0.5):
        self.alice_channel_loss = alice_channel_loss
        self.bob_channel_loss = bob_channel_loss
        self.bsm_success_prob = bsm_success_prob
        print("Entanglement Factory initialized.")

    def _simulate_bsm(self, qubit_a, qubit_b, rng):
        if qubit_a is None or qubit_b is None: return False
        return rng.random() < self.bsm_success_prob

    def generate_entangled_pairs(self, num_attempts: int, rng: random.Random) -> List[bool]:
        """
        Runs the MDI process to generate a "bank" of virtual entangled pairs.

        Returns:
            A list of booleans of length `num_attempts`, where `True` indicates
            a successfully generated entangled pair for that round.
        """
        print(f"[Factory] Attempting to generate {num_attempts} entangled pairs...")
        
        successful_pairs = []
        for _ in range(num_attempts):
            # For entanglement generation, Alice and Bob can use fixed, known states.
            # e.g., Alice always sends |0> and Bob always sends |+>
            qubit_a = prepare_bb84_qubit(0, 0)
            qubit_b = prepare_bb84_qubit(0, 1)

            qubit_a_after_channel = apply_lossy_channel(qubit_a, self.alice_channel_loss, rng)
            qubit_b_after_channel = apply_lossy_channel(qubit_b, self.bob_channel_loss, rng)

            if self._simulate_bsm(qubit_a_after_channel, qubit_b_after_channel, rng):
                successful_pairs.append(True)
            else:
                successful_pairs.append(False)
        
        print(f"[Factory] Successfully generated {sum(successful_pairs)} pairs.")
        return successful_pairs