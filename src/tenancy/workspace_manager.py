"""
Bartholomew Milestone 5.0: Multi-Tenant Enterprise Workspaces & Scoped Project Isolation.
=========================================================================================
Implements:
1. Organization & Project hierarchical tenancy.
2. Scoped API keys (btp_live_... and btp_test_...).
3. Deterministic cryptographic tenant hashing: T = SHA-256(org_id || project_id || environment).
4. Role-based tenant boundary controls.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import time
from typing import Dict, Any, List, Optional, Tuple


class EnvironmentType:
    DEVELOPMENT = "dev"
    STAGING = "staging"
    PRODUCTION = "prod"


class WorkspaceTenant:
    """Represents a fully qualified tenant isolation context."""

    def __init__(
        self,
        org_id: str,
        project_id: str,
        environment: str = EnvironmentType.DEVELOPMENT,
        display_name: Optional[str] = None,
        created_at: Optional[float] = None
    ):
        self.org_id = org_id.lower().strip()
        self.project_id = project_id.lower().strip()
        self.environment = environment.lower().strip()
        self.display_name = display_name or f"{self.org_id}/{self.project_id} ({self.environment})"
        self.created_at = created_at or time.time()
        self.tenant_id = self.compute_tenant_hash(self.org_id, self.project_id, self.environment)

    @staticmethod
    def compute_tenant_hash(org_id: str, project_id: str, environment: str) -> str:
        """Computes deterministic SHA-256 tenant hash."""
        seed = f"btp:tenant:{org_id.lower().strip()}:{project_id.lower().strip()}:{environment.lower().strip()}"
        return "ten_" + hashlib.sha256(seed.encode("utf-8")).hexdigest()[:24]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tenant_id": self.tenant_id,
            "org_id": self.org_id,
            "project_id": self.project_id,
            "environment": self.environment,
            "display_name": self.display_name,
            "created_at": self.created_at,
        }


class WorkspaceManager:
    """
    Manages multi-tenant organizations, projects, environments, and cryptographically
    scoped API keys.
    """

    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path or os.path.join(os.getcwd(), ".btp_workspaces.json")
        self.tenants: Dict[str, WorkspaceTenant] = {}
        self.api_keys: Dict[str, Dict[str, Any]] = {}
        self._load()

    def _load(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for t_data in data.get("tenants", []):
                    t = WorkspaceTenant(
                        org_id=t_data["org_id"],
                        project_id=t_data["project_id"],
                        environment=t_data.get("environment", EnvironmentType.DEVELOPMENT),
                        display_name=t_data.get("display_name"),
                        created_at=t_data.get("created_at")
                    )
                    self.tenants[t.tenant_id] = t
                self.api_keys = data.get("api_keys", {})
            except Exception:
                pass

    def _save(self):
        try:
            os.makedirs(os.path.dirname(os.path.abspath(self.storage_path)), exist_ok=True)
            data = {
                "tenants": [t.to_dict() for t in self.tenants.values()],
                "api_keys": self.api_keys,
                "updated_at": time.time()
            }
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def create_tenant(
        self,
        org_id: str,
        project_id: str,
        environment: str = EnvironmentType.DEVELOPMENT,
        display_name: Optional[str] = None
    ) -> WorkspaceTenant:
        """Creates or retrieves a workspace tenant."""
        tenant = WorkspaceTenant(org_id, project_id, environment, display_name)
        self.tenants[tenant.tenant_id] = tenant
        self._save()
        return tenant

    def get_tenant(self, org_id: str, project_id: str, environment: str) -> Optional[WorkspaceTenant]:
        tenant_id = WorkspaceTenant.compute_tenant_hash(org_id, project_id, environment)
        return self.tenants.get(tenant_id)

    def generate_scoped_api_key(
        self,
        org_id: str,
        project_id: str,
        environment: str = EnvironmentType.DEVELOPMENT,
        role: str = "developer"
    ) -> str:
        """
        Generates a scoped API key bound to the specific organization, project, and environment.
        Prefixes:
          - btp_live_... for production
          - btp_test_... for development / staging
        """
        tenant = self.create_tenant(org_id, project_id, environment)
        prefix = "btp_live_" if environment == EnvironmentType.PRODUCTION else "btp_test_"
        raw_secret = secrets.token_hex(20)
        api_key = f"{prefix}{raw_secret}"

        key_hash = hashlib.sha256(api_key.encode("utf-8")).hexdigest()
        self.api_keys[key_hash] = {
            "tenant_id": tenant.tenant_id,
            "org_id": tenant.org_id,
            "project_id": tenant.project_id,
            "environment": tenant.environment,
            "role": role,
            "created_at": time.time(),
            "prefix": prefix,
        }
        self._save()
        return api_key

    def verify_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Verifies an API key and returns its tenant context."""
        key_hash = hashlib.sha256(api_key.encode("utf-8")).hexdigest()
        return self.api_keys.get(key_hash)

    def list_tenants(self) -> List[Dict[str, Any]]:
        return [t.to_dict() for t in self.tenants.values()]
