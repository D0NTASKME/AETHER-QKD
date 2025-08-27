# test_suite.py

import unittest
import random
from protocols.bb84 import run_bb84_protocol
from protocols.mdi import run_mdi_protocol
from protocols.teal import run_teal_protocol
from controller.immune_system import TEALController

class TestProtocolIntegrity(unittest.TestCase):

    def test_bb84_in_perfect_world(self):
        print("\n\n--- Testing BB84 Protocol Integrity ---")
        results = run_bb84_protocol(10000, 0.0, 0.0, 0.0, 1)
        self.assertAlmostEqual(results['qber'], 0.0)
        self.assertGreater(results['secure_key_rate'], 0.48)
        print("BB84: PASSED")

    def test_mdi_in_perfect_world(self):
        print("\n--- Testing MDI Protocol Integrity ---")
        results = run_mdi_protocol(20000, 0.0, 0.0, 0.0, 2)
        self.assertAlmostEqual(results['qber'], 0.0)
        self.assertGreater(results['secure_key_rate'], 0.24)
        print("MDI: PASSED")

    def test_teal_nolock_in_perfect_world(self):
        print("\n--- Testing TEAL ('NoLock' Mode) Integrity ---")
        controller = TEALController()
        controller.qber_threshold = 999; controller.leakage_threshold = 999 # Force NoLock
        results = run_teal_protocol(5000, 4, 0.0, 0.0, 0.0, controller, 3)
        self.assertAlmostEqual(results['qber'], 0.0)
        self.assertGreater(results['secure_key_rate'], 0.24)
        print("TEAL ('NoLock'): PASSED")

    def test_teal_lock_in_perfect_world(self):
        print("\n--- Testing TEAL ('Lock' Mode) Integrity ---")
        controller = TEALController()
        controller.qber_threshold = 0; controller.leakage_threshold = 0 # Force Lock
        results = run_teal_protocol(500, 4, 0.0, 0.0, 0.0, controller, 4) # Fewer blocks for speed
        self.assertAlmostEqual(results['qber'], 0.0)
        # Sifting will be lower due to block-based nature, but still positive
        self.assertGreater(results['secure_key_rate'], 0.0)
        print("TEAL ('Lock'): PASSED")

if __name__ == '__main__':
    unittest.main()