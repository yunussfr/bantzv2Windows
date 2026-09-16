import time
from typing import Dict, Any, Optional
from packages.contracts.task import Task, TaskStep, TaskStepStatus
from packages.contracts.tool_request import ToolRequest
from packages.contracts.tool_result import ToolResult
from packages.core.ports.base_port import BasePort
from packages.core.event_bus import EventBus


class Executor:
    """Planlanmış adımları soyut Port arayüzleri üzerinden yürüten yürütücü."""

    def __init__(self, port_registry: Dict[str, BasePort], event_bus: Optional[EventBus] = None):
        self.port_registry = port_registry
        self.event_bus = event_bus

    async def execute_task(self, task: Task) -> bool:
        """Görevdeki adımları sırayla icra eder, sonuçları ve kanıtları task nesnesine yazar."""
        all_success = True

        for step in task.steps:
            step.status = TaskStepStatus.RUNNING
            if self.event_bus:
                await self.event_bus.publish(
                    event_type="step_started",
                    payload={"taskId": task.taskId, "stepId": step.stepId, "port": step.port, "action": step.action},
                    trace_id=task.traceId,
                    correlation_id=task.taskId
                )

            port = self.port_registry.get(step.port)
            if not port:
                step.status = TaskStepStatus.FAILED
                step.error = f"Kayıtlı adaptör bulunamadı: '{step.port}'"
                all_success = False
                break

            request = ToolRequest(
                taskId=task.taskId,
                traceId=task.traceId,
                port=step.port,
                action=step.action,
                parameters=step.params
            )

            start_t = time.perf_counter()
            try:
                result: ToolResult = await port.execute(request)
                elapsed_ms = (time.perf_counter() - start_t) * 1000.0
                result.executionTimeMs = elapsed_ms

                if result.success:
                    step.status = TaskStepStatus.SUCCESS
                    step.result = result.output
                    if result.evidenceIds:
                        task.evidenceIds.extend(result.evidenceIds)
                else:
                    step.status = TaskStepStatus.FAILED
                    step.error = result.error or "Bilinmeyen araç hatası"
                    all_success = False
                    break
            except Exception as e:
                step.status = TaskStepStatus.FAILED
                step.error = str(e)
                all_success = False
                break
            finally:
                if self.event_bus:
                    await self.event_bus.publish(
                        event_type="step_finished",
                        payload={"taskId": task.taskId, "stepId": step.stepId, "status": step.status.value},
                        trace_id=task.traceId,
                        correlation_id=task.taskId
                    )

        return all_success
