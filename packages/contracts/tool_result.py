from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


class ToolResult(BaseModel):
    requestId: str
    taskId: str
    success: bool
    output: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
    executionTimeMs: float = 0.0
    evidenceIds: List[str] = Field(default_factory=list)
