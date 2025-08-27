# test_aether_v2.py

import unittest
import random
from typing import Dict, Any

# --- Import the protocol and components under test ---
from protocols.aether_v2 import run_aether_v2_protocol
from controller.immune_system import TEALController
from analysis.aether_v2_key_rate import calculate_aether_v2_secure_key_rates

class TestAetherV2Protocol(unittest.TestCase):
    """
    A rigorous unit test and performance validation suite for the AETHER v2 protocol.
    This test simulates the two key environments from the final race to validate
    the protocol's performance and adaptive logic before the comparison.
    """

    def setUp(self):
        """Set up common parameters for all tests."""
        self.num_qubits = 20000
        self.block_size = 4
        
    def test_performance_in_clean_environment(self):
        """
        Tests AETHER v2's performance in a clean, noiseless, attack-free world.
        - The controller should choose 'NoLock'.
        - The sifting efficiency should be near 100% due to the perfect relay.
        - The secure key rate should be extremely high, approaching the theoretical
          limit for this type of protocol (~1.0 bits/qubit before loss).
        """
        print("\n\n--- Testing AETHER v2: Performance in CLEAN Environment ---")
        
        controller = TEALController()
        
        results = run_aether_v2_protocol(
            num_qubits=self.num_qubits,
            block_size=self.block_size,
            channel_loss_prob=0.02, # 2% loss
            hardware_noise_prob=0.001, # 0.1% noise
            source_leakage_prob=0.0, # No attack
            controller=controller,
            rng_seed=1
        )
        
        # --- VERDICT ---
        print("\n--- Verifying Clean Environment Performance ---")
        print(f"Mode Chosen: {results['mode_chosen']}")
        print(f"Sifted Key Length: {results['sifted_key_length']}")
        print(f"Final QBER: {results['qber']:.3%}")
        print(f"Final Secure Key Rate: {results['secure_key_rate']:.5f}")

        self.assertEqual(results['mode_chosen'], 'NoLock')
        self.assertAlmostEqual(results['qber'], 0.0, places=3)
        # With a perfect relay, sifting eff is ~98% (due to loss). Key rate should be very high.
        self.assertGreater(results['secure_key_rate'], 0.80,
                           "Key rate in clean environment is unexpectedly low.")
        
        print("Clean Environment Test: PASSED")

    def test_resilience_in_hostile_environment(self):
        """
        Tests AETHER v2's resilience in a hostile world with a source leakage attack.
        - The controller MUST choose 'Lock'.
        - The protocol must still produce a high secure key rate, proving it has
          nullified the attack.
        """
        print("\n--- Testing AETHER v2: Resilience in HOSTILE Environment ---")

        controller = TEALController()
        
        results = run_aether_v2_protocol(
            num_qubits=self.num_qubits,
            block_size=self.block_size,
            channel_loss_prob=0.02, # 2% loss
            hardware_noise_prob=0.001, # 0.1% noise
            source_leakage_prob=0.03, # 3% source leakage attack
            controller=controller,
            rng_seed=2
        )
        
        # --- VERDICT ---
        print("\n--- Verifying Hostile Environment Performance ---")
        print(f"Mode Chosen: {results['mode_chosen']}")
        print(f"Sifted Key Length: {results['sifted_key_length']}")
        print(f"Final QBER: {results['qber']:.3%}")
        print(f"Final Secure Key Rate: {results['secure_key_rate']:.5f}")

        self.assertEqual(results['mode_chosen'], 'Lock')
        # The key rate should be lower due to the lock's noise, but still very high.
        self.assertGreater(results['secure_key_rate'], 0.50, 
                           "Key rate under attack is unexpectedly low, the lock may be failing.")

        print("Hostile Environment Test: PASSED")


if __name__ == '__main__':
    unittest.main()