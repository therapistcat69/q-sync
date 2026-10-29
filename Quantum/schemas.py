import numpy as np
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class TelemetryObservation:
    timestamp: float
    digital_features: List[float]
    physical_features: List[float]
    source_id: str

    def validate(self):
        if not self.digital_features or not self.physical_features:
            raise ValueError("Feature vectors cannot be empty.")
        if any(not np.isfinite(x) for x in self.digital_features + self.physical_features):
            raise ValueError("All features must be finite numbers.")