import numpy as np
from scipy.spatial.distance import mahalanobis

def euclidean_distance(x: np.ndarray, y: np.ndarray) -> float:
    return float(np.linalg.norm(x - y))

def cosine_similarity(x: np.ndarray, y: np.ndarray) -> float:
    norm_x, norm_y = np.linalg.norm(x), np.linalg.norm(y)
    if norm_x == 0 or norm_y == 0:
        return 0.0 # Explicit zero-vector handling
    return float(np.dot(x, y) / (norm_x * norm_y))

def compute_mahalanobis(x: np.ndarray, y: np.ndarray, cov_matrix: np.ndarray) -> float:
    try:
        inv_cov = np.linalg.pinv(cov_matrix) # Stable pseudoinverse for singular matrices
        return float(mahalanobis(x, y, inv_cov))
    except np.linalg.LinAlgError:
        return -1.0 # Safe fallback