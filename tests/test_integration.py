import pytest
from schemas import TelemetryObservation
from normalization import FeatureNormalizer
from main_api import ProbiCoreAPI

def test_integration_api():
    # Setup normalizer with mock min/max bounds
    normalizer = FeatureNormalizer(
        digital_bounds=[(0, 100), (0, 16)], 
        physical_bounds=[(20, 80), (0, 10)]
    )
    api = ProbiCoreAPI(normalizer)
    
    # Create baseline observation
    base_obs = TelemetryObservation(
        timestamp=1.0, 
        digital_features=[10.0, 4.0], 
        physical_features=[30.0, 1.0], 
        source_id="host_1"
    )
    api.create_reference_baseline("baseline_idle", base_obs)
    
    # Analyze a live observation that slightly deviates
    live_obs = TelemetryObservation(
        timestamp=2.0, 
        digital_features=[12.0, 4.5], 
        physical_features=[31.0, 1.2], 
        source_id="host_1"
    )
    result = api.analyze_observation("baseline_idle", live_obs)
    
    # Validate API output contract
    assert result["status"] == "SUCCESS"
    assert "fidelity" in result
    assert "metrics" in result
    assert result["fidelity"] > 0.9  # Small change should yield high fidelity
    assert "euclidean" in result["metrics"]
    assert "cosine" in result["metrics"]