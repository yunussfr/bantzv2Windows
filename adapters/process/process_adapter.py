import asyncio
import shlex
from typing import Dict, Any, List, Optional, Set
from packages.core.ports.process_port import ProcessPort
from packages.contracts.tool_request import ToolRequest
from packages.contracts.tool_result import ToolResult


class WindowsProcessAdapter(ProcessPort):
    """Güvenli, beyaz liste ve zaman aşımı denetimli süreç (process) adaptörü."""

    # İzin verilen güvenli komutlar kümesi
    ALLOWED_COMMANDS: Set[str] = {
        "python", "py", "echo", "dir", "whoami", "hostname", "ping", "powershell", "git"
    }

    # Kesinlikle yasaklı komutlar
    FORBIDDEN_KEYWORDS: Set[str] = {
        "rmdir /s", "del /f", "format", "diskpart", "shutdown", "reg delete", "net user"
    }

    @property
    def port_name(self) -> str:
        return "process"

    async def run_command(
        self,
        command: str,
        args: Optional[List[str]] = None,
        timeout_seconds: int = 30
    ) -> Dict[str, Any]:
        cmd_lower = command.lower()

        # 1. Yasaklı anahtar kelime kontrolü
        for forbidden in self.FORBIDDEN_KEYWORDS:
            if forbidden in cmd_lower:
                raise PermissionError(f"Güvenlik ihlali: '{forbidden}' komutu kesinlikle çalıştırılamaz!")

        # 2. Temel çalıştırılabilir dosya beyaz liste kontrolü
        base_cmd = command.split()[0].replace(".exe", "").lower()
        if base_cmd not in self.ALLOWED_COMMANDS:
            raise PermissionError(f"İzin verilmeyen komut: '{base_cmd}'. Yalnızca izinli komutlar çalıştırılabilir.")

        full_cmd = command
        if args:
            full_cmd += " " + " ".join(args)

        try:
            proc = await asyncio.create_subprocess_shell(
                full_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout_seconds)
            return {
                "exit_code": proc.returncode,
                "stdout": stdout.decode("utf-8", errors="replace").strip(),
                "stderr": stderr.decode("utf-8", errors="replace").strip(),
            }
        except asyncio.TimeoutError:
            proc.kill()
            raise TimeoutError(f"Komut zaman aşımına uğradı ({timeout_seconds}s): '{command}'")

    async def execute(self, request: ToolRequest) -> ToolResult:
        cmd = request.parameters.get("command", request.action)
        args = request.parameters.get("args")
        timeout = request.parameters.get("timeout_seconds", request.timeoutSeconds)

        try:
            res = await self.run_command(command=cmd, args=args, timeout_seconds=timeout)
            return ToolResult(
                requestId=request.requestId,
                taskId=request.taskId,
                success=(res["exit_code"] == 0),
                output=res,
                error=res["stderr"] if res["exit_code"] != 0 else None
            )
        except Exception as e:
            return ToolResult(
                requestId=request.requestId,
                taskId=request.taskId,
                success=False,
                error=str(e)
            )
