"""
Security Configuration Module

Manages security settings and configurations for the test automation framework.
"""

import os
import json
from typing import Dict, Any, Optional, List
from pathlib import Path
import logging
from datetime import datetime

class SecurityConfig:
    def __init__(self, config_path: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        self.config_path = config_path or os.path.join('config', 'security.json')
        self.config = self._load_config()
        self._validate_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load security configuration from file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            else:
                return self._get_default_config()
        except Exception as e:
            self.logger.error(f"Error loading security config: {str(e)}")
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default security configuration"""
        return {
            'authentication': {
                'enabled': True,
                'jwt_secret': os.urandom(32).hex(),
                'token_expiry': 3600,
                'refresh_token_expiry': 86400,
                'password_policy': {
                    'min_length': 12,
                    'require_uppercase': True,
                    'require_lowercase': True,
                    'require_numbers': True,
                    'require_special_chars': True,
                    'max_age_days': 90
                }
            },
            'authorization': {
                'enabled': True,
                'role_based_access': True,
                'permission_groups': {
                    'admin': ['*'],
                    'user': ['read', 'execute'],
                    'viewer': ['read']
                }
            },
            'encryption': {
                'enabled': True,
                'algorithm': 'AES-256-GCM',
                'key_rotation_interval': 30,
                'encrypt_sensitive_data': True
            },
            'audit': {
                'enabled': True,
                'log_level': 'INFO',
                'retention_days': 90,
                'log_sensitive_operations': True
            },
            'network': {
                'enabled': True,
                'require_ssl': True,
                'allowed_origins': ['*'],
                'rate_limiting': {
                    'enabled': True,
                    'requests_per_minute': 60
                }
            },
            'vulnerability_scanning': {
                'enabled': True,
                'scan_frequency': 'daily',
                'severity_threshold': 'medium',
                'auto_remediation': False
            },
            'compliance': {
                'enabled': True,
                'standards': ['hipaa', 'gdpr', 'soc2'],
                'audit_trail': True,
                'data_retention': {
                    'enabled': True,
                    'period_days': 365
                }
            }
        }

    def _validate_config(self) -> None:
        """Validate security configuration"""
        required_sections = [
            'authentication',
            'authorization',
            'encryption',
            'audit',
            'network',
            'vulnerability_scanning',
            'compliance'
        ]
        
        for section in required_sections:
            if section not in self.config:
                self.logger.warning(f"Missing required section: {section}")
                self.config[section] = self._get_default_config()[section]

    def save_config(self) -> None:
        """Save security configuration to file"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving security config: {str(e)}")

    def update_config(self, updates: Dict[str, Any]) -> None:
        """Update security configuration"""
        for section, values in updates.items():
            if section in self.config:
                self.config[section].update(values)
            else:
                self.config[section] = values
        self._validate_config()
        self.save_config()

    def get_config(self, section: Optional[str] = None) -> Dict[str, Any]:
        """Get security configuration or specific section"""
        if section:
            return self.config.get(section, {})
        return self.config

    def is_feature_enabled(self, feature: str) -> bool:
        """Check if a security feature is enabled"""
        section, feature = feature.split('.')
        return self.config.get(section, {}).get('enabled', False) and \
               self.config.get(section, {}).get(feature, False)

    def get_password_policy(self) -> Dict[str, Any]:
        """Get password policy configuration"""
        return self.config['authentication']['password_policy']

    def get_audit_settings(self) -> Dict[str, Any]:
        """Get audit settings"""
        return self.config['audit']

    def get_compliance_standards(self) -> List[str]:
        """Get compliance standards"""
        return self.config['compliance']['standards']

    def get_network_security(self) -> Dict[str, Any]:
        """Get network security settings"""
        return self.config['network']

    def get_vulnerability_scanning(self) -> Dict[str, Any]:
        """Get vulnerability scanning settings"""
        return self.config['vulnerability_scanning']

    def get_authorization_groups(self) -> Dict[str, List[str]]:
        """Get authorization groups"""
        return self.config['authorization']['permission_groups'] 