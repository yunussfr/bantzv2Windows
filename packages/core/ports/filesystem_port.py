from abc import abstractmethod
from typing import List, Optional
from .base_port import BasePort


class FileSystemPort(BasePort):
    @property
    def port_name(self) -> str:
        return "filesystem"

    @abstractmethod
    async def read_file(self, path: str) -> str:
        """İzinli dizindeki dosyayı okur."""
        pass

    @abstractmethod
    async def write_file(self, path: str, content: str) -> bool:
        """İzinli dizine dosya yazar."""
        pass

    @abstractmethod
    async def list_files(self, directory: str) -> List[str]:
        """İzinli dizindeki dosyaları listeler."""
        pass
