# main.py

import random
from protocols.bb84 import run_bb84_protocol
from protocols.mdi import run_mdi_protocol
from protocols.teal import run_teal_protocol
from controller.immune_system import TEALController

def print_results(protocol_name, results, total_qubits):
    print(f"\n--- RESULTS for {protocol_name} ---")
    if results.get('mode_chosen'): print(f"Controller Mode Chosen: {results['mode_chosen']}")
    sifted_len = results.get('sifted_key_length', 0)
    qber = results.get('qber', 0); skr = results.get('secure_key_rate', 0)
    sift_rate = sifted_len / total_qubits if total_qubits > 0 else 0
    final_key_len = int(total_qubits * skr)
    print(f"Sifted Key Length: {sifted_len} bits (Efficiency: {sift_rate:.3%})")
    print(f"Final QBER: {qber:.3%}")
    print(f"Secure Key Rate: {skr:.5f} bits/qubit")
    print(f"Estimated Final Secure Key: {final_key_len} bits")

def run_comparison(env_name, num_signals, loss, noise, leakage, seed):
    print("\n" + "="*60 + f"\nEXPERIMENT: Simulating a {env_name} environment\n" + "="*60)
    print(f"Parameters: Signals={num_signals}, Loss={loss:.1%}, Noise={noise:.1%}, Leakage={leakage:.1%}\n")
    
    # --- 1. Run BB84 ---
    bb84_results = run_bb84_protocol(num_signals, loss, noise, leakage, seed)
    
    # --- 2. Run MDI ---
    mdi_results = run_mdi_protocol(num_signals, loss, noise, leakage, seed)
    
    # --- 3. Run TEAL ---
    block_size = 4
    num_blocks = num_signals // block_size
    controller = TEALController()
    teal_results = run_teal_protocol(
        num_blocks=num_blocks, block_size=block_size, channel_loss_prob=loss,
        hardware_noise_prob=noise, source_leakage_prob=leakage,
        controller=controller, rng_seed=seed
    )
    
    # --- Presentation ---
    print_results("Standard BB84", bb84_results, num_signals)
    print_results("Baseline MDI", mdi_results, num_signals)
    print_results("Advanced TEAL", teal_results, num_signals)
    
    # --- Verdict ---
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
    TOTAL_SIGNALS = 20000
    run_comparison("CLEAN, HEALTHY", TOTAL_SIGNALS, 0.02, 0.001, 0.0, 1)
    run_comparison("HOSTILE (Source Leakage Attack)", TOTAL_SIGNALS, 0.02, 0.001, 0.03, 2)