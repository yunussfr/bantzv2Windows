import pytest
from typing import Dict, Any
from packages.contracts import ToolRequest, ToolResult, TaskReport
from packages.core.ports.base_port import BasePort
from packages.core.orchestrator import Orchestrator
from packages.core.event_bus import EventBus


class MockBrowserPort(BasePort):
    @property
    def port_name(self) -> str:
        return "browser"

    async def execute(self, request: ToolRequest) -> ToolResult:
        return ToolResult(
            requestId=request.requestId,
            taskId=request.taskId,
            success=True,
            output={
                "sources": [
                    "https://arxiv.org/abs/2305.18290",
                    "https://openai.com/research/agents",
                    "https://deepmind.google/technologies/gemini",
                    "https://anthropic.com/research",
                    "https://microsoft.com/research/autogen"
                ],
                "extracted_content": "Yapay zeka ajanları modüler mimaride otonom karar verir."
            },
            evidenceIds=["mock-evidence-browser-01"]
        )


class MockFileSystemPort(BasePort):
    @property
    def port_name(self) -> str:
        return "filesystem"

    async def execute(self, request: ToolRequest) -> ToolResult:
        return ToolResult(
            requestId=request.requestId,
            taskId=request.taskId,
            success=True,
            output={"filename": request.parameters.get("filename", "report.md"), "bytes_written": 512},
            evidenceIds=["mock-evidence-fs-01"]
        )


class MockNotificationPort(BasePort):
    @property
    def port_name(self) -> str:
        return "notification"

    async def execute(self, request: ToolRequest) -> ToolResult:
        return ToolResult(
            requestId=request.requestId,
            taskId=request.taskId,
            success=True,
            output={"delivered": True}
        )


@pytest.mark.asyncio
async def test_end_to_end_orchestration_with_mock_ports():
    event_bus = EventBus()
    events_caught = []

    async def _catch_all(event):
        events_caught.append(event["eventType"])

    event_bus.subscribe_all(_catch_all)

    ports = {
        "browser": MockBrowserPort(),
        "filesystem": MockFileSystemPort(),
        "notification": MockNotificationPort(),
    }

    orchestrator = Orchestrator(port_registry=ports, event_bus=event_bus)
    instruction = "Yapay zeka ajanları hakkında araştırma yap ve rapor hazırla"

    report: TaskReport = await orchestrator.submit_instruction(instruction)

    assert report.status == "completed"
    assert report.taskId is not None
    assert report.traceId is not None
    assert len(report.completedSteps) == 3
    assert len(report.collectedSources) == 5
    assert len(report.createdFiles) >= 1
    assert "report_" in report.createdFiles[0]

    # EventBus olaylarının tetiklendiğini doğrula
    assert "task_created" in events_caught
    assert "step_started" in events_caught
    assert "step_finished" in events_caught
    assert "task_completed" in events_caught
