# main_aether.py

import random
from typing import Dict, Any

from protocols.bb84 import run_bb84_protocol
from protocols.decoy_mdi_v2 import run_decoy_mdi_protocol
from protocols.teal import run_teal_protocol
from protocols.teal_e import run_teal_e_protocol
from controller.immune_system import TEALController
from controller.aether_controller import AETHERController

def print_results(protocol_name: str, results: Dict[str, Any], total_qubits: int):
    print(f"\n--- RESULTS for {protocol_name} ---")
    if results.get('mode_chosen'): print(f"Controller Mode: {results['mode_chosen']}")
    sifted_len = results.get('sifted_key_length', 0)
    qber = results.get('qber_obs', results.get('qber', 0))
    skr = results.get('secure_key_rate', 0)
    sift_rate = sifted_len / total_qubits if total_qubits > 0 else 0
    final_key = int(total_qubits * skr)
    print(f"Sifted Key: {sifted_len} bits (Efficiency: {sift_rate:.3%})")
    print(f"Final QBER (Observed): {qber:.3%}"); print(f"Secure Key Rate (Finite-Key): {skr:.5f} bits/qubit"); print(f"Est. Final Key: {final_key} bits")

def run_comparison(env_name: str, signals: int, loss: float, noise: float, leakage: float, seed: int):
    print("\n" + "="*70 + f"\nEXPERIMENT: Simulating a {env_name} environment\n" + "="*70)
    print(f"Parameters: Signals={signals}, Loss={loss:.1%}, Noise={noise:.1%}, Leakage={leakage:.1%}\n")
    
    bb84 = run_bb84_protocol(signals, loss, noise, leakage, seed)
    mdi = run_decoy_mdi_protocol(signals, loss, noise, leakage, seed)

    aether_controller = AETHERController()
    chosen_protocol = aether_controller.choose_protocol(noise, leakage, random.Random(seed))
    
    if chosen_protocol == "TEAL":
        aether_results = run_teal_protocol(
            num_qubits=signals, block_size=4,
            channel_loss_prob=loss, hardware_noise_prob=noise,
            source_leakage_prob=leakage, controller=TEALController(), rng_seed=seed
        )
        aether_name = "AETHER System (deploying TEAL Fortress)"
    else:
        aether_results = run_teal_e_protocol(
            num_qubits=signals, hardware_noise_prob=noise,
            source_leakage_prob=leakage, rng_seed=seed
        )
        aether_name = "AETHER System (deploying TEAL-E Racer)"

    print_results("BB84 (Classic)", bb84, signals)
    print_results("Decoy-State MDI (State-of-the-Art)", mdi, signals)
    print_results(aether_name, aether_results, signals)
    
    skrs = [
        (bb84['secure_key_rate'], "BB84"),
        (mdi['secure_key_rate'], "Decoy-State MDI"),
        (aether_results['secure_key_rate'], "AETHER System")
    ]
    
    print("\n" + "-"*30 + " FINAL VERDICT " + "-"*30)
    for name, rate in [(n, r['secure_key_rate']) for r,n in [(bb84,"BB84"),(mdi,"Decoy-MDI"),(aether_results,"AETHER")]]:
        print(f"{name} SKR: {rate:.5f}")
    
    winner = max(skrs)
    print(f"\nCONCLUSION: {winner[1]} WINS in this environment.")
    print("="*70)

if __name__ == "__main__":
    TOTAL_SIGNALS = 20000
    run_comparison("CLEAN, HEALTHY", TOTAL_SIGNALS, 0.02, 0.001, 0.0, 1)
    run_comparison("HOSTILE (High Noise & Leakage)", TOTAL_SIGNALS, 0.02, 0.03, 0.03, 2)
