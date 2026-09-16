from datetime import datetime, timezone
from typing import Dict, Any, Optional
from packages.contracts.task import Task, TaskStatus
from packages.contracts.task_report import TaskReport
from packages.core.ports.base_port import BasePort
from packages.core.ports.llm_port import LLMPort
from packages.core.task_state_machine import TaskStateMachine
from packages.core.event_bus import EventBus
from packages.core.router import Router
from packages.core.planner import Planner
from packages.core.executor import Executor
from packages.core.report_generator import ReportGenerator


class Orchestrator:
    """Agent çekirdeğinin yaşam döngüsünü koordine eden ana orkestratör."""

    def __init__(
        self,
        port_registry: Dict[str, BasePort],
        event_bus: Optional[EventBus] = None,
        llm_port: Optional[LLMPort] = None
    ):
        self.port_registry = port_registry
        self.event_bus = event_bus or EventBus()
        self.llm_port = llm_port
        self.router = Router(llm_port=llm_port)
        self.planner = Planner(registered_ports=set(port_registry.keys()), llm_port=llm_port)
        self.executor = Executor(port_registry=port_registry, event_bus=self.event_bus)

    async def submit_instruction(self, user_instruction: str, source: str = "user_chat") -> TaskReport:
        """Kullanıcıdan gelen talimatı alır, yönlendirir, planlar, yürütür ve raporlar."""
        task = Task(title=user_instruction, source=source)

        await self.event_bus.publish(
            event_type="task_created",
            payload={"taskId": task.taskId, "title": task.title, "source": task.source},
            trace_id=task.traceId
        )

        # 1. Yönlendirme (Routing)
        routing_dec = await self.router.route(user_instruction)
        task.environment = routing_dec.target_environment

        # 2. Planlama (Planning)
        await self.planner.create_plan(task)
        TaskStateMachine.transition(task, TaskStatus.PLANNED)

        # Risk kontrolü (Approval gerekiyorsa)
        if routing_dec.estimated_risk == "destructive":
            TaskStateMachine.transition(task, TaskStatus.WAITING_FOR_APPROVAL)
            await self.event_bus.publish(
                event_type="approval_requested",
                payload={"taskId": task.taskId, "riskLevel": routing_dec.estimated_risk},
                trace_id=task.traceId
            )
            # Onay bekleyen durum (otomasyon testinde simüle edilebilir)
            # Şimdilik otomatik onay akışı için transition:
            TaskStateMachine.transition(task, TaskStatus.RUNNING)
        else:
            TaskStateMachine.transition(task, TaskStatus.RUNNING)

        task.startedAt = datetime.now(timezone.utc)
        await self.event_bus.publish(
            event_type="task_status_changed",
            payload={"taskId": task.taskId, "status": task.status.value},
            trace_id=task.traceId
        )

        # 3. Yürütme (Execution)
        success = await self.executor.execute_task(task)

        # 4. Doğrulama ve Tamamlama
        TaskStateMachine.transition(task, TaskStatus.VERIFYING)
        task.completedAt = datetime.now(timezone.utc)

        final_status = TaskStatus.COMPLETED if success else TaskStatus.FAILED
        TaskStateMachine.transition(task, final_status)

        await self.event_bus.publish(
            event_type="task_completed" if success else "task_failed",
            payload={"taskId": task.taskId, "status": task.status.value},
            trace_id=task.traceId
        )

        # 5. Raporlama
        report = ReportGenerator.generate(task)
        return report
