# main.py

import random
from typing import Dict, Any

# =============================================================================
# TEAL Simulator - Main Experiment Runner
# FINAL CORRECTED VERSION - All interfaces are now synchronized.
# =============================================================================


# --- Import all our perfected protocol blueprints ---
from protocols.bb84 import run_bb84_protocol
from protocols.mdi import run_mdi_protocol
from protocols.teal import run_teal_protocol
from controller.immune_system import TEALController


def print_results(protocol_name: str, results: Dict[str, Any], total_qubits: int):
    """A professional helper function to print protocol results in a standard format."""
    print(f"\n--- RESULTS for {protocol_name} ---")
    
    if results.get('mode_chosen'):
        print(f"Controller Mode Chosen: {results['mode_chosen']}")
    
    sifted_len = results.get('sifted_key_length', 0)
    qber = results.get('qber', 0)
    skr = results.get('secure_key_rate', 0)
    
    sift_rate = sifted_len / total_qubits if total_qubits > 0 else 0
    final_key_len = int(total_qubits * skr)

    print(f"Sifted Key Length: {sifted_len} bits (Efficiency: {sift_rate:.3%})")
    print(f"Final QBER: {qber:.3%}")
    print(f"Secure Key Rate: {skr:.5f} bits/qubit")
    print(f"Estimated Final Secure Key from this run: {final_key_len} bits")


def run_comparison(
    env_name: str,
    num_signals: int,
    loss: float,
    noise: float,
    leakage: float,
    seed: int
):
    """
    Runs all three protocols under the same environmental conditions and
    prints a comprehensive verdict.
    """
    print("\n" + "="*60 + f"\nEXPERIMENT: Simulating a {env_name} environment\n" + "="*60)
    print(f"Parameters: Signals={num_signals}, Loss={loss:.1%}, "
          f"Hardware Noise={noise:.1%}, Source Leakage={leakage:.1%}\n")
    
    # --- 1. Run Standard BB84 Protocol ---
    bb84_results = run_bb84_protocol(
        num_qubits=num_signals,
        channel_loss_prob=loss,
        hardware_noise_prob=noise,
        source_leakage_prob=leakage,
        rng_seed=seed
    )
    
    # --- 2. Run Baseline MDI Protocol ---
    mdi_results = run_mdi_protocol(
        num_qubits=num_signals,
        channel_loss_prob=loss,
        hardware_noise_prob=noise,
        source_leakage_prob=leakage,
        rng_seed=seed
    )
    
    # --- 3. Run Full TEAL Protocol ---
    # *** BUG FIX IS HERE: Correctly call run_teal_protocol with 'num_qubits' ***
    block_size = 4
    
    controller = TEALController()
    teal_results = run_teal_protocol(
        num_qubits=num_signals, # Pass total signals
        block_size=block_size,
        channel_loss_prob=loss,
        hardware_noise_prob=noise,
        source_leakage_prob=leakage,
        controller=controller,
        rng_seed=seed
    )
    
    # --- Presentation of Results ---
    print_results("Standard BB84", bb84_results, num_signals)
    print_results("Baseline MDI", mdi_results, num_signals)
    print_results("Advanced TEAL", teal_results, num_signals)
    
    # --- Final Verdict ---
    skr_bb84 = bb84_results['secure_key_rate']
    skr_mdi = mdi_results['secure_key_rate']
    skr_teal = teal_results['secure_key_rate']
    
    print("\n" + "-"*25 + " FINAL VERDICT " + "-"*25)
    print(f"BB84 Secure Key Rate:   {skr_bb84:.5f}")
    print(f"MDI Secure Key Rate:    {skr_mdi:.5f}")
    print(f"TEAL Secure Key Rate:   {skr_teal:.5f}")
    
    winner = max((skr_bb84, "BB84"), (skr_mdi, "MDI"), (skr_teal, "TEAL"))
    
    print(f"\nCONCLUSION: {winner[1]} WINS in this environment.")
    print("="*60)


if __name__ == "__main__":
    
    # --- Define Global Simulation Parameters ---
    TOTAL_SIGNALS = 20000 
    
    # --- Experiment 1: Clean, Low-Noise Environment ---
    run_comparison(
        env_name="CLEAN, HEALTHY",
        num_signals=TOTAL_SIGNALS,
        loss=0.02,
        noise=0.001,
        leakage=0.0,
        seed=1
    )

    # --- Experiment 2: Hostile Environment with Source Attack ---
    run_comparison(
        env_name="HOSTILE (Source Leakage Attack)",
        num_signals=TOTAL_SIGNALS,
        loss=0.02,
        noise=0.001,
        leakage=0.03,
        seed=2
    )