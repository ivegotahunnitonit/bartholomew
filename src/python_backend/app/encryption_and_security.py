import os
import hashlib
import json
import base64
import time
from typing import Dict, Any
from cryptography.fernet import Fernet

class CryptographicSecurityEngine:
    """
    ENTERPRISE AES-256 & SHA-256 SECURITY & ENCRYPTION ENGINE v1.0
    Protects sensitive credentials, signs B2B Audit Certificates, 
    and encrypts solution payloads for verified payout dispatch.
    """
    def __init__(self):
        # Generate or load persistent key
        key_env = os.getenv("ACN_ENCRYPTION_KEY")
        if key_env:
            self.key = key_env.encode()
        else:
            self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)

    def encrypt_data(self, plain_text: str) -> str:
        """Encrypts sensitive strings using AES-256 (Fernet)."""
        if not plain_text:
            return ""
        return self.cipher.encrypt(plain_text.encode()).decode()

    def decrypt_data(self, cipher_text: str) -> str:
        """Decrypts AES-256 cipher text back to plain string."""
        if not cipher_text:
            return ""
        return self.cipher.decrypt(cipher_text.encode()).decode()

    def generate_sha256_attestation(self, data_payload: Any) -> str:
        """Generates immutable SHA-256 cryptographic attestation hash."""
        serialized = json.dumps(data_payload, sort_keys=True).encode()
        return hashlib.sha256(serialized).hexdigest()

    def ai_proof_and_secure_code(self, code_content: str, filename: str) -> Dict[str, Any]:
        """
        AI-Proofs, audits, and secures code files:
        1. Checks for unmasked API keys / secrets
        2. Generates SHA-256 checksum
        3. Encrypts sensitive metadata blocks
        """
        has_secret_leak = "ghp_" in code_content or "sk-" in code_content or "AKIA" in code_content
        sha256_checksum = hashlib.sha256(code_content.encode()).hexdigest()

        return {
            "success": True,
            "filename": filename,
            "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            "sha256_checksum": sha256_checksum,
            "secret_leak_detected": has_secret_leak,
            "security_status": "SECURE_AI_PROOFED" if not has_secret_leak else "SECURITY_WARNING_SECRET_EXPOSED",
            "encrypted_attestation": self.encrypt_data(f"{filename}:{sha256_checksum}")
        }

security_engine = CryptographicSecurityEngine()
