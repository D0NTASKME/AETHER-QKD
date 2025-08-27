# main_aether.py

import random
from typing import Dict, Any

# --- Import all our perfected, industry-grade protocols ---
from protocols.bb84 import run_bb84_protocol
from protocols.mdi import run_mdi_protocol
from protocols.teal import run_teal_protocol
from protocols.teal_e import run_teal_e_protocol
from controller.aether_controller import AETHERController # The new Master Brain

def print_results(protocol_name: str, results: Dict[str, Any], total_qubits: int):
    print(f"\n--- RESULTS for {protocol_name} ---")
    if results.get('mode_chosen'): print(f"Controller Mode Chosen: {results['mode_chosen']}")
    sifted_len = results.get('sifted_key_length', 0)
    qber = results.get('qber', 0); skr = results.get('secure_key_rate', 0)
    sift_rate = sifted_len / total_qubits if total_qubits > 0 else 0
    final_key = int(total_qubits * skr)
    print(f"Sifted Key: {sifted_len} bits (Efficiency: {sift_rate:.3%})")
    print(f"Final QBER: {qber:.3%}"); print(f"Secure Key Rate: {skr:.5f} bits/qubit"); print(f"Est. Final Key: {final_key} bits")

def run_comparison(env_name: str, signals: int, loss: float, noise: float, leakage: float, seed: int):
    print("\n" + "="*70 + f"\nEXPERIMENT: Simulating a {env_name} environment\n" + "="*70)
    print(f"Parameters: Signals={signals}, Loss={loss:.1%}, Noise={noise:.1%}, Leakage={leakage:.1%}\n")

    # --- The Baselines ---
    bb84 = run_bb84_protocol(signals, loss, noise, leakage, seed)
    mdi = run_mdi_protocol(signals, loss, noise, leakage, seed)

    # --- The AETHER System ---
    # 1. The Controller makes its strategic decision
    controller = AETHERController()
    stats = controller.run_diagnostics(loss, noise, leakage, random.Random(seed))
    chosen_protocol = controller.choose_protocol(stats)

    # 2. The system executes the chosen protocol
    if chosen_protocol == "TEAL":
        # We need a dummy TEAL controller for the TEAL protocol itself
        from controller.immune_system import TEALController as TealCtrl
        aether_system_results = run_teal_protocol(signals, 4, loss, noise, leakage, TealCtrl(), seed)
        aether_system_name = "AETHER System (using TEAL Fortress)"
    else: # "TEAL-E"
        aether_system_results = run_teal_e_protocol(signals, noise, leakage, seed)
        aether_system_name = "AETHER System (using TEAL-E Racer)"

    # --- Presentation ---
    print_results("BB84 (Classic)", bb84, signals)
    print_results("MDI (Modern)", mdi, signals)
    print_results(aether_system_name, aether_system_results, signals)
    
    # --- Verdict ---
    skrs = [
        (bb84['secure_key_rate'], "BB84"),
        (mdi['secure_key_rate'], "MDI"),
        (aether_system_results['secure_key_rate'], "AETHER System")
    ]
    
    print("\n" + "-"*28 + " FINAL VERDICT " + "-"*28)
    for name, rate in [(n, r['secure_key_rate']) for r,n in [(bb84,"BB84"),(mdi,"MDI"),(aether_system_results,"AETHER")]]:
        print(f"{name} SKR: {rate:.5f}")
    
    winner = max(skrs)
    print(f"\nCONCLUSION: {winner[1]} WINS in this environment.")
    print("="*70)

if __name__ == "__main__":
    TOTAL_SIGNALS = 20000
    run_comparison("CLEAN, HEALTHY", TOTAL_SIGNALS, 0.02, 0.001, 0.0, 1)
    run_comparison("HOSTILE (High Noise & Leakage)", TOTAL_SIGNALS, 0.02, 0.03, 0.03, 2)