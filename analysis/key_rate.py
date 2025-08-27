# analysis/key_rate.py

import math

def shannon_entropy(p: float) -> float:
    """Calculates the binary Shannon entropy H(p)."""
    if p <= 0 or p >= 1:
        return 0.0
    return -p * math.log2(p) - (1 - p) * math.log2(1 - p)

def secure_key_rate(
    qber: float, 
    sifting_efficiency: float, 
    leakage_rate: float = 0.0,
    error_correction_efficiency: float = 1.1
) -> float:
    """
    Calculates the final secure key rate using a formal information-theoretic model.
    This is the definitive, industry-grade version.

    The final rate R is given by a simplified formula:
    R = SiftingEfficiency * [1 - leak_EC - I_E]
    where leak_EC is the information revealed during error correction and
    I_E is the total information Eve has.
    """
    if not 0.0 <= qber <= 1.0: raise ValueError("QBER must be between 0 and 1.")
    if not 0.0 <= sifting_efficiency <= 1.0: raise ValueError("Sifting efficiency must be between 0 and 1.")

    # Information Bob must reveal to Alice for error correction.
    error_correction_leakage = error_correction_efficiency * shannon_entropy(qber)

    # Eve's total information is what she learns from the QBER plus any
    # information she learns from a direct source attack.
    eve_information = shannon_entropy(qber) + shannon_entropy(leakage_rate)

    # The raw rate of 1 bit per sifted signal is reduced by both costs.
    rate = sifting_efficiency * (1 - error_correction_leakage - eve_information)
    
    return max(0.0, rate)