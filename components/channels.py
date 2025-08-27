# components/channels.py

import random

# MODIFICATION: The function now accepts an optional 'rng' object for reproducibility.
def apply_lossy_channel(photon_state, loss_probability: float, rng=None):
    """
    Simulates a simple lossy quantum channel.
    ... (docstring is the same) ...
    """
    if photon_state is None:
        return None

    if not 0.0 <= loss_probability <= 1.0:
        raise ValueError("loss_probability must be between 0 and 1.")

    # Use the provided random generator if it exists, otherwise use the global one.
    rand_gen = rng if rng is not None else random

    if rand_gen.random() < loss_probability:
        return None  # Photon is lost
    else:
        return photon_state  # Photon is transmitted successfully

if __name__ == "__main__":
    # --- Test Block ---
    my_photon = "qubit_state_0"
    loss_prob = 0.3
    num_simulations = 1000
    transmitted_count = 0
    lost_count = 0
    
    # Test with a specific RNG instance for reproducibility
    test_rng = random.Random(123)

    print("Starting simulation...")
    for i in range(num_simulations):
        # MODIFICATION: Pass the RNG to the function
        result = apply_lossy_channel(my_photon, loss_prob, rng=test_rng)
        if result is None:
            lost_count += 1
        else:
            transmitted_count += 1

    print("Simulation finished.")
    print(f"Photons successfully transmitted: {transmitted_count}")
    print(f"Photons lost: {lost_count}")

    measured_loss_rate = lost_count / num_simulations
    print(f"\nExpected loss rate: {loss_prob:.2f}")
    print(f"Measured loss rate: {measured_loss_rate:.2f}")