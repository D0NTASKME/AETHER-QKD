# test_aether_v3.py

import unittest
import random
from typing import Dict, Any

# --- Import all our perfected modules for the test ---
from protocols.aether_v3 import run_aether_v3_protocol
from protocols.mdi import run_mdi_protocol
from controller.immune_system import TEALController
from adversary.attacks import Adversary, SourceLeakageAdversary

class TestAetherV3Protocol(unittest.TestCase):
    """
    The definitive, industry-grade unit test and validation suite for the
    final AETHER protocol. This suite validates the core logic, the dual-stream
    diagnostics, the adaptive security, and the performance claims of the
    AETHER architecture.
    """

    def setUp(self):
        """Set up common parameters for all tests."""
        self.num_qubits = 10000
        self.block_size = 4
        print("-" * 70)

    def test_protocol_integrity_in_perfect_world(self):
        """
        VALIDATION 1: In a perfect, noiseless, attack-free world, the protocol
        must function flawlessly. The controller MUST choose 'NoLock', and the
        QBER from the diagnostic stream MUST be zero.
        """
        print("\nTEST CASE 1: AETHER Integrity in a PERFECT Environment")
        
        controller = TEALController()
        adversary = Adversary(strength=0.0)
        
        results = run_aether_v3_protocol(
            num_qubits=self.num_qubits,
            block_size=self.block_size,
            loss=0.0,
            noise=0.0,
            adversary=adversary,
            controller=controller,
            seed=1
        )
        
        print("\n--- Verifying Clean Environment Performance ---")
        print(f"Mode Chosen: {results['mode_chosen']}")
        print(f"Sifted Secret Key Length: {results['sifted_key_length']}")
        print(f"Diagnostic QBER: {results['diagnostic_qber']:.3%}")
        print(f"Final Secure Key Rate: {results['secure_key_rate']:.5f}")

        self.assertEqual(results['mode_chosen'], 'NoLock', "Controller failed to identify a clean environment.")
        self.assertAlmostEqual(results['diagnostic_qber'], 0.0, places=3,
                               msg="Diagnostic QBER should be 0 in a perfect world. Sifting logic is flawed.")
        # Theoretical max sifting for HQ stream is ~25%. With no errors, rate should be high.
        self.assertGreater(results['secure_key_rate'], 0.20,
                           "Secure key rate in clean environment is unexpectedly low.")
        
        print("--> Integrity Test: PASSED")

    def test_resilience_against_source_attack(self):
        """
        VALIDATION 2: The Quantum Immune System must function correctly. When faced
        with a source leakage attack, the controller MUST engage 'Lock' mode,
        and the final key rate must remain high, proving the attack was nullified.
        """
        print("\nTEST CASE 2: AETHER Resilience in a HOSTILE Environment")

        controller = TEALController()
        adversary = SourceLeakageAdversary(strength=0.03)
        
        results = run_aether_v3_protocol(
            num_qubits=self.num_qubits,
            block_size=self.block_size,
            loss=0.0,
            noise=0.0,
            adversary=adversary,
            controller=controller,
            seed=2
        )
        
        print("\n--- Verifying Hostile Environment Performance ---")
        print(f"Mode Chosen: {results['mode_chosen']}")
        print(f"Sifted Key Length: {results['sifted_key_length']}")
        print(f"Diagnostic QBER: {results['diagnostic_qber']:.3%}")
        print(f"Final Secure Key Rate: {results['secure_key_rate']:.5f}")

        self.assertEqual(results['mode_chosen'], 'Lock',
                         "Controller failed to engage defenses in a hostile environment.")
        self.assertAlmostEqual(results['diagnostic_qber'], 0.0, places=3,
                               msg="Diagnostic QBER should still be 0 in Lock mode with no hardware noise.")
        self.assertGreater(results['secure_key_rate'], 0.10, 
                           "Key rate under attack is unexpectedly low; the lock is failing.")

        print("--> Resilience Test: PASSED")

    def test_efficiency_advantage_over_mdi(self):
        """
        VALIDATION 3: This is the "Starship" test. AETHER must prove it is
        not just secure, but superior. In a realistic, noisy environment, it must
        achieve a higher secure key rate than the standard MDI protocol because
        it gets its QBER for free from the diagnostic stream.
        """
        print("\nTEST CASE 3: AETHER Efficiency Advantage vs. MDI")
        
        env_params = {
            "num_qubits": 20000,
            "channel_loss_prob": 0.02,
            "hardware_noise_prob": 0.005, # A bit more noise to make it interesting
            "source_leakage_prob": 0.0,
            "rng_seed": 3
        }

        # Run the Baseline MDI protocol
        mdi_results = run_mdi_protocol(**env_params)
        skr_mdi = mdi_results['secure_key_rate']
        print(f"\nBaseline MDI Performance: SKR = {skr_mdi:.5f}")

        # Run the AETHER protocol in the same environment
        # It should correctly choose 'NoLock' mode.
        controller = TEALController()
        adversary = Adversary(strength=0.0)
        aether_results = run_aether_v3_protocol(
            num_qubits=env_params['num_qubits'],
            block_size=self.block_size,
            loss=env_params['channel_loss_prob'],
            noise=env_params['hardware_noise_prob'],
            adversary=adversary,
            controller=controller,
            seed=env_params['rng_seed']
        )
        skr_aether = aether_results['secure_key_rate']
        print(f"AETHER Performance: SKR = {skr_aether:.5f}")

        # --- VERDICT ---
        self.assertGreater(skr_aether, skr_mdi,
                           "AETHER failed to demonstrate a key rate advantage over standard MDI.")
        
        print("--> Efficiency Advantage Test: PASSED")


if __name__ == '__main__':
    unittest.main()