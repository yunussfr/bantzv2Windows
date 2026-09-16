from abc import abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
from .base_port import BasePort


class SchedulerPort(BasePort):
    @property
    def port_name(self) -> str:
        return "scheduler"

    @abstractmethod
    async def schedule_task(
        self,
        task_id: str,
        run_at: datetime,
        repeat_interval_seconds: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Görevi belirli zamana planlar."""
        pass

    @abstractmethod
    async def cancel_scheduled_task(self, task_id: str) -> bool:
        """Zamanlanmış görevi iptal eder."""
        pass

    @abstractmethod
    async def list_scheduled_tasks(self) -> List[Dict[str, Any]]:
        """Planlanmış tüm görevleri listeler."""
        pass
