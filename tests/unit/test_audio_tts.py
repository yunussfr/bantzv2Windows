from adapters.audio.text_to_speech import TextToSpeechEngine


def test_clean_text_for_speech_strips_thinking():
    raw = "<think>Kullanıcı dosya arıyor, filesystem aracını çağırmalıyım.</think>Dosyayı buldum efendim."
    cleaned = TextToSpeechEngine.clean_text_for_speech(raw)
    assert cleaned == "Dosyayı buldum efendim."
    assert "think" not in cleaned


def test_clean_text_for_speech_strips_markdown():
    raw = "İşte liste:\n* **Öğe 1**: [link](http://test.com)\n* **Öğe 2**\n```python\nprint(1)\n```"
    cleaned = TextToSpeechEngine.clean_text_for_speech(raw)
    assert "```" not in cleaned
    assert "http://test.com" not in cleaned
    assert "Öğe 1: link" in cleaned
