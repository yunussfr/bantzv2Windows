from abc import abstractmethod
from typing import Dict, Any, Optional
from .base_port import BasePort


class ScreenPort(BasePort):
    @property
    def port_name(self) -> str:
        return "screen"

    @abstractmethod
    async def capture_screen(self, region: Optional[Dict[str, int]] = None) -> bytes:
        """Ekran görüntüsü alır."""
        pass

    @abstractmethod
    async def get_active_window(self) -> Dict[str, Any]:
        """Aktif pencere başlığı, işlem adı ve koordinatlarını getirir."""
        pass
