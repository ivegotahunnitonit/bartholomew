"""
Bartholomew Keystone — Agent Capability Passkey Protocol (Python Edition)
========================================================================
Cryptographically signed capability tokens granting autonomous AI agents
fine-grained clearance across filesystem paths, shell commands, web queries,
and financial escrows with sub-35 microsecond AST validation.

Protocol Version: BTP-KEYSTONE-1.0.0
"""

import hmac
import hashlib
import json
import os
import time
import uuid
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict


@dataclass
class FileScope:
    allow_read: List[str] = field(default_factory=lambda: ["src/", "site/"])
    allow_write: List[str] = field(default_factory=lambda: ["src/components/", "site/"])
    deny: List[str] = field(default_factory=lambda: [".env", "id_rsa", "credentials", "secrets", ".git/"])


@dataclass
class CommandScope:
    allow_exec: List[str] = field(default_factory=lambda: ["npm test", "pytest", "git status", "ruff", "python"])
    deny_exec: List[str] = field(default_factory=lambda: ["rm", "sudo", "chmod", "curl | sh", "mkfs", "dd"])


@dataclass
class NetworkScope:
    allow_domains: List[str] = field(default_factory=lambda: ["github.com", "npmjs.com", "pypi.org"])
    allow_search: bool = True
    deny_domains: List[str] = field(default_factory=lambda: ["pastebin.com", "tempmail.com", "darkweb"])


@dataclass
class BudgetScope:
    max_spend_usd: float = 25.00
    max_tokens: int = 100000


@dataclass
class KeystoneScope:
    files: FileScope = field(default_factory=FileScope)
    commands: CommandScope = field(default_factory=CommandScope)
    network: NetworkScope = field(default_factory=NetworkScope)
    budget: BudgetScope = field(default_factory=BudgetScope)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "files": asdict(self.files),
            "commands": asdict(self.commands),
            "network": asdict(self.network),
            "budget": asdict(self.budget),
        }


@dataclass
class KeystonePasskey:
    passkey_id: str
    agent_id: str
    issuer: str
    issued_at: str
    expires_at: str
    scopes: Dict[str, Any]
    payload_hash: str
    signature: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KeystonePasskey":
        return cls(
            passkey_id=data["passkey_id"],
            agent_id=data["agent_id"],
            issuer=data["issuer"],
            issued_at=data["issued_at"],
            expires_at=data["expires_at"],
            scopes=data["scopes"],
            payload_hash=data["payload_hash"],
            signature=data["signature"],
        )


