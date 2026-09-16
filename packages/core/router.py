from typing import Dict, Any, Optional
from pydantic import BaseModel
from packages.core.ports.llm_port import LLMPort


class RoutingDecision(BaseModel):
    is_chat: bool
    requires_planning: bool
    target_environment: str = "host"  # host, vm_hyperv, vm_mock
    estimated_risk: str = "safe"  # safe, moderate, destructive
    suggested_ports: list[str] = []
    reasoning: str = ""


class Router:
    """Kullanıcı girdisini analiz edip doğru çalışma ortamına ve planlayıcıya yönlendirir."""

    def __init__(self, llm_port: Optional[LLMPort] = None):
        self.llm_port = llm_port

    async def route(self, user_query: str) -> RoutingDecision:
        query_lower = user_query.lower()

        # Sanal makine (VM) anahtar kelimeleri
        needs_vm = any(kw in query_lower for kw in ["vm", "sanal makine", "virtual machine", "sandbox", "izole"])

        # Riskli işlem anahtar kelimeleri
        destructive_kws = ["rm -rf", "format", "sil", "delete", "shutdown", "drop database"]
        is_destructive = any(kw in query_lower for kw in destructive_kws)

        # Planlama gerektiren karmaşık görevler
        planning_kws = ["araştır", "hazırla", "rapor", "tara", "indir", "çalıştır", "listele", "zamanla", "schedule"]
        needs_planning = any(kw in query_lower for kw in planning_kws) or needs_vm

        target_env = "vm_hyperv" if needs_vm else "host"
        risk = "destructive" if is_destructive else ("moderate" if needs_planning else "safe")

        ports = []
        if any(w in query_lower for w in ["web", "araştır", "site", "url", "browser"]):
            ports.append("browser")
        if any(w in query_lower for w in ["dosya", "file", "klasör", "yaz"]):
            ports.append("filesystem")
        if any(w in query_lower for w in ["komut", "process", "çalıştır"]):
            ports.append("process")
        if any(w in query_lower for w in ["zamanla", "saat", "schedule", "yarın"]):
            ports.append("scheduler")

        return RoutingDecision(
            is_chat=not needs_planning,
            requires_planning=needs_planning,
            target_environment=target_env,
            estimated_risk=risk,
            suggested_ports=ports,
            reasoning=f"Query classified: needs_vm={needs_vm}, risk={risk}"
        )
