from datetime import datetime
from typing import Any, Literal
from pydantic import BaseModel, Field, ConfigDict

class Metric(BaseModel):
    model_config = ConfigDict(extra="allow")
    status: str = "ok"

class CPU(Metric): usage_percent: float = Field(ge=0, le=100)
class Memory(Metric): usage_percent: float = Field(ge=0, le=100); used_bytes: int | None = None; total_bytes: int | None = None
class Disk(Metric): read_bytes_per_sec: float | None = Field(default=None, ge=0); write_bytes_per_sec: float | None = Field(default=None, ge=0)
class Digital(BaseModel):
    timestamp_utc: datetime; sampling_interval_ms: int = Field(gt=0)
    cpu: CPU; memory: Memory; disk_io: Disk
    status: str = "ok"
class Temperature(Metric): object_temperature_c: float | None = None; ambient_temperature_c: float | None = None; sensor: str = "MLX90614"
class Accel(BaseModel): x: float; y: float; z: float
class Motion(Metric): sensor: str = "MPU6050"; acceleration_g: Accel; acceleration_magnitude_g: float = Field(ge=0); vibration_rms_g: float | None = None
class Physical(BaseModel): timestamp_utc: datetime; device_timestamp_ms: int | None = None; sequence: int | None = None; temperature: Temperature; motion: Motion; status: str = "ok"
class Wifi(BaseModel): scan_status: str = "unavailable"; access_point_count: int | None = Field(default=None, ge=0); access_points: list[dict[str, Any]] = []
class Metadata(BaseModel): device_id: str = "unknown"; host_id: str = "unknown"; session_id: str = "default"; sequence: int | None = None; firmware_version: str | None = None
class ObservationIn(BaseModel):
    schema_version: str = "1.0"; observation_id: str | None = None
    mode: Literal["live", "simulated", "replay"] = "live"; timestamp_utc: datetime
    metadata: Metadata = Field(default_factory=Metadata); digital: Digital; physical: Physical; wifi: Wifi = Field(default_factory=Wifi)
class ObservationOut(ObservationIn):
    assessment: dict[str, Any]; health: dict[str, str]; created_at: datetime
class ExperimentIn(BaseModel): scenario: Literal["baseline", "cpu_spike", "thermal_rise", "vibration", "wifi_change", "timing_lag", "combined"]
class IncidentUpdate(BaseModel): status: Literal["open", "investigating", "resolved"]
