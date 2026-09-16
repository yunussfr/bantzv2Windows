from typing import Set, Dict, Optional, Callable, Awaitable
from packages.contracts.task import Task, TaskStatus


class StateTransitionError(Exception):
    """Geçersiz durum geçişlerinde fırlatılır."""
    pass


class TaskStateMachine:
    """Görev durum geçişlerini denetleyen ve doğrulayan durum makinesi."""

    # İzin verilen durum geçiş haritası
    _VALID_TRANSITIONS: Dict[TaskStatus, Set[TaskStatus]] = {
        TaskStatus.CREATED: {
            TaskStatus.PLANNED,
            TaskStatus.FAILED,
            TaskStatus.CANCELLED
        },
        TaskStatus.PLANNED: {
            TaskStatus.WAITING_FOR_APPROVAL,
            TaskStatus.QUEUED,
            TaskStatus.RUNNING,
            TaskStatus.CANCELLED,
            TaskStatus.FAILED
        },
        TaskStatus.WAITING_FOR_APPROVAL: {
            TaskStatus.QUEUED,
            TaskStatus.RUNNING,
            TaskStatus.CANCELLED,
            TaskStatus.FAILED
        },
        TaskStatus.QUEUED: {
            TaskStatus.RUNNING,
            TaskStatus.CANCELLED,
            TaskStatus.TIMED_OUT
        },
        TaskStatus.RUNNING: {
            TaskStatus.WAITING_FOR_USER,
            TaskStatus.VERIFYING,
            TaskStatus.COMPLETED,
            TaskStatus.FAILED,
            TaskStatus.CANCELLED,
            TaskStatus.TIMED_OUT
        },
        TaskStatus.WAITING_FOR_USER: {
            TaskStatus.RUNNING,
            TaskStatus.CANCELLED,
            TaskStatus.TIMED_OUT,
            TaskStatus.FAILED
        },
        TaskStatus.VERIFYING: {
            TaskStatus.COMPLETED,
            TaskStatus.FAILED
        },
        # Son durumlar (terminal states)
        TaskStatus.COMPLETED: set(),
        TaskStatus.FAILED: set(),
        TaskStatus.CANCELLED: set(),
        TaskStatus.TIMED_OUT: set(),
    }

    @classmethod
    def can_transition(cls, from_status: TaskStatus, to_status: TaskStatus) -> bool:
        """Durum geçişinin geçerli olup olmadığını kontrol eder."""
        allowed = cls._VALID_TRANSITIONS.get(from_status, set())
        return to_status in allowed

    @classmethod
    def transition(cls, task: Task, to_status: TaskStatus, error: Optional[str] = None) -> Task:
        """Görevin durumunu günceller, kural dışı ise StateTransitionError fırlatır."""
        if not cls.can_transition(task.status, to_status):
            raise StateTransitionError(
                f"Geçersiz durum geçişi: '{task.status.value}' -> '{to_status.value}' (taskId={task.taskId})"
            )
        task.status = to_status
        if error:
            task.error = error
        return task
