import numpy as np

def compute_fidelity(psi_base: np.ndarray, psi_live: np.ndarray) -> float:
    """Computes pure-state fidelity F = |<psi_base | psi_live>|^2."""
    if len(psi_base) != 4 or len(psi_live) != 4:
        raise ValueError("Invalid statevector dimension. Must be 4.")
    if not np.isclose(np.linalg.norm(psi_base), 1.0) or not np.isclose(np.linalg.norm(psi_live), 1.0):
        raise ValueError("Inputs must be normalized states.")
        
    overlap = np.vdot(psi_base, psi_live) # Complex conjugate dot product
    fidelity = np.abs(overlap)**2
    return float(np.clip(fidelity, 0.0, 1.0))