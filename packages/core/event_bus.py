import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, List, Callable, Awaitable, Optional, Set
import uuid


class EventBus:
    """Modüller arası asenkron, tip güvenli olay veri yolu (Pub/Sub)."""

    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[Dict[str, Any]], Awaitable[None]]]] = {}
        self._all_subscribers: List[Callable[[Dict[str, Any]], Awaitable[None]]] = []
        self._history: List[Dict[str, Any]] = []

    def subscribe(
        self,
        event_type: str,
        handler: Callable[[Dict[str, Any]], Awaitable[None]]
    ) -> None:
        """Belirli bir olay tipine dinleyici kaydeder."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)

    def subscribe_all(self, handler: Callable[[Dict[str, Any]], Awaitable[None]]) -> None:
        """Tüm olay tiplerini dinleyen global işleyici ekler (örn. log/audit için)."""
        self._all_subscribers.append(handler)

    async def publish(
        self,
        event_type: str,
        payload: Dict[str, Any],
        trace_id: str,
        correlation_id: Optional[str] = None,
        source: str = "core"
    ) -> Dict[str, Any]:
        """Yeni bir olay yayınlar ve dinleyicilere asenkron olarak iletir."""
        event_record = {
            "eventId": str(uuid.uuid4()),
            "eventType": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "traceId": trace_id,
            "correlationId": correlation_id,
            "source": source,
            "payload": payload,
        }
        self._history.append(event_record)

        handlers = list(self._subscribers.get(event_type, [])) + list(self._all_subscribers)
        if handlers:
            await asyncio.gather(
                *(handler(event_record) for handler in handlers),
                return_exceptions=True
            )
        return event_record

    async def wait_for(
        self,
        event_type: str,
        predicate: Optional[Callable[[Dict[str, Any]], bool]] = None,
        timeout: float = 30.0
    ) -> Dict[str, Any]:
        """Belirli bir olay gerçekleşene kadar asenkron bekler."""
        loop = asyncio.get_running_loop()
        future = loop.create_future()

        async def _check(event: Dict[str, Any]) -> None:
            if predicate is None or predicate(event):
                if not future.done():
                    future.set_result(event)

        self.subscribe(event_type, _check)
        try:
            return await asyncio.wait_for(future, timeout=timeout)
        finally:
            if event_type in self._subscribers and _check in self._subscribers[event_type]:
                self._subscribers[event_type].remove(_check)