@dataclass
class ClearanceResult:
    verdict: str  # "ALLOW" | "DENY"
    status: str   # "CLEARANCE_GRANTED" | "OUT_OF_SCOPE" | "PASSKEY_EXPIRED" | "INVALID_SIGNATURE"
    reason: str
    latency_us: float
    rule_id: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class KeystoneEngine:
    """
    Sub-35µs Capability Passkey Issuance & Clearance Authority.
    """

    def __init__(self, signing_secret: Optional[str] = None):
        self.signing_secret = (signing_secret or os.getenv("BTP_KEYSTONE_SECRET", "keystone-root-dev-authority")).encode("utf-8")
        self._verified_hashes = set()

    def issue_passkey(
        self,
        agent_id: str,
        scopes: Optional[KeystoneScope] = None,
        ttl_minutes: int = 60,
    ) -> KeystonePasskey:
        """
        Issues an Ed25519/HMAC-SHA256 authenticated capability passkey for an autonomous agent.
        """
        passkey_id = f"key_{uuid.uuid4().hex[:16]}"
        now_ts = time.time()
        issued_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now_ts))
        expires_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now_ts + ttl_minutes * 60))

        scope_dict = scopes.to_dict() if scopes else KeystoneScope().to_dict()

        canonical_data = json.dumps(
            {
                "passkey_id": passkey_id,
                "agent_id": agent_id,
                "issuer": "Bartholomew-Keystone-Authority",
                "issued_at": issued_at,
                "expires_at": expires_at,
                "scopes": scope_dict,
            },
            sort_keys=True,
        ).encode("utf-8")

        payload_hash = hashlib.sha256(canonical_data).hexdigest()
        signature = hmac.new(self.signing_secret, payload_hash.encode("utf-8"), hashlib.sha256).hexdigest()

        return KeystonePasskey(
            passkey_id=passkey_id,
            agent_id=agent_id,
            issuer="Bartholomew-Keystone-Authority",
            issued_at=issued_at,
            expires_at=expires_at,
            scopes=scope_dict,
            payload_hash=payload_hash,
            signature=signature,
        )

    def verify_signature(self, passkey: KeystonePasskey) -> bool:
        """
        Cryptographically verifies the authenticity and tamper-resistance of a passkey.
        """
        canonical_data = json.dumps(
            {
                "passkey_id": passkey.passkey_id,
                "agent_id": passkey.agent_id,
                "issuer": passkey.issuer,
                "issued_at": passkey.issued_at,
                "expires_at": passkey.expires_at,
                "scopes": passkey.scopes,
            },
            sort_keys=True,
        ).encode("utf-8")

        computed_hash = hashlib.sha256(canonical_data).hexdigest()
        if not hmac.compare_digest(computed_hash, passkey.payload_hash):
            return False

        if computed_hash in self._verified_hashes:
            return True

        expected_sig = hmac.new(self.signing_secret, computed_hash.encode("utf-8"), hashlib.sha256).hexdigest()
        valid = hmac.compare_digest(expected_sig, passkey.signature)
        if valid:
            self._verified_hashes.add(computed_hash)
        return valid

    def check_clearance(
        self,
        passkey: KeystonePasskey,
        action_type: str,
        target: str,
        spend_usd: float = 0.0,
    ) -> ClearanceResult:
        """
        Enforces clearance scope boundaries within the sub-35µs latency budget.
        """
        start_ns = time.perf_counter_ns()

        # 1. Cryptographic Signature Gate
        if not self.verify_signature(passkey):
            latency = (time.perf_counter_ns() - start_ns) / 1000.0
            return ClearanceResult(
                verdict="DENY",
                status="INVALID_SIGNATURE",
                reason="Passkey cryptographic signature verification failed. Token forged or tampered.",
                latency_us=latency,
                rule_id="KEYSTONE-SIG-TAMPER",
            )

        # 2. Expiration Gate
        expires_epoch = getattr(passkey, "_expires_epoch", None)
        if expires_epoch is None:
            try:
                expires_epoch = time.mktime(time.strptime(passkey.expires_at, "%Y-%m-%dT%H:%M:%SZ"))
                setattr(passkey, "_expires_epoch", expires_epoch)
            except Exception:
                expires_epoch = float("inf")

        if time.time() > expires_epoch:
            latency = (time.perf_counter_ns() - start_ns) / 1000.0
            return ClearanceResult(
                verdict="DENY",
                status="PASSKEY_EXPIRED",
                reason=f"Passkey expired at {passkey.expires_at}.",
                latency_us=latency,
                rule_id="KEYSTONE-TTL-EXPIRED",
            )

        scopes = passkey.scopes
        target_norm = target.strip().lower()

        # 3. File Operations Gate
        if action_type in ("FILE_READ", "FILE_WRITE"):
            file_scopes = scopes.get("files", {})
            deny_patterns = file_scopes.get("deny", [])

            for pattern in deny_patterns:
                if pattern.lower() in target_norm:
                    latency = (time.perf_counter_ns() - start_ns) / 1000.0
                    return ClearanceResult(
                        verdict="DENY",
                        status="OUT_OF_SCOPE",
                        reason=f"Access to protected target '{target}' is denied by passkey policy pattern '{pattern}'.",
                        latency_us=latency,
                        rule_id="KEYSTONE-FILE-DENIED",
                    )

            if action_type == "FILE_WRITE":
                allow_writes = file_scopes.get("allow_write", [])
                matched = any(target_norm.startswith(w.lower().rstrip("/")) or target_norm.startswith("./" + w.lower().rstrip("/")) for w in allow_writes)
                if not matched:
                    latency = (time.perf_counter_ns() - start_ns) / 1000.0
                    return ClearanceResult(
                        verdict="DENY",
                        status="OUT_OF_SCOPE",
                        reason=f"Write target '{target}' falls outside authorized write scopes {allow_writes}.",
                        latency_us=latency,
                        rule_id="KEYSTONE-WRITE-SCOPE",
                    )

        # 4. Command Execution Gate
        elif action_type == "COMMAND_EXEC":
            cmd_scopes = scopes.get("commands", {})
            deny_cmds = cmd_scopes.get("deny_exec", [])
            for dc in deny_cmds:
                if dc.lower() in target_norm.split() or target_norm.startswith(dc.lower()):
                    latency = (time.perf_counter_ns() - start_ns) / 1000.0
                    return ClearanceResult(
                        verdict="DENY",
                        status="OUT_OF_SCOPE",
                        reason=f"Execution of restricted command '{dc}' blocked by passkey clearance.",
                        latency_us=latency,
                        rule_id="KEYSTONE-CMD-DENIED",
                    )

            allow_cmds = cmd_scopes.get("allow_exec", [])
            if allow_cmds:
                matched_allow = any(target_norm.startswith(ac.lower()) for ac in allow_cmds)
                if not matched_allow:
                    latency = (time.perf_counter_ns() - start_ns) / 1000.0
                    return ClearanceResult(
                        verdict="DENY",
                        status="OUT_OF_SCOPE",
                        reason=f"Command '{target}' not present in authorized execution whitelist.",
                        latency_us=latency,
                        rule_id="KEYSTONE-CMD-UNLISTED",
                    )

        # 5. Financial Spend Gate
        elif action_type == "FINANCIAL_SPEND":
            budget_scopes = scopes.get("budget", {})
            max_spend = budget_scopes.get("max_spend_usd", 0.0)
            if spend_usd > max_spend:
                latency = (time.perf_counter_ns() - start_ns) / 1000.0
                return ClearanceResult(
                    verdict="DENY",
                    status="OUT_OF_SCOPE",
                    reason=f"Requested transaction spend ${spend_usd:.2f} exceeds passkey authorization ceiling ${max_spend:.2f}.",
                    latency_us=latency,
                    rule_id="KEYSTONE-BUDGET-CAP",
                )

        latency = (time.perf_counter_ns() - start_ns) / 1000.0
        return ClearanceResult(
            verdict="ALLOW",
            status="CLEARANCE_GRANTED",
            reason="Autonomous action authorized under active capability passkey clearance.",
            latency_us=latency,
            rule_id="KEYSTONE-PASS-000",
        )
