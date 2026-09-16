from abc import abstractmethod
from typing import Dict, Any, List, Optional
from .base_port import BasePort


class LLMPort(BasePort):
    @property
    def port_name(self) -> str:
        return "llm"

    @abstractmethod
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1024,
        model: Optional[str] = None
    ) -> str:
        """Kullanıcıya veya sisteme yanıt üretir."""
        pass

    @abstractmethod
    async def check_health(self) -> bool:
        """Model sunucusunun (Ollama vb.) erişilebilirliğini test eder."""
        pass
