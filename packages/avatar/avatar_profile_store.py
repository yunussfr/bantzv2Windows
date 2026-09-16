import json
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class AvatarProfile(BaseModel):
    profile_id: str = "default"
    image_path: Optional[str] = None
    image_type: str = "png"  # png, webp, gif, spritesheet
    position_x: int = 100
    position_y: int = 100
    scale: float = 1.0
    opacity: float = 1.0
    bubble_enabled: bool = True
    custom_animations: Dict[str, Any] = Field(default_factory=dict)


class AvatarProfileStore:
    """Avatar profil ayarlarını yerel diskte güvenle saklayan yönetici."""

    def __init__(self, storage_path: str = "data/avatar_profile.json"):
        self.storage_path = Path(storage_path)

    def load_profile(self) -> AvatarProfile:
        if not self.storage_path.exists():
            return AvatarProfile()
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return AvatarProfile.model_validate(data)
        except Exception:
            return AvatarProfile()

    def save_profile(self, profile: AvatarProfile) -> bool:
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(profile.model_dump(), f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False
