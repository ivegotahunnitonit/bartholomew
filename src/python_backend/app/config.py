"""
python_backend.app.config
=========================
Environment Isolation & Deployment Boundary Manager for Bartholomew Enterprise Security Platform.
Enforces strict separation between Development, Staging, and Production enclaves.
"""

import os
from enum import Enum
from typing import Dict, Any

class EnvironmentMode(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

class AppConfig:
    def __init__(self):
        self.env_name: str = os.getenv("BARTHOLOMEW_ENV", EnvironmentMode.DEVELOPMENT.value).lower()
        self.port: int = int(os.getenv("PORT", "8000"))
        
        # Environment Boundary Policies
        self.allow_fuzzer_execution: bool = self.env_name in [EnvironmentMode.DEVELOPMENT.value, EnvironmentMode.STAGING.value]
        self.enforce_strict_rbac: bool = self.env_name == EnvironmentMode.PRODUCTION.value
        self.immutable_audit_logs: bool = self.env_name in [EnvironmentMode.STAGING.value, EnvironmentMode.PRODUCTION.value]
        self.allow_public_demo: bool = self.env_name == EnvironmentMode.DEVELOPMENT.value
        
    def get_environment_summary(self) -> Dict[str, Any]:
        return {
            "environment": self.env_name.upper(),
            "fuzzer_permitted": self.allow_fuzzer_execution,
            "strict_rbac_active": self.enforce_strict_rbac,
            "immutable_audit_logs": self.immutable_audit_logs,
            "public_demo_allowed": self.allow_public_demo,
            "isolation_status": "STRICT_3_TIER_BOUNDARY_ENFORCED"
        }

settings = AppConfig()
