"""
Pricing and Licensing Module
"""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import json
import logging
from enum import Enum

class FeatureTier(Enum):
    """Feature tiers for different pricing levels."""
    FREE = "free"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"
    MILITARY = "military"

class LicenseType(Enum):
    """Types of licenses available."""
    TRIAL = "trial"
    SUBSCRIPTION = "subscription"
    PERPETUAL = "perpetual"
    CUSTOM = "custom"

class PricingManager:
    """Manages pricing and licensing for different tiers."""
    
    def __init__(self):
        """Initialize pricing manager."""
        self.logger = logging.getLogger('pricing_manager')
        self.features = {
            FeatureTier.FREE: {
                'basic_scanning': True,
                'vulnerability_detection': True,
                'compliance_checking': True,
                'basic_reporting': True,
                'email_support': True
            },
            FeatureTier.PREMIUM: {
                'advanced_scanning': True,
                'supply_chain_analysis': True,
                'zero_day_detection': True,
                'cloud_security': True,
                'container_security': True,
                'priority_support': True,
                'api_access': True
            },
            FeatureTier.ENTERPRISE: {
                'custom_policies': True,
                'advanced_threat_detection': True,
                'integration_support': True,
                'dedicated_support': True,
                'on_premise_deployment': True,
                'custom_reporting': True
            },
            FeatureTier.MILITARY: {
                'military_grade_encryption': True,
                'advanced_persistent_threat_detection': True,
                'custom_compliance_frameworks': True,
                '24/7_support': True,
                'custom_integrations': True,
                'air_gapped_deployment': True
            }
        }
        
        self.pricing = {
            FeatureTier.FREE: {
                'monthly': 0,
                'annual': 0
            },
            FeatureTier.PREMIUM: {
                'monthly': 99,
                'annual': 990
            },
            FeatureTier.ENTERPRISE: {
                'monthly': 499,
                'annual': 4990
            },
            FeatureTier.MILITARY: {
                'monthly': 999,
                'annual': 9990
            }
        }
        
    def get_features(self, tier: FeatureTier) -> Dict[str, bool]:
        """Get features available for a specific tier."""
        return self.features.get(tier, {})
        
    def get_pricing(self, tier: FeatureTier, period: str = 'monthly') -> float:
        """Get pricing for a specific tier and period."""
        return self.pricing.get(tier, {}).get(period, 0)
        
    def calculate_discount(self, tier: FeatureTier, quantity: int) -> float:
        """Calculate volume discount."""
        if tier == FeatureTier.ENTERPRISE or tier == FeatureTier.MILITARY:
            if quantity >= 100:
                return 0.20  # 20% discount
            elif quantity >= 50:
                return 0.15  # 15% discount
            elif quantity >= 25:
                return 0.10  # 10% discount
        return 0.0
        
    def generate_quote(self, tier: FeatureTier, quantity: int = 1, 
                      period: str = 'monthly') -> Dict[str, Any]:
        """Generate a pricing quote."""
        base_price = self.get_pricing(tier, period)
        discount = self.calculate_discount(tier, quantity)
        subtotal = base_price * quantity
        discount_amount = subtotal * discount
        total = subtotal - discount_amount
        
        return {
            'tier': tier.value,
            'quantity': quantity,
            'period': period,
            'base_price': base_price,
            'subtotal': subtotal,
            'discount_percent': discount * 100,
            'discount_amount': discount_amount,
            'total': total,
            'features': self.get_features(tier)
        }

class LicenseManager:
    """Manages software licensing."""
    
    def __init__(self):
        """Initialize license manager."""
        self.logger = logging.getLogger('license_manager')
        
    def generate_license(self, tier: FeatureTier, 
                        license_type: LicenseType,
                        duration: Optional[int] = None,
                        quantity: int = 1) -> Dict[str, Any]:
        """Generate a new license."""
        try:
            license_data = {
                'tier': tier.value,
                'type': license_type.value,
                'quantity': quantity,
                'issued_at': datetime.utcnow().isoformat(),
                'features': PricingManager().get_features(tier)
            }
            
            if license_type == LicenseType.TRIAL:
                license_data['expires_at'] = (
                    datetime.utcnow() + timedelta(days=14)
                ).isoformat()
            elif license_type == LicenseType.SUBSCRIPTION:
                if duration:
                    license_data['expires_at'] = (
                        datetime.utcnow() + timedelta(days=duration)
                    ).isoformat()
            elif license_type == LicenseType.PERPETUAL:
                license_data['perpetual'] = True
                
            return license_data
            
        except Exception as e:
            self.logger.error(f"License generation failed: {str(e)}")
            return {'error': str(e)}
            
    def validate_license(self, license_data: Dict[str, Any]) -> bool:
        """Validate a license."""
        try:
            if license_data.get('perpetual', False):
                return True
                
            expires_at = datetime.fromisoformat(license_data['expires_at'])
            return datetime.utcnow() < expires_at
            
        except Exception as e:
            self.logger.error(f"License validation failed: {str(e)}")
            return False
            
    def check_feature_access(self, license_data: Dict[str, Any], 
                           feature: str) -> bool:
        """Check if a feature is accessible with the given license."""
        try:
            return license_data.get('features', {}).get(feature, False)
        except Exception as e:
            self.logger.error(f"Feature access check failed: {str(e)}")
            return False 