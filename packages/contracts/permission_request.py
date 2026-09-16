from enum import Enum
from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field
import uuid


class ApprovalDecision(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    TIMEOUT = "timeout"


class PermissionRequest(BaseModel):
    requestId: str = Field(default_factory=lambda: str(uuid.uuid4()))
    taskId: str
    traceId: str
    capability: str  # örn: process.run.destructive, filesystem.write.system
    reason: str
    riskLevel: str = "moderate"  # safe, moderate, destructive
    decision: ApprovalDecision = ApprovalDecision.PENDING
    decidedBy: Optional[str] = None  # user, policy_auto
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    resolvedAt: Optional[datetime] = None
