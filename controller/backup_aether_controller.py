# controller/aether_controller.py

import random

class AETHERController:
    """
    The definitive, industry-grade strategic controller. It functions as the
    central nervous system for the AETHER architecture, choosing the optimal
    protocol (the resilient TEAL or the efficient TEAL-E) based on a rigorous
    analysis of the environment.
    """

    def __init__(self, noise_threshold: float = 0.01, leakage_threshold: float = 0.01):
        self.noise_threshold = noise_threshold
        self.leakage_threshold = leakage_threshold
        print("AETHER Strategic Controller Initialized.")

    def run_diagnostics(self, true_channel_loss: float, true_noise: float, true_leakage: float, rng: random.Random) -> dict:
        """
        Generates noisy, realistic estimates of the environment.
        """
        print(f"\n[AETHER Controller] Running diagnostics...")
        # In a real system, these would be complex statistical estimates.
        # Here we model them as noisy measurements of the truth.
        est_noise = true_noise + rng.normalvariate(0, 0.002)
        est_leakage = true_leakage + rng.normalvariate(0, 0.005)
        
        stats = { 'noise': max(0, est_noise), 'leakage': max(0, est_leakage) }
        print(f"[AETHER Controller] Diagnostics complete: Est. Noise = {stats['noise']:.2%}, Est. Leakage = {stats['leakage']:.2%}")
        return stats

    def choose_protocol(self, diagnostic_stats: dict) -> str:
        """
        The core strategic decision logic.
        """
        if diagnostic_stats['leakage'] > self.leakage_threshold or diagnostic_stats['noise'] > self.noise_threshold:
            print("  -> Decision: Hostile environment detected. Deploying resilient TEAL protocol.")
            return "TEAL"
        else:
            print("  -> Decision: Clean environment detected. Deploying high-efficiency TEAL-E protocol.")
            return "TEAL-E"