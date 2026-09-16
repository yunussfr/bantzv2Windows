from enum import Enum
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import uuid


class EvidenceType(str, Enum):
    SCREENSHOT = "screenshot"
    DOM_SNAPSHOT = "dom_snapshot"
    PROCESS_OUTPUT = "process_output"
    FILE_DIFF = "file_diff"
    DOWNLOADED_FILE = "downloaded_file"
    AUDIT_LOG = "audit_log"


class Evidence(BaseModel):
    evidenceId: str = Field(default_factory=lambda: str(uuid.uuid4()))
    taskId: str
    traceId: str
    evidenceType: EvidenceType
    uriOrPath: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    sha256Hash: Optional[str] = None
    capturedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
