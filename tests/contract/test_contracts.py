import json
from pathlib import Path
import pytest
from jsonschema import validate
from packages.contracts import Task, TaskStatus, ToolRequest, ToolResult, PermissionRequest, Evidence, TaskReport


def test_task_model_and_json_schema():
    schema_path = Path("packages/contracts/schemas/task-contract.schema.json")
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    task = Task(title="Test görevi", description="Açıklama")
    task_dict = json.loads(task.model_dump_json())

    # JSON Schema doğrulaması
    validate(instance=task_dict, schema=schema)
    assert task.status == TaskStatus.CREATED
    assert task.taskId is not None
    assert task.traceId.startswith("trace-")


def test_event_bus_contract_schema():
    schema_path = Path("packages/contracts/schemas/event-contract.schema.json")
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    sample_event = {
        "eventId": "123e4567-e89b-12d3-a456-426614174000",
        "eventType": "task_created",
        "timestamp": "2026-09-16T12:00:00Z",
        "traceId": "trace-abcdef123456",
        "correlationId": None,
        "source": "core",
        "payload": {"taskId": "123e4567-e89b-12d3-a456-426614174000"}
    }
    validate(instance=sample_event, schema=schema)
