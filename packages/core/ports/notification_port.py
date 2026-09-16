from abc import abstractmethod
from typing import Dict, Any, Optional
from .base_port import BasePort


class NotificationPort(BasePort):
    @property
    def port_name(self) -> str:
        return "notification"

    @abstractmethod
    async def show_notification(
        self,
        title: str,
        message: str,
        level: str = "info",
        actions: Optional[Dict[str, str]] = None
    ) -> bool:
        """Kullanıcıya masaüstü bildirimi veya avatar konuşma balonu gösterir."""
        pass
