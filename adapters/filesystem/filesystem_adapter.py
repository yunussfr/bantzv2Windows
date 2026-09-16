import os
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
from packages.core.ports.filesystem_port import FileSystemPort
from packages.contracts.tool_request import ToolRequest
from packages.contracts.tool_result import ToolResult


class WindowsFileSystemAdapter(FileSystemPort):
    """Güvenli, sınırlandırılmış izinli dizin (sandbox) dosya sistemi adaptörü."""

    def __init__(self, allowed_base_dir: str = "data/sandbox"):
        self.allowed_base_dir = Path(allowed_base_dir).resolve()
        self.allowed_base_dir.mkdir(parents=True, exist_ok=True)

    @property
    def port_name(self) -> str:
        return "filesystem"

    def _resolve_and_check(self, path_str: str) -> Path:
        """Hedef yolun izinli dizin içinde kaldığını doğrular. Path traversal saldırılarını engeller."""
        target = (self.allowed_base_dir / path_str).resolve()
        if not str(target).startswith(str(self.allowed_base_dir)):
            raise PermissionError(f"Erişim engellendi: '{path_str}' izin verilen klasörün dışındadır!")
        return target

    async def read_file(self, path: str) -> str:
        safe_path = self._resolve_and_check(path)
        if not safe_path.exists():
            raise FileNotFoundError(f"Dosya bulunamadı: {path}")
        with open(safe_path, "r", encoding="utf-8") as f:
            return f.read()

    async def write_file(self, path: str, content: str) -> bool:
        safe_path = self._resolve_and_check(path)
        safe_path.parent.mkdir(parents=True, exist_ok=True)
        with open(safe_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True

    async def list_files(self, directory: str = "") -> List[str]:
        safe_dir = self._resolve_and_check(directory)
        if not safe_dir.exists():
            return []
        return [p.name for p in safe_dir.iterdir()]

    async def execute(self, request: ToolRequest) -> ToolResult:
        action = request.action
        params = request.parameters
        try:
            if action == "read":
                content = await self.read_file(params["path"])
                return ToolResult(requestId=request.requestId, taskId=request.taskId, success=True, output={"content": content})
            elif action in ("write", "write_report"):
                path = params.get("filename") or params.get("path") or "output.txt"
                content = params.get("content", "# Bantz Raporu\nGörev tamamlandı.")
                await self.write_file(path, content)
                return ToolResult(
                    requestId=request.requestId,
                    taskId=request.taskId,
                    success=True,
                    output={"filename": path, "file_path": str(self._resolve_and_check(path))}
                )
            elif action == "list":
                files = await self.list_files(params.get("directory", ""))
                return ToolResult(requestId=request.requestId, taskId=request.taskId, success=True, output={"files": files})
            else:
                return ToolResult(requestId=request.requestId, taskId=request.taskId, success=False, error=f"Bilinmeyen eylem: {action}")
        except Exception as e:
            return ToolResult(requestId=request.requestId, taskId=request.taskId, success=False, error=str(e))
