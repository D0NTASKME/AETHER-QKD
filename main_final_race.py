# main_final_race.py
import random
from protocols.bb84 import run_bb84_protocol
from protocols.mdi import run_mdi_protocol
from protocols.teal_e import run_teal_e_protocol # <-- The Starship

def print_results(protocol_name, results, total_qubits):
    print(f"\n--- RESULTS for {protocol_name} ---")
    sifted_len = results.get('sifted_key_length', 0); qber = results.get('qber', 0); skr = results.get('secure_key_rate', 0)
    sift_rate = sifted_len / total_qubits if total_qubits > 0 else 0
    final_key = int(total_qubits * skr)
    print(f"Sifted Key: {sifted_len} bits (Efficiency: {sift_rate:.3%})")
    print(f"Final QBER: {qber:.3%}"); print(f"Secure Key Rate: {skr:.5f} bits/qubit"); print(f"Est. Final Key: {final_key} bits")

def run_comparison(env, signals, loss, noise, leakage, seed):
    print("\n" + "="*60 + f"\nEXPERIMENT: Simulating a {env} environment\n" + "="*60)
    print(f"Parameters: Signals={signals}, Loss={loss:.1%}, Noise={noise:.1%}, Leakage={leakage:.1%}\n")
    
    bb84 = run_bb84_protocol(signals, loss, noise, leakage, seed)
    mdi = run_mdi_protocol(signals, loss, noise, leakage, seed)
    teal_e = run_teal_e_protocol(signals, noise, leakage, seed)
    
    print_results("BB84 (Classic)", bb84, signals)
    print_results("MDI (Modern)", mdi, signals)
    print_results("TEAL-E (Next-Gen)", teal_e, signals)
    
    skrs = [(bb84['secure_key_rate'], "BB84"), (mdi['secure_key_rate'], "MDI"), (teal_e['secure_key_rate'], "TEAL-E")]
    print("\n" + "-"*25 + " FINAL VERDICT " + "-"*25)
    for name, rate in [(n, r['secure_key_rate']) for r, n in [(bb84,"BB84"),(mdi,"MDI"),(teal_e,"TEAL-E")]]: print(f"{name} SKR: {rate:.5f}")
    winner = max(skrs)
    print(f"\nCONCLUSION: {winner[1]} WINS in this environment.")
    print("="*60)

if __name__ == "__main__":
    TOTAL_SIGNALS = 20000
    run_comparison("CLEAN, HEALTHY", TOTAL_SIGNALS, 0.02, 0.001, 0.0, 1)
    run_comparison("HOSTILE (High Noise & Leakage)", TOTAL_SIGNALS, 0.02, 0.03, 0.03, 2)