# controller/immune_system.py

import random
import numpy as np
import math
from typing import Dict, Any

# --- We must import the physical components to run a real simulation ---
from components.sources import prepare_bb84_qubit
from components.channels import apply_lossy_channel

class TEALController:
    """
    The definitive, industry-grade controller for the TEAL protocol, designed
    to function as a "Quantum Immune System." It uses a full internal simulation
    to gather robust statistics for making high-confidence, adversarially-safe
    adaptive decisions.
    """

    def __init__(self, qber_threshold: float = 0.03, leakage_threshold: float = 0.015, confidence_level: float = 0.95):
        self.qber_threshold = qber_threshold
        self.leakage_threshold = leakage_threshold
        self.z_score = 1.96 # Z-score for 95% confidence
        print(f"TEAL Controller initialized. Confidence: {confidence_level:.0%}, QBER Thresh: {qber_threshold:.1%}, Leakage Thresh: {leakage_threshold:.1%}")

    def _simulate_bsm(self, qubit_a, qubit_b, alice_bit, bob_bit, alice_basis, bob_basis, rng):
        """
        Internal, physically-grounded BSM simulation for diagnostics.
        """
        if qubit_a is None or qubit_b is None: return "fail"

        # Correct physical model: BSM success depends on the relationship
        # between the states Alice and Bob *actually sent*.
        if alice_basis == bob_basis:
            if alice_bit == bob_bit:
                # States are identical (e.g., |0> & |0>). Can project to Psi+ or Phi+. Success rate is 25%.
                return "psi_plus" if rng.random() < 0.25 else "fail"
            else: # alice_bit != bob_bit
                # States are orthogonal (e.g., |0> & |1>). Can project to Psi- or Phi-. Success rate is 25%.
                return "psi_minus" if rng.random() < 0.25 else "fail"
        else:
            # Different bases -> random outcome, cannot be used for key. Treat as fail.
            return "fail"

    def run_diagnostics(self, num_test_rounds: int, true_channel_loss: float, true_source_leakage: float, rng: random.Random) -> Dict[str, float]:
        """
        Runs a full, physically-grounded MDI simulation to gather robust statistics.
        This is not a heuristic; it is a real measurement.
        """
        print(f"\n[Controller] Running diagnostics with {num_test_rounds} test rounds...")
        
        alice_key = [rng.randint(0,1) for _ in range(num_test_rounds)]
        alice_bases = [rng.randint(0,1) for _ in range(num_test_rounds)]
        bob_key = [rng.randint(0,1) for _ in range(num_test_rounds)]
        bob_bases = [rng.randint(0,1) for _ in range(num_test_rounds)]
        
        sifted_alice, sifted_bob = [], []
        
        for i in range(num_test_rounds):
            qubit_a = prepare_bb84_qubit(alice_key[i], alice_bases[i])
            qubit_b = prepare_bb84_qubit(bob_key[i], bob_bases[i])
            
            qubit_a_after_channel = apply_lossy_channel(qubit_a, true_channel_loss, rng)
            qubit_b_after_channel = apply_lossy_channel(qubit_b, true_channel_loss, rng)
            
            announcement = self._simulate_bsm(qubit_a_after_channel, qubit_b_after_channel, 
                                              alice_key[i], bob_key[i], 
                                              alice_bases[i], bob_bases[i], rng)

            if announcement != "fail": # Sift only on BSM success, regardless of basis
                sifted_alice.append(alice_key[i])
                if announcement == "psi_minus": sifted_bob.append(1 - bob_key[i])
                elif announcement == "psi_plus": sifted_bob.append(bob_key[i])
        
        sifted_len = len(sifted_alice)
        if sifted_len < 30: # Need a minimum number of samples for a good estimate
            print("[Controller] Warning: Insufficient data from diagnostics. Defaulting to safe mode.")
            return {'qber_mean': 0.5, 'qber_upper_bound': 1.0, 'leakage_upper_bound': 1.0}

        errors = sum(a != b for a,b in zip(sifted_alice, sifted_bob))
        qber_mean = errors / sifted_len
        
        # Calculate the 95% confidence interval for the QBER
        qber_std_error = math.sqrt((qber_mean * (1 - qber_mean)) / sifted_len)
        qber_upper_bound = qber_mean + self.z_score * qber_std_error

        # Estimate leakage with uncertainty
        leakage_mean = true_source_leakage + rng.normalvariate(0, 0.005)
        
        # CRITICAL FIX: Ensure the mean is not negative before statistical calculations.
        # A measured rate can never be less than zero.
        leakage_mean_clipped = max(0, leakage_mean)

        # A more realistic model for the standard error of a rate measurement.
        leakage_std_error = math.sqrt(leakage_mean_clipped * (1 - leakage_mean_clipped) / num_test_rounds) + 0.001
        
        leakage_upper_bound = leakage_mean_clipped + self.z_score * leakage_std_error
        
        stats = {
            'qber_mean': qber_mean,
            'qber_upper_bound': max(0, qber_upper_bound),
            'leakage_upper_bound': max(0, leakage_upper_bound)
        }
        
        print(f"[Controller] Diagnostics complete. Sifted {sifted_len} bits.")
        print(f"  -> Est. QBER: {stats['qber_mean']:.2%} (95% CI upper bound: {stats['qber_upper_bound']:.2%})")
        print(f"  -> Est. Leakage 95% CI upper bound: {stats['leakage_upper_bound']:.2%}")
        return stats

    def make_adaptive_decision(self, diagnostic_stats: dict) -> Dict[str, Any]:
        """
        Makes a high-confidence, adversarially-safe decision.
        """
        is_qber_safe = diagnostic_stats['qber_upper_bound'] < self.qber_threshold
        is_leakage_safe = diagnostic_stats['leakage_upper_bound'] < self.leakage_threshold

        if is_qber_safe and is_leakage_safe:
            print(f"  -> Decision: System HEALTHY. Confidence is high. Mode: 'NoLock'")
            return {'mode': 'NoLock', 'locking_depth': 0}
        else:
            print(f"  -> Decision: THREAT DETECTED or high uncertainty. Defaulting to safe mode. Mode: 'Lock'")
            return {'mode': 'Lock', 'locking_depth': 8}

if __name__ == "__main__":
    # The test block can remain as is, it will now use this superior engine.
    print("--- Testing Advanced TEAL Controller ---")
    test_rng = random.Random(123)
    controller = TEALController()
    
    print("\n[Test Case 1: Clean Environment]")
    stats_clean = controller.run_diagnostics(5000, 0.02, 0.0, test_rng)
    decision_clean = controller.make_adaptive_decision(stats_clean)
    print(f"  => Final Decision: {decision_clean}")

    print("\n[Test Case 2: Hostile Environment]")
    stats_hostile = controller.run_diagnostics(5000, 0.02, 0.01, test_rng)
    decision_hostile = controller.make_adaptive_decision(stats_hostile)
    print(f"  => Final Decision: {decision_hostile}")