from abc import ABC, abstractmethod
from typing import Dict, Any
from packages.contracts.tool_request import ToolRequest
from packages.contracts.tool_result import ToolResult


class BasePort(ABC):
    """Tüm adaptör portlarının türediği temel soyut arayüz."""

    @property
    @abstractmethod
    def port_name(self) -> str:
        """Portun tekil kayıtlı adı (örn: browser, filesystem, llm)."""
        pass

    @abstractmethod
    async def execute(self, request: ToolRequest) -> ToolResult:
        """Gelen standart araç isteğini çalıştırıp standart sonuç döndürür."""
        pass
