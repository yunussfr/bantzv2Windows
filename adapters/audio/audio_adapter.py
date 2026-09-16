from typing import Optional, Dict, Any
from packages.core.ports.audio_port import AudioPort
from packages.contracts.tool_request import ToolRequest
from packages.contracts.tool_result import ToolResult
from .speech_to_text import SpeechToTextEngine
from .text_to_speech import TextToSpeechEngine


class WindowsAudioAdapter(AudioPort):
    """Windows ses adaptörü (Push-to-Talk, STT, TTS entegrasyonu)."""

    def __init__(self):
        self.stt = SpeechToTextEngine()
        self.tts = TextToSpeechEngine()
        self.is_recording = False

    @property
    def port_name(self) -> str:
        return "audio"

    async def listen_push_to_talk(self) -> bytes:
        # Bas-konuş tuşu dinleme simülasyonu
        return b"RIFF_SAMPLE_AUDIO_BYTES"

    async def speech_to_text(self, audio_data: bytes) -> str:
        return await self.stt.transcribe(audio_data)

    async def text_to_speech(self, text: str) -> None:
        await self.tts.speak(text)

    async def execute(self, request: ToolRequest) -> ToolResult:
        action = request.action
        if action == "speak":
            text = request.parameters.get("text", "")
            cleaned = await self.tts.speak(text)
            return ToolResult(
                requestId=request.requestId,
                taskId=request.taskId,
                success=True,
                output={"spoken_text": cleaned}
            )
        elif action == "transcribe":
            text = await self.speech_to_text(b"sample")
            return ToolResult(
                requestId=request.requestId,
                taskId=request.taskId,
                success=True,
                output={"transcribed_text": text}
            )
        else:
            return ToolResult(
                requestId=request.requestId,
                taskId=request.taskId,
                success=False,
                error=f"Bilinmeyen ses eylemi: {action}"
            )
