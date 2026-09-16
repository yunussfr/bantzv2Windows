import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone


class TraceSpan:
    def __init__(self, trace_id: str, span_name: str, parent_span_id: Optional[str] = None):
        self.trace_id = trace_id
        self.span_id = str(uuid.uuid4())[:8]
        self.parent_span_id = parent_span_id
        self.span_name = span_name
        self.started_at = datetime.now(timezone.utc).isoformat()
        self.ended_at: Optional[str] = None
        self.tags: Dict[str, Any] = {}

    def finish(self, tags: Optional[Dict[str, Any]] = None):
        self.ended_at = datetime.now(timezone.utc).isoformat()
        if tags:
            self.tags.update(tags)


class TraceManager:
    """Tekil traceId üzerinden tüm alt adımları ve logları ilişkilendiren izleme yöneticisi."""

    def __init__(self):
        self.spans: List[TraceSpan] = []

    def start_trace(self, trace_id: Optional[str] = None) -> str:
        return trace_id or f"trace-{uuid.uuid4().hex[:12]}"

    def create_span(self, trace_id: str, span_name: str, parent_span_id: Optional[str] = None) -> TraceSpan:
        span = TraceSpan(trace_id, span_name, parent_span_id)
        self.spans.append(span)
        return span

    def get_spans_for_trace(self, trace_id: str) -> List[TraceSpan]:
        return [s for s in self.spans if s.trace_id == trace_id]
