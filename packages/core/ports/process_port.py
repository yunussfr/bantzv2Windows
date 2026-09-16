from abc import abstractmethod
from typing import Dict, Any, List, Optional
from .base_port import BasePort


class ProcessPort(BasePort):
    @property
    def port_name(self) -> str:
        return "process"

    @abstractmethod
    async def run_command(
        self,
        command: str,
        args: Optional[List[str]] = None,
        timeout_seconds: int = 30
    ) -> Dict[str, Any]:
        """İzinli komutu çalıştırır, exit_code, stdout, stderr döndürür."""
        pass
