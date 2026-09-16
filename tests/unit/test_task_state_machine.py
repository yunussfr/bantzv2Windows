import pytest
from packages.contracts import Task, TaskStatus
from packages.core.task_state_machine import TaskStateMachine, StateTransitionError


def test_valid_state_transitions():
    task = Task(title="Test Görevi")
    assert task.status == TaskStatus.CREATED

    TaskStateMachine.transition(task, TaskStatus.PLANNED)
    assert task.status == TaskStatus.PLANNED

    TaskStateMachine.transition(task, TaskStatus.RUNNING)
    assert task.status == TaskStatus.RUNNING

    TaskStateMachine.transition(task, TaskStatus.VERIFYING)
    assert task.status == TaskStatus.VERIFYING

    TaskStateMachine.transition(task, TaskStatus.COMPLETED)
    assert task.status == TaskStatus.COMPLETED


def test_invalid_state_transition_raises():
    task = Task(title="Test Görevi")
    assert task.status == TaskStatus.CREATED

    # Created durumundan doğrudan Completed durumuna geçilemez!
    with pytest.raises(StateTransitionError):
        TaskStateMachine.transition(task, TaskStatus.COMPLETED)

    # Completed terminal durumdur, oradan Running durumuna dönülemez!
    TaskStateMachine.transition(task, TaskStatus.PLANNED)
    TaskStateMachine.transition(task, TaskStatus.RUNNING)
    TaskStateMachine.transition(task, TaskStatus.VERIFYING)
    TaskStateMachine.transition(task, TaskStatus.COMPLETED)

    with pytest.raises(StateTransitionError):
        TaskStateMachine.transition(task, TaskStatus.RUNNING)
