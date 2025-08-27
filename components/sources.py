# components/sources.py

import numpy as np

# 1. Quantum State Definitions
# Define the four BB84 quantum states as numpy arrays.
# Using dtype=complex is good practice for quantum states.
STATE_0 = np.array([1, 0], dtype=complex)
STATE_1 = np.array([0, 1], dtype=complex)
STATE_PLUS = (STATE_0 + STATE_1) / np.sqrt(2)
STATE_MINUS = (STATE_0 - STATE_1) / np.sqrt(2)

def prepare_bb84_qubit(bit_to_send: int, basis_choice: int):
    """
    Prepares one of the four BB84 quantum states based on classical inputs.

    This function simulates the quantum source (e.g., Alice's device) in a
    BB84-type protocol.

    Args:
        bit_to_send: The classical bit to encode (0 or 1).
        basis_choice: The basis to encode the bit in.
                      0 for Rectilinear (Z) basis {|0>, |1>}.
                      1 for Diagonal (X) basis {|+>, |->}.

    Returns:
        A numpy array representing the corresponding quantum state vector.

    Raises:
        ValueError: If bit_to_send or basis_choice are not 0 or 1.
    """
    if bit_to_send not in [0, 1]:
        raise ValueError(f"Invalid bit_to_send: {bit_to_send}. Must be 0 or 1.")
    if basis_choice not in [0, 1]:
        raise ValueError(f"Invalid basis_choice: {basis_choice}. Must be 0 or 1.")

    # Select the state based on the bit and basis choice
    if basis_choice == 0:  # Rectilinear (Z) basis
        if bit_to_send == 0:
            return STATE_0
        else:  # bit_to_send == 1
            return STATE_1
    else:  # basis_choice == 1, Diagonal (X) basis
        if bit_to_send == 0:
            return STATE_PLUS
        else:  # bit_to_send == 1
            return STATE_MINUS

if __name__ == "__main__":
    # --- Test Block ---
    # This block demonstrates the function's usage and verifies that
    # the correct quantum state is produced for each input combination.

    print("--- Testing the BB84 Qubit Preparation ---")

    # Combination 1: Bit 0, Basis 0 (should be |0>)
    prepared_state_00 = prepare_bb84_qubit(bit_to_send=0, basis_choice=0)
    print(f"Bit 0, Basis Z -> State: {prepared_state_00}")

    # Combination 2: Bit 1, Basis 0 (should be |1>)
    prepared_state_10 = prepare_bb84_qubit(bit_to_send=1, basis_choice=0)
    print(f"Bit 1, Basis Z -> State: {prepared_state_10}")

    # Combination 3: Bit 0, Basis 1 (should be |+>)
    prepared_state_01 = prepare_bb84_qubit(bit_to_send=0, basis_choice=1)
    print(f"Bit 0, Basis X -> State: {np.round(prepared_state_01, 3)}")

    # Combination 4: Bit 1, Basis 1 (should be |->)
    prepared_state_11 = prepare_bb84_qubit(bit_to_send=1, basis_choice=1)
    print(f"Bit 1, Basis X -> State: {np.round(prepared_state_11, 3)}")

    print("\n--- Verifying State Definitions ---")
    print(f"STATE_0:     {STATE_0}")
    print(f"STATE_1:     {STATE_1}")
    print(f"STATE_PLUS:  {np.round(STATE_PLUS, 3)}")
    print(f"STATE_MINUS: {np.round(STATE_MINUS, 3)}")
    print("-" * 38)