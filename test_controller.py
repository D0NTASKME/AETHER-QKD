# test_controller.py

import unittest
import random

# --- Import the component we are testing ---
from controller.immune_system import TEALController
# We also need the physical components for the controller's internal simulation
from components.sources import prepare_bb84_qubit
from components.channels import apply_lossy_channel

class TestTEALController(unittest.TestCase):
    """
    A rigorous unit test suite for the TEAL protocol's adaptive controller.
    This test is designed to verify the statistical soundness and decision-making
    logic of the "Quantum Immune System."
    """

    def test_decision_in_clean_environment(self):
        """
        Tests the controller's ability to correctly identify a safe environment.
        In a perfect, noiseless world, the diagnostics must report near-zero
        error and the controller must choose 'NoLock'.
        """
        print("\n\n--- Testing Controller: Clean Environment ---")
        
        # Use a dedicated RNG for reproducibility
        test_rng = random.Random(123)
        
        # Instantiate the controller with standard thresholds
        controller = TEALController(qber_threshold=0.03, leakage_threshold=0.015)
        
        # Run diagnostics in a perfect environment
        stats = controller.run_diagnostics(
            num_test_rounds=5000, # Use a large number for good statistics
            true_channel_loss=0.0,
            true_source_leakage=0.0,
            rng=test_rng
        )
        
        # Make the decision
        decision = controller.make_adaptive_decision(stats)
        
        # --- VERDICT ---
        # The QBER should be zero, and the leakage should be zero.
        self.assertAlmostEqual(stats['qber_mean'], 0.0, places=3)
        # The final decision MUST be 'NoLock'.
        self.assertEqual(decision['mode'], 'NoLock',
                         msg="Controller FAILED to identify a clean environment.")
        
        print("Clean Environment Test: PASSED")

    def test_decision_in_hostile_environment(self):
        """
        Tests the controller's ability to correctly identify a threat.
        In an environment with a known source leakage attack, the controller
        must detect the threat and choose 'Lock'.
        """
        print("\n--- Testing Controller: Hostile Environment (Leakage) ---")
        
        test_rng = random.Random(456)
        controller = TEALController(qber_threshold=0.03, leakage_threshold=0.015)
        
        # Run diagnostics in an environment with a 3% source leakage attack
        stats = controller.run_diagnostics(
            num_test_rounds=5000,
            true_channel_loss=0.0,
            true_source_leakage=0.03, # 3% leakage
            rng=test_rng
        )
        
        decision = controller.make_adaptive_decision(stats)
        
        # --- VERDICT ---
        # The controller's leakage estimate should be above its threshold.
        self.assertGreater(stats['leakage_upper_bound'], controller.leakage_threshold,
                           msg="Controller FAILED to statistically detect leakage.")
        # The final decision MUST be 'Lock'.
        self.assertEqual(decision['mode'], 'Lock',
                         msg="Controller FAILED to engage defenses in a hostile environment.")

        print("Hostile Environment Test: PASSED")

if __name__ == '__main__':
    unittest.main()