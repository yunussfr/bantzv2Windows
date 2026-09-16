from abc import abstractmethod
from typing import Dict, Any, List, Optional
from .base_port import BasePort


class BrowserPort(BasePort):
    @property
    def port_name(self) -> str:
        return "browser"

    @abstractmethod
    async def navigate(self, url: str) -> bool:
        """Belirtilen URL'e gider."""
        pass

    @abstractmethod
    async def extract_text(self, selector: Optional[str] = None) -> str:
        """Sayfadan veya seçiciden metin çeker."""
        pass

    @abstractmethod
    async def fill_form(self, selector: str, value: str) -> bool:
        """Form girdisini doldurur."""
        pass

    @abstractmethod
    async def capture_screenshot(self) -> bytes:
        """Tarayıcı sayfasının ekran görüntüsünü alır."""
        pass
