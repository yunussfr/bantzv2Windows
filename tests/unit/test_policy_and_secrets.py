import pytest
from packages.policy.capability_registry import CapabilityRegistry
from packages.policy.approval_engine import ApprovalEngine
from packages.policy.risk_classifier import RiskClassifier
from packages.secrets.secret_broker import SecretBroker


def test_capability_authorization_and_rejection():
    registry = CapabilityRegistry()
    registry.revoke_capability("process.run.destructive")

    engine = ApprovalEngine(capability_registry=registry, autonomy_tier="medium")

    # İzinli safe işlem
    assert engine.requires_approval("browser.read") is False

    # İzinli destructive işlem medium tier'da onay gerektirir
    assert engine.requires_approval("email.send") is True

    # Yetkisiz capability reddedilir
    with pytest.raises(PermissionError, match="Yetkisiz capability talebi reddedildi"):
        engine.requires_approval("process.run.destructive")


def test_secret_broker_zero_knowledge_masking_and_audit():
    broker = SecretBroker()
    ref = "secret://gmail/api_token"
    raw_token = "ya29.a0AfH6SMB_secret_access_token_12345"

    broker.register_secret(ref, raw_token)

    # Adaptör sırrı çeker
    resolved = broker.get_secret_for_adapter(ref, task_id="task-99", trace_id="tr-99")
    assert resolved == raw_token

    # Audit log kaydı doğrulanır
    audit_logs = broker.get_audit_records(task_id="task-99")
    assert len(audit_logs) == 1
    assert audit_logs[0]["credential_ref"] == ref

    # Loglarda maskeleme (***)
    raw_log = f"Görevi icra ederken token={raw_token} kullanıldı."
    masked_log = broker.mask_secrets(raw_log)
    assert raw_token not in masked_log
    assert "token=***" in masked_log
