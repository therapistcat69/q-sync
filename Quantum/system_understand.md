Q-SYNC INTEGRATION CONTRACT & TECHNICAL HANDOVERSubsystem: ProbiCore (Quantum & Mathematical Core)
Target Audience: Lead Backend Architect, Lead Machine Learning Engineer1. Subsystem OverviewProbiCore is the foundational quantum-inspired mathematical module for Q-SYNC. It computes the state overlap (fidelity) and classical similarity metrics between a trusted reference baseline and live cyber-physical telemetry.   Mathematical Model: ProbiCore utilizes a two-qubit architecture where Qubit 0 encodes the digital domain (e.g., CPU, memory, disk I/O) and Qubit 1 encodes the physical domain (e.g., temperature, vibration).   Execution Environment: The quantum statevector is simulated entirely on the host machine using Qiskit. It does not require physical quantum hardware or ESP32 embedded processing for its calculations.   Validation Status: All numerical constraints have been verified via automated tests. The module guarantees normalization within floating-point tolerance, rejects invalid states, and explicitly handles classical zero-vector edge cases.   2. Environment & DependenciesThe backend host environment must install the following dependencies before initializing the module.Plaintext# requirements.txt
numpy>=1.24.0
scipy>=1.10.0
qiskit>=1.0.0
3. Data Contracts & SchemasInput Schema (TelemetryObservation)All data passed to ProbiCore must be packaged in the TelemetryObservation dataclass.FieldTypeDescriptionStrict ConstraintstimestampfloatEpoch timestamp of the synchronized observation.Must be aligned by the Time-Series agent.digital_featuresList[float]Ordered array of digital metrics.Must not be empty. Must contain only finite numbers.   physical_featuresList[float]Ordered array of physical metrics.Must not be empty. Must contain only finite numbers.   source_idstrIdentifier of the host/ESP32 pair.Used for telemetry tracing and logging.Pre-Processing Mandate for Time-Series Agent: ProbiCore does not impute data. Missing readings (NaN) or stale sensor data must be explicitly resolved (dropped or imputed) by the temporal synchronization pipeline before ingestion. The module will raise a ValueError if non-finite inputs are provided.   4. Backend Integration GuidePhase A: InitializationInstantiate the FeatureNormalizer and ProbiCoreAPI once during the FastAPI application startup. The normalizer requires pre-calibrated boundaries (min/max) for your specific feature set to map inputs to rotation angles $[0, \pi]$.   Pythonfrom probicore.normalization import FeatureNormalizer
from probicore.main_api import ProbiCoreAPI

# Example bounds: [(CPU_min, CPU_max), (Mem_min, Mem_max)]
normalizer = FeatureNormalizer(
    digital_bounds=[(0.0, 100.0), (0.0, 16384.0)], 
    physical_bounds=[(20.0, 80.0), (0.0, 10.0)]
)
probicore_engine = ProbiCoreAPI(normalizer)
Phase B: Baseline CreationBefore live evaluation can occur, the system must register a reference baseline. This must be constructed from a verified NORMAL or LEGITIMATE_WORKLOAD operational state, not from arbitrary, untrusted live traffic.   Pythonfrom probicore.schemas import TelemetryObservation

calibration_obs = TelemetryObservation(
    timestamp=1713024000.0,
    digital_features=[12.5, 4096.0],
    physical_features=[45.0, 1.02],
    source_id="host_node_1"
)

# Registers the statevector in memory for future comparison
probicore_engine.create_reference_baseline("baseline_idle_v1", calibration_obs)
Phase C: Live Analytics LoopDuring the live streaming loop, pass incoming observations to analyze_observation(). This calculates the pure-state fidelity ($F = \vert{}\langle\Psi_{\mathrm{base}} \mid \Psi_{\mathrm{live}}\rangle\vert{}^2$) alongside Euclidean and Cosine classical baselines.   Pythonlive_obs = TelemetryObservation(
    timestamp=1713024005.0,
    digital_features=[89.0, 8192.0],
    physical_features=[55.0, 3.5],
    source_id="host_node_1"
)

try:
    result = probicore_engine.analyze_observation("baseline_idle_v1", live_obs)
    # Forward 'result' to ML Pipeline & Dashboard
except ValueError as e:
    # Log error and trigger classical-only fallback
    logger.error(f"ProbiCore computation failed: {e}")
5. Machine Learning Integration GuideThe analyze_observation() method returns a structured, JSON-compatible dictionary. The ML agent must consume this payload to append quantum-derived features to the Random Forest and Isolation Forest models.   Output Payload:JSON{
    "timestamp": 1713024005.0,
    "baseline_id": "baseline_idle_v1",
    "fidelity": 0.432,
    "metrics": {
        "euclidean": 45.6,
        "cosine": 0.812
    },
    "processing_latency_ms": 2.15,
    "status": "SUCCESS"
}
Interpretation & Usage Rules for ML Pipeline:Feature Integration: Extract fidelity, metrics.euclidean, and metrics.cosine to use as continuous features in the ablation studies.   No Direct Translation: Fidelity must never be presented as a direct percentage of safety, attack probability, or security confidence. It strictly represents mathematical overlap.   Threshold Calibration: Do not hardcode an arbitrary fidelity threshold. If converting fidelity to an anomaly flag, the threshold must be calibrated experimentally using validation data.   Ablation Support: The ML pipeline must be built so that it continues to function effectively (using classical-only features) when ProbiCore is disabled or unavailable.   6. Fault Tolerance & IntegrityExplicit Failure States: If quantum computation fails (e.g., due to unnormalized external states or dimensionality errors), ProbiCore will raise an exception rather than returning a misleading number.   Backend Responsibility: The Backend integration agent must catch these exceptions. Do not silently substitute a failed calculation with a zero or a fabricated 1.0 fidelity score. The ML subsystem must recognize the missing feature and utilize its classical logic.