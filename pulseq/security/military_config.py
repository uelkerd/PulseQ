"""
Military-Grade Security Configuration

Provides advanced security configuration management meeting military and government standards.
"""

import hashlib
import json
import logging
import os
import secrets
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


class MilitaryConfig:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.logger = logging.getLogger(__name__)
        self.config = self._load_config()
        self.secure_random = secrets.SystemRandom()

    def _load_config(self) -> Dict[str, Any]:
        """Load military-grade security configuration"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r") as f:
                    return json.load(f)
            else:
                return self._get_default_config()
        except Exception as e:
            self.logger.error(f"Error loading config: {str(e)}")
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default military-grade security configuration"""
        return {
            "authentication": {
                "enabled": True,
                "password_policy": {
                    "min_length": 16,
                    "require_uppercase": True,
                    "require_lowercase": True,
                    "require_numbers": True,
                    "require_special_chars": True,
                    "max_age_days": 90,
                    "history_size": 24,
                    "lockout_attempts": 5,
                    "lockout_duration_minutes": 30,
                },
                "mfa": {
                    "enabled": True,
                    "required": True,
                    "methods": ["totp", "fido2", "smart_card"],
                },
                "session": {
                    "timeout_minutes": 15,
                    "max_concurrent_sessions": 1,
                    "invalidate_on_ip_change": True,
                },
            },
            "authorization": {
                "enabled": True,
                "rbac": {
                    "enabled": True,
                    "default_role": "user",
                    "roles": {
                        "admin": ["*"],
                        "user": ["read", "execute"],
                        "auditor": ["read", "audit"],
                    },
                },
                "abac": {
                    "enabled": True,
                    "attributes": ["department", "clearance_level", "location"],
                },
            },
            "encryption": {
                "enabled": True,
                "algorithms": {
                    "symmetric": "AES-256-GCM",
                    "asymmetric": "RSA-4096",
                    "hash": "SHA-512",
                    "key_derivation": "PBKDF2-SHA512",
                },
                "key_rotation": {
                    "enabled": True,
                    "interval_days": 30,
                    "grace_period_days": 7,
                },
                "fips_mode": True,
            },
            "audit": {
                "enabled": True,
                "log_level": "INFO",
                "retention_days": 365,
                "events": [
                    "authentication",
                    "authorization",
                    "data_access",
                    "configuration_changes",
                    "security_events",
                ],
                "syslog": {
                    "enabled": True,
                    "host": "localhost",
                    "port": 514,
                    "protocol": "tcp",
                },
            },
            "network_security": {
                "enabled": True,
                "ssl": {
                    "enabled": True,
                    "min_version": "TLSv1.2",
                    "ciphers": [
                        "TLS_AES_256_GCM_SHA384",
                        "TLS_CHACHA20_POLY1305_SHA256",
                    ],
                },
                "firewall": {
                    "enabled": True,
                    "rules": [
                        {
                            "action": "allow",
                            "protocol": "tcp",
                            "ports": [443, 22],
                            "source": "0.0.0.0/0",
                        }
                    ],
                },
                "ids": {"enabled": True, "rules": "strict"},
            },
            "vulnerability_scanning": {
                "enabled": True,
                "schedule": "daily",
                "severity_threshold": "medium",
                "exclusions": [],
                "reporting": {"format": "pdf", "recipients": ["security@example.com"]},
            },
            "compliance": {
                "enabled": True,
                "standards": [
                    "fips_140_2",
                    "nist_800_53",
                    "nist_800_171",
                    "iso_27001",
                    "common_criteria",
                ],
                "audit_frequency": "quarterly",
                "documentation": {"required": True, "retention_years": 7},
            },
            "threat_protection": {
                "enabled": True,
                "insider_threat": {
                    "enabled": True,
                    "monitoring": ["file_access", "data_transfer", "privilege_use"],
                },
                "data_exfiltration": {
                    "enabled": True,
                    "monitoring": ["network_traffic", "usb_devices", "cloud_storage"],
                },
                "privilege_escalation": {
                    "enabled": True,
                    "monitoring": [
                        "sudo_usage",
                        "setuid_execution",
                        "capability_changes",
                    ],
                },
            },
        }

    def save_config(self) -> bool:
        """Save current configuration to file"""
        try:
            with open(self.config_path, "w") as f:
                json.dump(self.config, f, indent=4)
            return True
        except Exception as e:
            self.logger.error(f"Error saving config: {str(e)}")
            return False

    def update_config(self, section: str, settings: Dict[str, Any]) -> bool:
        """Update specific configuration section"""
        try:
            if section in self.config:
                self.config[section].update(settings)
                return self.save_config()
            return False
        except Exception as e:
            self.logger.error(f"Error updating config: {str(e)}")
            return False

    def get_config(self) -> Dict[str, Any]:
        """Get entire configuration"""
        return self.config

    def get_section(self, section: str) -> Optional[Dict[str, Any]]:
        """Get specific configuration section"""
        return self.config.get(section)

    def is_feature_enabled(self, feature: str) -> bool:
        """Check if specific security feature is enabled"""
        section = feature.split(".")[0]
        setting = feature.split(".")[1]
        return self.config.get(section, {}).get(setting, False)

    def get_password_policy(self) -> Dict[str, Any]:
        """Get password policy settings"""
        return self.config["authentication"]["password_policy"]

    def get_audit_settings(self) -> Dict[str, Any]:
        """Get audit settings"""
        return self.config["audit"]

    def get_compliance_standards(self) -> List[str]:
        """Get enabled compliance standards"""
        return self.config["compliance"]["standards"]

    def get_network_security_settings(self) -> Dict[str, Any]:
        """Get network security settings"""
        return self.config["network_security"]

    def get_vulnerability_scanning_settings(self) -> Dict[str, Any]:
        """Get vulnerability scanning settings"""
        return self.config["vulnerability_scanning"]

    def get_authorization_groups(self) -> Dict[str, List[str]]:
        """Get authorization groups and their permissions"""
        return self.config["authorization"]["rbac"]["roles"]

    def validate_config(self) -> List[str]:
        """Validate configuration against military standards"""
        issues = []

        # Check password policy
        policy = self.get_password_policy()
        if policy["min_length"] < 16:
            issues.append("Password minimum length must be at least 16 characters")
        if not all(
            [
                policy["require_uppercase"],
                policy["require_lowercase"],
                policy["require_numbers"],
                policy["require_special_chars"],
            ]
        ):
            issues.append("Password policy must require all character types")

        # Check encryption settings
        encryption = self.config["encryption"]
        if not encryption["fips_mode"]:
            issues.append("FIPS mode must be enabled")
        if encryption["algorithms"]["symmetric"] != "AES-256-GCM":
            issues.append("Symmetric encryption must use AES-256-GCM")
        if encryption["algorithms"]["asymmetric"] != "RSA-4096":
            issues.append("Asymmetric encryption must use RSA-4096")

        # Check network security
        network = self.get_network_security_settings()
        if network["ssl"]["min_version"] != "TLSv1.2":
            issues.append("Minimum TLS version must be 1.2")

        # Check compliance
        compliance = self.config["compliance"]
        required_standards = ["fips_140_2", "nist_800_53", "nist_800_171"]
        for standard in required_standards:
            if standard not in compliance["standards"]:
                issues.append(f"Required compliance standard {standard} is missing")

        return issues

    def generate_security_report(self) -> Dict[str, Any]:
        """Generate comprehensive security configuration report"""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "configuration_status": {
                "valid": len(self.validate_config()) == 0,
                "issues": self.validate_config(),
            },
            "features_enabled": {
                "authentication": self.is_feature_enabled("authentication.enabled"),
                "authorization": self.is_feature_enabled("authorization.enabled"),
                "encryption": self.is_feature_enabled("encryption.enabled"),
                "audit": self.is_feature_enabled("audit.enabled"),
                "network_security": self.is_feature_enabled("network_security.enabled"),
                "vulnerability_scanning": self.is_feature_enabled(
                    "vulnerability_scanning.enabled"
                ),
                "compliance": self.is_feature_enabled("compliance.enabled"),
                "threat_protection": self.is_feature_enabled(
                    "threat_protection.enabled"
                ),
            },
            "compliance_status": {
                "standards": self.get_compliance_standards(),
                "documentation": self.config["compliance"]["documentation"],
            },
            "security_controls": {
                "password_policy": self.get_password_policy(),
                "network_security": self.get_network_security_settings(),
                "authorization": self.get_authorization_groups(),
            },
        }
