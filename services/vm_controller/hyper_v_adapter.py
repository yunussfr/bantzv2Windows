import asyncio
import subprocess
from typing import Dict, Any, Optional


class HyperVAdapter:
    """Windows Hyper-V yönetim adaptörü (PowerShell / WMI CLI).

    Eğer Hyper-V makinede yüklü veya aktif değilse (örneğin dev ortamında),
    simüle (mock) modda çalışarak sistemin tıkanmasını engeller.
    """

    def __init__(self, use_simulation: bool = True):
        self.use_simulation = use_simulation
        self._vm_states: Dict[str, str] = {}
        self._checkpoints: Dict[str, list[str]] = {}

    async def get_vm_state(self, vm_name: str) -> str:
        """VM durumunu döndürür: 'Running', 'Off', 'Saved'."""
        if self.use_simulation:
            return self._vm_states.get(vm_name, "Off")

        cmd = f"Get-VM -Name '{vm_name}' | Select-Object -ExpandProperty State"
        proc = await asyncio.create_subprocess_exec(
            "powershell.exe", "-NoProfile", "-Command", cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await proc.communicate()
        return stdout.decode().strip() or "Unknown"

    async def start_vm(self, vm_name: str) -> bool:
        if self.use_simulation:
            self._vm_states[vm_name] = "Running"
            return True

        cmd = f"Start-VM -Name '{vm_name}'"
        proc = await asyncio.create_subprocess_exec(
            "powershell.exe", "-NoProfile", "-Command", cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await proc.communicate()
        return proc.returncode == 0

    async def stop_vm(self, vm_name: str, force: bool = False) -> bool:
        if self.use_simulation:
            self._vm_states[vm_name] = "Off"
            return True

        param = "-TurnOff" if force else "-Save"
        cmd = f"Stop-VM -Name '{vm_name}' {param}"
        proc = await asyncio.create_subprocess_exec(
            "powershell.exe", "-NoProfile", "-Command", cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await proc.communicate()
        return proc.returncode == 0

    async def checkpoint_vm(self, vm_name: str, snapshot_name: str) -> bool:
        if self.use_simulation:
            if vm_name not in self._checkpoints:
                self._checkpoints[vm_name] = []
            self._checkpoints[vm_name].append(snapshot_name)
            return True

        cmd = f"Checkpoint-VM -Name '{vm_name}' -SnapshotName '{snapshot_name}'"
        proc = await asyncio.create_subprocess_exec(
            "powershell.exe", "-NoProfile", "-Command", cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await proc.communicate()
        return proc.returncode == 0

    async def restore_checkpoint(self, vm_name: str, snapshot_name: str) -> bool:
        if self.use_simulation:
            return snapshot_name in self._checkpoints.get(vm_name, [])

        cmd = f"Restore-VMSnapshot -Name '{snapshot_name}' -VMName '{vm_name}' -Confirm:$false"
        proc = await asyncio.create_subprocess_exec(
            "powershell.exe", "-NoProfile", "-Command", cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await proc.communicate()
        return proc.returncode == 0
