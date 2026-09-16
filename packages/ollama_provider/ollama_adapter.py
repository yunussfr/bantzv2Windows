import httpx
from typing import Dict, Any, List, Optional
from packages.core.ports.llm_port import LLMPort
from packages.contracts.tool_request import ToolRequest
from packages.contracts.tool_result import ToolResult


class OllamaAdapter(LLMPort):
    """Ollama REST API adaptörü (Sağlık kontrolü, model yönlendirme ve cevap üretimi)."""

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        main_model: str = "llama3.2",
        routing_model: Optional[str] = None,
        timeout_seconds: float = 60.0
    ):
        self.base_url = base_url.rstrip("/")
        self.main_model = main_model
        # Karar: Routing modeli boş bırakılırsa ana model kullanılır
        self.routing_model = routing_model if routing_model else main_model
        self.timeout_seconds = timeout_seconds

    @property
    def port_name(self) -> str:
        return "llm"

    async def check_health(self) -> bool:
        """Gerçek Ollama API endpoint'ine (/api/tags veya /api/version) istek atar."""
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.get(f"{self.base_url}/api/version")
                return res.status_code == 200
        except Exception:
            return False

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1024,
        model: Optional[str] = None
    ) -> str:
        target_model = model or self.main_model
        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                payload = {
                    "model": target_model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens
                    }
                }
                res = await client.post(f"{self.base_url}/api/chat", json=payload)
                if res.status_code != 200:
                    raise RuntimeError(f"Ollama API hatası: HTTP {res.status_code} - {res.text}")
                data = res.json()
                return data.get("message", {}).get("content", "")
        except httpx.ConnectError:
            # Kabul kriteri: Ollama bağlantısı kesildiğinde kontrollü hata üretimi
            raise ConnectionError(f"Ollama servisine ({self.base_url}) bağlanılamadı. Lütfen Ollama'nın çalıştığından emin olun.")

    async def execute(self, request: ToolRequest) -> ToolResult:
        """BasePort standardı gereği LLM sorgusunu çalıştırır."""
        try:
            messages = request.parameters.get("messages", [{"role": "user", "content": request.action}])
            model = request.parameters.get("model")
            content = await self.generate_response(messages=messages, model=model)
            return ToolResult(
                requestId=request.requestId,
                taskId=request.taskId,
                success=True,
                output={"content": content}
            )
        except Exception as e:
            return ToolResult(
                requestId=request.requestId,
                taskId=request.taskId,
                success=False,
                error=str(e)
            )
