import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import jsonschema
from jsonschema import validate


@dataclass
class LoadBalancerConfig:
    strategy: str
    health_check_interval: int
    timeout: int
    max_retries: int


@dataclass
class WorkloadPatternConfig:
    requests_per_second: int
    request_size: int
    duration: int
    peak_hours: Optional[list[int]] = None
    device_types: Optional[list[str]] = None
    patterns: Optional[list[str]] = None
    request_type: Optional[str] = None
    payload_type: Optional[str] = None
    concurrency_level: Optional[int] = None
    session_duration: Optional[int] = None
    retry_policy: Optional[Dict[str, Any]] = None
    rate_limiting: Optional[Dict[str, Any]] = None
    cloud_provider: Optional["CloudProviderConfig"] = None
    quantum: Optional["QuantumConfig"] = None
    edge: Optional["EdgeConfig"] = None
    ai_ml: Optional["AIMLConfig"] = None
    aws_pattern: Optional[Dict[str, Any]] = None
    azure_pattern: Optional[Dict[str, Any]] = None
    gcp_pattern: Optional[Dict[str, Any]] = None


@dataclass
class EdgeCaseConfig:
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None
    network_usage: Optional[float] = None
    duration: int = 30
    disk_io: Optional[Dict[str, Any]] = None
    network_latency: Optional[Dict[str, Any]] = None
    packet_loss: Optional[float] = None
    cache_contention: Optional[Dict[str, Any]] = None
    numa_effects: Optional[Dict[str, Any]] = None
    thermal_throttling: Optional[Dict[str, Any]] = None


@dataclass
class MetricsConfig:
    collection_interval: int
    thresholds: Dict[str, float]
    aggregation_periods: list[int]
    alert_thresholds: Dict[str, float]
    anomaly_detection: Dict[str, Any]
    trend_analysis: Dict[str, Any]


@dataclass
class ReportingConfig:
    output_dir: str
    format: str
    include_metrics: list[str]


@dataclass
class VisualizationConfig:
    output_dir: str
    format: str
    include_metrics: list[str]
    theme: str = "default"
    refresh_interval: int = 5
    interactive: bool = True
    export_formats: list[str] = None
    dashboard_layout: Dict[str, Any] = None
    chart_types: Dict[str, str] = None


@dataclass
class CloudProviderConfig:
    provider: str
    region: str
    instance_type: str
    auto_scaling: Dict[str, Any]
    load_balancer_type: str
    health_check: Dict[str, Any]
    ssl_config: Dict[str, Any]
    network_config: Dict[str, Any]


@dataclass
class QuantumConfig:
    enabled: bool
    qubit_count: int
    error_correction: str
    quantum_algorithm: str
    classical_hybrid: bool


@dataclass
class EdgeConfig:
    enabled: bool
    edge_type: str
    latency_requirements: Dict[str, float]
    data_processing: Dict[str, Any]
    synchronization: Dict[str, Any]


@dataclass
class AIMLConfig:
    enabled: bool
    model_type: str
    training_interval: int
    features: list[str]
    prediction_horizon: int
    confidence_threshold: float


