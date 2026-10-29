import numpy as np

class FeatureNormalizer:
    def __init__(self, digital_bounds, physical_bounds):
        self.digital_bounds = digital_bounds # [(min, max), ...]
        self.physical_bounds = physical_bounds
        
    def normalize_to_angle(self, features, bounds):
        angles = []
        for val, (min_val, max_val) in zip(features, bounds):
            if max_val == min_val:
                angles.append(0.0)
                continue
            clipped = np.clip(val, min_val, max_val)
            normalized = (clipped - min_val) / (max_val - min_val)
            angles.append(normalized * np.pi) # Map to [0, pi] for Ry gate
        return np.mean(angles) # Aggregate to a single angle per domain for baseline 2-qubit mapping