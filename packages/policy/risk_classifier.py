from typing import Dict, Any


class RiskClassifier:
    """Eylemin veya yeteneğin risk seviyesini sınıflandırır."""

    RISK_MAP = {
        "browser.read": "safe",
        "filesystem.read": "safe",
        "calendar.read": "safe",
        "email.read": "safe",
        "browser.form.fill": "moderate",
        "filesystem.write": "moderate",
        "process.run.safe": "moderate",
        "calendar.write": "moderate",
        "process.run.destructive": "destructive",
        "email.send": "destructive",
        "credential.use": "destructive",
    }

    @classmethod
    def classify(cls, capability: str, params: Dict[str, Any] = None) -> str:
        # Parametre bazlı dinamik denetim
        if params:
            cmd = str(params.get("command", "")).lower()
            if any(k in cmd for k in ["rm -rf", "format", "del /f", "shutdown"]):
                return "destructive"

        return cls.RISK_MAP.get(capability, "moderate")
