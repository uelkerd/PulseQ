"""
License Management System

Handles license key generation, validation, and feature access control.
"""

import json
import hashlib
import datetime
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

class LicenseManager:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.fernet = self._create_fernet(secret_key)
    
    def _create_fernet(self, secret_key: str) -> Fernet:
        """Create Fernet instance for encryption"""
        salt = b'pulseq_license_salt'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(secret_key.encode()))
        return Fernet(key)
    
    def generate_license(self, 
                        customer_id: str,
                        tier: str,
                        features: Dict[str, Any],
                        expiry_date: Optional[datetime.datetime] = None) -> str:
        """Generate a new license key"""
        license_data = {
            'customer_id': customer_id,
            'tier': tier,
            'features': features,
            'issued_at': datetime.datetime.utcnow().isoformat(),
            'expiry_date': expiry_date.isoformat() if expiry_date else None
        }
        
        # Encrypt license data
        encrypted_data = self.fernet.encrypt(
            json.dumps(license_data).encode()
        )
        
        # Create license key
        license_key = base64.urlsafe_b64encode(encrypted_data).decode()
        return license_key
    
    def validate_license(self, license_key: str) -> Dict[str, Any]:
        """Validate a license key and return license data"""
        try:
            # Decode and decrypt license data
            encrypted_data = base64.urlsafe_b64decode(license_key)
            decrypted_data = self.fernet.decrypt(encrypted_data)
            license_data = json.loads(decrypted_data)
            
            # Check expiry
            if license_data.get('expiry_date'):
                expiry = datetime.datetime.fromisoformat(license_data['expiry_date'])
                if datetime.datetime.utcnow() > expiry:
                    raise ValueError("License has expired")
            
            return license_data
        except Exception as e:
            raise ValueError(f"Invalid license key: {str(e)}")
    
    def check_feature_access(self, license_key: str, feature: str) -> bool:
        """Check if a feature is available in the license"""
        license_data = self.validate_license(license_key)
        return feature in license_data['features']
    
    def get_usage_limits(self, license_key: str) -> Dict[str, Any]:
        """Get usage limits from license"""
        license_data = self.validate_license(license_key)
        return license_data['features'].get('usage_limits', {})
    
    def revoke_license(self, license_key: str) -> None:
        """Revoke a license key"""
        # Implementation for license revocation
        pass 