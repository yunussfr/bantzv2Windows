import re
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid


class SecretAuditRecord:
    def __init__(self, task_id: str, trace_id: str, credential_ref: str, action: str):
        self.record_id = str(uuid.uuid4())
        self.task_id = task_id
        self.trace_id = trace_id
        self.credential_ref = credential_ref
        self.action = action
        self.timestamp = datetime.now(timezone.utc).isoformat()


class SecretBroker:
    """Sırları (parola, API token, oturum çerezi) güvenle saklayan, izleyen ve maskeleyen aracı.

    Zero-Knowledge: Planner ve LLM asla gerçek sırrı göremez; sadece 'credentialRef' ile işlem yapar.
    """

    def __init__(self):
        # Güvenli iç kasa (gerçek ortamda Windows DPAPI veya Credential Manager kullanılır)
        self._vault: Dict[str, str] = {}
        self._audit_log: List[SecretAuditRecord] = []

    def register_secret(self, credential_ref: str, secret_value: str) -> None:
        """Kullanıcı veya auth modülü tarafından sır kasaya kaydedilir."""
        self._vault[credential_ref] = secret_value

    def get_secret_for_adapter(self, credential_ref: str, task_id: str, trace_id: str) -> Optional[str]:
        """Yalnızca icra anında izole adaptöre gerçek sırrı verir ve kullanımı audit loga işler."""
        if credential_ref not in self._vault:
            return None

        # Audit kaydı oluştur
        record = SecretAuditRecord(
            task_id=task_id,
            trace_id=trace_id,
            credential_ref=credential_ref,
            action="ACCESS"
        )
        self._audit_log.append(record)
        return self._vault[credential_ref]

    def mask_secrets(self, text: str) -> str:
        """Log veya kullanıcı çıktılarında bilinen sırları '***' ile maskeler."""
        masked_text = text
        for secret_val in self._vault.values():
            if secret_val and len(secret_val) >= 4:
                masked_text = masked_text.replace(secret_val, "***")
        return masked_text

    def get_audit_records(self, task_id: Optional[str] = None) -> List[Dict[str, Any]]:
        records = self._audit_log
        if task_id:
            records = [r for r in records if r.task_id == task_id]
        return [
            {
                "record_id": r.record_id,
                "task_id": r.task_id,
                "credential_ref": r.credential_ref,
                "timestamp": r.timestamp,
                "action": r.action
            }
            for r in records
        ]
