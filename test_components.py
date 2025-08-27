# test_components.py

import unittest
import numpy as np
import random

# --- Import the components we are testing ---
from components.sources import prepare_bb84_qubit, STATE_0, STATE_1, STATE_PLUS, STATE_MINUS
from components.channels import apply_lossy_channel
from components.relays import measure_qubit

class TestQuantumComponents(unittest.TestCase):
    """
    A rigorous unit test suite for the foundational physical components
    of the TEAL simulator.
    """

    def test_source_preparation(self):
        """Verifies that the source produces the correct quantum states."""
        print("\n\n--- Testing Component: sources.py ---")
        # Test Case 1: Bit 0, Z-basis should be |0>
        state = prepare_bb84_qubit(0, 0)
        np.testing.assert_allclose(state, STATE_0)
        
        # Test Case 2: Bit 1, Z-basis should be |1>
        state = prepare_bb84_qubit(1, 0)
        np.testing.assert_allclose(state, STATE_1)

        # Test Case 3: Bit 0, X-basis should be |+>
        state = prepare_bb84_qubit(0, 1)
        np.testing.assert_allclose(state, STATE_PLUS)

        # Test Case 4: Bit 1, X-basis should be |->
        state = prepare_bb84_qubit(1, 1)
        np.testing.assert_allclose(state, STATE_MINUS)
        
        print("Source Preparation: PASSED")

    def test_lossy_channel(self):
        """Verifies the statistical behavior of the lossy channel."""
        print("\n--- Testing Component: channels.py ---")
        rng = random.Random(123)
        num_trials = 10000
        loss_prob = 0.3
        lost_count = 0
        
        for _ in range(num_trials):
            photon = apply_lossy_channel("photon", loss_prob, rng)
            if photon is None:
                lost_count += 1
        
        measured_loss_rate = lost_count / num_trials
        # We expect the measured rate to be very close to the true rate.
        # assertAlmostEqual checks if the values are close within a certain number of decimal places.
        self.assertAlmostEqual(measured_loss_rate, loss_prob, places=2, 
                               msg="Channel loss rate is not statistically correct.")
        print("Lossy Channel: PASSED")

    def test_measurement_relay(self):
        """Verifies the measurement logic against quantum mechanical predictions."""
        print("\n--- Testing Component: relays.py ---")
        rng = random.Random(456)
        num_trials = 10000

        # Test Case 1: Measuring in the correct basis should be deterministic.
        # Measuring |+> in the X-basis (1) should always yield 0.
        outcomes_correct_basis = [measure_qubit(STATE_PLUS, 1) for _ in range(num_trials)]
        self.assertEqual(sum(outcomes_correct_basis), 0, 
                         msg="Measurement in the correct basis was not deterministic.")
        print("Measurement (Correct Basis): PASSED")

        # Test Case 2: Measuring in the wrong basis should be 50/50 random.
        # Measuring |+> in the Z-basis (0) should yield 0 about 50% of the time.
        outcomes_wrong_basis = [measure_qubit(STATE_PLUS, 0, rng) for _ in range(num_trials)]
        prob_0 = outcomes_wrong_basis.count(0) / num_trials
        self.assertAlmostEqual(prob_0, 0.5, places=2,
                               msg="Measurement in the wrong basis is not 50/50.")
        print("Measurement (Incorrect Basis): PASSED")

if __name__ == '__main__':
    unittest.main()