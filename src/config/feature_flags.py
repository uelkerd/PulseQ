from typing import Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

class FeatureFlags:
    _instance = None
    _flags: Dict[str, bool] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FeatureFlags, cls).__new__(cls)
            cls._instance._initialize_flags()
        return cls._instance

    def _initialize_flags(self):
        # Distributed Testing
        self._flags['distributed_testing'] = os.getenv('FEATURE_DISTRIBUTED_TESTING', 'false').lower() == 'true'
        
        # Cloud Integration
        self._flags['cloud_integration'] = os.getenv('FEATURE_CLOUD_INTEGRATION', 'false').lower() == 'true'
        
        # Advanced Caching
        self._flags['advanced_caching'] = os.getenv('FEATURE_ADVANCED_CACHING', 'false').lower() == 'true'
        
        # Multi-environment Testing
        self._flags['multi_env_testing'] = os.getenv('FEATURE_MULTI_ENV_TESTING', 'false').lower() == 'true'
        
        # Enhanced Monitoring
        self._flags['enhanced_monitoring'] = os.getenv('FEATURE_ENHANCED_MONITORING', 'false').lower() == 'true'

    def is_enabled(self, feature: str) -> bool:
        return self._flags.get(feature, False)

    def enable(self, feature: str) -> None:
        self._flags[feature] = True
        os.environ[f'FEATURE_{feature.upper()}'] = 'true'

    def disable(self, feature: str) -> None:
        self._flags[feature] = False
        os.environ[f'FEATURE_{feature.upper()}'] = 'false'

    def get_all_flags(self) -> Dict[str, bool]:
        return self._flags.copy()

# Singleton instance
feature_flags = FeatureFlags() 