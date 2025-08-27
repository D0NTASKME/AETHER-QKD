# main_rigor.py

import random
from typing import Dict, Any

# =============================================================================
# TEAL Simulator - The Definitive, Publication-Ready Experiment
# =============================================================================
# This is the final, top-level script. It orchestrates the definitive,
# head-to-head comparison between our three perfected protocols and the
# new, fully rigorous TEAL protocol.
# =============================================================================

# --- Import all our perfected protocol blueprints ---
from protocols.bb84 import run_bb84_protocol
from protocols.mdi import run_mdi_protocol
from protocols.teal_rigor import run_teal_rigor_protocol # The flagship
from controller.immune_system import TEALController
from adversary.attacks import Adversary, SourceLeakageAdversary, AdaptiveAdversary

def print_results(protocol_name: str, results: Dict[str, Any], total_qubits: int):
    """A professional helper function to print protocol results."""
    print(f"\n--- RESULTS for {protocol_name} ---")
    if results.get('mode_chosen'): print(f"Controller Mode Chosen: {results['mode_chosen']}")
    sifted_len = results.get('sifted_key_length', 0)
    qber = results.get('qber', 0); skr = results.get('secure_key_rate', 0)
    sift_rate = sifted_len / total_qubits if total_qubits > 0 else 0
    final_key_len = int(total_qubits * skr)
    print(f"Sifted Key Length: {sifted_len} bits (Efficiency: {sift_rate:.3%})")
    print(f"Final QBER: {qber:.3%}")
    print(f"Secure Key Rate (Lower Bound): {skr:.5f} bits/qubit")
    print(f"Estimated Final Secure Key: {final_key_len} bits")

def run_comparison(env_name: str, signals: int, loss: float, noise: float, adversary: Adversary, seed: int):
    """Runs the full comparison and prints the verdict."""
    print("\n" + "="*70 + f"\nEXPERIMENT: Simulating a {env_name} environment\n" + "="*70)
    print(f"Parameters: Signals={signals}, Loss={loss:.1%}, Noise={noise:.1%}, Adversary={adversary.name}\n")
    
    # --- 1. Run Standard BB84 Protocol ---
    bb84_results = run_bb84_protocol(signals, loss, noise, adversary.strength, seed)
    
    # --- 2. Run Baseline MDI Protocol ---
    mdi_results = run_mdi_protocol(signals, loss, noise, adversary.strength, seed)
    
    # --- 3. Run TEAL Rigor Protocol ---
    controller = TEALController()
    teal_results = run_teal_rigor_protocol(
        num_qubits=signals, block_size=4, loss_prob=loss,
        noise_prob=noise, adversary=adversary,
        controller=controller, seed=seed
    )
    
    # --- Presentation ---
    print_results("Standard BB84", bb84_results, signals)
    print_results("Baseline MDI", mdi_results, signals)
    print_results("TEAL (Rigor)", teal_results, signals)
    
    # --- Verdict ---
    skr_bb84 = bb84_results['secure_key_rate']
    skr_mdi = mdi_results['secure_key_rate']
    skr_teal = teal_results['secure_key_rate']
    
    print("\n" + "-"*28 + " FINAL VERDICT " + "-"*28)
    print(f"BB84 SKR (Lower Bound):   {skr_bb84:.5f}")
    print(f"MDI SKR (Lower Bound):    {skr_mdi:.5f}")
    print(f"TEAL SKR (Lower Bound):   {skr_teal:.5f}")
    
    winner = max((skr_bb84, "BB84"), (skr_mdi, "MDI"), (skr_teal, "TEAL (Rigor)"))
    print(f"\nCONCLUSION: {winner[1]} WINS in this environment.")
    print("="*70)

if __name__ == "__main__":
    TOTAL_SIGNALS = 20000
    
    # --- Experiment 1: Clean, with a simple, static adversary ---
    run_comparison(
        env_name="CLEAN (Static Adversary)",
        signals=TOTAL_SIGNALS, loss=0.02, noise=0.001,
        adversary=SourceLeakageAdversary(strength=0.0), # Noisy but not actively malicious
        seed=1
    )

    # --- Experiment 2: Hostile, with a powerful adaptive adversary ---
    run_comparison(
        env_name="HOSTILE (Adaptive Adversary)",
        signals=TOTAL_SIGNALS, loss=0.02, noise=0.001,
        adversary=AdaptiveAdversary(base_strength=0.02), # Starts at 2% leakage
        seed=2
    )