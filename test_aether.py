# test_aether.py

import unittest
import random
from typing import Dict, Any

# --- Import all our perfected modules for the test ---
from protocols.aether import run_aether_protocol
from protocols.mdi import run_mdi_protocol
from controller.immune_system import TEALController
from adversary.attacks import Adversary, SourceLeakageAdversary

class TestAetherProtocol(unittest.TestCase):
    """
    The definitive, industry-grade unit test suite for the AETHER protocol.
    This is the final, corrected version with fully synchronized interfaces.
    """

    def setUp(self):
        """Set up common parameters for all tests."""
        self.num_qubits = 10000
        self.block_size = 4
        print("-" * 70)

    def test_protocol_integrity_in_perfect_world(self):
        """VALIDATION 1: Test AETHER in a perfect, noiseless environment."""
        print("\nTEST CASE 1: AETHER Integrity in a PERFECT Environment")
        
        controller = TEALController()
        adversary = Adversary(strength=0.0)
        
        # *** BUG FIX: Use the correct, consistent argument names for aether ***
        results = run_aether_protocol(
            num_qubits=self.num_qubits,
            block_size=self.block_size,
            loss=0.0,
            noise=0.0,
            adversary=adversary,
            controller=controller,
            seed=1
        )
        
        print("\n--- Verifying Clean Environment Performance ---")
        self.assertEqual(results['mode_chosen'], 'NoLock')
        self.assertAlmostEqual(results['diagnostic_qber'], 0.0, places=3)
        self.assertGreater(results['secure_key_rate'], 0.40)
        print("--> Integrity Test: PASSED")

    def test_resilience_against_source_attack(self):
        """VALIDATION 2: Test AETHER's resilience against a source leakage attack."""
        print("\nTEST CASE 2: AETHER Resilience in a HOSTILE Environment")

        controller = TEALController()
        adversary = SourceLeakageAdversary(strength=0.03)
        
        # *** BUG FIX: Use the correct, consistent argument names for aether ***
        results = run_aether_protocol(
            num_qubits=self.num_qubits,
            block_size=self.block_size,
            loss=0.0,
            noise=0.0,
            adversary=adversary,
            controller=controller,
            seed=2
        )
        
        print("\n--- Verifying Hostile Environment Performance ---")
        self.assertEqual(results['mode_chosen'], 'Lock')
        self.assertAlmostEqual(results['diagnostic_qber'], 0.0, places=3)
        self.assertGreater(results['secure_key_rate'], 0.20)
        print("--> Resilience Test: PASSED")

    def test_efficiency_advantage_over_mdi(self):
        """VALIDATION 3: Test AETHER's key rate advantage over MDI."""
        print("\nTEST CASE 3: AETHER Efficiency Advantage vs. MDI")
        
        # *** BUG FIX: Use the correct, consistent argument names for all calls ***
        env_params_mdi = {
            "num_qubits": 20000,
            "channel_loss_prob": 0.02,
            "hardware_noise_prob": 0.001,
            "source_leakage_prob": 0.0,
            "rng_seed": 3
        }
        env_params_aether = {
            "num_qubits": 20000,
            "block_size": self.block_size,
            "loss": 0.02,
            "noise": 0.001,
            "seed": 3
        }

        mdi_results = run_mdi_protocol(**env_params_mdi)
        skr_mdi = mdi_results['secure_key_rate']
        print(f"\nBaseline MDI Performance: SKR = {skr_mdi:.5f}")

        controller = TEALController()
        adversary = Adversary(strength=0.0)
        aether_results = run_aether_protocol(
            adversary=adversary, controller=controller, **env_params_aether
        )
        skr_aether = aether_results['secure_key_rate']
        print(f"AETHER Performance: SKR = {skr_aether:.5f}")

        self.assertGreater(skr_aether, skr_mdi)
        print("--> Efficiency Advantage Test: PASSED")

if __name__ == '__main__':
    unittest.main()