import re
from typing import Optional


class TextToSpeechEngine:
    """TTS motoru: Düşünce etiketlerini ve markdown işaretlerini temizleyerek seslendirir."""

    @classmethod
    def clean_text_for_speech(cls, text: str) -> str:
        """<think>...</think>, markdown başlıkları, linkler ve kod bloklarını temizler."""
        # 1. <think> ve [CONTEXT:...] gibi iç monologları temizle
        text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"\[CONTEXT:.*?\]", "", text, flags=re.DOTALL | re.IGNORECASE)

        # 2. Markdown kod bloklarını (```...```) temizle
        text = re.sub(r"```.*?```", "kod bloğu atlandı.", text, flags=re.DOTALL)

        # 3. Markdown bağlantılarını [text](url) -> text haline getir
        text = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", text)

        # 4. Yıldız, kare, alt çizgi gibi markdown biçimlendirmelerini sadeleştir
        text = re.sub(r"[*#_`~>]", "", text)

        return text.strip()

    async def speak(self, text: str) -> str:
        clean_text = self.clean_text_for_speech(text)
        # Windows SAPI veya Piper simülasyonu
        # Gerçek ortamda pyttsx3 / piper.exe / XTTS çağrılır
        return clean_text
