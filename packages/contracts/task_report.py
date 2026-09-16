from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class TaskReport(BaseModel):
    taskId: str
    traceId: str
    title: str
    status: str  # completed, failed, cancelled, timed_out
    environment: str  # host, vm_hyperv, vm_mock
    startedAt: Optional[datetime] = None
    completedAt: Optional[datetime] = None
    durationSeconds: float = 0.0
    usedTools: List[str] = Field(default_factory=list)
    completedSteps: List[Dict[str, Any]] = Field(default_factory=list)
    failedSteps: List[Dict[str, Any]] = Field(default_factory=list)
    collectedSources: List[str] = Field(default_factory=list)
    createdFiles: List[str] = Field(default_factory=list)
    secretUsage: List[str] = Field(default_factory=list)  # masked credential references
    approvalsReceived: List[Dict[str, Any]] = Field(default_factory=list)
    evidenceSummary: List[Dict[str, Any]] = Field(default_factory=list)
    summaryText: str = ""
