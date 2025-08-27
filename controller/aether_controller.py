# controller/aether_controller.py
import random

class AETHERController:
    def __init__(self, noise_threshold: float = 0.01, leakage_threshold: float = 0.01):
        self.noise_threshold = noise_threshold
        self.leakage_threshold = leakage_threshold
        print("AETHER Strategic Controller Initialized.")

    def choose_protocol(self, true_noise: float, true_leakage: float, rng: random.Random) -> str:
        """Makes the strategic decision of which protocol to deploy."""
        print(f"\n[AETHER Controller] Diagnosing environment...")
        est_noise = true_noise + rng.normalvariate(0, 0.002)
        est_leakage = true_leakage + rng.normalvariate(0, 0.005)
        print(f"[AETHER Controller] Diagnostics complete: Est. Noise = {max(0,est_noise):.2%}, Est. Leakage = {max(0,est_leakage):.2%}")
        
        if est_leakage > self.leakage_threshold or est_noise > self.noise_threshold:
            print("  -> Decision: Hostile environment. Deploying resilient TEAL Fortress.")
            return "TEAL"
        else:
            print("  -> Decision: Clean environment. Deploying high-efficiency TEAL-E Racer.")
            return "TEAL-E"