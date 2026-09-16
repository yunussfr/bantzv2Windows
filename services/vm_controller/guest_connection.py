import hmac
import hashlib
import json
from typing import Dict, Any, Optional


class GuestConnection:
    """Host ve Guest Agent arasında paylaşımlı gizli anahtarlı (HMAC) kimlik doğrulamalı kanal."""

    def __init__(self, shared_secret: str = "bantz-vm-guest-key-2026"):
        self.shared_secret = shared_secret.encode("utf-8")
        self.is_connected = False

    def generate_auth_token(self, payload_str: str) -> str:
        """İleti için HMAC-SHA256 imzası üretir."""
        return hmac.new(self.shared_secret, payload_str.encode("utf-8"), hashlib.sha256).hexdigest()

    def verify_auth_token(self, payload_str: str, signature: str) -> bool:
        """Gelen iletinin HMAC-SHA256 imzasını doğrular."""
        expected = self.generate_auth_token(payload_str)
        return hmac.compare_digest(expected, signature)

    def pack_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """İletiyi imzalı zarf içine koyar."""
        payload_str = json.dumps(message, sort_keys=True)
        sig = self.generate_auth_token(payload_str)
        return {
            "payload": message,
            "signature": sig
        }

    def unpack_message(self, envelope: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Zarfı açar ve imzayı doğrular. İmzası geçersizse None döndürür."""
        payload = envelope.get("payload")
        sig = envelope.get("signature")
        if not payload or not sig:
            return None

        payload_str = json.dumps(payload, sort_keys=True)
        if not self.verify_auth_token(payload_str, sig):
            return None
        return payload
