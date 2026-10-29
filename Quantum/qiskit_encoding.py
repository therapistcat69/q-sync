import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

def prepare_two_qubit_state(theta_digital: float, theta_physical: float) -> np.ndarray:
    """Encodes digital and physical angles into a 2-qubit statevector."""
    qc = QuantumCircuit(2)
    # Qubit 0: Digital, Qubit 1: Physical
    qc.ry(theta_digital, 0)
    qc.ry(theta_physical, 1)
    
    # Extract the statevector (C^4)
    state = Statevector(qc)
    sv_data = state.data
    
    # Validate exactly 4 complex amplitudes and normalization
    assert len(sv_data) == 4, "Statevector must have exactly 4 amplitudes."
    assert np.isclose(np.linalg.norm(sv_data), 1.0, atol=1e-6), "State is not normalized."
    
    return sv_data