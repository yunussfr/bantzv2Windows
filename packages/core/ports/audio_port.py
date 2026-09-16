from abc import abstractmethod
from typing import Optional
from .base_port import BasePort


class AudioPort(BasePort):
    @property
    def port_name(self) -> str:
        return "audio"

    @abstractmethod
    async def listen_push_to_talk(self) -> bytes:
        """Bas-konuş tuşu basılıyken mikrofon akışını yakalar."""
        pass

    @abstractmethod
    async def speech_to_text(self, audio_data: bytes) -> str:
        """Ses baytlarını metne çevirir (Whisper)."""
        pass

    @abstractmethod
    async def text_to_speech(self, text: str) -> None:
        """Metni seslendirir (Piper/XTTS) - iç monolog temizlenmiş olarak."""
        pass
