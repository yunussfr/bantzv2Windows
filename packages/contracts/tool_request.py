from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import uuid


class ToolRequest(BaseModel):
    requestId: str = Field(default_factory=lambda: str(uuid.uuid4()))
    taskId: str
    traceId: str
    port: str
    action: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    credentialRef: Optional[str] = None
    timeoutSeconds: int = 60
