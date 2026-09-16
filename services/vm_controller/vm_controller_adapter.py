from typing import Dict, Any, Optional
from packages.core.ports.vm_port import VMPort
from packages.contracts.tool_request import ToolRequest
from packages.contracts.tool_result import ToolResult
from .hyper_v_adapter import HyperVAdapter
from .guest_connection import GuestConnection
from services.guest_agent.task_runner import GuestTaskRunner


class WindowsVMControllerAdapter(VMPort):
    """Host tarafında çalışan tam teşekküllü Hyper-V ve Guest Agent orkestratörü."""

    def __init__(self, vm_name: str = "BantzSandboxVM", use_simulation: bool = True):
        self.vm_name = vm_name
        self.hyper_v = HyperVAdapter(use_simulation=use_simulation)
        self.connection = GuestConnection()
        self.guest_runner = GuestTaskRunner()

    @property
    def port_name(self) -> str:
        return "vm"

    async def start_vm(self, vm_name: str) -> bool:
        return await self.hyper_v.start_vm(vm_name)

    async def stop_vm(self, vm_name: str, force: bool = False) -> bool:
        return await self.hyper_v.stop_vm(vm_name, force=force)

    async def create_checkpoint(self, vm_name: str, checkpoint_name: str) -> str:
        ok = await self.hyper_v.checkpoint_vm(vm_name, checkpoint_name)
        return checkpoint_name if ok else ""

    async def revert_checkpoint(self, vm_name: str, checkpoint_name: str) -> bool:
        return await self.hyper_v.restore_checkpoint(vm_name, checkpoint_name)

    async def dispatch_to_guest(self, vm_name: str, guest_task: Dict[str, Any]) -> Dict[str, Any]:
        """Görev paketini HMAC imzalı zarfa koyar, doğrular ve VM içinde çalıştırır."""
        envelope = self.connection.pack_message(guest_task)
        unpacked = self.connection.unpack_message(envelope)
        if not unpacked:
            return {"success": False, "error": "Kimlik doğrulama hatası: HMAC imzası geçersiz!"}

        # VM içinde icra et
        result = await self.guest_runner.execute_guest_step(unpacked)
        return result

    async def execute(self, request: ToolRequest) -> ToolResult:
        """VM Yaşam Döngüsü:

        Kontrol et -> Başlat -> Checkpoint -> Gönder -> Sonucu al -> Kapat/Kaydet
        """
        try:
            # 1. VM Başlat
            await self.start_vm(self.vm_name)

            # 2. Checkpoint oluştur
            chk_name = f"chk_pre_{request.taskId[:8]}"
            await self.create_checkpoint(self.vm_name, chk_name)

            # 3. Görevi Guest Agent'a ilet
            guest_payload = {
                "taskId": request.taskId,
                "action": request.action,
                "params": request.parameters
            }
            guest_result = await self.dispatch_to_guest(self.vm_name, guest_payload)

            # 4. VM'yi durdur
            await self.stop_vm(self.vm_name)

            return ToolResult(
                requestId=request.requestId,
                taskId=request.taskId,
                success=guest_result.get("success", False),
                output=guest_result.get("output", {}),
                error=guest_result.get("error"),
                evidenceIds=guest_result.get("evidenceIds", [])
            )
        except Exception as e:
            return ToolResult(
                requestId=request.requestId,
                taskId=request.taskId,
                success=False,
                error=str(e)
            )
