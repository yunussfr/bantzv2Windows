from typing import Dict, Any, Optional
from packages.contracts.permission_request import PermissionRequest, ApprovalDecision
from .capability_registry import CapabilityRegistry
from .risk_classifier import RiskClassifier


class ApprovalEngine:
    """Otonomi seviyesine ve risk sınıflandırmasına göre kullanıcı onayını yönetir."""

    def __init__(self, capability_registry: CapabilityRegistry, autonomy_tier: str = "medium"):
        self.capability_registry = capability_registry
        self.autonomy_tier = autonomy_tier  # low, medium, high
        self.pending_approvals: Dict[str, PermissionRequest] = {}

    def requires_approval(self, capability: str, params: Dict[str, Any] = None) -> bool:
        """Yetkisiz ise hata verir; risk durumuna göre onay gerekip gerekmediğini döndürür."""
        if not self.capability_registry.is_granted(capability):
            raise PermissionError(f"Yetkisiz capability talebi reddedildi: '{capability}'")

        risk = RiskClassifier.classify(capability, params)

        if self.autonomy_tier == "low":
            return risk in ("moderate", "destructive")
        elif self.autonomy_tier == "medium":
            return risk == "destructive"
        elif self.autonomy_tier == "high":
            return False
        return True

    def create_approval_request(
        self,
        task_id: str,
        trace_id: str,
        capability: str,
        reason: str,
        params: Dict[str, Any] = None
    ) -> PermissionRequest:
        risk = RiskClassifier.classify(capability, params)
        req = PermissionRequest(
            taskId=task_id,
            traceId=trace_id,
            capability=capability,
            reason=reason,
            riskLevel=risk
        )
        self.pending_approvals[req.requestId] = req
        return req

    def resolve_approval(self, request_id: str, approved: bool, decided_by: str = "user") -> Optional[PermissionRequest]:
        req = self.pending_approvals.pop(request_id, None)
        if req:
            req.decision = ApprovalDecision.APPROVED if approved else ApprovalDecision.DENIED
            req.decidedBy = decided_by
        return req
