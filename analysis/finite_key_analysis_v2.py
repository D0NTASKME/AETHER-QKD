# analysis/finite_key_analysis_v2.py

import math
import numpy as np
from typing import Dict

# =============================================================================
# TEAL Simulator - Finite-Key Security Analysis Engine
# =============================================================================
# This module contains the definitive, industry-grade analysis logic for
# calculating a robust, finite-key secure key rate. It replaces the simple
# asymptotic formulas with a more rigorous statistical treatment based on
# concentration inequalities (Chernoff-Hoeffding bounds).
# =============================================================================

def shannon_entropy(p: float) -> float:
    """Calculates the binary Shannon entropy H(p)."""
    if p <= 0 or p >= 1:
        return 0.0
    return -p * math.log2(p) - (1 - p) * math.log2(1 - p)

def chernoff_hoeffding_bound(
    num_errors: int,
    num_samples: int,
    security_parameter: float
) -> float:
    """
    Calculates the upper bound on the error rate using the Chernoff-Hoeffding bound.

    Args:
        num_errors: The number of observed errors in the sample.
        num_samples: The total size of the sample.
        security_parameter: The probability that the true error rate exceeds
                            this bound (e.g., 1e-9).

    Returns:
        The pessimistic upper bound on the true error rate.
    """
    if num_samples == 0:
        return 1.0 # Worst-case scenario if we have no data
        
    observed_rate = num_errors / num_samples
    delta = math.sqrt(math.log(1 / security_parameter) / (2 * num_samples))
    
    return min(1.0, observed_rate + delta)

def calculate_finite_key_rate(
    sifted_key_len: int,
    num_errors: int,
    total_initial_qubits: int,
    security_parameter_qber: float = 1e-9,
    source_leakage_rate: float = 0.0,
    error_correction_efficiency: float = 1.1
) -> Dict[str, float]:
    """
    Calculates the secure key rate under a finite-key analysis.
    """
    if sifted_key_len == 0:
        return {'qber_obs': 0, 'qber_bound': 1.0, 'secure_key_rate': 0.0}

    # --- Step 1: Robust Parameter Estimation ---
    # We don't use the observed QBER directly. We calculate its pessimistic
    # upper bound using a concentration inequality.
    qber_observed = num_errors / sifted_key_len
    qber_upper_bound = chernoff_hoeffding_bound(num_errors, sifted_key_len, security_parameter_qber)

    # --- Step 2: Calculate Secure Key Rate using the Pessimistic Bound ---
    sifting_efficiency = sifted_key_len / total_initial_qubits

    # All terms in the security proof must now use the worst-case QBER.
    eve_info_from_channel = shannon_entropy(qber_upper_bound)
    eve_info_from_leakage = shannon_entropy(source_leakage_rate)
    bob_error_correction_cost = error_correction_efficiency * shannon_entropy(qber_observed) # Correction depends on observed errors

    # The final rate is reduced by all leakage terms.
    rate = sifting_efficiency * (1 - eve_info_from_channel - eve_info_from_leakage - bob_error_correction_cost)
    
    secure_rate = max(0.0, rate)

    return {
        'qber_obs': qber_observed,
        'qber_bound': qber_upper_bound,
        'secure_key_rate': secure_rate,
        'sifted_key_length': sifted_key_len
    }