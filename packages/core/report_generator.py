from datetime import datetime, timezone
from typing import Dict, Any, List
from packages.contracts.task import Task, TaskStatus, TaskStepStatus
from packages.contracts.task_report import TaskReport


class ReportGenerator:
    """Tamamlanan veya başarısız olan görev için kanıtlı, yapılandırılmış rapor üretir."""

    @classmethod
    def generate(cls, task: Task) -> TaskReport:
        now = datetime.now(timezone.utc)
        start = task.startedAt or task.createdAt
        end = task.completedAt or now
        duration = max(0.0, (end - start).total_seconds())

        used_tools = list({s.port for s in task.steps})
        completed_steps = [
            {"stepId": s.stepId, "port": s.port, "action": s.action, "result": s.result}
            for s in task.steps if s.status == TaskStepStatus.SUCCESS
        ]
        failed_steps = [
            {"stepId": s.stepId, "port": s.port, "action": s.action, "error": s.error}
            for s in task.steps if s.status == TaskStepStatus.FAILED
        ]

        # Sonuçlardan kaynak ve dosya çıkarımı
        collected_sources: List[str] = []
        created_files: List[str] = []
        for s in completed_steps:
            res = s.get("result") or {}
            if "sources" in res and isinstance(res["sources"], list):
                collected_sources.extend(res["sources"])
            if "filename" in res:
                created_files.append(str(res["filename"]))
            if "file_path" in res:
                created_files.append(str(res["file_path"]))

        summary = (
            f"Görev: '{task.title}'\n"
            f"Durum: {task.status.value.upper()}\n"
            f"Ortam: {task.environment}\n"
            f"Süre: {duration:.2f} saniye\n"
            f"Tamamlanan Adım: {len(completed_steps)}/{len(task.steps)}\n"
        )
        if failed_steps:
            summary += f"Hata: {failed_steps[0].get('error')}\n"

        return TaskReport(
            taskId=task.taskId,
            traceId=task.traceId,
            title=task.title,
            status=task.status.value,
            environment=task.environment,
            startedAt=start,
            completedAt=end,
            durationSeconds=duration,
            usedTools=used_tools,
            completedSteps=completed_steps,
            failedSteps=failed_steps,
            collectedSources=collected_sources,
            createdFiles=created_files,
            secretUsage=[],
            approvalsReceived=[],
            evidenceSummary=[{"evidenceId": eid} for eid in task.evidenceIds],
            summaryText=summary
        )
