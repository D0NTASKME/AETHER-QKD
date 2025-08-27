# adversary/threat_models.py
import random

class Adversary:
    """Base class for adversarial agents."""
    def __init__(self, name="Benign"):
        self.name = name

    def execute_source_attack(self, alice_key_bit): return alice_key_bit, 0.0
    def adapt_to_protocol_choice(self, mode): pass

class SourceLeakageAdversary(Adversary):
    """A simple adversary that leaks classical source bits with some probability."""
    def __init__(self, strength: float):
        super().__init__(name=f"Source Leakage ({strength:.1%})")
        self.strength = strength
    
    def execute_source_attack(self, alice_key_bit, rng: random.Random):
        leakage = 1.0 if rng.random() < self.strength else 0.0
        return alice_key_bit, leakage

class AdaptiveAdversary(Adversary):
    """
    A more powerful adversary that changes its behavior based on the
    protocol mode chosen by the controller.
    """
    def __init__(self, base_strength: float):
        super().__init__(name="Adaptive Adversary")
        self.base_strength = base_strength
        self.current_strength = base_strength

    def adapt_to_protocol_choice(self, mode: str):
        """If the controller chooses NoLock, the adversary increases its attack strength."""
        if mode == 'NoLock':
            self.current_strength = self.base_strength * 2 # Double the attack
            print(f"[Adversary] Controller chose 'NoLock'. Increasing attack strength to {self.current_strength:.1%}")
        else:
            self.current_strength = self.base_strength
            print(f"[Adversary] Controller chose 'Lock'. Maintaining attack strength at {self.current_strength:.1%}")

    def execute_source_attack(self, alice_key_bit, rng: random.Random):
        leakage = 1.0 if rng.random() < self.current_strength else 0.0
        return alice_key_bit, leakage