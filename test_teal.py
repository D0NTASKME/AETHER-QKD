# test_teal.py

import random
from protocols.teal import run_teal_protocol
from controller.immune_system import TEALController

# =============================================================================
# This is a dedicated unit test script for the final, industry-grade
# TEAL protocol simulator. Its purpose is to verify the core logic in a
# controlled, noiseless environment before running the full comparison.
# =============================================================================

if __name__ == "__main__":
    
    # --- Define Simulation Parameters for Testing ---
    # We can use fewer blocks for a unit test to make it run faster.
    NUM_BLOCKS_TEST = 1000
    BLOCK_SIZE_TEST = 4

    print("="*60)
    print("RUNNING UNIT TEST FOR THE TEAL PROTOCOL")
    print("="*60)

    # --- Test Case 1: Verifying the 'NoLock' Path in a Perfect World ---
    print("\n[Test Case 1: Perfect Environment -> 'NoLock' Mode]")
    
    # In a clean world, a normal controller should choose NoLock.
    controller_clean = TEALController()
    
    results_nolock = run_teal_protocol(
        num_blocks=NUM_BLOCKS_TEST,
        block_size=BLOCK_SIZE_TEST,
        channel_loss_prob=0.0,      # No loss
        hardware_noise_prob=0.0,    # No noise
        source_leakage_prob=0.0,    # No attack
        controller=controller_clean,
        rng_seed=1
    )
    
    print("\n--- Results for 'NoLock' Test ---")
    print(f"Mode Chosen: {results_nolock['mode_chosen']}")
    print(f"Sifted Key Length: {results_nolock['sifted_key_length']}")
    print(f"Final QBER: {results_nolock['qber']:.3%}")
    
    test1_passed = results_nolock['qber'] == 0.0 and results_nolock['mode_chosen'] == 'NoLock'
    print(f"\n---> Test 1 Verdict: {'PASS' if test1_passed else 'FAIL'}")
    print("-" * 60)


    # --- Test Case 2: Verifying the 'Lock' Path in a Perfect World ---
    print("\n[Test Case 2: Forcing 'Lock' Mode in a Perfect World]")
    
    # We force the controller to choose 'Lock' by setting its thresholds to zero.
    controller_forced_lock = TEALController(qber_threshold=0.0, leakage_threshold=0.0)
    
    results_lock = run_teal_protocol(
        num_blocks=NUM_BLOCKS_TEST,
        block_size=BLOCK_SIZE_TEST,
        channel_loss_prob=0.0,      # No loss
        hardware_noise_prob=0.0,    # No noise
        source_leakage_prob=0.0,    # No attack
        controller=controller_forced_lock,
        rng_seed=2
    )

    print("\n--- Results for 'Lock' Test ---")
    print(f"Mode Chosen: {results_lock['mode_chosen']}")
    print(f"Sifted Key Length: {results_lock['sifted_key_length']}")
    print(f"Final QBER: {results_lock['qber']:.3%}")
    
    test2_passed = results_lock['qber'] == 0.0 and results_lock['mode_chosen'] == 'Lock'
    print(f"\n---> Test 2 Verdict: {'PASS' if test2_passed else 'FAIL'}")
    print("-" * 60)
    
    print("\n" + "="*60)
    if test1_passed and test2_passed:
        print("CONCLUSION: The TEAL protocol passed all unit tests. The core logic is sound.")
    else:
        print("CONCLUSION: The TEAL protocol FAILED a unit test. There is a bug in the core logic.")
    print("="*60)