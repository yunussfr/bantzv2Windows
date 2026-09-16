from typing import Set, Dict, Any, Optional


class CapabilityRegistry:
    """Sistemde tanımlı izinli yetenekler (capabilities) listesi ve doğrulaması."""

    STANDARD_CAPABILITIES: Set[str] = {
        "browser.read",
        "browser.form.fill",
        "filesystem.read",
        "filesystem.write",
        "process.run.safe",
        "process.run.destructive",
        "email.read",
        "email.send",
        "calendar.read",
        "calendar.write",
        "credential.use",
    }

    def __init__(self, granted_capabilities: Optional[Set[str]] = None):
        self._granted = granted_capabilities if granted_capabilities is not None else set(self.STANDARD_CAPABILITIES)

    def is_granted(self, capability: str) -> bool:
        return capability in self._granted

    def register_capability(self, capability: str) -> None:
        self.STANDARD_CAPABILITIES.add(capability)
        self._granted.add(capability)

    def revoke_capability(self, capability: str) -> None:
        self._granted.discard(capability)
