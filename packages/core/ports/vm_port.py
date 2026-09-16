from abc import abstractmethod
from typing import Dict, Any, Optional
from .base_port import BasePort


class VMPort(BasePort):
    @property
    def port_name(self) -> str:
        return "vm"

    @abstractmethod
    async def start_vm(self, vm_name: str) -> bool:
        """Sanal makineyi başlatır."""
        pass

    @abstractmethod
    async def stop_vm(self, vm_name: str, force: bool = False) -> bool:
        """Sanal makineyi durdurur."""
        pass

    @abstractmethod
    async def create_checkpoint(self, vm_name: str, checkpoint_name: str) -> str:
        """Görev öncesi anlık görüntü (checkpoint/snapshot) oluşturur."""
        pass

    @abstractmethod
    async def revert_checkpoint(self, vm_name: str, checkpoint_name: str) -> bool:
        """Sanal makineyi ilgili checkpoint'e geri sarar."""
        pass

    @abstractmethod
    async def dispatch_to_guest(self, vm_name: str, guest_task: Dict[str, Any]) -> Dict[str, Any]:
        """VM içerisindeki Guest Agent'a görev paketini güvenli kanaldan iletir."""
        pass
