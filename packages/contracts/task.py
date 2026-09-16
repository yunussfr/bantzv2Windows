from enum import Enum
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import uuid


class TaskStatus(str, Enum):
    CREATED = "created"
    PLANNED = "planned"
    WAITING_FOR_APPROVAL = "waiting_for_approval"
    QUEUED = "queued"
    RUNNING = "running"
    WAITING_FOR_USER = "waiting_for_user"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMED_OUT = "timed_out"


class TaskStepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class TaskStep(BaseModel):
    stepId: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    port: str
    action: str
    params: Dict[str, Any] = Field(default_factory=dict)
    status: TaskStepStatus = TaskStepStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class Task(BaseModel):
    taskId: str = Field(default_factory=lambda: str(uuid.uuid4()))
    traceId: str = Field(default_factory=lambda: f"trace-{uuid.uuid4().hex[:12]}")
    title: str
    description: str = ""
    status: TaskStatus = TaskStatus.CREATED
    source: str = "user_chat"  # user_chat, voice_input, scheduler, proactive, guest_agent
    environment: str = "host"  # host, vm_hyperv, vm_mock
    steps: List[TaskStep] = Field(default_factory=list)
    evidenceIds: List[str] = Field(default_factory=list)
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    startedAt: Optional[datetime] = None
    completedAt: Optional[datetime] = None
    error: Optional[str] = None
