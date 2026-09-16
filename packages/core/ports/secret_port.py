from abc import abstractmethod
from typing import Optional
from .base_port import BasePort


class SecretPort(BasePort):
    @property
    def port_name(self) -> str:
        return "secret"

    @abstractmethod
    async def get_secret(self, credential_ref: str) -> Optional[str]:
        """Yalnızca yetkili adaptör çağrısında referans çözülür, asla loglanmaz."""
        pass

    @abstractmethod
    async def store_secret(self, key: str, secret_value: str) -> bool:
        """Sırrı güvenli yerel kasaya yazar (DPAPI/Credential Manager)."""
        pass
