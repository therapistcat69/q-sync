import time
import numpy as np
from schemas import TelemetryObservation
from normalization import FeatureNormalizer
from qiskit_encoding import prepare_two_qubit_state
from fidelity import compute_fidelity
from classical_metrics import euclidean_distance, cosine_similarity

class ProbiCoreAPI:
    def __init__(self, normalizer: FeatureNormalizer):
        self.normalizer = normalizer
        self.baselines = {}

    def create_reference_baseline(self, baseline_id: str, obs: TelemetryObservation):
        obs.validate()
        theta_d = self.normalizer.normalize_to_angle(obs.digital_features, self.normalizer.digital_bounds)
        theta_p = self.normalizer.normalize_to_angle(obs.physical_features, self.normalizer.physical_bounds)
        state = prepare_two_qubit_state(theta_d, theta_p)
        self.baselines[baseline_id] = {
            "state": state,
            "raw_digital": np.array(obs.digital_features),
            "raw_physical": np.array(obs.physical_features)
        }
        return baseline_id

    def analyze_observation(self, baseline_id: str, obs: TelemetryObservation) -> dict:
        start_time = time.time()
        obs.validate()
        
        if baseline_id not in self.baselines:
            raise ValueError(f"Baseline {baseline_id} not found.")
            
        base_data = self.baselines[baseline_id]
        
        theta_d = self.normalizer.normalize_to_angle(obs.digital_features, self.normalizer.digital_bounds)
        theta_p = self.normalizer.normalize_to_angle(obs.physical_features, self.normalizer.physical_bounds)
        live_state = prepare_two_qubit_state(theta_d, theta_p)
        
        fidelity = compute_fidelity(base_data["state"], live_state)
        
        live_combined = np.concatenate([obs.digital_features, obs.physical_features])
        base_combined = np.concatenate([base_data["raw_digital"], base_data["raw_physical"]])
        
        results = {
            "timestamp": obs.timestamp,
            "baseline_id": baseline_id,
            "fidelity": fidelity,
            "metrics": {
                "euclidean": euclidean_distance(live_combined, base_combined),
                "cosine": cosine_similarity(live_combined, base_combined)
            },
            "processing_latency_ms": (time.time() - start_time) * 1000,
            "status": "SUCCESS"
        }
        return results