import pytest
from packages.avatar.motion_engine import MotionEngine, SafeMotionType, AvatarState


def test_valid_motion_validation():
    valid_payload = {
        "description": "Avatar sevinçle zıplar",
        "target_state": "success",
        "commands": [
            {
                "command": "bounce",
                "duration_ms": 400,
                "parameters": {"intensity": 1.5, "count": 2}
            },
            {
                "command": "show_bubble",
                "duration_ms": 1000,
                "parameters": {"text": "Görev başarıyla tamamlandı!", "timeout_ms": 3000}
            }
        ]
    }
    sequence = MotionEngine.validate_motion_json(valid_payload)
    assert sequence.target_state == AvatarState.SUCCESS
    assert len(sequence.commands) == 2
    assert sequence.commands[0].command == SafeMotionType.BOUNCE


def test_malicious_script_rejected():
    malicious_payload = {
        "description": "Kötü niyetli hareket",
        "target_state": "working",
        "commands": [
            {
                "command": "move",
                "duration_ms": 500,
                "parameters": {"x": 10, "y": 20, "extra": "<script>alert('hack')</script>"}
            }
        ]
    }
    with pytest.raises(ValueError, match="Güvenlik ihlali"):
        MotionEngine.validate_motion_json(malicious_payload)


def test_unregistered_parameter_rejected():
    invalid_param_payload = {
        "description": "Geçersiz parametreli hareket",
        "target_state": "idle",
        "commands": [
            {
                "command": "fade",
                "duration_ms": 300,
                "parameters": {"opacity": 0.5, "unallowed_param": 123}
            }
        ]
    }
    with pytest.raises(ValueError, match="izin verilmeyen parametreler"):
        MotionEngine.validate_motion_json(invalid_param_payload)
