# locking/core.py

import random
import numpy as np
from typing import List, Tuple

# =============================================================================
# TEAL Simulator - The Locking Core
# =============================================================================
# This module contains the definitive, industry-grade logic for generating and
# compiling the advanced, adaptive locking unitaries for the TEAL protocol.
# The architectures within are the result of the full research and validation
# process.
# =============================================================================

# --- Type Aliases for clarity ---
AbstractGate = Tuple[str, int, int, np.ndarray, np.ndarray]
CompiledGate = Tuple

# --- Vetted Helper ---
def random_single_qubit_rotation_from_rng(rng: np.random.RandomState) -> np.ndarray:
    phi = rng.uniform(0, 2 * np.pi)
    theta = np.arccos(rng.uniform(-1, 1))
    lam = rng.uniform(0, 2 * np.pi)
    Rz1 = np.array([[np.exp(-1j*phi/2), 0],[0, np.exp(1j*phi/2)]], dtype=complex)
    Ry  = np.array([[np.cos(theta/2), -np.sin(theta/2)],[np.sin(theta/2), np.cos(theta/2)]], dtype=complex)
    Rz2 = np.array([[np.exp(-1j*lam/2), 0],[0, np.exp(1j*lam/2)]], dtype=complex)
    return Rz1 @ Ry @ Rz2

# --- Vetted Abstract Circuit Generators ---

def build_adaptive_braid_v4_gate_list(
    n_qubits: int, 
    depth: int, 
    seed: int, 
    p_initial: float = 0.5, 
    p_final: float = 0.05
) -> List[AbstractGate]:
    """ Generates an 'Adaptive Braid' gate list (our v4 flagship model). """
    rng_py = random.Random(seed)
    rng_np = np.random.RandomState(seed)
    gates = []
    long_range_pairs = [ (i,j) for i in range(n_qubits) for j in range(n_qubits) if abs(i-j)>1 ]
    for step in range(depth):
        current_prob = p_initial + (p_final - p_initial) * (step / (depth - 1)) if depth > 1 else p_final
        if rng_py.random() < current_prob and n_qubits >= 4:
            control, target = rng_py.choice(long_range_pairs)
        else:
            i = rng_py.randint(0, n_qubits - 2)
            control, target = i, i + 1
            if rng_py.random() < 0.5:
                control, target = target, control
        Rc = random_single_qubit_rotation_from_rng(rng_np)
        Rt = random_single_qubit_rotation_from_rng(rng_np)
        gates.append(('G', control, target, Rc, Rt))
    return gates

def build_random_unitary_fair_gate_list(n_qubits: int, depth: int, seed: int) -> List[AbstractGate]:
    """ Generates a 'Purely Random' gate list for baseline comparison. """
    rng_py = random.Random(seed + 9999)
    rng_np = np.random.RandomState(seed + 9999)
    gates = []
    for _ in range(depth):
        control, target = rng_py.sample(range(n_qubits), 2)
        Rc = random_single_qubit_rotation_from_rng(rng_np)
        Rt = random_single_qubit_rotation_from_rng(rng_np)
        gates.append(('G', control, target, Rc, Rt))
    return gates

# --- Vetted Hardware-Aware Compiler ---

def compile_circuit(n_qubits: int, gate_list: List[AbstractGate]) -> List[CompiledGate]:
    """ Compiles an abstract gate list for a linear-chain hardware topology. """
    compiled = []
    for _, c, t, Rc, Rt in gate_list:
        if abs(c - t) == 1:
            compiled.append(('G', c, t, Rc, Rt))
        else:
            path = list(range(c, t, 1 if c < t else -1))
            swaps = list(zip(path, path[1:]))
            for a, b in swaps: compiled.append(('SWAP', a, b))
            compiled.append(('G', path[-1], t, Rc, Rt))
            for a, b in reversed(swaps): compiled.append(('SWAP', a, b))
    return compiled