class ConfigManager:
    """Manages loading and validation of load balancer configuration."""

    CONFIG_SCHEMA = {
        "type": "object",
        "required": [
            "load_balancer",
            "workload_patterns",
            "edge_cases",
            "metrics",
            "reporting",
            "visualization",
        ],
        "properties": {
            "load_balancer": {
                "type": "object",
                "required": [
                    "strategy",
                    "health_check_interval",
                    "timeout",
                    "max_retries",
                ],
                "properties": {
                    "strategy": {
                        "type": "string",
                        "enum": ["round_robin", "least_connections", "weighted"],
                    },
                    "health_check_interval": {"type": "integer", "minimum": 1},
                    "timeout": {"type": "integer", "minimum": 1},
                    "max_retries": {"type": "integer", "minimum": 1},
                },
            },
            "workload_patterns": {
                "type": "object",
                "patternProperties": {
                    "^.*$": {
                        "type": "object",
                        "required": ["requests_per_second", "request_size", "duration"],
                        "properties": {
                            "requests_per_second": {"type": "integer", "minimum": 1},
                            "request_size": {"type": "integer", "minimum": 1},
                            "duration": {"type": "integer", "minimum": 1},
                            "peak_hours": {
                                "type": "array",
                                "items": {"type": "integer"},
                            },
                            "device_types": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "patterns": {"type": "array", "items": {"type": "string"}},
                            "request_type": {
                                "type": "string",
                                "enum": ["http", "websocket", "grpc", "tcp"],
                            },
                            "payload_type": {
                                "type": "string",
                                "enum": ["json", "xml", "binary", "text"],
                            },
                            "concurrency_level": {"type": "integer", "minimum": 1},
                            "session_duration": {"type": "integer", "minimum": 1},
                            "retry_policy": {
                                "type": "object",
                                "properties": {
                                    "max_retries": {"type": "integer", "minimum": 0},
                                    "backoff_factor": {"type": "number", "minimum": 0},
                                    "timeout": {"type": "integer", "minimum": 1},
                                },
                            },
                            "rate_limiting": {
                                "type": "object",
                                "properties": {
                                    "requests_per_second": {
                                        "type": "integer",
                                        "minimum": 1,
                                    },
                                    "burst_size": {"type": "integer", "minimum": 1},
                                },
                            },
                            "cloud_provider": {
                                "type": "object",
                                "properties": {
                                    "provider": {
                                        "type": "string",
                                        "enum": ["aws", "azure", "gcp"],
                                    },
                                    "region": {"type": "string"},
                                    "instance_type": {"type": "string"},
                                    "auto_scaling": {
                                        "type": "object",
                                        "properties": {
                                            "min_instances": {
                                                "type": "integer",
                                                "minimum": 1,
                                            },
                                            "max_instances": {
                                                "type": "integer",
                                                "minimum": 1,
                                            },
                                            "scaling_policies": {
                                                "type": "array",
                                                "items": {"type": "object"},
                                            },
                                        },
                                    },
                                    "load_balancer_type": {"type": "string"},
                                    "health_check": {
                                        "type": "object",
                                        "properties": {
                                            "protocol": {"type": "string"},
                                            "port": {"type": "integer"},
                                            "path": {"type": "string"},
                                            "interval": {"type": "integer"},
                                            "timeout": {"type": "integer"},
                                            "healthy_threshold": {"type": "integer"},
                                            "unhealthy_threshold": {"type": "integer"},
                                        },
                                    },
                                },
                            },
                            "quantum": {
                                "type": "object",
                                "properties": {
                                    "enabled": {"type": "boolean"},
                                    "qubit_count": {"type": "integer", "minimum": 1},
                                    "error_correction": {"type": "string"},
                                    "quantum_algorithm": {"type": "string"},
                                    "classical_hybrid": {"type": "boolean"},
                                },
                            },
                            "edge": {
                                "type": "object",
                                "properties": {
                                    "enabled": {"type": "boolean"},
                                    "edge_type": {
                                        "type": "string",
                                        "enum": ["iot", "mobile", "fog"],
                                    },
                                    "latency_requirements": {
                                        "type": "object",
                                        "properties": {
                                            "max_latency": {
                                                "type": "number",
                                                "minimum": 0,
                                            },
                                            "jitter": {"type": "number", "minimum": 0},
                                        },
                                    },
                                    "data_processing": {
                                        "type": "object",
                                        "properties": {
                                            "local_processing": {"type": "boolean"},
                                            "data_retention": {"type": "integer"},
                                            "compression": {"type": "boolean"},
                                        },
                                    },
                                },
                            },
                            "ai_ml": {
                                "type": "object",
                                "properties": {
                                    "enabled": {"type": "boolean"},
                                    "model_type": {
                                        "type": "string",
                                        "enum": [
                                            "regression",
                                            "classification",
                                            "clustering",
                                        ],
                                    },
                                    "training_interval": {
                                        "type": "integer",
                                        "minimum": 1,
                                    },
                                    "features": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                    },
                                    "prediction_horizon": {
                                        "type": "integer",
                                        "minimum": 1,
                                    },
                                    "confidence_threshold": {
                                        "type": "number",
                                        "minimum": 0,
                                        "maximum": 1,
                                    },
                                },
                            },
                            "aws_pattern": {
                                "type": "object",
                                "properties": {
                                    "alb_config": {
                                        "type": "object",
                                        "properties": {
                                            "scheme": {
                                                "type": "string",
                                                "enum": ["internet-facing", "internal"],
                                            },
                                            "ip_address_type": {
                                                "type": "string",
                                                "enum": ["ipv4", "dualstack"],
                                            },
                                            "security_groups": {
                                                "type": "array",
                                                "items": {"type": "string"},
                                            },
                                            "subnets": {
                                                "type": "array",
                                                "items": {"type": "string"},
                                            },
                                        },
                                    },
                                    "target_groups": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "protocol": {"type": "string"},
                                                "port": {"type": "integer"},
                                                "target_type": {"type": "string"},
                                                "health_check_path": {"type": "string"},
                                            },
                                        },
                                    },
                                },
                            },
                            "azure_pattern": {
                                "type": "object",
                                "properties": {
                                    "sku": {
                                        "type": "string",
                                        "enum": ["Basic", "Standard", "Gateway"],
                                    },
                                    "frontend_ip_configurations": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "name": {"type": "string"},
                                                "public_ip_address": {"type": "string"},
                                                "subnet": {"type": "string"},
                                            },
                                        },
                                    },
                                    "backend_pools": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "name": {"type": "string"},
                                                "virtual_network": {"type": "string"},
                                                "ip_addresses": {
                                                    "type": "array",
                                                    "items": {"type": "string"},
                                                },
                                            },
                                        },
                                    },
                                },
                            },
                            "gcp_pattern": {
                                "type": "object",
                                "properties": {
                                    "load_balancing_scheme": {
                                        "type": "string",
                                        "enum": ["EXTERNAL", "INTERNAL"],
                                    },
                                    "network_tier": {
                                        "type": "string",
                                        "enum": ["PREMIUM", "STANDARD"],
                                    },
                                    "backend_services": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "name": {"type": "string"},
                                                "protocol": {"type": "string"},
                                                "timeout_sec": {"type": "integer"},
                                                "health_checks": {
                                                    "type": "array",
                                                    "items": {"type": "string"},
                                                },
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    }
                },
            },
            "edge_cases": {
                "type": "object",
                "patternProperties": {
                    "^.*$": {
                        "type": "object",
                        "required": ["duration"],
                        "properties": {
                            "cpu_usage": {"type": "number", "minimum": 0, "maximum": 1},
                            "memory_usage": {
                                "type": "number",
                                "minimum": 0,
                                "maximum": 1,
                            },
                            "network_usage": {
                                "type": "number",
                                "minimum": 0,
                                "maximum": 1,
                            },
                            "duration": {"type": "integer", "minimum": 1},
                            "disk_io": {
                                "type": "object",
                                "properties": {
                                    "read_latency": {"type": "number", "minimum": 0},
                                    "write_latency": {"type": "number", "minimum": 0},
                                    "iops": {"type": "integer", "minimum": 0},
                                },
                            },
                            "network_latency": {
                                "type": "object",
                                "properties": {
                                    "min_latency": {"type": "number", "minimum": 0},
                                    "max_latency": {"type": "number", "minimum": 0},
                                    "jitter": {"type": "number", "minimum": 0},
                                },
                            },
                            "packet_loss": {
                                "type": "number",
                                "minimum": 0,
                                "maximum": 1,
                            },
                            "cache_contention": {
                                "type": "object",
                                "properties": {
                                    "cache_size": {"type": "integer", "minimum": 0},
                                    "contention_level": {
                                        "type": "number",
                                        "minimum": 0,
                                        "maximum": 1,
                                    },
                                },
                            },
                            "numa_effects": {
                                "type": "object",
                                "properties": {
                                    "numa_nodes": {"type": "integer", "minimum": 1},
                                    "memory_access_pattern": {
                                        "type": "string",
                                        "enum": ["local", "remote", "mixed"],
                                    },
                                },
                            },
                            "thermal_throttling": {
                                "type": "object",
                                "properties": {
                                    "temperature_threshold": {
                                        "type": "number",
                                        "minimum": 0,
                                    },
                                    "throttling_level": {
                                        "type": "number",
                                        "minimum": 0,
                                        "maximum": 1,
                                    },
                                },
                            },
                        },
                    }
                },
            },
            "metrics": {
                "type": "object",
                "required": [
                    "collection_interval",
                    "thresholds",
                    "aggregation_periods",
                    "alert_thresholds",
                ],
                "properties": {
                    "collection_interval": {"type": "integer", "minimum": 1},
                    "thresholds": {
                        "type": "object",
                        "required": [
                            "success_rate",
                            "load_balance",
                            "response_time",
                            "error_rate",
                        ],
                        "properties": {
                            "success_rate": {
                                "type": "number",
                                "minimum": 0,
                                "maximum": 1,
                            },
                            "load_balance": {
                                "type": "number",
                                "minimum": 0,
                                "maximum": 1,
                            },
                            "response_time": {"type": "number", "minimum": 0},
                            "error_rate": {
                                "type": "number",
                                "minimum": 0,
                                "maximum": 1,
                            },
                        },
                    },
                    "aggregation_periods": {
                        "type": "array",
                        "items": {"type": "integer", "minimum": 1},
                    },
                    "alert_thresholds": {
                        "type": "object",
                        "properties": {
                            "critical": {"type": "number"},
                            "warning": {"type": "number"},
                            "info": {"type": "number"},
                        },
                    },
                    "anomaly_detection": {
                        "type": "object",
                        "properties": {
                            "method": {
                                "type": "string",
                                "enum": ["zscore", "iqr", "mad"],
                            },
                            "threshold": {"type": "number", "minimum": 0},
                            "window_size": {"type": "integer", "minimum": 1},
                        },
                    },
                    "trend_analysis": {
                        "type": "object",
                        "properties": {
                            "window_size": {"type": "integer", "minimum": 1},
                            "confidence_level": {
                                "type": "number",
                                "minimum": 0,
                                "maximum": 1,
                            },
                        },
                    },
                },
            },
            "reporting": {
                "type": "object",
                "required": ["output_dir", "format", "include_metrics"],
                "properties": {
                    "output_dir": {"type": "string"},
                    "format": {"type": "string", "enum": ["html", "json", "csv"]},
                    "include_metrics": {"type": "array", "items": {"type": "string"}},
                },
            },
            "visualization": {
                "type": "object",
                "required": ["output_dir", "format", "include_metrics"],
                "properties": {
                    "theme": {"type": "string"},
                    "refresh_interval": {"type": "integer", "minimum": 1},
                    "interactive": {"type": "boolean"},
                    "export_formats": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["png", "svg", "pdf", "html"],
                        },
                    },
                    "dashboard_layout": {
                        "type": "object",
                        "properties": {
                            "grid_size": {
                                "type": "array",
                                "items": {"type": "integer"},
                            },
                            "widgets": {"type": "array", "items": {"type": "string"}},
                        },
                    },
                    "chart_types": {
                        "type": "object",
                        "patternProperties": {
                            "^.*$": {
                                "type": "string",
                                "enum": ["line", "bar", "scatter", "heatmap"],
                            }
                        },
                    },
                },
            },
        },
    }

    def __init__(self, config_path: str):
        """Initialize the configuration manager with a path to the config file."""
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self.load_balancer_config: Optional[LoadBalancerConfig] = None
        self.workload_patterns: Dict[str, WorkloadPatternConfig] = {}
        self.edge_cases: Dict[str, EdgeCaseConfig] = {}
        self.metrics_config: Optional[MetricsConfig] = None
        self.reporting_config: Optional[ReportingConfig] = None
        self.visualization_config: Optional[VisualizationConfig] = None

    def load_config(self) -> None:
        """Load and validate the configuration file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        with open(self.config_path, "r") as f:
            self.config = json.load(f)

        # Validate against schema
        validate(instance=self.config, schema=self.CONFIG_SCHEMA)

        # Parse into dataclasses
        self._parse_config()

    def _parse_config(self) -> None:
        """Parse the validated configuration into dataclasses."""
        # Parse load balancer config
        lb = self.config["load_balancer"]
        self.load_balancer_config = LoadBalancerConfig(
            strategy=lb["strategy"],
            health_check_interval=lb["health_check_interval"],
            timeout=lb["timeout"],
            max_retries=lb["max_retries"],
        )

        # Parse workload patterns with cloud-specific configurations
        for name, pattern in self.config["workload_patterns"].items():
            cloud_provider = None
            if "cloud_provider" in pattern:
                cp = pattern["cloud_provider"]
                cloud_provider = CloudProviderConfig(
                    provider=cp["provider"],
                    region=cp["region"],
                    instance_type=cp["instance_type"],
                    auto_scaling=cp["auto_scaling"],
                    load_balancer_type=cp["load_balancer_type"],
                    health_check=cp["health_check"],
                    ssl_config=cp.get("ssl_config", {}),
                    network_config=cp.get("network_config", {}),
                )

            quantum = None
            if "quantum" in pattern:
                q = pattern["quantum"]
                quantum = QuantumConfig(
                    enabled=q["enabled"],
                    qubit_count=q["qubit_count"],
                    error_correction=q["error_correction"],
                    quantum_algorithm=q["quantum_algorithm"],
                    classical_hybrid=q["classical_hybrid"],
                )

            edge = None
            if "edge" in pattern:
                e = pattern["edge"]
                edge = EdgeConfig(
                    enabled=e["enabled"],
                    edge_type=e["edge_type"],
                    latency_requirements=e["latency_requirements"],
                    data_processing=e["data_processing"],
                    synchronization=e.get("synchronization", {}),
                )

            ai_ml = None
            if "ai_ml" in pattern:
                am = pattern["ai_ml"]
                ai_ml = AIMLConfig(
                    enabled=am["enabled"],
                    model_type=am["model_type"],
                    training_interval=am["training_interval"],
                    features=am["features"],
                    prediction_horizon=am["prediction_horizon"],
                    confidence_threshold=am["confidence_threshold"],
                )

            self.workload_patterns[name] = WorkloadPatternConfig(
                requests_per_second=pattern["requests_per_second"],
                request_size=pattern["request_size"],
                duration=pattern["duration"],
                peak_hours=pattern.get("peak_hours"),
                device_types=pattern.get("device_types"),
                patterns=pattern.get("patterns"),
                request_type=pattern.get("request_type"),
                payload_type=pattern.get("payload_type"),
                concurrency_level=pattern.get("concurrency_level"),
                session_duration=pattern.get("session_duration"),
                cloud_provider=cloud_provider,
                quantum=quantum,
                edge=edge,
                ai_ml=ai_ml,
                aws_pattern=pattern.get("aws_pattern"),
                azure_pattern=pattern.get("azure_pattern"),
                gcp_pattern=pattern.get("gcp_pattern"),
            )

        # Parse edge cases
        for name, case in self.config["edge_cases"].items():
            self.edge_cases[name] = EdgeCaseConfig(
                cpu_usage=case.get("cpu_usage"),
                memory_usage=case.get("memory_usage"),
                network_usage=case.get("network_usage"),
                duration=case["duration"],
                disk_io=case.get("disk_io"),
                network_latency=case.get("network_latency"),
                packet_loss=case.get("packet_loss"),
                cache_contention=case.get("cache_contention"),
                numa_effects=case.get("numa_effects"),
                thermal_throttling=case.get("thermal_throttling"),
            )

        # Parse metrics config
        metrics = self.config["metrics"]
        self.metrics_config = MetricsConfig(
            collection_interval=metrics["collection_interval"],
            thresholds=metrics["thresholds"],
            aggregation_periods=metrics["aggregation_periods"],
            alert_thresholds=metrics["alert_thresholds"],
            anomaly_detection=metrics["anomaly_detection"],
            trend_analysis=metrics["trend_analysis"],
        )

        # Parse reporting config
        reporting = self.config["reporting"]
        self.reporting_config = ReportingConfig(
            output_dir=reporting["output_dir"],
            format=reporting["format"],
            include_metrics=reporting["include_metrics"],
        )

        # Parse visualization config
        visualization = self.config["visualization"]
        self.visualization_config = VisualizationConfig(
            output_dir=visualization["output_dir"],
            format=visualization["format"],
            include_metrics=visualization["include_metrics"],
            theme=visualization.get("theme", "default"),
            refresh_interval=visualization.get("refresh_interval", 5),
            interactive=visualization.get("interactive", True),
            export_formats=visualization.get("export_formats"),
            dashboard_layout=visualization.get("dashboard_layout"),
            chart_types=visualization.get("chart_types"),
        )

    def get_workload_pattern(self, name: str) -> WorkloadPatternConfig:
        """Get a specific workload pattern configuration."""
        if name not in self.workload_patterns:
            raise KeyError(f"Workload pattern '{name}' not found in configuration")
        return self.workload_patterns[name]

    def get_edge_case(self, name: str) -> EdgeCaseConfig:
        """Get a specific edge case configuration."""
        if name not in self.edge_cases:
            raise KeyError(f"Edge case '{name}' not found in configuration")
        return self.edge_cases[name]

    def validate_workload_pattern(self, pattern: WorkloadPatternConfig) -> bool:
        """Validate a workload pattern configuration."""
        if pattern.requests_per_second <= 0:
            return False
        if pattern.request_size <= 0:
            return False
        if pattern.duration <= 0:
            return False
        if pattern.peak_hours and not all(0 <= h <= 23 for h in pattern.peak_hours):
            return False
        if pattern.concurrency_level is not None and pattern.concurrency_level <= 0:
            return False
        if pattern.session_duration is not None and pattern.session_duration <= 0:
            return False
        if pattern.retry_policy is not None:
            if pattern.retry_policy.get("max_retries", 0) < 0:
                return False
            if pattern.retry_policy.get("backoff_factor", 0) < 0:
                return False
            if pattern.retry_policy.get("timeout", 0) <= 0:
                return False
        if pattern.rate_limiting is not None:
            if pattern.rate_limiting.get("requests_per_second", 0) <= 0:
                return False
            if pattern.rate_limiting.get("burst_size", 0) <= 0:
                return False
        return True

    def validate_edge_case(self, case: EdgeCaseConfig) -> bool:
        """Validate an edge case configuration."""
        if case.duration <= 0:
            return False
        if case.cpu_usage is not None and not 0 <= case.cpu_usage <= 1:
            return False
        if case.memory_usage is not None and not 0 <= case.memory_usage <= 1:
            return False
        if case.network_usage is not None and not 0 <= case.network_usage <= 1:
            return False
        if case.disk_io is not None:
            if case.disk_io.get("read_latency", 0) < 0:
                return False
            if case.disk_io.get("write_latency", 0) < 0:
                return False
            if case.disk_io.get("iops", 0) < 0:
                return False
        if case.network_latency is not None:
            if case.network_latency.get("min_latency", 0) < 0:
                return False
            if case.network_latency.get("max_latency", 0) < 0:
                return False
            if case.network_latency.get("jitter", 0) < 0:
                return False
        if case.packet_loss is not None and not 0 <= case.packet_loss <= 1:
            return False
        if case.cache_contention is not None:
            if case.cache_contention.get("cache_size", 0) < 0:
                return False
            if not 0 <= case.cache_contention.get("contention_level", 0) <= 1:
                return False
        if case.numa_effects is not None:
            if case.numa_effects.get("numa_nodes", 0) < 1:
                return False
        if case.thermal_throttling is not None:
            if case.thermal_throttling.get("temperature_threshold", 0) < 0:
                return False
            if not 0 <= case.thermal_throttling.get("throttling_level", 0) <= 1:
                return False
        return True
