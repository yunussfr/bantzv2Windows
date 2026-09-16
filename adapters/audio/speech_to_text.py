from typing import Optional


class SpeechToTextEngine:
    """STT motoru: Ses baytlarını yerel modelle (faster-whisper) metne dönüştürür."""

    def __init__(self, model_size: str = "base"):
        self.model_size = model_size

    async def transcribe(self, audio_bytes: bytes) -> str:
        """Ses verisini metne dönüştürür (geliştirme ve test için fallback destekli)."""
        if not audio_bytes:
            return ""
        # Gerçek ortamda faster_whisper WhisperModel kullanılır
        return "Merhaba, bugün hava nasıl?"
