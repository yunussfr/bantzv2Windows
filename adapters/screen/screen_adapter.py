from typing import Dict, Any, Optional
from packages.core.ports.screen_port import ScreenPort
from packages.contracts.tool_request import ToolRequest
from packages.contracts.tool_result import ToolResult


class WindowsScreenAdapter(ScreenPort):
    """Ekran görüntüsü ve aktif pencere denetim adaptörü."""

    @property
    def port_name(self) -> str:
        return "screen"

    async def capture_screen(self, region: Optional[Dict[str, int]] = None) -> bytes:
        # Gerçek ortamda PIL.ImageGrab veya Win32 BitBlt kullanılır
        return b"PNG_SCREEN_EVIDENCE_SAMPLE"

    async def get_active_window(self) -> Dict[str, Any]:
        # Aktif pencere bilgisi
        return {
            "title": "Bantz Operations Center",
            "process_name": "bantz-ui.exe",
            "bounds": {"x": 0, "y": 0, "width": 1920, "height": 1080}
        }

    async def execute(self, request: ToolRequest) -> ToolResult:
        action = request.action
        try:
            if action in ("capture", "screenshot"):
                data = await self.capture_screen()
                return ToolResult(
                    requestId=request.requestId,
                    taskId=request.taskId,
                    success=True,
                    output={"bytes": len(data)},
                    evidenceIds=[f"ev-screen-{request.taskId[:8]}"]
                )
            elif action == "active_window":
                win = await self.get_active_window()
                return ToolResult(
                    requestId=request.requestId,
                    taskId=request.taskId,
                    success=True,
                    output=win
                )
            else:
                return ToolResult(
                    requestId=request.requestId,
                    taskId=request.taskId,
                    success=False,
                    error=f"Bilinmeyen ekran eylemi: {action}"
                )
        except Exception as e:
            return ToolResult(
                requestId=request.requestId,
                taskId=request.taskId,
                success=False,
                error=str(e)
            )
