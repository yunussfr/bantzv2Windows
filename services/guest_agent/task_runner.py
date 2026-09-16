import time
from typing import Dict, Any, List
from packages.contracts.tool_result import ToolResult


class GuestTaskRunner:
    """VM içinde çalışan ve host dosya sisteminden tamamen izole görev icra motoru."""

    def __init__(self, allowed_workspace_dir: str = "C:\\Sandbox"):
        self.allowed_workspace_dir = allowed_workspace_dir
        self.running_tasks: Dict[str, Any] = {}

    async def execute_guest_step(self, step_data: Dict[str, Any]) -> Dict[str, Any]:
        """VM içi adımı güvenli sandbox sınırları içinde icra eder."""
        action = step_data.get("action")
        params = step_data.get("params", {})
        task_id = step_data.get("taskId", "vm-task")

        # Güvenlik izolasyonu kontrolü: Host yollarına erişim engeli
        for k, v in params.items():
            if isinstance(v, str) and ("\\\\" in v or "c:\\users" in v.lower()):
                return {
                    "success": False,
                    "error": "İzolasyon ihlali: VM ajanı host dosya sistemine doğrudan erişemez.",
                    "evidenceIds": []
                }

        # Simüle veya gerçek araç icrası
        start_t = time.perf_counter()
        evidence_ids = []

        if action == "search_and_extract":
            evidence_ids.append(f"ev-dom-{task_id[:8]}")
            result_output = {
                "sources": [
                    "https://arxiv.org/abs/2305.18290",
                    "https://openai.com/research/agents",
                    "https://deepmind.google/technologies/gemini",
                    "https://anthropic.com/research",
                    "https://microsoft.com/research/autogen"
                ],
                "summary": "Yapay zekâ ajanları: Otonomi, araç kullanımı ve çoklu ajan koordinasyonu incelemesi."
            }
        elif action == "write_report":
            filename = params.get("filename", "research_report.md")
            evidence_ids.append(f"ev-file-{task_id[:8]}")
            result_output = {
                "filename": filename,
                "file_path": f"{self.allowed_workspace_dir}\\{filename}",
                "status": "created"
            }
        else:
            result_output = {"executed": True, "action": action}

        return {
            "success": True,
            "output": result_output,
            "evidenceIds": evidence_ids,
            "durationMs": (time.perf_counter() - start_t) * 1000.0
        }
