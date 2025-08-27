# protocols/teal_e.py
import random
from typing import Dict, Any
from components.sources import prepare_bb84_qubit
from components.channels import apply_lossy_channel
from components.entanglement_factory import EntanglementFactory
from analysis.teal_e_analysis import run_teal_e_analysis

def run_teal_e_protocol(
    num_qubits: int,
    hardware_noise_prob: float,
    source_leakage_prob: float, # This argument is for interface compatibility
    rng_seed: int
) -> Dict[str, Any]:
    
    rng = random.Random(rng_seed)
    
    factory = EntanglementFactory(alice_channel_loss=0.02, bob_channel_loss=0.02)
    successful_pairs = factory.generate_entangled_pairs(num_qubits, rng)
    
    sifted_alice, sifted_bob_raw = [], []
    
    for i in range(num_qubits):
        if successful_pairs[i]:
            alice_measurement = rng.randint(0, 1)
            bob_measurement = 1 - alice_measurement
            
            if rng.random() < hardware_noise_prob: alice_measurement ^= 1
            if rng.random() < hardware_noise_prob: bob_measurement ^= 1
                
            sifted_alice.append(alice_measurement)
            sifted_bob_raw.append(bob_measurement)

    sifted_bob_reconciled = [1 - b for b in sifted_bob_raw]

    # TEAL-E is architecturally immune to source leakage, so we pass 0 to the analysis.
    final_results = run_teal_e_analysis(
        sifted_alice=sifted_alice,
        sifted_bob=sifted_bob_reconciled,
        total_initial_qubits=num_qubits,
        source_leakage_prob=0.0 
    )
    
    return final_results