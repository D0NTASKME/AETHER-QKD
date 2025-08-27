# postprocessing/privacy_amplification.py
import math
def shannon_entropy(p):
    if p <= 0 or p >= 1: return 0.0
    return -p * math.log2(p) - (1 - p) * math.log2(1 - p)

def calculate_privacy_amplification(
    key_to_amplify: list,
    qber: float,
    leakage_from_source: float,
    leakage_from_ec: int
) -> int:
    """
    Calculates the length of the final, perfectly secret key.
    """
    n = len(key_to_amplify)
    eve_info_from_qber = n * shannon_entropy(qber)
    eve_info_from_leakage = n * shannon_entropy(leakage_from_source)
    
    final_key_length = n - eve_info_from_qber - eve_info_from_leakage - leakage_from_ec
    return math.floor(max(0.0, final_key_length))