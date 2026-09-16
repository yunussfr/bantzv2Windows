import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from packages.contracts.evidence import Evidence, EvidenceType


class EvidenceStore:
    """Görev sırasında toplanan ekran görüntüleri, loglar ve dosyaları saklayan kanıt deposu."""

    def __init__(self, base_dir: str = "data/evidence"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self._records: Dict[str, Evidence] = {}

    def save_evidence(
        self,
        task_id: str,
        trace_id: str,
        evidence_type: EvidenceType,
        raw_data: bytes,
        file_extension: str = "bin",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Evidence:
        sha256 = hashlib.sha256(raw_data).hexdigest()
        filename = f"{task_id[:8]}_{sha256[:10]}.{file_extension}"
        file_path = self.base_dir / filename

        with open(file_path, "wb") as f:
            f.write(raw_data)

        ev = Evidence(
            taskId=task_id,
            traceId=trace_id,
            evidenceType=evidence_type,
            uriOrPath=str(file_path),
            metadata=metadata or {},
            sha256Hash=sha256
        )
        self._records[ev.evidenceId] = ev
        return ev

    def get_evidence_for_task(self, task_id: str) -> List[Evidence]:
        return [ev for ev in self._records.values() if ev.taskId == task_id]
