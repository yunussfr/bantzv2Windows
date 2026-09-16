from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, ValidationError


class AvatarState(str, Enum):
    IDLE = "idle"
    LISTENING = "listening"
    VOICE_CHAT = "voice_chat"
    THINKING = "thinking"
    WORKING = "working"
    SUCCESS = "success"
    ERROR = "error"
    WAITING_FOR_USER = "waiting_for_user"


class SafeMotionType(str, Enum):
    MOVE = "move"
    SCALE = "scale"
    ROTATE = "rotate"
    FADE = "fade"
    BOUNCE = "bounce"
    SHAKE = "shake"
    PULSE = "pulse"
    SHOW_BUBBLE = "show_bubble"
    PLAY_UPLOADED_ANIMATION = "play_uploaded_animation"


class MotionCommand(BaseModel):
    command: SafeMotionType
    duration_ms: int = Field(default=500, ge=50, le=5000)
    parameters: Dict[str, Any] = Field(default_factory=dict)


class AvatarMotionSequence(BaseModel):
    """LLM tarafından üretilen ve doğrulanmadan asla UI'a gönderilmeyen güvenli animasyon dizisi."""
    description: str
    target_state: Optional[AvatarState] = None
    commands: List[MotionCommand] = Field(default_factory=list)


class MotionEngine:
    """Güvenli hareket komutlarını doğrulayan ve zararlı kodları engelleyen motor."""

    ALLOWED_PARAMS = {
        SafeMotionType.MOVE: {"x", "y", "relative"},
        SafeMotionType.SCALE: {"scale_x", "scale_y"},
        SafeMotionType.ROTATE: {"degrees"},
        SafeMotionType.FADE: {"opacity"},
        SafeMotionType.BOUNCE: {"intensity", "count"},
        SafeMotionType.SHAKE: {"intensity", "count"},
        SafeMotionType.PULSE: {"scale", "count"},
        SafeMotionType.SHOW_BUBBLE: {"text", "timeout_ms"},
        SafeMotionType.PLAY_UPLOADED_ANIMATION: {"animation_name", "loop"},
    }

    @classmethod
    def validate_motion_json(cls, raw_data: Dict[str, Any]) -> AvatarMotionSequence:
        """JSON verisini şemaya göre doğrular. Kod enjeksiyonu şüphesi varsa hata verir."""
        # 1. Zararlı olabilecek dizgileri denetle (JS, powershell, eval vb.)
        raw_str = str(raw_data).lower()
        forbidden_patterns = ["<script", "javascript:", "eval(", "powershell", "cmd.exe", "exec("]
        for pattern in forbidden_patterns:
            if pattern in raw_str:
                raise ValueError(f"Güvenlik ihlali: Hareket komutunda yasaklı ifade tespit edildi: '{pattern}'")

        # 2. Pydantic şema doğrulaması
        sequence = AvatarMotionSequence.model_validate(raw_data)

        # 3. Parametre anahtar beyaz listesi doğrulaması
        for cmd in sequence.commands:
            allowed = cls.ALLOWED_PARAMS.get(cmd.command, set())
            extra_keys = set(cmd.parameters.keys()) - allowed
            if extra_keys:
                raise ValueError(f"'{cmd.command.value}' için izin verilmeyen parametreler: {extra_keys}")

        return sequence
