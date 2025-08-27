import unittest
import random
from protocols.teal_e import run_teal_e_protocol
class TestTealEProtocol(unittest.TestCase):
    def setUp(self):
        self.num_qubits = 20000
        print("-" * 70)
    def test_integrity_in_perfect_world(self):
        print("\nTEST CASE: TEAL-E Integrity in a PERFECT Environment")
        
        results = run_teal_e_protocol(
            num_qubits=self.num_qubits,
            hardware_noise_prob=0.0,
            source_leakage_prob=0.0,
            rng_seed=123
        )
        
        print("\n--- Verifying Perfect World Performance ---")
        print(f"Sifted Key Length: {results['sifted_key_length']}")
        print(f"Final QBER: {results['qber']:.3%}")
        print(f"Final Secure Key Rate: {results['secure_key_rate']:.5f}")

        self.assertAlmostEqual(results['qber'], 0.0, places=3)
        self.assertGreater(results['secure_key_rate'], 0.45)
        print("--> Integrity Test: PASSED")
if __name__ == '__main__':
    unittest.main()