# physics/evolution.py

import random
import numpy as np
from typing import List, Tuple, Dict

# =============================================================================
# TEAL Simulator - The Physics Engine
# =============================================================================
# This module is the physical core of the entire simulation. It is responsible
# for correctly modeling the evolution of quantum states through noisy, compiled
# quantum circuits. It is designed to be a robust, reusable, and physically
# accurate component.
# =============================================================================


# -----------------------------------------------------------------------------
# SECTION 1: CORE QUANTUM PRIMITIVES AND HELPERS
# -----------------------------------------------------------------------------

# --- Type Aliases for clarity ---
QuantumState = np.ndarray
GatePrimitive = np.ndarray
CompiledGate = Tuple
CompiledCircuit = List[CompiledGate]

# --- Vetted Quantum Objects ---
I2 = np.eye(2, dtype=complex)
CNOT_2 = np.array([[1,0,0,0], [0,1,0,0], [0,0,0,1], [0,0,1,0]], dtype=complex)
SWAP_2 = np.array([[1,0,0,0], [0,0,1,0], [0,1,0,0], [0,0,0,1]], dtype=complex)
PAULI_1Q_LIST = [
    np.eye(2, dtype=complex),
    np.array([[0,1],[1,0]], dtype=complex), # X
    np.array([[0,-1j],[1j,0]], dtype=complex), # Y
    np.array([[1,0],[0,-1]], dtype=complex)  # Z
]

def local_pair_gate_from_rotations(Rc: np.ndarray, Rt: np.ndarray) -> GatePrimitive:
    """Creates the standard 2-qubit gate primitive: rotations then CNOT."""
    return CNOT_2 @ np.kron(Rc, Rt)

def _gate_on_n(gate: GatePrimitive, n_qubits: int, targets: List[int]) -> GatePrimitive:
    """
    The robust, basis-sum embedding function. This is the internal workhorse.
    It correctly embeds a k-qubit gate onto a full n-qubit Hilbert space.
    """
    # This function is a direct copy of the vetted, correct logic from our
    # final OTOC experiment. Its complexity is warranted for its correctness.
    targets = list(targets); k = len(targets)
    if gate.shape != (2**k, 2**k): raise ValueError("Gate dims mismatch")
    
    sorted_targets = sorted(targets)
    if sorted_targets != targets:
        perm = [targets.index(t) for t in sorted_targets]
        dim = 2**k; P = np.zeros((dim, dim), dtype=complex)
        for i in range(dim):
            bits_in = [int(c) for c in f'{i:0{k}b}']
            bits_out = [bits_in[p] for p in perm]
            P[int("".join(map(str, bits_out)), 2), i] = 1.0
        gate_local = P @ gate @ P.T
        targets_use = sorted_targets
    else:
        gate_local = gate
        targets_use = targets

    D = 2**n_qubits; full = np.zeros((D, D), dtype=complex)
    
    other_indices = [i for i in range(n_qubits) if i not in targets_use]
    
    for i in range(D):
        bits_i = [int(c) for c in f'{i:0{n_qubits}b}']
        local_bits_i = [bits_i[t] for t in targets_use]
        other_bits_i = [bits_i[t] for t in other_indices]
        local_idx_i = int("".join(map(str, local_bits_i)), 2)
        
        row_from_gate = gate_local[:, local_idx_i]
        
        for j_local, amplitude in enumerate(row_from_gate):
            if abs(amplitude) > 1e-9:
                bits_j_local = [int(c) for c in f'{j_local:0{k}b}']
                bits_j = [0] * n_qubits
                for idx, t in enumerate(targets_use): bits_j[t] = bits_j_local[idx]
                for idx, t in enumerate(other_indices): bits_j[t] = other_bits_i[idx]
                
                j = int("".join(map(str, bits_j)), 2)
                full[j, i] = amplitude
    return full

# -----------------------------------------------------------------------------
# SECTION 2: THE PUBLIC-FACING PHYSICS ENGINE FUNCTIONS
# -----------------------------------------------------------------------------

def build_unitary_from_compiled(n_qubits: int, compiled_list: CompiledCircuit) -> np.ndarray:
    """
    Constructs the final, ideal (noiseless) unitary matrix from a compiled circuit.
    This is essential for the "unlocking" operation in the TEAL protocol.

    Args:
        n_qubits: The number of qubits in the system.
        compiled_list: A list of compiled gates from the locking.core module.

    Returns:
        The final 2^n x 2^n unitary matrix for the entire circuit.
    """
    U = np.eye(2**n_qubits, dtype=complex)
    for gate_type, *args in compiled_list:
        if gate_type == 'SWAP':
            a, b = args; local_gate = SWAP_2; targets = sorted([a,b])
        elif gate_type == 'G':
            c, t, Rc, Rt = args; local_gate = local_pair_gate_from_rotations(Rc, Rt); targets = sorted([c,t])
        
        U_gate = _gate_on_n(local_gate, n_qubits, targets)
        U = U_gate @ U
    return U

def evolve_state_vector_noisily(
    initial_psi: QuantumState,
    compiled_list: CompiledCircuit,
    noise_p: float,
    rng: random.Random
) -> QuantumState:
    """
    Evolves a quantum state vector through a noisy, compiled quantum circuit.
    This is the core of the physics simulation, modeling a real quantum computer.

    Args:
        initial_psi: The starting n-qubit state vector.
        compiled_list: The sequence of physical gates to apply.
        noise_p: The probability of a depolarizing error occurring after each gate.
        rng: A random number generator for reproducible noise.

    Returns:
        The final, noisy n-qubit state vector after the full evolution.
    """
    n_qubits = int(np.log2(len(initial_psi)))
    psi = initial_psi.copy()

    for gate_type, *args in compiled_list:
        if gate_type == 'SWAP':
            a, b = args; local_gate = SWAP_2; targets = sorted([a,b])
        elif gate_type == 'G':
            c, t, Rc, Rt = args; local_gate = local_pair_gate_from_rotations(Rc, Rt); targets = sorted([c,t])
        
        # 1. Apply the ideal gate evolution
        U_gate = _gate_on_n(local_gate, n_qubits, targets)
        psi = U_gate @ psi

        # 2. Apply the stochastic noise model (Pauli Twirl)
        if noise_p > 0 and rng.random() < noise_p:
            # Pick a random non-identity Pauli for each of the two qubits.
            pauli_1 = PAULI_1Q_LIST[rng.randint(1, 3)]
            pauli_2 = PAULI_1Q_LIST[rng.randint(1, 3)]
            
            noise_gate = np.kron(pauli_1, pauli_2)
            noise_op = _gate_on_n(noise_gate, n_qubits, targets)
            psi = noise_op @ psi
            
    return psi