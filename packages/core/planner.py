import json
from typing import List, Dict, Any, Optional, Set
from packages.contracts.task import Task, TaskStep, TaskStepStatus
from packages.core.ports.llm_port import LLMPort


class Planner:
    """Kullanıcı isteğini kayıtlı port ve araçlar kümesi üzerinden adımlara bölen planlayıcı."""

    def __init__(self, registered_ports: Set[str], llm_port: Optional[LLMPort] = None):
        self.registered_ports = registered_ports
        self.llm_port = llm_port

    async def create_plan(self, task: Task) -> List[TaskStep]:
        """Görev için kayıtlı portları kullanan sıralı adımlar üretir."""
        query = task.title.lower()
        steps: List[TaskStep] = []

        # Örnek Araştırma Görevi Şablonu: Web araştırması + Dosya Raporlama
        if "araştırma" in query or "rapor" in query:
            if "browser" in self.registered_ports:
                steps.append(TaskStep(
                    port="browser",
                    action="search_and_extract",
                    params={"topic": task.title, "min_sources": 5}
                ))
            if "filesystem" in self.registered_ports:
                steps.append(TaskStep(
                    port="filesystem",
                    action="write_report",
                    params={"filename": f"report_{task.taskId[:8]}.md"}
                ))
            if "notification" in self.registered_ports:
                steps.append(TaskStep(
                    port="notification",
                    action="notify_user",
                    params={"message": f"'{task.title}' görevi tamamlandı ve rapor kaydedildi."}
                ))
        elif "dosya" in query or "file" in query:
            if "filesystem" in self.registered_ports:
                steps.append(TaskStep(
                    port="filesystem",
                    action="list_or_read",
                    params={"query": task.title}
                ))
        else:
            # Genel varsayılan tek adımlı genel süreç
            default_port = next(iter(self.registered_ports)) if self.registered_ports else "generic"
            steps.append(TaskStep(
                port=default_port,
                action="execute_query",
                params={"query": task.title}
            ))

        # Adımların geçerli kayıtlı portları kullandığından emin ol
        for step in steps:
            if step.port not in self.registered_ports:
                raise ValueError(f"Planlayıcı kayıtlı olmayan bir port kullanamaz: '{step.port}'")

        task.steps = steps
        return steps
